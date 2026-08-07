from __future__ import annotations

import contextlib
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, HTTPException, Query, status

from credibil.api.monitoring.dependencies import (
    current_user_id,
    get_company_repo,
    get_monitoring_engine,
    get_monitoring_repo,
)
from credibil.api.monitoring.schemas import (
    AddMonitoringRequest,
    ChangeEventResponse,
    MonitoredCompanyResponse,
    MonitoringApiResponse,
    NotificationResponse,
)
from credibil.domain.monitoring.entities import MonitoredCompany

if TYPE_CHECKING:
    from credibil.application.monitoring.engine import MonitoringEngine
    from credibil.ports.repositories.company import CompanyRepository
    from credibil.ports.repositories.monitoring import MonitoringRepository

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/companies", response_model=MonitoringApiResponse)
async def list_monitored(
    user_id: UUID = Depends(current_user_id),
    repo: MonitoringRepository = Depends(get_monitoring_repo),
) -> MonitoringApiResponse:
    items = await repo.list_monitored(user_id)
    return MonitoringApiResponse(
        data=[MonitoredCompanyResponse.model_validate(m) for m in items]
    )


@router.post("/companies", response_model=MonitoringApiResponse)
async def add_monitored(
    body: AddMonitoringRequest,
    user_id: UUID = Depends(current_user_id),
    repo: MonitoringRepository = Depends(get_monitoring_repo),
    company_repo: CompanyRepository = Depends(get_company_repo),
    engine: MonitoringEngine = Depends(get_monitoring_engine),
) -> MonitoringApiResponse:
    company = await company_repo.find_by_idno(body.idno)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    monitored = await repo.add_monitored(
        MonitoredCompany(
            user_id=user_id,
            idno=body.idno,
            company_id=company.id,
            company_name=company.name_ro or company.name_ru,
        )
    )

    # Capture a baseline snapshot immediately so the next run can diff against it.
    batch_id = datetime.utcnow().strftime("baseline-%Y%m%dT%H%M%S")
    with contextlib.suppress(Exception):  # baseline is best-effort
        await engine.check_company(body.idno, batch_id)

    # Warm up external signals for this company (best-effort, async).
    with contextlib.suppress(Exception):  # broker may be unavailable
        from credibil.workers.tasks import sync_court_cases, sync_enforcement_by_idno

        sync_enforcement_by_idno.delay(body.idno)
        sync_court_cases.delay(body.idno)

    return MonitoringApiResponse(data=MonitoredCompanyResponse.model_validate(monitored))


@router.delete("/companies/{idno}", response_model=MonitoringApiResponse)
async def remove_monitored(
    idno: str,
    user_id: UUID = Depends(current_user_id),
    repo: MonitoringRepository = Depends(get_monitoring_repo),
) -> MonitoringApiResponse:
    removed = await repo.remove_monitored(user_id, idno)
    return MonitoringApiResponse(data={"idno": idno, "removed": removed})


@router.get("/companies/{idno}/changes", response_model=MonitoringApiResponse)
async def company_changes(
    idno: str,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user_id: UUID = Depends(current_user_id),
    repo: MonitoringRepository = Depends(get_monitoring_repo),
) -> MonitoringApiResponse:
    events = await repo.list_change_events(idno, limit=limit, offset=offset)
    return MonitoringApiResponse(
        data=[ChangeEventResponse.model_validate(e) for e in events]
    )


@router.get("/notifications", response_model=MonitoringApiResponse)
async def list_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user_id: UUID = Depends(current_user_id),
    repo: MonitoringRepository = Depends(get_monitoring_repo),
) -> MonitoringApiResponse:
    items = await repo.list_notifications(
        user_id, unread_only=unread_only, limit=limit, offset=offset
    )
    return MonitoringApiResponse(
        data=[NotificationResponse.model_validate(n) for n in items]
    )


@router.get("/notifications/unread-count", response_model=MonitoringApiResponse)
async def unread_count(
    user_id: UUID = Depends(current_user_id),
    repo: MonitoringRepository = Depends(get_monitoring_repo),
) -> MonitoringApiResponse:
    return MonitoringApiResponse(data={"unread": await repo.count_unread(user_id)})


@router.post("/notifications/{notification_id}/read", response_model=MonitoringApiResponse)
async def mark_read(
    notification_id: UUID,
    user_id: UUID = Depends(current_user_id),
    repo: MonitoringRepository = Depends(get_monitoring_repo),
) -> MonitoringApiResponse:
    ok = await repo.mark_notification_read(user_id, notification_id)
    return MonitoringApiResponse(data={"id": str(notification_id), "read": ok})


@router.post("/notifications/read-all", response_model=MonitoringApiResponse)
async def mark_all_read(
    user_id: UUID = Depends(current_user_id),
    repo: MonitoringRepository = Depends(get_monitoring_repo),
) -> MonitoringApiResponse:
    return MonitoringApiResponse(data={"marked": await repo.mark_all_read(user_id)})
