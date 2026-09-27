"""Pipeline routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.security import get_current_user
from app.dependencies.authorization import get_pipeline_or_404, get_project_or_404
from app.database import get_db
from app.models.pipeline import Pipeline
from app.models.project import Project
from app.models.user import User
from app.schemas.pipeline import PipelineCreate, PipelineRead, PipelineUpdate
from app.services.pipeline import PipelineService

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.post("", response_model=PipelineRead, status_code=status.HTTP_201_CREATED)
def create_pipeline(
    payload: PipelineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_project_or_404(db, payload.project_id, current_user)
    return PipelineService.create(db, payload)


@router.get("", response_model=list[PipelineRead])
def list_pipelines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.ADMIN.value:
        return PipelineService.list(db, skip, limit)
    return (
        db.query(Pipeline)
        .join(Project)
        .filter(Project.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{pipeline_id}", response_model=PipelineRead)
def get_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_pipeline_or_404(db, pipeline_id, current_user)


@router.put("/{pipeline_id}", response_model=PipelineRead)
def update_pipeline(
    pipeline_id: int,
    payload: PipelineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_pipeline_or_404(db, pipeline_id, current_user)
    item = PipelineService.update(db, pipeline_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return item


@router.delete("/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_pipeline_or_404(db, pipeline_id, current_user)
    if not PipelineService.delete(db, pipeline_id):
        raise HTTPException(status_code=404, detail="Pipeline not found")
