"""Deployment schemas."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.core.domain_enums import DeploymentStatus


class DeploymentCreate(BaseModel):
    run_id: int = Field(..., gt=0)
    environment: str = Field(..., min_length=1, max_length=50)
    cloud_provider: str = Field(..., min_length=1, max_length=50)
    status: DeploymentStatus = DeploymentStatus.PENDING
    started_at: datetime | None = None
    finished_at: datetime | None = None


class DeploymentUpdate(BaseModel):
    status: DeploymentStatus | None = None
    environment: str | None = Field(None, min_length=1, max_length=50)
    cloud_provider: str | None = Field(None, min_length=1, max_length=50)
    started_at: datetime | None = None
    finished_at: datetime | None = None


class DeploymentRead(DeploymentCreate):
    id: int

    model_config = {"from_attributes": True}
