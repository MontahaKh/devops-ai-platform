"""Pipeline service."""
from sqlalchemy.orm import Session

from app.models.pipeline import Pipeline
from app.schemas.pipeline import PipelineCreate, PipelineUpdate


class PipelineService:
    @staticmethod
    def create(db: Session, payload: PipelineCreate) -> Pipeline:
        values = payload.model_dump(mode="json")
        item = Pipeline(**values)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get(db: Session, item_id: int) -> Pipeline | None:
        return db.query(Pipeline).filter(Pipeline.id == item_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> list[Pipeline]:
        return db.query(Pipeline).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, item_id: int, payload: PipelineUpdate) -> Pipeline | None:
        item = PipelineService.get(db, item_id)
        if not item:
            return None
        values = payload.model_dump(mode="json", exclude_unset=True)
        for key, value in values.items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, item_id: int) -> bool:
        item = PipelineService.get(db, item_id)
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True
