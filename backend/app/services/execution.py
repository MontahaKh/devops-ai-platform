"""Pipeline run execution service."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.run import Run


TERMINAL_STATUSES = {"success", "failed", "cancelled"}


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

    run.status = "running"
    run.started_at = run.started_at or datetime.now(timezone.utc)
    db.commit()

    definition = run.pipeline.definition or {}
    if definition.get("simulate_failure") is True:
        raise RuntimeError("Pipeline definition requested a simulated failure")

    run.status = "success"
    run.error_summary = None
    run.finished_at = datetime.now(timezone.utc)
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
        if run and run.status != "cancelled":
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
        if not run or run.status == "cancelled":
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
