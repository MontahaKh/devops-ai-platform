"""Deployment schemas."""
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.core.domain_enums import DeploymentStatus


class DeploymentCreate(BaseModel):
    run_id: int = Field(..., gt=0)
    environment: str = Field(..., min_length=1, max_length=50)
    cloud_provider: str = Field(..., min_length=1, max_length=50)
    status: DeploymentStatus = DeploymentStatus.PENDING
    started_at: datetime | None = None
    finished_at: datetime | None = None

    @model_validator(mode="after")
    def validate_timestamps(self):
        if self.started_at and self.finished_at and self.finished_at < self.started_at:
            raise ValueError("finished_at must be greater than or equal to started_at")
        return self


class DeploymentUpdate(BaseModel):
    status: DeploymentStatus | None = None
    environment: str | None = Field(None, min_length=1, max_length=50)
    cloud_provider: str | None = Field(None, min_length=1, max_length=50)
    started_at: datetime | None = None
    finished_at: datetime | None = None

    @model_validator(mode="after")
    def validate_timestamps(self):
        if self.started_at and self.finished_at and self.finished_at < self.started_at:
            raise ValueError("finished_at must be greater than or equal to started_at")
        return self


class DeploymentRead(DeploymentCreate):
    id: int

    model_config = {"from_attributes": True}
