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
"""User service."""
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service for user operations."""

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """Create a new user."""
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hash_password(user_create.password),
            is_active=True,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """List all users with pagination."""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User | None:
        """Update user."""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        for key, value in update_data.items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user."""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False
        db.delete(db_user)
        db.commit()
        return True
