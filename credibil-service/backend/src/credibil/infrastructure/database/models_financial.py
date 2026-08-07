from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from credibil.infrastructure.database.base import Base


class FinancialReportModel(Base):
    __tablename__ = "financial_reports"
    __table_args__ = ({"schema": None},)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_idno = Column(String(13), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    period = Column(String(50), nullable=False, default="annual")
    company_name = Column(String(500), nullable=True)
    caem_code = Column(String(10), nullable=True)
    caem_description = Column(Text, nullable=True)
    business_category = Column(String(200), nullable=True)
    # P&L summary
    revenue = Column(Float, nullable=True)
    expenses = Column(Float, nullable=True)
    profit = Column(Float, nullable=True)
    # Balance sheet summary
    total_assets = Column(Float, nullable=True)
    total_liabilities = Column(Float, nullable=True)
    equity = Column(Float, nullable=True)
    # P&L detail
    cost_of_goods_sold = Column(Float, nullable=True)
    distribution_expenses = Column(Float, nullable=True)
    admin_expenses = Column(Float, nullable=True)
    other_operating_expenses = Column(Float, nullable=True)
    financial_income = Column(Float, nullable=True)
    financial_expenses = Column(Float, nullable=True)
    income_tax = Column(Float, nullable=True)
    # Balance sheet detail
    current_assets = Column(Float, nullable=True)
    fixed_assets = Column(Float, nullable=True)
    inventories = Column(Float, nullable=True)
    trade_receivables = Column(Float, nullable=True)
    cash_and_banks = Column(Float, nullable=True)
    short_term_debt = Column(Float, nullable=True)
    long_term_debt = Column(Float, nullable=True)
    share_capital = Column(Float, nullable=True)
    # Cash flow
    operating_cash_flow = Column(Float, nullable=True)
    investing_cash_flow = Column(Float, nullable=True)
    financing_cash_flow = Column(Float, nullable=True)
    # Misc
    employees_count = Column(Integer, nullable=True)
    source_url = Column(Text, nullable=True)
    raw_data = Column(JSONB, nullable=False, default=dict)
    metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
    fetched_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<FinancialReportModel idno={self.company_idno} year={self.year}>"
