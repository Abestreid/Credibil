from __future__ import annotations

from typing import TYPE_CHECKING

from credibil.application.analytics.tender_analytics import (
    compute_award_statistics,
    compute_method_breakdown,
    compute_tender_statistics,
    compute_timeline,
    compute_win_rate,
)
from credibil.application.tender.dto import (
    AwardStatisticsDTO,
    MethodBreakdownDTO,
    TenderAnalyticsDTO,
    TenderDTO,
    TenderStatisticsDTO,
    TimelinePointDTO,
    WinRateDTO,
)
from credibil.domain.tender.errors import TenderNotFoundError

if TYPE_CHECKING:
    from credibil.application.tender.commands import (
        GetTenderAnalyticsQuery,
        GetTenderByOcidQuery,
        GetTenderQuery,
        GetTendersByBuyerQuery,
        GetTendersBySupplierQuery,
        ListTendersQuery,
        SyncRecentTendersCommand,
        SyncTendersByBuyerCommand,
    )
    from credibil.countries.moldova.sync.tender_orchestrator import TenderSyncOrchestrator
    from credibil.domain.tender.entities import Tender
    from credibil.ports.repositories.tender import (
        TenderAwardRepository,
        TenderBidRepository,
        TenderRepository,
    )


def _tender_to_dto(entity: Tender) -> TenderDTO:
    return TenderDTO(**entity.__dict__)


class TenderHandlers:
    """Application service for tender operations."""

    def __init__(
        self,
        tender_repo: TenderRepository,
        award_repo: TenderAwardRepository,
        bid_repo: TenderBidRepository,
        sync_orchestrator: TenderSyncOrchestrator | None = None,
    ) -> None:
        self._tender_repo = tender_repo
        self._award_repo = award_repo
        self._bid_repo = bid_repo
        self._orchestrator = sync_orchestrator

    async def list_tenders(self, query: ListTendersQuery) -> list[TenderDTO]:
        if query.buyer_idno:
            tenders = await self._tender_repo.find_by_buyer_idno(
                query.buyer_idno, limit=query.limit, offset=query.offset
            )
        elif query.status:
            tenders = await self._tender_repo.find_by_status(
                query.status, limit=query.limit, offset=query.offset
            )
        else:
            tenders = await self._tender_repo.list_tenders(limit=query.limit, offset=query.offset)
        return [_tender_to_dto(t) for t in tenders]

    async def get_tender(self, query: GetTenderQuery) -> TenderDTO:
        tender = await self._tender_repo.find_by_id(query.tender_id)
        if not tender:
            raise TenderNotFoundError(str(query.tender_id))
        return _tender_to_dto(tender)

    async def get_tender_by_ocid(self, query: GetTenderByOcidQuery) -> TenderDTO:
        tender = await self._tender_repo.find_by_ocid(query.ocid)
        if not tender:
            raise TenderNotFoundError(query.ocid)
        return _tender_to_dto(tender)

    async def get_tenders_by_buyer(self, query: GetTendersByBuyerQuery) -> list[TenderDTO]:
        tenders = await self._tender_repo.find_by_buyer_idno(
            query.idno, limit=query.limit, offset=query.offset
        )
        return [_tender_to_dto(t) for t in tenders]

    async def get_tenders_by_supplier(self, query: GetTendersBySupplierQuery) -> list[TenderDTO]:
        tenders = await self._tender_repo.find_by_supplier_idno(
            query.idno, limit=query.limit, offset=query.offset
        )
        return [_tender_to_dto(t) for t in tenders]

    async def get_analytics(self, query: GetTenderAnalyticsQuery) -> TenderAnalyticsDTO:
        tenders = await self._tender_repo.find_by_buyer_idno(query.idno)
        supplier_tenders = await self._tender_repo.find_by_supplier_idno(query.idno)
        all_tenders = tenders + [
            t for t in supplier_tenders if t.ocid not in {tt.ocid for tt in tenders}
        ]

        awards = await self._award_repo.find_by_supplier_idno(query.idno)

        stats = compute_tender_statistics(all_tenders)
        award_stats = compute_award_statistics(awards)
        win_rate = compute_win_rate(all_tenders, awards, query.idno)
        method_breakdown = compute_method_breakdown(all_tenders)
        timeline = compute_timeline(all_tenders)

        return TenderAnalyticsDTO(
            idno=query.idno,
            statistics=TenderStatisticsDTO(**stats),
            award_statistics=AwardStatisticsDTO(**award_stats),
            win_rate=WinRateDTO(**win_rate),
            method_breakdown=[MethodBreakdownDTO(**m) for m in method_breakdown],
            timeline=[TimelinePointDTO(**t) for t in timeline],
        )

    async def sync_recent(self, cmd: SyncRecentTendersCommand) -> dict[str, int]:
        if not self._orchestrator:
            raise RuntimeError("Sync orchestrator not configured")
        return await self._orchestrator.sync_recent(limit=cmd.limit)

    async def sync_by_buyer(self, cmd: SyncTendersByBuyerCommand) -> dict[str, int]:
        if not self._orchestrator:
            raise RuntimeError("Sync orchestrator not configured")
        return await self._orchestrator.sync_by_buyer_idno(cmd.idno, cmd.limit)
