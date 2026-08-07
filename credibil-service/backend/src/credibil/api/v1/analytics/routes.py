from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException

from credibil.api.v1.analytics.schemas import ApiResponse, DashboardResponse
from credibil.application.analytics.dashboard import (
    CompanyDashboard,
    DashboardService,
)
from credibil.core.database import get_session_dependency

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _dashboard_to_response(dashboard: CompanyDashboard) -> DashboardResponse:
    """Convert a CompanyDashboard dataclass to an API response schema."""
    summary = None
    if dashboard.summary:
        from credibil.api.v1.analytics.schemas import CompanySummaryResponse

        summary = CompanySummaryResponse(
            idno=dashboard.summary.idno,
            name_ro=dashboard.summary.name_ro,
            name_ru=dashboard.summary.name_ru,
            status=dashboard.summary.status,
            legal_form=dashboard.summary.legal_form,
            caem=dashboard.summary.caem,
            caem_description=dashboard.summary.caem_description,
            legal_address=dashboard.summary.legal_address,
            registration_date=dashboard.summary.registration_date,
            founder_count=dashboard.summary.founder_count,
            director_count=dashboard.summary.director_count,
            tax_debt=dashboard.summary.tax_debt,
        )

    financial = None
    if dashboard.financial:
        from credibil.api.v1.analytics.schemas import (
            ChartDataPointResponse,
            EmployeeDynamicsResponse,
            FinancialAnalyticsResponse,
            GrowthMetricsResponse,
            LiquidityMetricsResponse,
            MarginMetricsResponse,
        )

        financial = FinancialAnalyticsResponse(
            company_idno=dashboard.financial.company_idno,
            company_name=dashboard.financial.company_name,
            years_analyzed=dashboard.financial.years_analyzed,
            growth=[
                GrowthMetricsResponse(
                    current_year=g.current_year,
                    previous_year=g.previous_year,
                    revenue_growth_pct=g.revenue_growth_pct,
                    profit_growth_pct=g.profit_growth_pct,
                    assets_growth_pct=g.assets_growth_pct,
                    employees_growth_pct=g.employees_growth_pct,
                )
                for g in dashboard.financial.growth
            ],
            margins=[
                MarginMetricsResponse(
                    year=m.year,
                    gross_margin_pct=m.gross_margin_pct,
                    net_margin_pct=m.net_margin_pct,
                    operating_margin_pct=m.operating_margin_pct,
                    expense_ratio_pct=m.expense_ratio_pct,
                )
                for m in dashboard.financial.margins
            ],
            liquidity=[
                LiquidityMetricsResponse(
                    year=liq.year,
                    current_ratio=liq.current_ratio,
                    debt_to_equity_ratio=liq.debt_to_equity_ratio,
                    autonomy_ratio=liq.autonomy_ratio,
                    debt_ratio=liq.debt_ratio,
                    equity_ratio=liq.equity_ratio,
                )
                for liq in dashboard.financial.liquidity
            ],
            employee_dynamics=[
                EmployeeDynamicsResponse(
                    year=e.year,
                    employees_count=e.employees_count,
                    yoy_change=e.yoy_change,
                    yoy_change_pct=e.yoy_change_pct,
                )
                for e in dashboard.financial.employee_dynamics
            ],
            revenue_chart=[
                ChartDataPointResponse(year=c["year"], value=c["value"])
                for c in dashboard.financial.revenue_chart
            ],
            profit_chart=[
                ChartDataPointResponse(year=c["year"], value=c["value"])
                for c in dashboard.financial.profit_chart
            ],
            assets_chart=[
                ChartDataPointResponse(year=c["year"], value=c["value"])
                for c in dashboard.financial.assets_chart
            ],
            employees_chart=[
                ChartDataPointResponse(year=c["year"], value=c["value"])
                for c in dashboard.financial.employees_chart
            ],
        )

    from credibil.api.v1.analytics.schemas import (
        RelationshipEdgeResponse,
        RelationshipGraphResponse,
        RelationshipNodeResponse,
        RiskIndicatorResponse,
        SanctionsIndicatorResponse,
        TimelineEntryResponse,
    )

    graph = RelationshipGraphResponse(
        nodes=[
            RelationshipNodeResponse(
                id=n.id,
                label=n.label,
                node_type=n.node_type,
                idno=n.idno,
                idnp=n.idnp,
            )
            for n in dashboard.relationship_graph.nodes
        ],
        edges=[
            RelationshipEdgeResponse(
                source=e.source,
                target=e.target,
                relationship_type=e.relationship_type,
                is_active=e.is_active,
                start_date=e.start_date,
            )
            for e in dashboard.relationship_graph.edges
        ],
        total_nodes=dashboard.relationship_graph.total_nodes,
        total_edges=dashboard.relationship_graph.total_edges,
    )

    timeline = [
        TimelineEntryResponse(
            date=t.date,
            event_type=t.event_type,
            title=t.title,
            description=t.description,
            source=t.source,
        )
        for t in dashboard.timeline
    ]

    risk = [
        RiskIndicatorResponse(
            category=r.category,
            level=r.level.value,
            score=r.score,
            factors=r.factors,
            details=r.details,
        )
        for r in dashboard.risk_indicators
    ]

    sanctions = SanctionsIndicatorResponse(
        is_sanctioned=dashboard.sanctions.is_sanctioned,
        sanctions_count=dashboard.sanctions.sanctions_count,
        active_sanctions=dashboard.sanctions.active_sanctions,
        sanction_types=dashboard.sanctions.sanction_types,
        lists=dashboard.sanctions.lists,
        latest_entry_date=dashboard.sanctions.latest_entry_date,
    )

    return DashboardResponse(
        summary=summary,
        financial=financial,
        court_statistics=dashboard.court_statistics,
        court_judges=dashboard.court_judges,
        court_distribution=dashboard.court_distribution,
        court_timeline=dashboard.court_timeline,
        tender_statistics=dashboard.tender_statistics,
        tender_awards=dashboard.tender_awards,
        tender_win_rate=dashboard.tender_win_rate,
        tender_methods=dashboard.tender_methods,
        tender_timeline=dashboard.tender_timeline,
        relationship_graph=graph,
        timeline=timeline,
        risk_indicators=risk,
        sanctions=sanctions,
    )


async def _get_dashboard_service(
    session: AsyncSession = Depends(get_session_dependency),
) -> DashboardService:
    """Create a DashboardService with PostgreSQL-backed repos."""
    from credibil.infrastructure.database.repositories.company import (
        SQLAlchemyCompanyRepository,
    )
    from credibil.infrastructure.database.repositories.court_case import (
        SQLAlchemyCourtCaseRepository,
        SQLAlchemyCourtHearingRepository,
    )
    from credibil.infrastructure.database.repositories.financial_report import (
        SQLAlchemyFinancialReportRepository,
    )
    from credibil.infrastructure.database.repositories.relationship import (
        SQLAlchemyPersonRepository,
        SQLAlchemyRelationshipRepository,
    )
    from credibil.infrastructure.database.repositories.tender import (
        SQLAlchemyTenderAwardRepository,
        SQLAlchemyTenderBidRepository,
        SQLAlchemyTenderRepository,
    )

    return DashboardService(
        company_repo=SQLAlchemyCompanyRepository(session),
        financial_repo=SQLAlchemyFinancialReportRepository(session),
        court_case_repo=SQLAlchemyCourtCaseRepository(session),
        court_hearing_repo=SQLAlchemyCourtHearingRepository(session),
        tender_repo=SQLAlchemyTenderRepository(session),
        tender_award_repo=SQLAlchemyTenderAwardRepository(session),
        tender_bid_repo=SQLAlchemyTenderBidRepository(session),
        relationship_repo=SQLAlchemyRelationshipRepository(session),
        person_repo=SQLAlchemyPersonRepository(session),
        sanctions_repo=None,
    )


@router.get("/dashboard/{idno}", response_model=ApiResponse)
async def get_company_dashboard(
    idno: str,
    dashboard_service: DashboardService = Depends(_get_dashboard_service),
):
    """Get the complete analytics dashboard for a company.

    Returns company summary, financial charts, court charts, tender charts,
    relationship graph, timeline, risk indicators, and sanctions indicators.
    """
    if len(idno) != 13 or not idno.isdigit():
        raise HTTPException(status_code=400, detail="IDNO must be exactly 13 digits")

    dashboard = await dashboard_service.get_company_dashboard(idno)
    response = _dashboard_to_response(dashboard)
    return ApiResponse(data=response.model_dump())
