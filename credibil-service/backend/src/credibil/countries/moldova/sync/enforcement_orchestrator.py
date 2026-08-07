from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING

from credibil.domain.enforcement.entities import EnforcementProceeding, EnforcementState
from credibil.domain.sync.entities import SyncHistory, SyncType

if TYPE_CHECKING:
    from credibil.countries.moldova.providers.unej_provider import UnejProvider
    from credibil.ports.repositories.enforcement import EnforcementRepository
    from credibil.ports.repositories.sync_history import SyncHistoryRepository

logger = logging.getLogger(__name__)

PROVIDER_ID = "unej_md"


class EnforcementSyncOrchestrator:
    """Orchestrates enforcement-proceeding sync from unej.md.

    * ``full_sync`` crawls the entire Somații board, upserts every entry, and
      moves anything that has disappeared from the source to the ARCHIVED state
      (we never delete — archived entries surface in a separate tab).
    * ``search_by_idno`` resolves the debtor/creditor linkage for one company
      by querying its full IDNO in both roles.
    """

    def __init__(
        self,
        enforcement_repo: EnforcementRepository,
        sync_repo: SyncHistoryRepository,
        provider: UnejProvider,
    ) -> None:
        self._repo = enforcement_repo
        self._sync_repo = sync_repo
        self._provider = provider

    async def full_sync(
        self, max_pages: int = 60, enrich_limit: int = 300
    ) -> dict[str, int]:
        sync = SyncHistory(
            provider_id=PROVIDER_ID,
            sync_type=SyncType.FULL,
            country_code="MD",
        )
        sync.start()
        await self._sync_repo.save(sync)

        try:
            known_ids = await self._repo.all_somation_ids()
            crawled = await self._provider.crawl_all(max_pages=max_pages)
            crawled_ids = {p.somation_id for p in crawled}
            now = datetime.utcnow()

            created = updated = enriched = 0
            for row in crawled:
                is_new = row.somation_id not in known_ids
                # Enrich brand-new rows with detail-page fields (bounded per run).
                if is_new and enriched < enrich_limit:
                    try:
                        detail = await self._provider.fetch_detail(row.somation_id)
                        _apply_detail(row, detail)
                        enriched += 1
                        await asyncio.sleep(0.3)
                    except Exception as exc:  # noqa: BLE001
                        logger.warning(
                            "unej detail fetch failed for %s: %s", row.somation_id, exc
                        )
                if await self._upsert(row, seen_at=now):
                    created += 1
                else:
                    updated += 1

            # Anything we knew but did not see this crawl has disappeared.
            # Guard: never archive on an empty crawl (source down / in maintenance)
            # — that would wrongly flag the entire dataset as gone.
            archived = 0
            if crawled_ids:
                disappeared = list(known_ids - crawled_ids)
                archived = await self._repo.mark_archived(disappeared)
            else:
                logger.warning(
                    "unej full_sync crawled 0 rows; skipping archive step to avoid "
                    "false-archiving %d known proceedings",
                    len(known_ids),
                )

            sync.complete(
                records_total=len(crawled),
                records_created=created,
                records_updated=updated,
                records_unchanged=0,
                records_failed=0,
            )
            sync.metadata = {"archived": archived, "enriched": enriched}
            sync.file_checksum = f"crawled={len(crawled)}"
            await self._sync_repo.save(sync)

            return {
                "crawled": len(crawled),
                "created": created,
                "updated": updated,
                "archived": archived,
                "enriched": enriched,
            }
        except Exception as e:
            sync.fail(str(e))
            await self._sync_repo.save(sync)
            raise

    async def search_by_idno(self, idno: str) -> list[EnforcementProceeding]:
        """Resolve enforcement proceedings for a company IDNO (both roles)."""
        existing = await self._repo.find_by_idno(idno)
        if existing:
            fresh = [
                p
                for p in existing
                if p.fetched_at and p.fetched_at.date() == datetime.utcnow().date()
            ]
            if fresh:
                logger.info("Enforcement for IDNO %s is fresh, returning cached", idno)
                return existing

        sync = SyncHistory(
            provider_id=PROVIDER_ID,
            sync_type=SyncType.ON_DEMAND,
            country_code="MD",
        )
        sync.start()
        await self._sync_repo.save(sync)

        try:
            now = datetime.utcnow()
            as_debtor = await self._provider.search(debtor=idno)
            as_creditor = await self._provider.search(creditor=idno)

            for row in as_debtor:
                row.debtor_idno = idno
                row.fetched_at = now
                await self._upsert(row, seen_at=now, role_field="debtor_idno")
            for row in as_creditor:
                row.creditor_idno = idno
                row.fetched_at = now
                await self._upsert(row, seen_at=now, role_field="creditor_idno")

            total = len(as_debtor) + len(as_creditor)
            sync.complete(
                records_total=total,
                records_created=0,
                records_updated=total,
                records_unchanged=0,
                records_failed=0,
            )
            sync.file_checksum = f"idno={idno}"
            await self._sync_repo.save(sync)

            return await self._repo.find_by_idno(idno)
        except Exception as e:
            sync.fail(str(e))
            await self._sync_repo.save(sync)
            raise

    async def _upsert(
        self,
        row: EnforcementProceeding,
        *,
        seen_at: datetime,
        role_field: str | None = None,
    ) -> bool:
        """Insert or merge a proceeding by somation_id. Returns True if created."""
        existing = await self._repo.find_by_somation_id(row.somation_id)
        if existing:
            payload = {
                "debtor_name": row.debtor_name or existing.debtor_name,
                "debtor_idno_masked": row.debtor_idno_masked or existing.debtor_idno_masked,
                "creditor_name": row.creditor_name or existing.creditor_name,
                "executory_doc_number": row.executory_doc_number
                or existing.executory_doc_number,
                "court_name": row.court_name or existing.court_name,
                "case_number": row.case_number or existing.case_number,
                "amount": row.amount if row.amount is not None else existing.amount,
                "publication_date": row.publication_date or existing.publication_date,
                "source_url": row.source_url or existing.source_url,
                "state": EnforcementState.ACTIVE,
                "last_seen_at": seen_at,
                "fetched_at": row.fetched_at or existing.fetched_at,
                "raw_data": {**existing.raw_data, **row.raw_data},
            }
            # Only fill an idno side when this call resolved it.
            if row.debtor_idno:
                payload["debtor_idno"] = row.debtor_idno
            if row.creditor_idno and (
                role_field == "creditor_idno"
                or (existing.creditor_idno is None and role_field is None)
            ):
                payload["creditor_idno"] = row.creditor_idno
            existing.update(**payload)
            await self._repo.save(existing)
            return False

        row.state = EnforcementState.ACTIVE
        row.first_seen_at = seen_at
        row.last_seen_at = seen_at
        if row.fetched_at is None:
            row.fetched_at = seen_at
        await self._repo.save(row)
        return True


def _apply_detail(row: EnforcementProceeding, detail: dict) -> None:
    row.debtor_name = detail.get("debtor_name") or row.debtor_name
    row.debtor_idno_masked = detail.get("debtor_idno_masked") or row.debtor_idno_masked
    row.creditor_idno = detail.get("creditor_idno") or row.creditor_idno
    row.executory_doc_number = detail.get("executory_doc_number") or row.executory_doc_number
    row.court_name = detail.get("court_name") or row.court_name
    row.case_number = detail.get("case_number") or row.case_number
    if detail.get("amount") is not None:
        row.amount = detail["amount"]
    row.publication_date = detail.get("publication_date") or row.publication_date
    row.raw_data = {**row.raw_data, "detail_text": detail.get("raw_text", "")[:2000]}
