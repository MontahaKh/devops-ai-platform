"""Generated file schemas."""
from datetime import datetime

from pydantic import BaseModel, Field


class GeneratedFileCreate(BaseModel):
    run_id: int = Field(..., gt=0)
    file_type: str = Field(..., min_length=1, max_length=30)
    path: str = Field(..., min_length=1, max_length=500)
    content: str
    version: int = Field(default=1, ge=1)
    is_user_edited: bool = False


class GeneratedFileUpdate(BaseModel):
    file_type: str | None = Field(None, min_length=1, max_length=30)
    path: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = None
    version: int | None = Field(None, ge=1)
    is_user_edited: bool | None = None


class GeneratedFileRead(GeneratedFileCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
