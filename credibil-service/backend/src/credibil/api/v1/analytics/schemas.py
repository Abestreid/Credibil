from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CompanySummaryResponse(BaseModel):
    idno: str
    name_ro: str | None = None
    name_ru: str | None = None
    status: str | None = None
    legal_form: str | None = None
    caem: str | None = None
    caem_description: str | None = None
    legal_address: str | None = None
    registration_date: str | None = None
    founder_count: int = 0
    director_count: int = 0
    tax_debt: float | None = None


class RelationshipNodeResponse(BaseModel):
    id: str
    label: str
    node_type: str
    idno: str | None = None
    idnp: str | None = None


class RelationshipEdgeResponse(BaseModel):
    source: str
    target: str
    relationship_type: str
    is_active: bool = True
    start_date: str | None = None


class RelationshipGraphResponse(BaseModel):
    nodes: list[RelationshipNodeResponse] = Field(default_factory=list)
    edges: list[RelationshipEdgeResponse] = Field(default_factory=list)
    total_nodes: int = 0
    total_edges: int = 0


class TimelineEntryResponse(BaseModel):
    date: str
    event_type: str
    title: str
    description: str | None = None
    source: str | None = None


class RiskIndicatorResponse(BaseModel):
    category: str
    level: str
    score: float | None = None
    factors: list[str] = Field(default_factory=list)
    details: str | None = None


class SanctionsIndicatorResponse(BaseModel):
    is_sanctioned: bool = False
    sanctions_count: int = 0
    active_sanctions: int = 0
    sanction_types: list[str] = Field(default_factory=list)
    lists: list[str] = Field(default_factory=list)
    latest_entry_date: str | None = None


class GrowthMetricsResponse(BaseModel):
    current_year: int
    previous_year: int | None = None
    revenue_growth_pct: float | None = None
    profit_growth_pct: float | None = None
    assets_growth_pct: float | None = None
    employees_growth_pct: float | None = None


class MarginMetricsResponse(BaseModel):
    year: int
    gross_margin_pct: float | None = None
    net_margin_pct: float | None = None
    operating_margin_pct: float | None = None
    expense_ratio_pct: float | None = None


class LiquidityMetricsResponse(BaseModel):
    year: int
    current_ratio: float | None = None
    debt_to_equity_ratio: float | None = None
    autonomy_ratio: float | None = None
    debt_ratio: float | None = None
    equity_ratio: float | None = None


class EmployeeDynamicsResponse(BaseModel):
    year: int
    employees_count: int | None = None
    yoy_change: int | None = None
    yoy_change_pct: float | None = None


class ChartDataPointResponse(BaseModel):
    year: int
    value: float | int


class FinancialAnalyticsResponse(BaseModel):
    company_idno: str
    company_name: str | None = None
    years_analyzed: list[int] = Field(default_factory=list)
    growth: list[GrowthMetricsResponse] = Field(default_factory=list)
    margins: list[MarginMetricsResponse] = Field(default_factory=list)
    liquidity: list[LiquidityMetricsResponse] = Field(default_factory=list)
    employee_dynamics: list[EmployeeDynamicsResponse] = Field(default_factory=list)
    revenue_chart: list[ChartDataPointResponse] = Field(default_factory=list)
    profit_chart: list[ChartDataPointResponse] = Field(default_factory=list)
    assets_chart: list[ChartDataPointResponse] = Field(default_factory=list)
    employees_chart: list[ChartDataPointResponse] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    summary: CompanySummaryResponse | None = None
    financial: FinancialAnalyticsResponse | None = None
    court_statistics: dict[str, Any] = Field(default_factory=dict)
    court_judges: list[dict[str, Any]] = Field(default_factory=list)
    court_distribution: list[dict[str, Any]] = Field(default_factory=list)
    court_timeline: list[dict[str, Any]] = Field(default_factory=list)
    tender_statistics: dict[str, Any] = Field(default_factory=dict)
    tender_awards: dict[str, Any] = Field(default_factory=dict)
    tender_win_rate: dict[str, Any] = Field(default_factory=dict)
    tender_methods: list[dict[str, Any]] = Field(default_factory=list)
    tender_timeline: list[dict[str, Any]] = Field(default_factory=list)
    relationship_graph: RelationshipGraphResponse = Field(default_factory=RelationshipGraphResponse)
    timeline: list[TimelineEntryResponse] = Field(default_factory=list)
    risk_indicators: list[RiskIndicatorResponse] = Field(default_factory=list)
    sanctions: SanctionsIndicatorResponse = Field(default_factory=SanctionsIndicatorResponse)


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    meta: Any = None
    request_id: str | None = None
