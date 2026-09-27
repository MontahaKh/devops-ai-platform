"""Authorization helpers for project-owned resources."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.models.deployment import Deployment
from app.models.generated_file import GeneratedFile
from app.models.pipeline import Pipeline
from app.models.project import Project
from app.models.run import Run
from app.models.user import User
from app.models.validation import Validation


def _check_owner(owner_id: int, current_user: User) -> None:
    if owner_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def get_project_or_404(db: Session, project_id: int, current_user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _check_owner(project.owner_id, current_user)
    return project


def get_pipeline_or_404(db: Session, pipeline_id: int, current_user: User) -> Pipeline:
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")
    get_project_or_404(db, pipeline.project_id, current_user)
    return pipeline


def get_run_or_404(db: Session, run_id: int, current_user: User) -> Run:
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    pipeline = get_pipeline_or_404(db, run.pipeline_id, current_user)
    return run


def get_validation_or_404(db: Session, validation_id: int, current_user: User) -> Validation:
    item = db.query(Validation).filter(Validation.id == validation_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation not found")
    get_run_or_404(db, item.run_id, current_user)
    return item


def get_deployment_or_404(db: Session, deployment_id: int, current_user: User) -> Deployment:
    item = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")
    get_run_or_404(db, item.run_id, current_user)
    return item


def get_generated_file_or_404(
    db: Session, file_id: int, current_user: User
) -> GeneratedFile:
    item = db.query(GeneratedFile).filter(GeneratedFile.id == file_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Generated file not found"
        )
    get_run_or_404(db, item.run_id, current_user)
    return item


def can_access_run(db: Session, run_id: int, current_user: User) -> bool:
    if current_user.role == UserRole.ADMIN.value:
        return True
    return (
        db.query(Run)
        .join(Pipeline)
        .join(Project)
        .filter(Run.id == run_id, Project.owner_id == current_user.id)
        .first()
        is not None
    )
