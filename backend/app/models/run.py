"""Pipeline run model."""
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Run(Base):
    """One execution of a pipeline."""

    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    pipeline_id: Mapped[int] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), index=True, nullable=False
    )
    correlation_id: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), default="pending", server_default="pending", index=True, nullable=False
    )
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=2, server_default="2", nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(
        Integer, default=300, server_default="300", nullable=False
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="runs")
    validations: Mapped[list["Validation"]] = relationship(
        "Validation", back_populates="run", cascade="all, delete-orphan"
    )
    deployments: Mapped[list["Deployment"]] = relationship(
        "Deployment", back_populates="run", cascade="all, delete-orphan"
    )
    generated_files: Mapped[list["GeneratedFile"]] = relationship(
        "GeneratedFile", back_populates="run", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'success', 'failed', 'cancelled')",
            name="ck_runs_status",
        ),
        CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="ck_runs_timestamps",
        ),
        CheckConstraint("retry_count >= 0", name="ck_runs_retry_count"),
        CheckConstraint("max_retries >= 0", name="ck_runs_max_retries"),
        CheckConstraint("timeout_seconds > 0", name="ck_runs_timeout_seconds"),
    )
