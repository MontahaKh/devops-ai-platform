"""Project routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.security import get_current_user
from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project import ProjectService
from app.services.user import UserService

router = APIRouter(prefix="/projects", tags=["projects"])


def ensure_project_access(project: Project, current_user: User) -> None:
    if (
        project.owner_id != current_user.id
        and current_user.role != UserRole.ADMIN.value
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    project_create: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new project."""
    project = ProjectService.create_project(db, project_create, current_user.id)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all projects."""
    if current_user.role == UserRole.ADMIN.value:
        projects = ProjectService.list_projects(db, skip=skip, limit=limit)
    else:
        projects = ProjectService.list_projects_by_owner(
            db, current_user.id, skip=skip, limit=limit
        )
    return projects


@router.get("/owner/{owner_id}", response_model=list[ProjectRead])
def list_user_projects(
    owner_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List projects by owner."""
    if owner_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    # Verify owner exists
    owner = UserService.get_user_by_id(db, owner_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner user not found",
        )

    projects = ProjectService.list_projects_by_owner(
        db, owner_id, skip=skip, limit=limit
    )
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project by ID."""
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    ensure_project_access(project, current_user)
    return project


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project."""
    existing_project = ProjectService.get_project_by_id(db, project_id)
    if not existing_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    ensure_project_access(existing_project, current_user)
    project = ProjectService.update_project(db, project_id, project_update)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete project."""
    existing_project = ProjectService.get_project_by_id(db, project_id)
    if not existing_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    ensure_project_access(existing_project, current_user)
    success = ProjectService.delete_project(db, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return None
