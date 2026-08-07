from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccreditationDTO(BaseModel):
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
    last_synced: Any = None
    created_at: Any = None
    updated_at: Any = None


class AccreditationStatisticsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)
    by_category: dict[str, int] = Field(default_factory=dict)
    by_standard: dict[str, int] = Field(default_factory=dict)


class AccreditationSyncResultDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sync_id: UUID
    status: str
    records_created: int = 0
    records_updated: int = 0
    records_unchanged: int = 0
    records_failed: int = 0
