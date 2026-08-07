from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Query

from credibil.api.v1.tenders.dependencies import (
    get_tender_award_repo,
    get_tender_bid_repo,
    get_tender_repo,
)
from credibil.api.v1.tenders.schemas import (
    ApiResponse,
    TenderAnalyticsResponse,
    TenderResponse,
)
from credibil.application.tender.commands import (
    GetTenderAnalyticsQuery,
    GetTenderByOcidQuery,
    GetTenderQuery,
    GetTendersByBuyerQuery,
    GetTendersBySupplierQuery,
    ListTendersQuery,
)
from credibil.application.tender.handlers import TenderHandlers

if TYPE_CHECKING:
    from credibil.ports.repositories.tender import (
        TenderAwardRepository,
        TenderBidRepository,
        TenderRepository,
    )

router = APIRouter(prefix="/tenders", tags=["tenders"])


@router.get("", response_model=ApiResponse)
async def list_tenders(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
    buyer_idno: str | None = Query(default=None, min_length=13, max_length=13),
    tender_repo: TenderRepository = Depends(get_tender_repo),
    award_repo: TenderAwardRepository = Depends(get_tender_award_repo),
    bid_repo: TenderBidRepository = Depends(get_tender_bid_repo),
) -> ApiResponse:
    handlers = TenderHandlers(tender_repo=tender_repo, award_repo=award_repo, bid_repo=bid_repo)
    result = await handlers.list_tenders(
        ListTendersQuery(limit=limit, offset=offset, status=status, buyer_idno=buyer_idno)
    )
    items = [TenderResponse(**r.model_dump()) for r in result]
    return ApiResponse(data=items)


@router.get("/analytics", response_model=ApiResponse)
async def get_analytics(
    idno: str = Query(..., min_length=13, max_length=13, pattern=r"^\d{13}$"),
    tender_repo: TenderRepository = Depends(get_tender_repo),
    award_repo: TenderAwardRepository = Depends(get_tender_award_repo),
    bid_repo: TenderBidRepository = Depends(get_tender_bid_repo),
) -> ApiResponse:
    handlers = TenderHandlers(tender_repo=tender_repo, award_repo=award_repo, bid_repo=bid_repo)
    result = await handlers.get_analytics(GetTenderAnalyticsQuery(idno=idno))
    return ApiResponse(data=TenderAnalyticsResponse(**result.model_dump()))


@router.get("/by-buyer/{idno}", response_model=ApiResponse)
async def get_tenders_by_buyer(
    idno: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    tender_repo: TenderRepository = Depends(get_tender_repo),
    award_repo: TenderAwardRepository = Depends(get_tender_award_repo),
    bid_repo: TenderBidRepository = Depends(get_tender_bid_repo),
) -> ApiResponse:
    handlers = TenderHandlers(tender_repo=tender_repo, award_repo=award_repo, bid_repo=bid_repo)
    result = await handlers.get_tenders_by_buyer(
        GetTendersByBuyerQuery(idno=idno, limit=limit, offset=offset)
    )
    items = [TenderResponse(**r.model_dump()) for r in result]
    return ApiResponse(data=items)


@router.get("/by-supplier/{idno}", response_model=ApiResponse)
async def get_tenders_by_supplier(
    idno: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    tender_repo: TenderRepository = Depends(get_tender_repo),
    award_repo: TenderAwardRepository = Depends(get_tender_award_repo),
    bid_repo: TenderBidRepository = Depends(get_tender_bid_repo),
) -> ApiResponse:
    handlers = TenderHandlers(tender_repo=tender_repo, award_repo=award_repo, bid_repo=bid_repo)
    result = await handlers.get_tenders_by_supplier(
        GetTendersBySupplierQuery(idno=idno, limit=limit, offset=offset)
    )
    items = [TenderResponse(**r.model_dump()) for r in result]
    return ApiResponse(data=items)


@router.get("/{tender_id}", response_model=ApiResponse)
async def get_tender(
    tender_id: UUID,
    tender_repo: TenderRepository = Depends(get_tender_repo),
    award_repo: TenderAwardRepository = Depends(get_tender_award_repo),
    bid_repo: TenderBidRepository = Depends(get_tender_bid_repo),
) -> ApiResponse:
    handlers = TenderHandlers(tender_repo=tender_repo, award_repo=award_repo, bid_repo=bid_repo)
    result = await handlers.get_tender(GetTenderQuery(tender_id=tender_id))
    return ApiResponse(data=TenderResponse(**result.model_dump()))


@router.get("/ocid/{ocid}", response_model=ApiResponse)
async def get_tender_by_ocid(
    ocid: str,
    tender_repo: TenderRepository = Depends(get_tender_repo),
    award_repo: TenderAwardRepository = Depends(get_tender_award_repo),
    bid_repo: TenderBidRepository = Depends(get_tender_bid_repo),
) -> ApiResponse:
    handlers = TenderHandlers(tender_repo=tender_repo, award_repo=award_repo, bid_repo=bid_repo)
    result = await handlers.get_tender_by_ocid(GetTenderByOcidQuery(ocid=ocid))
    return ApiResponse(data=TenderResponse(**result.model_dump()))
