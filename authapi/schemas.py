"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr
    username: str
    password: str
    full_name: str | None = None

    @field_validator("username")
    @classmethod
    def username_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip()


class UserRead(BaseModel):
    """Schema for reading a user."""

    id: int
    email: str
    username: str
    full_name: str | None = None
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    full_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None


class Token(BaseModel):
    """Auth token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Refresh token request."""

    refresh_token: str


class Message(BaseModel):
    """Generic message response."""

    detail: str


class PasswordResetRequest(BaseModel):
    """Password reset request."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirm."""

    token: str
    new_password: str
