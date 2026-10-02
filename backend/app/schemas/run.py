"""Pipeline run schemas."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.core.domain_enums import RunStatus
from app.schemas.validation import ValidationRead


class RunCreate(BaseModel):
    pipeline_id: int = Field(..., gt=0)
    max_retries: int = Field(default=2, ge=0, le=10)
    timeout_seconds: int = Field(default=300, gt=0, le=86400)


class RunUpdate(BaseModel):
    status: RunStatus | None = None
    error_summary: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class RunRead(BaseModel):
    id: int
    pipeline_id: int
    status: RunStatus
    error_summary: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    correlation_id: str
    retry_count: int
    max_retries: int
    timeout_seconds: int
    celery_task_id: str | None

    model_config = {"from_attributes": True}


class RunLogsRead(BaseModel):
    run_id: int
    status: RunStatus
    validations: list[ValidationRead]
