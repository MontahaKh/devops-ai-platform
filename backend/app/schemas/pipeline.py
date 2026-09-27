"""Pipeline schemas."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.core.domain_enums import PipelineStatus


class PipelineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    project_id: int = Field(..., gt=0)
    definition: dict = Field(default_factory=dict)
    status: PipelineStatus = PipelineStatus.ACTIVE


class PipelineUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    definition: dict | None = None
    status: PipelineStatus | None = None


class PipelineRead(BaseModel):
    id: int
    name: str
    description: str | None
    project_id: int
    definition: dict
    status: PipelineStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
