from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Query

from credibil.api.v1.financial.dependencies import get_financial_repo
from credibil.api.v1.financial.schemas import (
    ApiResponse,
    FinancialReportResponse,
    ManualFinancialReportRequest,
)
from credibil.application.financial.commands import (
    GetCompanyAnalyticsQuery,
    GetFinancialReportQuery,
    GetFinancialReportsByIdnoQuery,
)
from credibil.application.financial.handlers import FinancialHandlers

if TYPE_CHECKING:
    from credibil.ports.repositories.financial_report import FinancialReportRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/financial", tags=["financial"])


@router.get("", response_model=ApiResponse)
async def list_reports(
    idno: str = Query(..., min_length=13, max_length=13, pattern=r"^\d{13}$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: FinancialReportRepository = Depends(get_financial_repo),
) -> ApiResponse:
    handlers = FinancialHandlers(financial_repo=repo)
    query = GetFinancialReportsByIdnoQuery(company_idno=idno, limit=limit, offset=offset)
    result = await handlers.get_reports_by_idno(query)
    items = [FinancialReportResponse(**r.model_dump()) for r in result]
    return ApiResponse(data=items)


@router.post("/sync/{idno}", response_model=ApiResponse)
async def trigger_sync(
    idno: str,
    repo: FinancialReportRepository = Depends(get_financial_repo),
) -> ApiResponse:
    """Trigger on-demand financial data fetch from the Depozitar.

    This enqueues a Celery task that fetches all available financial statements
    for the given IDNO and stores them permanently in PostgreSQL.
    """
    from celery.result import AsyncResult

    from credibil.workers.tasks import sync_financial_all_years

    task = sync_financial_all_years.delay(idno)
    logger.info("Enqueued financial sync for %s: task=%s", idno, task.id)

    return ApiResponse(data={"task_id": task.id, "status": "queued", "company_idno": idno})


@router.post("/manual", response_model=ApiResponse)
async def create_manual_report(
    body: ManualFinancialReportRequest,
    repo: FinancialReportRepository = Depends(get_financial_repo),
) -> ApiResponse:
    """Create a financial report manually (for companies not in Depozitar)."""
    from datetime import datetime

    from credibil.domain.financial import FinancialReport, ReportPeriod

    report = FinancialReport(
        company_idno=body.company_idno,
        year=body.year,
        period=ReportPeriod(body.period),
        revenue=body.revenue,
        expenses=body.expenses,
        total_assets=body.total_assets,
        total_liabilities=body.total_liabilities,
        equity=body.equity,
        profit=body.profit,
        employees_count=body.employees_count,
        source_url="manual",
        raw_data={"source": "manual", "entered_at": datetime.utcnow().isoformat()},
    )
    await repo.save(report)
    logger.info("Created manual financial report for %s year=%d", body.company_idno, body.year)
    return ApiResponse(data=FinancialReportResponse(**report.__dict__))


@router.get("/analytics", response_model=ApiResponse)
async def get_analytics(
    idno: str = Query(..., min_length=13, max_length=13, pattern=r"^\d{13}$"),
    repo: FinancialReportRepository = Depends(get_financial_repo),
) -> ApiResponse:
    handlers = FinancialHandlers(financial_repo=repo)
    query = GetCompanyAnalyticsQuery(company_idno=idno)
    result = await handlers.get_analytics(query)
    from credibil.api.v1.financial.schemas import AnalyticsResponse

    return ApiResponse(data=AnalyticsResponse(**result.model_dump()))


@router.get("/{report_id}", response_model=ApiResponse)
async def get_report(
    report_id: UUID,
    repo: FinancialReportRepository = Depends(get_financial_repo),
) -> ApiResponse:
    handlers = FinancialHandlers(financial_repo=repo)
    result = await handlers.get_report(GetFinancialReportQuery(report_id=report_id))
    return ApiResponse(data=FinancialReportResponse(**result.model_dump()))
