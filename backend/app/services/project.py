"""Project service."""
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service for project operations."""

    @staticmethod
    def create_project(db: Session, project_create: ProjectCreate, owner_id: int) -> Project:
        """Create a new project."""
        db_project = Project(
            name=project_create.name,
            description=project_create.description,
            owner_id=owner_id,
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    @staticmethod
    def get_project_by_id(db: Session, project_id: int) -> Project | None:
        """Get project by ID."""
        return db.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def list_projects(db: Session, skip: int = 0, limit: int = 100) -> list[Project]:
        """List all projects with pagination."""
        return db.query(Project).offset(skip).limit(limit).all()

    @staticmethod
    def list_projects_by_owner(
        db: Session, owner_id: int, skip: int = 0, limit: int = 100
    ) -> list[Project]:
        """List projects by owner."""
        return (
            db.query(Project)
            .filter(Project.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_project(db: Session, project_id: int, project_update: ProjectUpdate) -> Project | None:
        """Update project."""
        db_project = ProjectService.get_project_by_id(db, project_id)
        if not db_project:
            return None

        update_data = project_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)

        db.commit()
        db.refresh(db_project)
        return db_project

    @staticmethod
    def delete_project(db: Session, project_id: int) -> bool:
        """Delete project."""
        db_project = ProjectService.get_project_by_id(db, project_id)
        if not db_project:
            return False
        db.delete(db_project)
        db.commit()
        return True
