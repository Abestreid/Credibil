from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from uuid import UUID


class SyncFinancialReportCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_idno: str
    year: int


class SyncMultiYearCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_idno: str
    years: list[int]


class GetFinancialReportQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    report_id: UUID


class GetFinancialReportsByIdnoQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_idno: str
    limit: int = 100
    offset: int = 0


class GetCompanyAnalyticsQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_idno: str
