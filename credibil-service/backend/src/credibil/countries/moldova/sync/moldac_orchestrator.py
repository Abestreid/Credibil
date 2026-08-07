from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from credibil.domain.sync.entities import SyncHistory, SyncStatus, SyncType

if TYPE_CHECKING:
    from credibil.countries.moldova.providers.moldac_provider import MOLDACProvider
    from credibil.domain.accreditation.entities import AccreditationCategory
    from credibil.ports.repositories.accreditation import AccreditationRepository
    from credibil.ports.repositories.sync_history import SyncHistoryRepository

logger = logging.getLogger(__name__)

PROVIDER_ID = "moldac"
COUNTRY_CODE = "MD"


class MoldacSyncOrchestrator:
    """Orchestrates MOLDAC accreditation data synchronization."""

    def __init__(
        self,
        provider: MOLDACProvider,
        accreditation_repo: AccreditationRepository,
        sync_repo: SyncHistoryRepository,
    ) -> None:
        self._provider = provider
        self._accreditation_repo = accreditation_repo
        self._sync_repo = sync_repo

    async def sync_all_categories(self) -> SyncHistory:
        """Sync all 7 registry categories from acreditare.md."""
        running = await self._sync_repo.find_running_by_provider(PROVIDER_ID)
        if running:
            logger.warning("Sync already running (id=%s), skipping", running.id)
            return running

        sync = SyncHistory(
            provider_id=PROVIDER_ID,
            sync_type=SyncType.FULL,
            country_code=COUNTRY_CODE,
            status=SyncStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        await self._sync_repo.save(sync)

        created = 0
        updated = 0
        unchanged = 0
        failed = 0

        try:
            accreditations = await self._provider.fetch_all_categories()
            sync.records_total = len(accreditations)

            for acc in accreditations:
                try:
                    existing = await self._accreditation_repo.find_by_certificate_number(
                        acc.certificate_number
                    )
                    if existing:
                        if existing.status != acc.status or existing.remarks != acc.remarks:
                            existing.update(
                                status=acc.status,
                                remarks=acc.remarks,
                                expiry_date=acc.expiry_date,
                                scope=acc.scope,
                                annex_urls=acc.annex_urls,
                                raw_data=acc.raw_data,
                                last_synced=datetime.utcnow(),
                            )
                            await self._accreditation_repo.save(existing)
                            updated += 1
                        else:
                            unchanged += 1
                    else:
                        acc.last_synced = datetime.utcnow()
                        await self._accreditation_repo.save(acc)
                        created += 1
                except Exception as e:
                    logger.error(
                        "Failed to upsert accreditation %s: %s",
                        acc.certificate_number,
                        e,
                    )
                    failed += 1

            sync.status = SyncStatus.COMPLETED
            sync.records_created = created
            sync.records_updated = updated
            sync.records_unchanged = unchanged
            sync.records_failed = failed
            sync.finished_at = datetime.utcnow()

            logger.info(
                "MOLDAC sync completed: created=%d updated=%d unchanged=%d failed=%d",
                created,
                updated,
                unchanged,
                failed,
            )
        except Exception as e:
            sync.status = SyncStatus.FAILED
            sync.records_failed = failed + 1
            sync.finished_at = datetime.utcnow()
            sync.error_message = str(e)
            logger.error("MOLDAC sync failed: %s", e)

        await self._sync_repo.save(sync)
        return sync

    async def sync_category(self, category: AccreditationCategory) -> SyncHistory:
        """Sync a single registry category."""
        running = await self._sync_repo.find_running_by_provider(PROVIDER_ID)
        if running:
            logger.warning("Sync already running (id=%s), skipping", running.id)
            return running

        sync = SyncHistory(
            provider_id=f"{PROVIDER_ID}:{category.value}",
            sync_type=SyncType.INCREMENTAL,
            country_code=COUNTRY_CODE,
            status=SyncStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        await self._sync_repo.save(sync)

        created = 0
        updated = 0
        unchanged = 0
        failed = 0

        try:
            accreditations = await self._provider.fetch_by_category(category)
            sync.records_total = len(accreditations)

            for acc in accreditations:
                try:
                    existing = await self._accreditation_repo.find_by_certificate_number(
                        acc.certificate_number
                    )
                    if existing:
                        if existing.status != acc.status or existing.remarks != acc.remarks:
                            existing.update(
                                status=acc.status,
                                remarks=acc.remarks,
                                expiry_date=acc.expiry_date,
                                last_synced=datetime.utcnow(),
                            )
                            await self._accreditation_repo.save(existing)
                            updated += 1
                        else:
                            unchanged += 1
                    else:
                        acc.last_synced = datetime.utcnow()
                        await self._accreditation_repo.save(acc)
                        created += 1
                except Exception as e:
                    logger.error(
                        "Failed to upsert accreditation %s: %s",
                        acc.certificate_number,
                        e,
                    )
                    failed += 1

            sync.status = SyncStatus.COMPLETED
            sync.records_created = created
            sync.records_updated = updated
            sync.records_unchanged = unchanged
            sync.records_failed = failed
            sync.finished_at = datetime.utcnow()
        except Exception as e:
            sync.status = SyncStatus.FAILED
            sync.records_failed = failed + 1
            sync.finished_at = datetime.utcnow()
            sync.error_message = str(e)
            logger.error("MOLDAC category sync failed: %s", e)

        await self._sync_repo.save(sync)
        return sync
