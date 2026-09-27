"""Deployment service."""
from sqlalchemy.orm import Session

from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate, DeploymentUpdate


class DeploymentService:
    @staticmethod
    def create(db: Session, payload: DeploymentCreate) -> Deployment:
        item = Deployment(**payload.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get(db: Session, item_id: int) -> Deployment | None:
        return db.query(Deployment).filter(Deployment.id == item_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> list[Deployment]:
        return db.query(Deployment).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, item_id: int, payload: DeploymentUpdate) -> Deployment | None:
        item = DeploymentService.get(db, item_id)
        if not item:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, item_id: int) -> bool:
        item = DeploymentService.get(db, item_id)
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True
