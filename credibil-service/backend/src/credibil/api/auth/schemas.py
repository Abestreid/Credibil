from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Any
    email: str
    full_name: str
    role: str
    status: str
    tenant_id: str | None = None
    last_login_at: str | None = None
    created_at: Any
    updated_at: Any

    @field_serializer("id")
    def _ser_id(self, v: Any) -> str:
        return str(v)

    @field_serializer("created_at", "updated_at")
    def _ser_dt(self, v: Any) -> str:
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthApiResponse(BaseModel):
    success: bool = True
    data: dict | list | None = None
    error: dict | None = None
    request_id: str | None = None
