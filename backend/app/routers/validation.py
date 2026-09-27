"""Validation routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.dependencies.authorization import (
    can_access_run,
    get_run_or_404,
    get_validation_or_404,
)
from app.database import get_db
from app.models.run import Run
from app.models.user import User
from app.schemas.validation import ValidationCreate, ValidationRead, ValidationUpdate
from app.services.validation import ValidationService

router = APIRouter(prefix="/validations", tags=["validations"])


@router.post("", response_model=ValidationRead, status_code=status.HTTP_201_CREATED)
def create_validation(
    payload: ValidationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_run_or_404(db, payload.run_id, current_user)
    return ValidationService.create(db, payload)


@router.get("", response_model=list[ValidationRead])
def list_validations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = ValidationService.list(db, skip, limit)
    return [item for item in items if can_access_run(db, item.run_id, current_user)]


@router.get("/{validation_id}", response_model=ValidationRead)
def get_validation(
    validation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_validation_or_404(db, validation_id, current_user)


@router.put("/{validation_id}", response_model=ValidationRead)
def update_validation(
    validation_id: int,
    payload: ValidationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_validation_or_404(db, validation_id, current_user)
    item = ValidationService.update(db, validation_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Validation not found")
    return item


@router.delete("/{validation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_validation(
    validation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_validation_or_404(db, validation_id, current_user)
    if not ValidationService.delete(db, validation_id):
        raise HTTPException(status_code=404, detail="Validation not found")
