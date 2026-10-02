"""Pipeline run execution service."""
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.core.lifecycle import ensure_run_transition, utc_now
from app.models.run import Run
from app.models.validation import Validation
from app.schemas.pipeline import PipelineDefinition


TERMINAL_STATUSES = {"success", "failed", "cancelled"}


def _write_terraform_files(root: Path, run: Run) -> list[str]:
    terraform_files = [item for item in run.generated_files if item.file_type == "terraform"]
    for item in terraform_files:
        destination = (root / item.path).resolve()
        if root != destination and root not in destination.parents:
            raise ValueError(f"Generated file path escapes the validation workspace: {item.path}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(item.content, encoding="utf-8")
    return [item.path for item in terraform_files]


def _create_validation(db: Session, run: Run) -> Validation:
    item = Validation(
        run_id=run.id,
        validation_type="terraform_validate",
        status="running",
        executed_at=utc_now(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _execute_terraform_validation(
    db: Session, run: Run, definition: PipelineDefinition
) -> Validation:
    validation = _create_validation(db, run)
    unsupported_steps = [
        step.name for step in definition.steps if step.action == "deploy"
    ]
    if unsupported_steps:
        validation.status = "failed"
        validation.message = (
            "Deployment steps are not executable yet: " + ", ".join(unsupported_steps)
        )
        validation.exit_code = 2
        db.commit()
        raise RuntimeError(validation.message)
    terraform_files = [item for item in run.generated_files if item.file_type == "terraform"]
    required_paths = {
        item.path for item in definition.required_files if item.required
    }
    for step in definition.steps:
        required_paths.update(step.required_files)
    available_paths = {item.path for item in terraform_files}
    missing_paths = sorted(required_paths - available_paths)
    if missing_paths:
        validation.status = "failed"
        validation.message = f"Missing required Terraform files: {', '.join(missing_paths)}"
        validation.exit_code = 2
        db.commit()
        raise RuntimeError(validation.message)

    if not terraform_files:
        validation.status = "success"
        validation.message = "No Terraform files were provided; validation was skipped."
        validation.exit_code = 0
        db.commit()
        return validation

    terraform = shutil.which("terraform")
    if not terraform:
        validation.status = "failed"
        validation.message = "Terraform executable was not found on the worker."
        validation.exit_code = 127
        db.commit()
        raise RuntimeError(validation.message)

    commands: list[list[str]] = []
    strategy = definition.validation_strategy.terraform_commands
    if "fmt" in strategy:
        commands.append([terraform, "fmt", "-check", "-diff", "-no-color"])
    if "validate" in strategy or "plan" in strategy:
        commands.append(
            [terraform, "init", "-backend=false", "-input=false", "-no-color"]
        )
    if "validate" in strategy:
        commands.append([terraform, "validate", "-no-color"])
    if "plan" in strategy:
        commands.append(
            [terraform, "plan", "-input=false", "-refresh=false", "-no-color"]
        )

    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    command_parts: list[str] = []
    try:
        with tempfile.TemporaryDirectory(prefix=f"devops-run-{run.id}-") as directory:
            root = Path(directory).resolve()
            _write_terraform_files(root, run)
            for command in commands:
                command_parts.append(" ".join(command))
                result = subprocess.run(
                    command,
                    cwd=root,
                    capture_output=True,
                    text=True,
                    timeout=run.timeout_seconds,
                    check=False,
                )
                stdout_parts.append(result.stdout or "")
                stderr_parts.append(result.stderr or "")
                if result.returncode != 0:
                    validation.status = "failed"
                    validation.message = "Terraform validation command failed."
                    validation.exit_code = result.returncode
                    break
            else:
                validation.status = "success"
                validation.message = (
                    "Terraform validation and plan completed successfully."
                    if "plan" in strategy
                    else "Terraform validation completed successfully."
                )
                validation.exit_code = 0
    except subprocess.TimeoutExpired as exc:
        validation.status = "failed"
        validation.message = "Terraform validation timed out."
        validation.exit_code = 124
        stdout_parts.append(str(exc.stdout or ""))
        stderr_parts.append(str(exc.stderr or ""))
    finally:
        validation.stdout = "\n".join(stdout_parts)
        validation.stderr = "\n".join(stderr_parts)
        validation.command = "\n".join(command_parts)
        db.commit()

    if validation.status == "failed":
        raise RuntimeError(validation.message or "Terraform validation failed")
    return validation


def execute_run_in_session(db: Session, run_id: int) -> str:
    """Execute a run and persist its lifecycle state.

    The current executor validates the pipeline definition and provides a stable
    worker boundary. Terraform and Ansible commands will be added behind this
    function in the next execution phase.
    """
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise ValueError(f"Run {run_id} not found")
    if run.status == "cancelled":
        return run.status
    if run.status in TERMINAL_STATUSES:
        return run.status

    ensure_run_transition(run.status, "running")
    run.status = "running"
    run.started_at = run.started_at or utc_now()
    db.commit()

    try:
        definition = PipelineDefinition.model_validate(run.pipeline.definition or {})
    except ValidationError as exc:
        raise RuntimeError(f"Invalid pipeline definition: {exc}") from exc
    if definition.parameters.get("simulate_failure") is True:
        raise RuntimeError("Pipeline definition requested a simulated failure")
    _execute_terraform_validation(db, run, definition)

    ensure_run_transition(run.status, "success")
    run.status = "success"
    run.error_summary = None
    run.finished_at = utc_now()
    db.commit()
    return run.status


def execute_run(run_id: int) -> str:
    """Execute a run using a worker-owned database session."""
    db: Session = SessionLocal()
    try:
        return execute_run_in_session(db, run_id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def mark_run_failed(run_id: int, message: str) -> None:
    """Persist a terminal failure for a run."""
    db: Session = SessionLocal()
    try:
        run = db.query(Run).filter(Run.id == run_id).first()
        if run and run.status in {"pending", "running"}:
            ensure_run_transition(run.status, "failed")
            run.status = "failed"
            run.error_summary = message[:4000]
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


def prepare_run_retry(run_id: int, message: str) -> bool:
    """Move a failed attempt back to pending when retries remain."""
    db: Session = SessionLocal()
    try:
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run or run.status not in {"pending", "failed"}:
            return False
        if run.retry_count >= run.max_retries:
            return False
        run.retry_count += 1
        run.status = "pending"
        run.error_summary = message[:4000]
        run.started_at = None
        run.finished_at = None
        db.commit()
        return True
    finally:
        db.close()
