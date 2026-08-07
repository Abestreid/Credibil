from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FinancialReportDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_idno: str
    year: int
    period: str
    company_name: str | None = None
    caem_code: str | None = None
    caem_description: str | None = None
    business_category: str | None = None
    # P&L summary
    revenue: float | None = None
    expenses: float | None = None
    profit: float | None = None
    # Balance sheet summary
    total_assets: float | None = None
    total_liabilities: float | None = None
    equity: float | None = None
    # P&L detail
    cost_of_goods_sold: float | None = None
    distribution_expenses: float | None = None
    admin_expenses: float | None = None
    other_operating_expenses: float | None = None
    financial_income: float | None = None
    financial_expenses: float | None = None
    income_tax: float | None = None
    # Balance sheet detail
    current_assets: float | None = None
    fixed_assets: float | None = None
    inventories: float | None = None
    trade_receivables: float | None = None
    cash_and_banks: float | None = None
    short_term_debt: float | None = None
    long_term_debt: float | None = None
    share_capital: float | None = None
    # Cash flow
    operating_cash_flow: float | None = None
    investing_cash_flow: float | None = None
    financing_cash_flow: float | None = None
    # Misc
    employees_count: int | None = None
    source_url: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)
    fetched_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class GrowthMetricsDTO(BaseModel):
    current_year: int
    previous_year: int | None = None
    revenue_growth_pct: float | None = None
    profit_growth_pct: float | None = None
    assets_growth_pct: float | None = None
    employees_growth_pct: float | None = None


class MarginMetricsDTO(BaseModel):
    year: int
    gross_margin_pct: float | None = None
    net_margin_pct: float | None = None
    operating_margin_pct: float | None = None
    expense_ratio_pct: float | None = None


class LiquidityMetricsDTO(BaseModel):
    year: int
    current_ratio: float | None = None
    debt_to_equity_ratio: float | None = None
    autonomy_ratio: float | None = None
    debt_ratio: float | None = None
    equity_ratio: float | None = None


class EmployeeDynamicsDTO(BaseModel):
    year: int
    employees_count: int | None = None
    yoy_change: int | None = None
    yoy_change_pct: float | None = None


class ChartDataPoint(BaseModel):
    year: int
    value: float | int


class CompanyAnalyticsDTO(BaseModel):
    company_idno: str
    company_name: str | None = None
    years_analyzed: list[int] = Field(default_factory=list)
    growth: list[GrowthMetricsDTO] = Field(default_factory=list)
    margins: list[MarginMetricsDTO] = Field(default_factory=list)
    liquidity: list[LiquidityMetricsDTO] = Field(default_factory=list)
    employee_dynamics: list[EmployeeDynamicsDTO] = Field(default_factory=list)
    revenue_chart: list[ChartDataPoint] = Field(default_factory=list)
    profit_chart: list[ChartDataPoint] = Field(default_factory=list)
    assets_chart: list[ChartDataPoint] = Field(default_factory=list)
    employees_chart: list[ChartDataPoint] = Field(default_factory=list)
