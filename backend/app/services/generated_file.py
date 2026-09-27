"""Generated file service."""
from sqlalchemy.orm import Session

from app.models.generated_file import GeneratedFile
from app.schemas.generated_file import GeneratedFileCreate, GeneratedFileUpdate


class GeneratedFileService:
    @staticmethod
    def create(db: Session, payload: GeneratedFileCreate) -> GeneratedFile:
        item = GeneratedFile(**payload.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get(db: Session, item_id: int) -> GeneratedFile | None:
        return db.query(GeneratedFile).filter(GeneratedFile.id == item_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> list[GeneratedFile]:
        return db.query(GeneratedFile).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, item_id: int, payload: GeneratedFileUpdate) -> GeneratedFile | None:
        item = GeneratedFileService.get(db, item_id)
        if not item:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, item_id: int) -> bool:
        item = GeneratedFileService.get(db, item_id)
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True
