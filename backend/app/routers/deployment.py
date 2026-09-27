"""Deployment routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.dependencies.authorization import (
    can_access_run,
    get_deployment_or_404,
    get_run_or_404,
)
from app.database import get_db
from app.models.run import Run
from app.models.user import User
from app.schemas.deployment import DeploymentCreate, DeploymentRead, DeploymentUpdate
from app.services.deployment import DeploymentService

router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.post("", response_model=DeploymentRead, status_code=status.HTTP_201_CREATED)
def create_deployment(
    payload: DeploymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_run_or_404(db, payload.run_id, current_user)
    return DeploymentService.create(db, payload)


@router.get("", response_model=list[DeploymentRead])
def list_deployments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = DeploymentService.list(db, skip, limit)
    return [item for item in items if can_access_run(db, item.run_id, current_user)]


@router.get("/{deployment_id}", response_model=DeploymentRead)
def get_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_deployment_or_404(db, deployment_id, current_user)


@router.put("/{deployment_id}", response_model=DeploymentRead)
def update_deployment(
    deployment_id: int,
    payload: DeploymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_deployment_or_404(db, deployment_id, current_user)
    item = DeploymentService.update(db, deployment_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return item


@router.delete("/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_deployment_or_404(db, deployment_id, current_user)
    if not DeploymentService.delete(db, deployment_id):
        raise HTTPException(status_code=404, detail="Deployment not found")
