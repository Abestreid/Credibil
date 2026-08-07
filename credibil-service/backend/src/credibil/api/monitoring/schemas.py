from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MonitoringApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    meta: Any = None
    request_id: str | None = None


class AddMonitoringRequest(BaseModel):
    idno: str = Field(..., min_length=13, max_length=13, pattern=r"^\d{13}$")


class MonitoredCompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Any
    idno: str
    company_id: Any = None
    company_name: str | None = None
    is_active: bool
    created_at: Any = None
    last_checked_at: Any = None
    last_change_at: Any = None


class ChangeEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Any
    idno: str
    category: str
    field: str
    description: str
    old_value: str | None = None
    new_value: str | None = None
    detected_at: Any = None


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Any
    idno: str
    company_name: str | None = None
    change_count: int
    categories: list[str] = Field(default_factory=list)
    summary: str | None = None
    is_read: bool
    created_at: Any = None
