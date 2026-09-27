"""Validation schemas."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.core.domain_enums import ValidationStatus


class ValidationCreate(BaseModel):
    run_id: int = Field(..., gt=0)
    validation_type: str = Field(..., min_length=1, max_length=50)
    status: ValidationStatus
    message: str | None = None
    executed_at: datetime


class ValidationUpdate(BaseModel):
    status: ValidationStatus | None = None
    message: str | None = None
    executed_at: datetime | None = None


class ValidationRead(ValidationCreate):
    id: int

    model_config = {"from_attributes": True}
