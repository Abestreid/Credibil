from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from datetime import date, datetime
    from uuid import UUID


class CourtCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_number: str
    case_type: str
    court_name: str
    court_type: str
    court_slug: str | None = None
    registration_date: date | None = None
    decision_date: date | None = None
    status: str
    plaintiff_name: str | None = None
    plaintiff_idno: str | None = None
    defendant_name: str | None = None
    defendant_idno: str | None = None
    judge_name: str | None = None
    subject_matter: str | None = None
    decision_summary: str | None = None
    source_url: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)
    fetched_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CourtHearingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID | None = None
    case_number: str
    hearing_date: date
    hearing_time: str | None = None
    court_name: str | None = None
    department: str | None = None
    room: str | None = None
    judge_name: str | None = None
    hearing_type: str | None = None
    outcome: str | None = None
    source_url: str | None = None
    created_at: datetime
    updated_at: datetime


class CaseStatisticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_cases: int = 0
    active_cases: int = 0
    closed_cases: int = 0
    cases_by_type: dict[str, int] = Field(default_factory=dict)
    cases_by_court_type: dict[str, int] = Field(default_factory=dict)
    cases_by_status: dict[str, int] = Field(default_factory=dict)
    cases_by_year: dict[str, int] = Field(default_factory=dict)
    as_plaintiff: int = 0
    as_defendant: int = 0


class JudgeFrequencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    judge_name: str
    case_count: int


class CourtDistributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    court_name: str
    case_count: int


class TimelinePointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: str
    count: int


class CaseAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str
    statistics: CaseStatisticsResponse = Field(default_factory=CaseStatisticsResponse)
    top_judges: list[JudgeFrequencyResponse] = Field(default_factory=list)
    court_distribution: list[CourtDistributionResponse] = Field(default_factory=list)
    timeline: list[TimelinePointResponse] = Field(default_factory=list)


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    meta: Any = None
    request_id: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    court_slug: str | None = None
    case_type: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    limit: int = Field(default=50, ge=1, le=200)


class SyncHearingsRequest(BaseModel):
    court_slug: str | None = None
