"""Pipeline run routes."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.config import settings
from app.core.security import get_current_user
from app.dependencies.authorization import get_pipeline_or_404, get_run_or_404
from app.database import get_db
from app.models.pipeline import Pipeline
from app.models.project import Project
from app.models.run import Run
from app.models.user import User
from app.schemas.run import RunCreate, RunLogsRead, RunRead, RunUpdate
from app.services.execution import execute_run_in_session
from app.services.run import RunService
from app.workers.celery_app import celery_app
from app.workers.tasks import execute_run_task

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunRead, status_code=status.HTTP_201_CREATED)
def create_run(
    payload: RunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_pipeline_or_404(db, payload.pipeline_id, current_user)
    return RunService.create(db, payload)


@router.post("/{run_id}/execute", response_model=RunRead)
def execute_run_endpoint(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a pending run after its generated files have been prepared."""
    run = get_run_or_404(db, run_id, current_user)
    if run.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending runs can be executed",
        )
    if not any(item.file_type == "terraform" for item in run.generated_files):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="At least one Terraform file is required before execution",
        )

    if settings.task_queue_enabled:
        try:
            task = execute_run_task.apply_async(
                args=[run.id],
                time_limit=run.timeout_seconds,
                soft_time_limit=max(run.timeout_seconds - 5, 1),
            )
            run.celery_task_id = task.id
            db.commit()
            db.refresh(run)
        except Exception as exc:
            run.status = "failed"
            run.error_summary = "Unable to enqueue pipeline run"
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Execution queue is unavailable",
            ) from exc
    else:
        try:
            execute_run_in_session(db, run.id)
        except Exception as exc:
            db.refresh(run)
            if run.status in {"pending", "running"}:
                run.status = "failed"
                run.error_summary = str(exc)[:4000]
                run.finished_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(run)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

    db.refresh(run)
    return run


@router.get("/{run_id}/logs", response_model=RunLogsRead)
def get_run_logs(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return validation logs for an accessible run."""
    run = get_run_or_404(db, run_id, current_user)
    return RunLogsRead(
        run_id=run.id,
        status=run.status,
        validations=run.validations,
    )


@router.get("", response_model=list[RunRead])
def list_runs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.ADMIN.value:
        return RunService.list(db, skip, limit)
    return (
        db.query(Run)
        .join(Pipeline)
        .join(Project)
        .filter(Project.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{run_id}", response_model=RunRead)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_run_or_404(db, run_id, current_user)


@router.put("/{run_id}", response_model=RunRead)
def update_run(
    run_id: int,
    payload: RunUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_run_or_404(db, run_id, current_user)
    try:
        item = RunService.update(db, run_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not item:
        raise HTTPException(status_code=404, detail="Run not found")
    return item


@router.delete("/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_run_or_404(db, run_id, current_user)
    if not RunService.delete(db, run_id):
        raise HTTPException(status_code=404, detail="Run not found")


@router.post("/{run_id}/cancel", response_model=RunRead)
def cancel_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a pending or running pipeline run."""
    run = get_run_or_404(db, run_id, current_user)
    if run.status in {"success", "failed", "cancelled"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Run is already finished",
        )
    if run.celery_task_id:
        celery_app.control.revoke(run.celery_task_id, terminate=True)
    run.status = "cancelled"
    run.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run
