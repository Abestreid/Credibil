from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class ReportPeriod(StrEnum):
    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"


class FinancialReport:
    """One financial report for a company for a given year/period.

    All monetary values are in MDL (leu) as reported by Depozitar.
    """

    def __init__(
        self,
        *,
        report_id: UUID | None = None,
        company_idno: str,
        year: int,
        period: ReportPeriod = ReportPeriod.ANNUAL,
        company_name: str | None = None,
        caem_code: str | None = None,
        caem_description: str | None = None,
        business_category: str | None = None,
        # P&L summary
        revenue: float | None = None,
        expenses: float | None = None,
        profit: float | None = None,
        # Balance sheet summary
        total_assets: float | None = None,
        total_liabilities: float | None = None,
        equity: float | None = None,
        # P&L detail
        cost_of_goods_sold: float | None = None,
        distribution_expenses: float | None = None,
        admin_expenses: float | None = None,
        other_operating_expenses: float | None = None,
        financial_income: float | None = None,
        financial_expenses: float | None = None,
        income_tax: float | None = None,
        # Balance sheet detail
        current_assets: float | None = None,
        fixed_assets: float | None = None,
        inventories: float | None = None,
        trade_receivables: float | None = None,
        cash_and_banks: float | None = None,
        short_term_debt: float | None = None,
        long_term_debt: float | None = None,
        share_capital: float | None = None,
        # Cash flow (anexa4)
        operating_cash_flow: float | None = None,
        investing_cash_flow: float | None = None,
        financing_cash_flow: float | None = None,
        # Misc
        employees_count: int | None = None,
        source_url: str | None = None,
        raw_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        fetched_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = report_id or new_id()
        self.company_idno = company_idno
        self.year = year
        self.period = period
        self.company_name = company_name
        self.caem_code = caem_code
        self.caem_description = caem_description
        self.business_category = business_category
        self.revenue = revenue
        self.expenses = expenses
        self.profit = profit
        self.total_assets = total_assets
        self.total_liabilities = total_liabilities
        self.equity = equity
        self.cost_of_goods_sold = cost_of_goods_sold
        self.distribution_expenses = distribution_expenses
        self.admin_expenses = admin_expenses
        self.other_operating_expenses = other_operating_expenses
        self.financial_income = financial_income
        self.financial_expenses = financial_expenses
        self.income_tax = income_tax
        self.current_assets = current_assets
        self.fixed_assets = fixed_assets
        self.inventories = inventories
        self.trade_receivables = trade_receivables
        self.cash_and_banks = cash_and_banks
        self.short_term_debt = short_term_debt
        self.long_term_debt = long_term_debt
        self.share_capital = share_capital
        self.operating_cash_flow = operating_cash_flow
        self.investing_cash_flow = investing_cash_flow
        self.financing_cash_flow = financing_cash_flow
        self.employees_count = employees_count
        self.source_url = source_url
        self.raw_data = raw_data or {}
        self.metadata = metadata or {}
        self.fetched_at = fetched_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, **kwargs: Any) -> None:
        allowed = {
            "company_name", "caem_code", "caem_description", "business_category",
            "revenue", "expenses", "profit", "total_assets", "total_liabilities", "equity",
            "cost_of_goods_sold", "distribution_expenses", "admin_expenses",
            "other_operating_expenses", "financial_income", "financial_expenses", "income_tax",
            "current_assets", "fixed_assets", "inventories", "trade_receivables",
            "cash_and_banks", "short_term_debt", "long_term_debt", "share_capital",
            "operating_cash_flow", "investing_cash_flow", "financing_cash_flow",
            "employees_count", "source_url", "raw_data", "metadata", "fetched_at",
        }
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<FinancialReport idno={self.company_idno} year={self.year} "
            f"revenue={self.revenue} profit={self.profit}>"
        )
