"""Pipeline run service."""
from sqlalchemy.orm import Session

from app.core.lifecycle import ensure_run_transition, ensure_timestamp_order, utc_now
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
        values = payload.model_dump(exclude_unset=True)
        target_status = values.get("status", item.status)
        ensure_run_transition(item.status, target_status)
        started_at = values.get("started_at", item.started_at)
        finished_at = values.get("finished_at", item.finished_at)
        if target_status == "running" and started_at is None:
            started_at = utc_now()
            values["started_at"] = started_at
        if target_status in {"success", "failed", "cancelled"} and finished_at is None:
            finished_at = utc_now()
            values["finished_at"] = finished_at
        ensure_timestamp_order(started_at, finished_at)
        for key, value in values.items():
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
