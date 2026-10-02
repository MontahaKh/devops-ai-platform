"""Generated file service."""
import ntpath
from pathlib import PurePosixPath

from sqlalchemy.orm import Session

from app.models.generated_file import GeneratedFile
from app.schemas.generated_file import GeneratedFileCreate, GeneratedFileUpdate


MAX_FILE_CONTENT_BYTES = 1_048_576
TERRAFORM_EXTENSIONS = (".tf", ".tf.json")


def validate_generated_file_values(
    *,
    file_type: str,
    path: str,
    content: str,
) -> None:
    """Validate file metadata before it is persisted or executed."""
    if not content.strip():
        raise ValueError("Generated file content must not be empty")
    if len(content.encode("utf-8")) > MAX_FILE_CONTENT_BYTES:
        raise ValueError("Generated file content exceeds the 1 MiB limit")

    if "\\" in path:
        raise ValueError("Generated file path must use forward slashes")
    if ntpath.splitdrive(path)[0]:
        raise ValueError("Generated file path must be relative")

    normalized_path = PurePosixPath(path)
    if normalized_path.is_absolute() or not normalized_path.parts:
        raise ValueError("Generated file path must be relative")
    if any(part in {"", ".", ".."} for part in normalized_path.parts):
        raise ValueError("Generated file path contains an invalid path segment")

    if file_type == "terraform" and not path.endswith(TERRAFORM_EXTENSIONS):
        raise ValueError("Terraform files must use .tf or .tf.json extensions")


class GeneratedFileService:
    @staticmethod
    def create(db: Session, payload: GeneratedFileCreate) -> GeneratedFile:
        validate_generated_file_values(
            file_type=payload.file_type,
            path=payload.path,
            content=payload.content,
        )
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
        values = payload.model_dump(exclude_unset=True)
        validate_generated_file_values(
            file_type=values.get("file_type", item.file_type),
            path=values.get("path", item.path),
            content=values.get("content", item.content),
        )
        for key, value in values.items():
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
