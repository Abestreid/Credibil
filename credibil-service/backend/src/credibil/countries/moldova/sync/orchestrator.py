from __future__ import annotations

import contextlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import httpx

from credibil.countries.moldova.normalizer import raw_row_to_company
from credibil.countries.moldova.parsers.xlsx_parser import XLSXCompanyParser
from credibil.countries.moldova.providers.ckan_provider import CKANMetadata
from credibil.domain.sync.entities import SyncHistory, SyncType
from credibil.domain.sync.errors import SyncAlreadyRunningError

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from credibil.domain.company.entities import Company
    from credibil.ports.providers.storage import StorageProvider
    from credibil.ports.repositories.company import CompanyRepository
    from credibil.ports.repositories.sync_history import SyncHistoryRepository

logger = logging.getLogger(__name__)

# Provider priority defaults (lower = higher priority)
DEFAULT_PROVIDER_PRIORITY: dict[str, int] = {
    "ckan_bulk": 1,
    "idno_md": 2,
    "manual": 3,
}


class CKANSyncOrchestrator:
    """Orchestrates bulk CKAN data sync into the local database.

    Steps:
    1. Fetch metadata from CKAN to get download URL
    2. Download XLSX to local storage
    3. Parse XLSX rows
    4. Normalize each row into a Company entity
    5. Upsert into the repository (idempotent by IDNO)
    6. Record sync history
    """

    def __init__(
        self,
        company_repo: CompanyRepository,
        sync_repo: SyncHistoryRepository,
        storage: StorageProvider,
        session: AsyncSession | None = None,
        provider_priorities: dict[str, int] | None = None,
    ) -> None:
        self._company_repo = company_repo
        self._sync_repo = sync_repo
        self._storage = storage
        self._session = session
        self._priorities = provider_priorities or DEFAULT_PROVIDER_PRIORITY
        self._ckan = CKANMetadata()

    async def sync_full(self) -> SyncHistory:
        """Full sync — download latest XLSX and upsert all rows."""
        return await self._run_sync(SyncType.FULL)

    async def sync_incremental(self) -> SyncHistory:
        """Incremental sync — same as full for CKAN bulk (no delta available)."""
        return await self._run_sync(SyncType.INCREMENTAL)

    async def _run_sync(self, sync_type: SyncType) -> SyncHistory:
        sync = SyncHistory(
            provider_id="ckan_bulk",
            sync_type=sync_type,
            country_code="MD",
        )

        existing = await self._sync_repo.find_running_by_provider("ckan_bulk")
        if existing:
            raise SyncAlreadyRunningError("ckan_bulk")

        try:
            sync.start()
            await self._sync_repo.save(sync)

            # Step 1: Download
            filepath, checksum = await self._download_xlsx()
            sync.file_path = filepath
            sync.file_checksum = checksum
            await self._sync_repo.save(sync)

            # Step 2: Parse + normalize + upsert
            stats = await self._parse_and_upsert(filepath)

            # Step 3: Complete
            sync.complete(
                records_total=stats["total"],
                records_created=stats["created"],
                records_updated=stats["updated"],
                records_unchanged=stats["unchanged"],
                records_failed=stats["failed"],
            )
            await self._sync_repo.save(sync)
            logger.info(
                "CKAN sync completed: total=%d created=%d updated=%d unchanged=%d failed=%d",
                stats["total"],
                stats["created"],
                stats["updated"],
                stats["unchanged"],
                stats["failed"],
            )
            return sync

        except Exception as e:
            sync.fail(str(e))
            await self._sync_repo.save(sync)
            raise

    async def _download_xlsx(self) -> tuple[str, str]:
        """Download XLSX from CKAN to local storage."""
        url = await self._ckan.get_download_url()
        logger.info("Downloading CKAN XLSX from %s", url)

        async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        import hashlib

        checksum = hashlib.sha256(resp.content).hexdigest()
        filename = url.split("/")[-1] or "moldova_companies.xlsx"
        if not filename.endswith((".xlsx", ".xls")):
            filename += ".xlsx"

        from io import BytesIO

        stored = await self._storage.store(
            file_obj=BytesIO(resp.content),
            filename=filename,
            directory="ckan/moldova",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            metadata={"source_url": url, "ckan_checksum": checksum},
        )

        logger.info(
            "Downloaded %s (%d bytes, sha256=%s)",
            filename,
            stored.size_bytes,
            checksum[:16],
        )
        return stored.path, checksum

    async def _parse_and_upsert(self, filepath: str) -> dict[str, int]:
        """Parse XLSX and upsert companies. Returns stats.

        Commits each batch of rows individually to avoid long-running
        transactions. On failure within a batch, falls back to row-by-row
        commits so one bad row doesn't lose the whole batch.
        """
        full_path = str(Path("data/raw") / filepath)
        parser = XLSXCompanyParser(full_path)

        stats = {"total": 0, "created": 0, "updated": 0, "unchanged": 0, "failed": 0}
        batch_size = 500
        pending_batch: list[tuple] = []

        for raw_row in parser.parse_rows():
            stats["total"] += 1
            try:
                company = raw_row_to_company(raw_row)
                pending_batch.append((raw_row, company))
            except Exception as e:
                stats["failed"] += 1
                if stats["failed"] <= 10:
                    logger.warning("Failed to normalize row %s: %s", raw_row.get("idno"), e)

            if len(pending_batch) >= batch_size:
                batch_stats = await self._commit_batch(pending_batch)
                for k, v in batch_stats.items():
                    stats[k] += v
                pending_batch.clear()
                logger.info(
                    "Progress: total=%d created=%d updated=%d unchanged=%d failed=%d",
                    stats["total"],
                    stats["created"],
                    stats["updated"],
                    stats["unchanged"],
                    stats["failed"],
                )

        # Final batch
        if pending_batch:
            batch_stats = await self._commit_batch(pending_batch)
            for k, v in batch_stats.items():
                stats[k] += v

        return stats

    async def _commit_batch(self, batch: list[tuple]) -> dict[str, int]:
        """Try to commit a batch. On failure, fall back to row-by-row."""
        batch_stats = {"created": 0, "updated": 0, "unchanged": 0, "failed": 0}

        # Try batch insert first
        try:
            for _raw_row, company in batch:
                existing = await self._company_repo.find_by_idno(company.idno)
                if existing:
                    if self._has_meaningful_changes(existing, company):
                        existing.update(
                            name_ro=company.name_ro,
                            name_ru=company.name_ru,
                            registration_date=company.registration_date,
                            status=company.status,
                            legal_form=company.legal_form,
                            legal_address=company.legal_address,
                            caem_description=company.caem_description,
                            cuatm=company.cuatm,
                            founder_count=company.founder_count,
                            director_count=company.director_count,
                            metadata=company.metadata,
                        )
                        await self._company_repo.save(existing)
                        batch_stats["updated"] += 1
                    else:
                        batch_stats["unchanged"] += 1
                else:
                    await self._company_repo.save(company)
                    batch_stats["created"] += 1
            await self._session.commit()
            return batch_stats
        except Exception:
            with contextlib.suppress(Exception):
                await self._session.rollback()

        # Fallback: row-by-row
        batch_stats = {"created": 0, "updated": 0, "unchanged": 0, "failed": 0}
        for raw_row, company in batch:
            try:
                existing = await self._company_repo.find_by_idno(company.idno)
                if existing:
                    if self._has_meaningful_changes(existing, company):
                        existing.update(
                            name_ro=company.name_ro,
                            name_ru=company.name_ru,
                            registration_date=company.registration_date,
                            status=company.status,
                            legal_form=company.legal_form,
                            legal_address=company.legal_address,
                            caem_description=company.caem_description,
                            cuatm=company.cuatm,
                            founder_count=company.founder_count,
                            director_count=company.director_count,
                            metadata=company.metadata,
                        )
                        await self._company_repo.save(existing)
                        await self._session.commit()
                        batch_stats["updated"] += 1
                    else:
                        batch_stats["unchanged"] += 1
                else:
                    await self._company_repo.save(company)
                    await self._session.commit()
                    batch_stats["created"] += 1
            except Exception as e:
                batch_stats["failed"] += 1
                with contextlib.suppress(Exception):
                    await self._session.rollback()
                if batch_stats["failed"] <= 5:
                    logger.warning("Row-by-row failed for %s: %s", raw_row.get("idno"), e)

        return batch_stats

    def _has_meaningful_changes(self, existing: Company, incoming: Company) -> bool:
        """Check if incoming data has meaningful changes vs existing."""
        fields_to_compare = [
            "name_ro",
            "registration_date",
            "status",
            "legal_form",
            "legal_address",
            "caem_description",
            "cuatm",
            "founder_count",
            "director_count",
        ]
        for field in fields_to_compare:
            if getattr(existing, field) != getattr(incoming, field):
                return True
        return False

    async def health_check(self) -> bool:
        return await self._ckan.health_check()
