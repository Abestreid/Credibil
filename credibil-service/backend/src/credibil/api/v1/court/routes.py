from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Query

from credibil.api.v1.court.dependencies import get_court_case_repo, get_court_hearing_repo
from credibil.api.v1.court.schemas import (
    ApiResponse,
    CaseAnalyticsResponse,
    CourtCaseResponse,
    CourtHearingResponse,
)
from credibil.application.court.commands import (
    GetCaseAnalyticsQuery,
    GetCaseByNumberQuery,
    GetCaseQuery,
    GetCasesByIdnoQuery,
    GetHearingsQuery,
    GetUpcomingHearingsQuery,
    SearchByNameCommand,
)
from credibil.application.court.handlers import CourtHandlers

if TYPE_CHECKING:
    from credibil.ports.repositories.court_case import CourtCaseRepository, CourtHearingRepository

router = APIRouter(prefix="/court", tags=["court"])


@router.get("/cases", response_model=ApiResponse)
async def search_cases_by_idno(
    idno: str = Query(..., min_length=13, max_length=13, pattern=r"^\d{13}$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    case_repo: CourtCaseRepository = Depends(get_court_case_repo),
    hearing_repo: CourtHearingRepository = Depends(get_court_hearing_repo),
) -> ApiResponse:
    handlers = CourtHandlers(case_repo=case_repo, hearing_repo=hearing_repo)
    result = await handlers.get_cases_by_idno(
        GetCasesByIdnoQuery(idno=idno, limit=limit, offset=offset)
    )
    items = [CourtCaseResponse(**r.model_dump()) for r in result]
    return ApiResponse(data=items)


@router.get("/cases/search", response_model=ApiResponse)
async def search_by_name(
    name: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(default=50, ge=1, le=200),
    case_repo: CourtCaseRepository = Depends(get_court_case_repo),
    hearing_repo: CourtHearingRepository = Depends(get_court_hearing_repo),
) -> ApiResponse:
    handlers = CourtHandlers(case_repo=case_repo, hearing_repo=hearing_repo)
    result = await handlers.search_by_name(SearchByNameCommand(name=name))
    items = [CourtCaseResponse(**r.model_dump()) for r in result]
    return ApiResponse(data=items)


@router.get("/cases/{case_id}", response_model=ApiResponse)
async def get_case(
    case_id: UUID,
    case_repo: CourtCaseRepository = Depends(get_court_case_repo),
    hearing_repo: CourtHearingRepository = Depends(get_court_hearing_repo),
) -> ApiResponse:
    handlers = CourtHandlers(case_repo=case_repo, hearing_repo=hearing_repo)
    result = await handlers.get_case(GetCaseQuery(case_id=case_id))
    return ApiResponse(data=CourtCaseResponse(**result.model_dump()))


@router.get("/cases/number/{case_number}", response_model=ApiResponse)
async def get_case_by_number(
    case_number: str,
    case_repo: CourtCaseRepository = Depends(get_court_case_repo),
    hearing_repo: CourtHearingRepository = Depends(get_court_hearing_repo),
) -> ApiResponse:
    handlers = CourtHandlers(case_repo=case_repo, hearing_repo=hearing_repo)
    result = await handlers.get_case_by_number(GetCaseByNumberQuery(case_number=case_number))
    return ApiResponse(data=CourtCaseResponse(**result.model_dump()))


@router.get("/analytics", response_model=ApiResponse)
async def get_analytics(
    idno: str = Query(..., min_length=13, max_length=13, pattern=r"^\d{13}$"),
    case_repo: CourtCaseRepository = Depends(get_court_case_repo),
    hearing_repo: CourtHearingRepository = Depends(get_court_hearing_repo),
) -> ApiResponse:
    handlers = CourtHandlers(case_repo=case_repo, hearing_repo=hearing_repo)
    result = await handlers.get_analytics(GetCaseAnalyticsQuery(idno=idno))
    return ApiResponse(data=CaseAnalyticsResponse(**result.model_dump()))


@router.get("/hearings", response_model=ApiResponse)
async def get_hearings(
    case_number: str = Query(..., min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    case_repo: CourtCaseRepository = Depends(get_court_case_repo),
    hearing_repo: CourtHearingRepository = Depends(get_court_hearing_repo),
) -> ApiResponse:
    handlers = CourtHandlers(case_repo=case_repo, hearing_repo=hearing_repo)
    result = await handlers.get_hearings(
        GetHearingsQuery(case_number=case_number, limit=limit, offset=offset)
    )
    items = [CourtHearingResponse(**r.model_dump()) for r in result]
    return ApiResponse(data=items)


@router.get("/hearings/upcoming", response_model=ApiResponse)
async def get_upcoming_hearings(
    idno: str = Query(..., min_length=13, max_length=13, pattern=r"^\d{13}$"),
    limit: int = Query(default=50, ge=1, le=200),
    case_repo: CourtCaseRepository = Depends(get_court_case_repo),
    hearing_repo: CourtHearingRepository = Depends(get_court_hearing_repo),
) -> ApiResponse:
    handlers = CourtHandlers(case_repo=case_repo, hearing_repo=hearing_repo)
    result = await handlers.get_upcoming_hearings(GetUpcomingHearingsQuery(idno=idno, limit=limit))
    items = [CourtHearingResponse(**r.model_dump()) for r in result]
    return ApiResponse(data=items)
