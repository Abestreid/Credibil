from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from credibil.countries.moldova.providers.mtender_provider import (
    parse_awards,
    parse_bids,
    parse_tender,
)
from credibil.domain.sync.entities import SyncHistory, SyncType

if TYPE_CHECKING:
    from credibil.countries.moldova.providers.mtender_provider import MTenderProvider
    from credibil.ports.repositories.sync_history import SyncHistoryRepository
    from credibil.ports.repositories.tender import (
        TenderAwardRepository,
        TenderBidRepository,
        TenderRepository,
    )

logger = logging.getLogger(__name__)


class TenderSyncOrchestrator:
    """Orchestrates tender data fetching from mtender.gov.md.

    Fetches recent tenders from the OCDS API, parses them into domain
    entities, and upserts into the database.
    """

    def __init__(
        self,
        tender_repo: TenderRepository,
        award_repo: TenderAwardRepository,
        bid_repo: TenderBidRepository,
        sync_repo: SyncHistoryRepository,
        provider: MTenderProvider,
    ) -> None:
        self._tender_repo = tender_repo
        self._award_repo = award_repo
        self._bid_repo = bid_repo
        self._sync_repo = sync_repo
        self._provider = provider

    async def sync_recent(self, limit: int = 50) -> dict[str, int]:
        """Fetch and sync recent tenders from the OCDS API.

        Returns counts of created/updated/failed records.
        """
        sync = SyncHistory(
            provider_id="mtender_gov_md",
            sync_type=SyncType.INCREMENTAL,
            country_code="MD",
        )
        sync.start()
        await self._sync_repo.save(sync)

        created = 0
        updated = 0
        failed = 0
        awards_saved = 0
        bids_saved = 0

        try:
            records = await self._provider.fetch_recent_tenders(limit=limit)

            for record in records:
                try:
                    tender = parse_tender(record)
                    if tender:
                        existing = await self._tender_repo.find_by_ocid(tender.ocid)
                        if existing:
                            tender.id = existing.id
                            tender.created_at = existing.created_at
                            updated += 1
                        else:
                            created += 1

                        saved_tender = await self._tender_repo.save(tender)

                        awards = parse_awards(record)
                        for award in awards:
                            award.tender_id = saved_tender.id
                            await self._award_repo.save(award)
                            awards_saved += 1

                        bids = parse_bids(record)
                        for bid in bids:
                            bid.tender_id = saved_tender.id
                            await self._bid_repo.save(bid)
                            bids_saved += 1

                except Exception as e:
                    logger.error("Failed to parse/sync tender: %s", e)
                    failed += 1

            sync.complete(
                records_total=len(records),
                records_created=created,
                records_updated=updated,
                records_unchanged=0,
                records_failed=failed,
            )
            sync.file_checksum = f"awards={awards_saved};bids={bids_saved}"
            await self._sync_repo.save(sync)

            logger.info(
                "Tender sync complete: created=%d updated=%d awards=%d bids=%d failed=%d",
                created,
                updated,
                awards_saved,
                bids_saved,
                failed,
            )

            return {
                "created": created,
                "updated": updated,
                "awards_saved": awards_saved,
                "bids_saved": bids_saved,
                "failed": failed,
            }

        except Exception as e:
            sync.fail(str(e))
            await self._sync_repo.save(sync)
            raise

    async def sync_by_buyer_idno(self, idno: str, limit: int = 50) -> dict[str, int]:
        """Search for tenders where a specific IDNO is the buyer.

        This is an on-demand operation that searches the API for tenders
        by the given buyer IDNO.
        """
        sync = SyncHistory(
            provider_id="mtender_gov_md_buyer",
            sync_type=SyncType.ON_DEMAND,
            country_code="MD",
        )
        sync.start()
        await self._sync_repo.save(sync)

        created = 0
        updated = 0
        failed = 0

        try:
            records = await self._provider.fetch_recent_tenders(limit=limit)

            for record in records:
                try:
                    tender = parse_tender(record)
                    if tender and tender.buyer_idno == idno:
                        existing = await self._tender_repo.find_by_ocid(tender.ocid)
                        if existing:
                            tender.id = existing.id
                            tender.created_at = existing.created_at
                            updated += 1
                        else:
                            created += 1
                        await self._tender_repo.save(tender)
                except Exception as e:
                    logger.error("Failed to sync tender for buyer %s: %s", idno, e)
                    failed += 1

            sync.complete(
                records_total=created + updated,
                records_created=created,
                records_updated=updated,
                records_unchanged=0,
                records_failed=failed,
            )
            sync.file_checksum = f"buyer_idno={idno}"
            await self._sync_repo.save(sync)

            return {
                "created": created,
                "updated": updated,
                "failed": failed,
            }

        except Exception as e:
            sync.fail(str(e))
            await self._sync_repo.save(sync)
            raise
