"""Authentication schemas."""

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Schema for login request."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """Schema for register request."""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8)


class TokenPayload(BaseModel):
    """Schema for JWT payload."""

    sub: str
    username: str
    exp: int


class TokenResponse(BaseModel):
    """Schema for login response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Schema for logout request."""

    pass


class LogoutResponse(BaseModel):
    """Schema for logout response."""

    message: str = "Successfully logged out"
