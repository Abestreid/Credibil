from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

VALID_SCOPES = ["companies", "enforcement", "court", "relationships", "*"]


class CreateKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Human-readable label")
    scopes: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Any of: companies, enforcement, court, relationships, or * for all",
    )
    rate_limit: int = Field(default=1000, ge=1, le=1_000_000, description="Requests per hour")
    expires_at: datetime | None = None


class IssuedKeyResponse(BaseModel):
    id: Any
    name: str
    api_key: str = Field(..., description="The raw key — shown ONCE. Store it securely.")
    key_prefix: str
    scopes: list[str]
    rate_limit: int
    expires_at: datetime | None = None


class KeyListItem(BaseModel):
    id: Any
    name: str
    key_prefix: str
    scopes: list[str]
    rate_limit: int
    status: str
    last_used_at: datetime | None = None
    created_at: datetime | None = None


class ApiKeyApiResponse(BaseModel):
    success: bool = True
    data: Any = None
