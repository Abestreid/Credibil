from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccreditationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_name: str
    director_name: str | None = None
    address: str | None = None
    phone: str | None = None
    fax: str | None = None
    email: str | None = None
    certificate_number: str
    category: str
    standard: str
    status: str
    issue_date: str | None = None
    expiry_date: str | None = None
    scope: str | None = None
    certificate_url: str | None = None
    annex_urls: list[dict[str, str]] = Field(default_factory=list)
    remarks: str | None = None
    country_code: str
    source_url: str | None = None
    last_synced: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class AccreditationStatisticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)
    by_category: dict[str, int] = Field(default_factory=dict)
    by_standard: dict[str, int] = Field(default_factory=dict)


class AccreditationSyncResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sync_id: UUID
    status: str
    records_created: int = 0
    records_updated: int = 0
    records_unchanged: int = 0
    records_failed: int = 0


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    meta: Any = None
    request_id: str | None = None
