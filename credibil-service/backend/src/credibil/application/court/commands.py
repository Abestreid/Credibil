from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from uuid import UUID


class SearchByIdnoCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str


class SearchByNameCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class SearchCasesCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    query: str
    court_slug: str | None = None
    case_type: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    limit: int = 50


class GetCaseQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: UUID


class GetCaseByNumberQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_number: str


class GetCasesByIdnoQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str
    role: str | None = None
    limit: int = 100
    offset: int = 0


class GetCaseAnalyticsQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str


class GetHearingsQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_number: str
    limit: int = 50
    offset: int = 0


class GetUpcomingHearingsQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str
    limit: int = 50


class SyncHearingsCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    court_slug: str | None = None
