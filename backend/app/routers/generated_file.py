"""Generated file routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.dependencies.authorization import (
    can_access_run,
    get_generated_file_or_404,
    get_run_or_404,
)
from app.database import get_db
from app.models.run import Run
from app.models.user import User
from app.schemas.generated_file import GeneratedFileCreate, GeneratedFileRead, GeneratedFileUpdate
from app.services.generated_file import GeneratedFileService

router = APIRouter(prefix="/generated-files", tags=["generated-files"])


@router.post("", response_model=GeneratedFileRead, status_code=status.HTTP_201_CREATED)
def create_generated_file(
    payload: GeneratedFileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_run_or_404(db, payload.run_id, current_user)
    return GeneratedFileService.create(db, payload)


@router.get("", response_model=list[GeneratedFileRead])
def list_generated_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = GeneratedFileService.list(db, skip, limit)
    return [item for item in items if can_access_run(db, item.run_id, current_user)]


@router.get("/{file_id}", response_model=GeneratedFileRead)
def get_generated_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_generated_file_or_404(db, file_id, current_user)


@router.put("/{file_id}", response_model=GeneratedFileRead)
def update_generated_file(
    file_id: int,
    payload: GeneratedFileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_generated_file_or_404(db, file_id, current_user)
    item = GeneratedFileService.update(db, file_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Generated file not found")
    return item


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_generated_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_generated_file_or_404(db, file_id, current_user)
    if not GeneratedFileService.delete(db, file_id):
        raise HTTPException(status_code=404, detail="Generated file not found")
