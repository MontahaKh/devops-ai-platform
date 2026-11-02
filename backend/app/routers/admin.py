"""Administrator-only platform statistics."""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.security import require_role
from app.database import get_db
from app.models.project import Project
from app.models.run import Run
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> dict[str, int]:
    """Return aggregate platform statistics for administrators."""
    return {
        "users": db.query(func.count(User.id)).scalar() or 0,
        "projects": db.query(func.count(Project.id)).scalar() or 0,
        "successful_runs": db.query(func.count(Run.id)).filter(Run.status == "success").scalar() or 0,
        "failed_runs": db.query(func.count(Run.id)).filter(Run.status == "failed").scalar() or 0,
    }
