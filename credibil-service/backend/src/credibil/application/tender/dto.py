from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TenderDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ocid: str
    title: str
    description: str | None = None
    status: str
    status_details: str | None = None
    procurement_method: str | None = None
    procurement_method_details: str | None = None
    main_category: str | None = None
    cpv_code: str | None = None
    cpv_description: str | None = None
    buyer_idno: str | None = None
    buyer_name: str | None = None
    value_amount: float | None = None
    value_currency: str | None = None
    budget_amount: float | None = None
    budget_currency: str | None = None
    is_eu_funded: bool = False
    tender_start_date: date | None = None
    tender_end_date: date | None = None
    contract_start_date: date | None = None
    contract_end_date: date | None = None
    published_date: datetime | None = None
    source_url: str | None = None
    created_at: datetime
    updated_at: datetime


class TenderAwardDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tender_id: UUID | None = None
    tender_ocid: str
    ocds_award_id: str | None = None
    status: str
    status_details: str | None = None
    award_date: date | None = None
    value_amount: float | None = None
    value_currency: str | None = None
    supplier_idno: str | None = None
    supplier_name: str | None = None
    related_lots: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class TenderBidDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tender_id: UUID | None = None
    tender_ocid: str
    ocds_bid_id: str | None = None
    status: str
    bid_date: date | None = None
    value_amount: float | None = None
    value_currency: str | None = None
    tenderer_idno: str | None = None
    tenderer_name: str | None = None
    related_lots: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class TenderStatisticsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_tenders: int = 0
    active_tenders: int = 0
    completed_tenders: int = 0
    tenders_by_status: dict[str, int] = Field(default_factory=dict)
    tenders_by_method: dict[str, int] = Field(default_factory=dict)
    tenders_by_category: dict[str, int] = Field(default_factory=dict)
    tenders_by_year: dict[str, int] = Field(default_factory=dict)
    total_value: float = 0
    average_value: float = 0
    total_budget: float = 0
    eu_funded_count: int = 0


class AwardStatisticsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_awards: int = 0
    successful_awards: int = 0
    pending_awards: int = 0
    total_award_value: float = 0
    average_award_value: float = 0
    awards_by_status: dict[str, int] = Field(default_factory=dict)
    awards_by_year: dict[str, int] = Field(default_factory=dict)
    top_suppliers: list[dict[str, Any]] = Field(default_factory=list)


class WinRateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_idno: str
    tenders_participated: int = 0
    awards_won: int = 0
    win_rate_percent: float = 0


class MethodBreakdownDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    method: str
    count: int
    total_value: float = 0


class TimelinePointDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: str
    count: int


class TenderAnalyticsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str
    statistics: TenderStatisticsDTO = Field(default_factory=TenderStatisticsDTO)
    award_statistics: AwardStatisticsDTO = Field(default_factory=AwardStatisticsDTO)
    win_rate: WinRateDTO = Field(default_factory=WinRateDTO)
    method_breakdown: list[MethodBreakdownDTO] = Field(default_factory=list)
    timeline: list[TimelinePointDTO] = Field(default_factory=list)
