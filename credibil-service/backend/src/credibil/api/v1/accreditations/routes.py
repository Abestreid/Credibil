from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from credibil.api.v1.accreditations.dependencies import (
    get_accreditation_repo,
    get_orchestrator,
)
from credibil.api.v1.accreditations.schemas import (
    AccreditationResponse,
    AccreditationStatisticsResponse,
    AccreditationSyncResponse,
    ApiResponse,
)
from credibil.application.accreditation import (
    GetAccreditationQuery,
    GetAccreditationStatisticsQuery,
    ListAccreditationsQuery,
    SyncAccreditationsCommand,
)
from credibil.application.accreditation.handlers import AccreditationHandlers
from credibil.domain.accreditation.entities import AccreditationCategory, AccreditationStatus

router = APIRouter(prefix="/accreditations", tags=["accreditations"])


@router.get("", response_model=ApiResponse)
async def list_accreditations(
    category: str | None = Query(default=None),
    status: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    accreditation_repo: Any = Depends(get_accreditation_repo),
) -> ApiResponse:
    handlers = AccreditationHandlers(accreditation_repo=accreditation_repo)

    cat = AccreditationCategory(category) if category else None
    stat = AccreditationStatus(status) if status else None

    result = await handlers.list(
        ListAccreditationsQuery(
            category=cat, status=stat, keyword=keyword, limit=limit, offset=offset
        )
    )
    items = [AccreditationResponse(**r.model_dump()) for r in result]
    return ApiResponse(data=items)


@router.get("/statistics", response_model=ApiResponse)
async def get_statistics(
    category: str | None = Query(default=None),
    accreditation_repo: Any = Depends(get_accreditation_repo),
) -> ApiResponse:
    handlers = AccreditationHandlers(accreditation_repo=accreditation_repo)

    cat = AccreditationCategory(category) if category else None
    result = await handlers.get_statistics(GetAccreditationStatisticsQuery(category=cat))
    return ApiResponse(data=AccreditationStatisticsResponse(**result.model_dump()))


@router.get("/search", response_model=ApiResponse)
async def search_accreditations(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    accreditation_repo: Any = Depends(get_accreditation_repo),
) -> ApiResponse:
    handlers = AccreditationHandlers(accreditation_repo=accreditation_repo)
    result = await handlers.search(keyword=q, limit=limit)
    items = [AccreditationResponse(**r.model_dump()) for r in result]
    return ApiResponse(data=items)


@router.get("/{accreditation_id}", response_model=ApiResponse)
async def get_accreditation(
    accreditation_id: str,
    accreditation_repo: Any = Depends(get_accreditation_repo),
) -> ApiResponse:
    from uuid import UUID

    handlers = AccreditationHandlers(accreditation_repo=accreditation_repo)
    result = await handlers.get(GetAccreditationQuery(accreditation_id=UUID(accreditation_id)))
    return ApiResponse(data=AccreditationResponse(**result.model_dump()))


@router.get("/certificate/{cert_number}", response_model=ApiResponse)
async def get_by_certificate(
    cert_number: str,
    accreditation_repo: Any = Depends(get_accreditation_repo),
) -> ApiResponse:
    handlers = AccreditationHandlers(accreditation_repo=accreditation_repo)
    result = await handlers.get(GetAccreditationQuery(certificate_number=cert_number))
    return ApiResponse(data=AccreditationResponse(**result.model_dump()))


@router.post("/sync", response_model=ApiResponse)
async def sync_accreditations(
    category: str | None = Query(default=None),
    accreditation_repo: Any = Depends(get_accreditation_repo),
    orchestrator: Any = Depends(get_orchestrator),
) -> ApiResponse:
    handlers = AccreditationHandlers(
        accreditation_repo=accreditation_repo, orchestrator=orchestrator
    )
    cat = AccreditationCategory(category) if category else None
    result = await handlers.sync(SyncAccreditationsCommand(category=cat))
    return ApiResponse(data=AccreditationSyncResponse(**result.model_dump()))
