"""User schemas for API."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.core.enums import UserRole


class UserCreate(BaseModel):
    """Schema for creating a user."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)


class UserRead(BaseModel):
    """Schema for reading a user."""

    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChangeRoleRequest(BaseModel):
    """Schema for changing a user's role."""

    role: UserRole = Field(..., description="The new role for the user")
