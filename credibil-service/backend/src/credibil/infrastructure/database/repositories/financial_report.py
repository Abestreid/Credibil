from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from credibil.domain.financial import FinancialReport, ReportPeriod
from credibil.infrastructure.database.models_financial import FinancialReportModel
from credibil.ports.repositories.financial_report import FinancialReportRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


def _to_entity(model: FinancialReportModel) -> FinancialReport:
    return FinancialReport(
        report_id=model.id,
        company_idno=model.company_idno,
        year=model.year,
        period=ReportPeriod(model.period),
        company_name=model.company_name,
        caem_code=model.caem_code,
        caem_description=model.caem_description,
        business_category=model.business_category,
        revenue=model.revenue,
        expenses=model.expenses,
        profit=model.profit,
        total_assets=model.total_assets,
        total_liabilities=model.total_liabilities,
        equity=model.equity,
        cost_of_goods_sold=model.cost_of_goods_sold,
        distribution_expenses=model.distribution_expenses,
        admin_expenses=model.admin_expenses,
        other_operating_expenses=model.other_operating_expenses,
        financial_income=model.financial_income,
        financial_expenses=model.financial_expenses,
        income_tax=model.income_tax,
        current_assets=model.current_assets,
        fixed_assets=model.fixed_assets,
        inventories=model.inventories,
        trade_receivables=model.trade_receivables,
        cash_and_banks=model.cash_and_banks,
        short_term_debt=model.short_term_debt,
        long_term_debt=model.long_term_debt,
        share_capital=model.share_capital,
        operating_cash_flow=model.operating_cash_flow,
        investing_cash_flow=model.investing_cash_flow,
        financing_cash_flow=model.financing_cash_flow,
        employees_count=model.employees_count,
        source_url=model.source_url,
        raw_data=model.raw_data,
        metadata=model.metadata_,
        fetched_at=model.fetched_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_model(entity: FinancialReport) -> FinancialReportModel:
    return FinancialReportModel(
        id=entity.id,
        company_idno=entity.company_idno,
        year=entity.year,
        period=entity.period,
        company_name=entity.company_name,
        caem_code=entity.caem_code,
        caem_description=entity.caem_description,
        business_category=entity.business_category,
        revenue=entity.revenue,
        expenses=entity.expenses,
        profit=entity.profit,
        total_assets=entity.total_assets,
        total_liabilities=entity.total_liabilities,
        equity=entity.equity,
        cost_of_goods_sold=entity.cost_of_goods_sold,
        distribution_expenses=entity.distribution_expenses,
        admin_expenses=entity.admin_expenses,
        other_operating_expenses=entity.other_operating_expenses,
        financial_income=entity.financial_income,
        financial_expenses=entity.financial_expenses,
        income_tax=entity.income_tax,
        current_assets=entity.current_assets,
        fixed_assets=entity.fixed_assets,
        inventories=entity.inventories,
        trade_receivables=entity.trade_receivables,
        cash_and_banks=entity.cash_and_banks,
        short_term_debt=entity.short_term_debt,
        long_term_debt=entity.long_term_debt,
        share_capital=entity.share_capital,
        operating_cash_flow=entity.operating_cash_flow,
        investing_cash_flow=entity.investing_cash_flow,
        financing_cash_flow=entity.financing_cash_flow,
        employees_count=entity.employees_count,
        source_url=entity.source_url,
        raw_data=entity.raw_data,
        metadata_=entity.metadata,
        fetched_at=entity.fetched_at,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class SQLAlchemyFinancialReportRepository(FinancialReportRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, report_id: UUID) -> FinancialReport | None:
        result = await self._session.execute(
            select(FinancialReportModel).where(FinancialReportModel.id == report_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_by_idno_and_year(self, idno: str, year: int) -> FinancialReport | None:
        result = await self._session.execute(
            select(FinancialReportModel).where(
                FinancialReportModel.company_idno == idno,
                FinancialReportModel.year == year,
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_by_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[FinancialReport]:
        result = await self._session.execute(
            select(FinancialReportModel)
            .where(FinancialReportModel.company_idno == idno)
            .order_by(FinancialReportModel.year.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def save(self, report: FinancialReport) -> FinancialReport:
        import json

        from sqlalchemy import text

        stmt = text("""
            INSERT INTO financial_reports (
                id, company_idno, year, period, company_name, caem_code,
                caem_description, business_category,
                revenue, expenses, profit, total_assets, total_liabilities, equity,
                cost_of_goods_sold, distribution_expenses, admin_expenses,
                other_operating_expenses, financial_income, financial_expenses, income_tax,
                current_assets, fixed_assets, inventories, trade_receivables,
                cash_and_banks, short_term_debt, long_term_debt, share_capital,
                operating_cash_flow, investing_cash_flow, financing_cash_flow,
                employees_count, source_url, raw_data, metadata, fetched_at
            ) VALUES (
                :id, :company_idno, :year, :period, :company_name, :caem_code,
                :caem_description, :business_category,
                :revenue, :expenses, :profit, :total_assets, :total_liabilities, :equity,
                :cost_of_goods_sold, :distribution_expenses, :admin_expenses,
                :other_operating_expenses, :financial_income, :financial_expenses, :income_tax,
                :current_assets, :fixed_assets, :inventories, :trade_receivables,
                :cash_and_banks, :short_term_debt, :long_term_debt, :share_capital,
                :operating_cash_flow, :investing_cash_flow, :financing_cash_flow,
                :employees_count, :source_url, CAST(:raw_data AS jsonb), CAST(:metadata AS jsonb), :fetched_at
            )
            ON CONFLICT (company_idno, year) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                caem_code = EXCLUDED.caem_code,
                caem_description = EXCLUDED.caem_description,
                business_category = EXCLUDED.business_category,
                revenue = EXCLUDED.revenue,
                expenses = EXCLUDED.expenses,
                profit = EXCLUDED.profit,
                total_assets = EXCLUDED.total_assets,
                total_liabilities = EXCLUDED.total_liabilities,
                equity = EXCLUDED.equity,
                cost_of_goods_sold = EXCLUDED.cost_of_goods_sold,
                distribution_expenses = EXCLUDED.distribution_expenses,
                admin_expenses = EXCLUDED.admin_expenses,
                other_operating_expenses = EXCLUDED.other_operating_expenses,
                financial_income = EXCLUDED.financial_income,
                financial_expenses = EXCLUDED.financial_expenses,
                income_tax = EXCLUDED.income_tax,
                current_assets = EXCLUDED.current_assets,
                fixed_assets = EXCLUDED.fixed_assets,
                inventories = EXCLUDED.inventories,
                trade_receivables = EXCLUDED.trade_receivables,
                cash_and_banks = EXCLUDED.cash_and_banks,
                short_term_debt = EXCLUDED.short_term_debt,
                long_term_debt = EXCLUDED.long_term_debt,
                share_capital = EXCLUDED.share_capital,
                operating_cash_flow = EXCLUDED.operating_cash_flow,
                investing_cash_flow = EXCLUDED.investing_cash_flow,
                financing_cash_flow = EXCLUDED.financing_cash_flow,
                employees_count = EXCLUDED.employees_count,
                source_url = EXCLUDED.source_url,
                raw_data = EXCLUDED.raw_data,
                metadata = EXCLUDED.metadata,
                fetched_at = EXCLUDED.fetched_at,
                updated_at = NOW()
        """)
        await self._session.execute(stmt, {
            "id": str(report.id),
            "company_idno": report.company_idno,
            "year": report.year,
            "period": report.period.value,
            "company_name": report.company_name,
            "caem_code": report.caem_code,
            "caem_description": report.caem_description,
            "business_category": report.business_category,
            "revenue": report.revenue,
            "expenses": report.expenses,
            "profit": report.profit,
            "total_assets": report.total_assets,
            "total_liabilities": report.total_liabilities,
            "equity": report.equity,
            "cost_of_goods_sold": report.cost_of_goods_sold,
            "distribution_expenses": report.distribution_expenses,
            "admin_expenses": report.admin_expenses,
            "other_operating_expenses": report.other_operating_expenses,
            "financial_income": report.financial_income,
            "financial_expenses": report.financial_expenses,
            "income_tax": report.income_tax,
            "current_assets": report.current_assets,
            "fixed_assets": report.fixed_assets,
            "inventories": report.inventories,
            "trade_receivables": report.trade_receivables,
            "cash_and_banks": report.cash_and_banks,
            "short_term_debt": report.short_term_debt,
            "long_term_debt": report.long_term_debt,
            "share_capital": report.share_capital,
            "operating_cash_flow": report.operating_cash_flow,
            "investing_cash_flow": report.investing_cash_flow,
            "financing_cash_flow": report.financing_cash_flow,
            "employees_count": report.employees_count,
            "source_url": report.source_url,
            "raw_data": json.dumps(report.raw_data, default=str),
            "metadata": json.dumps(report.metadata, default=str),
            "fetched_at": report.fetched_at,
        })
        return report

    async def delete(self, report_id: UUID) -> None:
        model = await self._session.get(FinancialReportModel, report_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_reports(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> list[FinancialReport]:
        stmt = select(FinancialReportModel)
        if filters:
            for key, value in filters.items():
                if hasattr(FinancialReportModel, key):
                    stmt = stmt.where(getattr(FinancialReportModel, key) == value)
        stmt = stmt.order_by(FinancialReportModel.year.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]

    async def count_by_idno(self, idno: str) -> int:
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count())
            .select_from(FinancialReportModel)
            .where(FinancialReportModel.company_idno == idno)
        )
        return result.scalar_one()

    async def find_years_for_idno(self, idno: str) -> list[int]:
        result = await self._session.execute(
            select(FinancialReportModel.year)
            .where(FinancialReportModel.company_idno == idno)
            .order_by(FinancialReportModel.year.desc())
            .distinct()
        )
        return [row[0] for row in result.all()]

    async def find_latest_by_idno(self, idno: str) -> FinancialReport | None:
        result = await self._session.execute(
            select(FinancialReportModel)
            .where(FinancialReportModel.company_idno == idno)
            .order_by(FinancialReportModel.year.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None
