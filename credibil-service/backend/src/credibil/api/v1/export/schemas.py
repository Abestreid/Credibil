from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ExportErrorResponse(BaseModel):
    detail: str


class CompanyExportData(BaseModel):
    """Aggregated company data for export."""

    company: dict[str, Any]
    persons: list[dict[str, Any]]
    dashboard: dict[str, Any] | None = None


class PersonExportData(BaseModel):
    """Aggregated person data for export."""

    person: dict[str, Any]
    connected_companies: list[dict[str, Any]]
    total_companies: int = 0
    active_companies: int = 0
    liquidated_companies: int = 0
