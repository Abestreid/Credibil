from __future__ import annotations

from typing import TYPE_CHECKING

from credibil.application.analytics.service import compute_analytics
from credibil.application.financial.dto import (
    ChartDataPoint,
    CompanyAnalyticsDTO,
    EmployeeDynamicsDTO,
    FinancialReportDTO,
    GrowthMetricsDTO,
    LiquidityMetricsDTO,
    MarginMetricsDTO,
)
from credibil.domain.financial.errors import FinancialReportNotFoundError

if TYPE_CHECKING:
    from credibil.application.financial.commands import (
        GetCompanyAnalyticsQuery,
        GetFinancialReportQuery,
        GetFinancialReportsByIdnoQuery,
        SyncFinancialReportCommand,
        SyncMultiYearCommand,
    )
    from credibil.countries.moldova.sync.financial_orchestrator import (
        FinancialSyncOrchestrator,
    )
    from credibil.domain.financial import FinancialReport
    from credibil.ports.repositories.financial_report import FinancialReportRepository


def _to_dto(entity: FinancialReport) -> FinancialReportDTO:
    return FinancialReportDTO(**entity.__dict__)


class FinancialHandlers:
    """Application service for financial report operations."""

    def __init__(
        self,
        financial_repo: FinancialReportRepository,
        sync_orchestrator: FinancialSyncOrchestrator | None = None,
    ) -> None:
        self._repo = financial_repo
        self._orchestrator = sync_orchestrator

    async def sync_report(self, cmd: SyncFinancialReportCommand) -> FinancialReportDTO:
        if not self._orchestrator:
            raise RuntimeError("Sync orchestrator not configured")
        report = await self._orchestrator.fetch_and_store(cmd.company_idno, cmd.year)
        return _to_dto(report)

    async def sync_multi_year(self, cmd: SyncMultiYearCommand) -> list[FinancialReportDTO]:
        if not self._orchestrator:
            raise RuntimeError("Sync orchestrator not configured")
        reports = await self._orchestrator.fetch_multi_year(cmd.company_idno, cmd.years)
        return [_to_dto(r) for r in reports]

    async def get_report(self, query: GetFinancialReportQuery) -> FinancialReportDTO:
        report = await self._repo.find_by_id(query.report_id)
        if not report:
            raise FinancialReportNotFoundError(str(query.report_id))
        return _to_dto(report)

    async def get_reports_by_idno(
        self, query: GetFinancialReportsByIdnoQuery
    ) -> list[FinancialReportDTO]:
        reports = await self._repo.find_by_idno(
            query.company_idno, limit=query.limit, offset=query.offset
        )
        return [_to_dto(r) for r in reports]

    async def get_analytics(self, query: GetCompanyAnalyticsQuery) -> CompanyAnalyticsDTO:
        reports = await self._repo.find_by_idno(query.company_idno)
        if not reports:
            raise FinancialReportNotFoundError(query.company_idno)

        report_dicts = [
            {
                "company_idno": r.company_idno,
                "company_name": r.company_name,
                "year": r.year,
                "revenue": r.revenue,
                "expenses": r.expenses,
                "total_assets": r.total_assets,
                "total_liabilities": r.total_liabilities,
                "equity": r.equity,
                "profit": r.profit,
                "employees_count": r.employees_count,
            }
            for r in reports
        ]

        analytics = compute_analytics(report_dicts)

        return CompanyAnalyticsDTO(
            company_idno=analytics.company_idno,
            company_name=analytics.company_name,
            years_analyzed=analytics.years_analyzed,
            growth=[GrowthMetricsDTO(**g.__dict__) for g in analytics.growth],
            margins=[MarginMetricsDTO(**m.__dict__) for m in analytics.margins],
            liquidity=[LiquidityMetricsDTO(**liq.__dict__) for liq in analytics.liquidity],
            employee_dynamics=[
                EmployeeDynamicsDTO(**e.__dict__) for e in analytics.employee_dynamics
            ],
            revenue_chart=[ChartDataPoint(**c) for c in analytics.revenue_chart],
            profit_chart=[ChartDataPoint(**c) for c in analytics.profit_chart],
            assets_chart=[ChartDataPoint(**c) for c in analytics.assets_chart],
            employees_chart=[ChartDataPoint(**c) for c in analytics.employees_chart],
        )
