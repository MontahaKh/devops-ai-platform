"""Validation model."""
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Validation(Base):
    """Validation result produced during a pipeline run."""

    __tablename__ = "validations"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("runs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    validation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    stdout: Mapped[str | None] = mapped_column(Text, nullable=True)
    stderr: Mapped[str | None] = mapped_column(Text, nullable=True)
    command: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    exit_code: Mapped[int | None] = mapped_column(nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    run: Mapped["Run"] = relationship("Run", back_populates="validations")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'success', 'failed', 'cancelled')",
            name="ck_validations_status",
        ),
    )
