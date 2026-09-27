"""Validation service."""
from sqlalchemy.orm import Session

from app.models.validation import Validation
from app.schemas.validation import ValidationCreate, ValidationUpdate


class ValidationService:
    @staticmethod
    def create(db: Session, payload: ValidationCreate) -> Validation:
        item = Validation(**payload.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get(db: Session, item_id: int) -> Validation | None:
        return db.query(Validation).filter(Validation.id == item_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> list[Validation]:
        return db.query(Validation).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, item_id: int, payload: ValidationUpdate) -> Validation | None:
        item = ValidationService.get(db, item_id)
        if not item:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, item_id: int) -> bool:
        item = ValidationService.get(db, item_id)
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True
