"""Pipeline run service."""
from sqlalchemy.orm import Session

from app.models.run import Run
from app.schemas.run import RunCreate, RunUpdate


class RunService:
    @staticmethod
    def create(db: Session, payload: RunCreate) -> Run:
        item = Run(**payload.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get(db: Session, item_id: int) -> Run | None:
        return db.query(Run).filter(Run.id == item_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> list[Run]:
        return db.query(Run).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, item_id: int, payload: RunUpdate) -> Run | None:
        item = RunService.get(db, item_id)
        if not item:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, item_id: int) -> bool:
        item = RunService.get(db, item_id)
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True
