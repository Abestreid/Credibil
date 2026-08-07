from __future__ import annotations

from pydantic import BaseModel, Field


class SanctionsSearchRequest(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=200, description="Company or person name to search"
    )
    limit: int = Field(default=10, ge=1, le=50)


class SanctionsEntryResponse(BaseModel):
    target_name: str
    sanction_type: str
    status: str
    list_name: str | None = None
    country_code: str | None = None
    reason: str | None = None
    program: str | None = None
    metadata: dict | None = None


class SanctionsBatchRequest(BaseModel):
    names: list[str] = Field(..., min_length=1, max_length=100)
    only_sanctioned: bool = Field(default=True)


class SanctionsCheckResponse(BaseModel):
    company_name: str
    is_sanctioned: bool
    matches: list[SanctionsEntryResponse]
    checked_at: str
