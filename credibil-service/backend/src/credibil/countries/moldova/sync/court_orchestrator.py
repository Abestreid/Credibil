from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from credibil.domain.court.entities import CourtCase, CourtHearing
from credibil.domain.sync.entities import SyncHistory, SyncType

if TYPE_CHECKING:
    from credibil.countries.moldova.providers.justitie_provider import InstanteProvider
    from credibil.ports.repositories.court_case import CourtCaseRepository, CourtHearingRepository
    from credibil.ports.repositories.sync_history import SyncHistoryRepository

logger = logging.getLogger(__name__)


class CourtSyncOrchestrator:
    """Orchestrates court case data fetching from instente.justice.md.

    Supports on-demand search by IDNO and bulk hearing sync.
    """

    def __init__(
        self,
        case_repo: CourtCaseRepository,
        hearing_repo: CourtHearingRepository,
        sync_repo: SyncHistoryRepository,
        provider: InstanteProvider,
    ) -> None:
        self._case_repo = case_repo
        self._hearing_repo = hearing_repo
        self._sync_repo = sync_repo
        self._provider = provider

    async def search_by_idno(self, idno: str) -> list[CourtCase]:
        """Search court cases where the given IDNO appears as plaintiff or defendant."""
        existing = await self._case_repo.find_by_idno(idno)
        if existing:
            fresh_cases = [
                c
                for c in existing
                if c.fetched_at and c.fetched_at.date() == datetime.utcnow().date()
            ]
            if fresh_cases:
                logger.info("Court cases for IDNO %s are fresh, returning cached", idno)
                return existing

        sync = SyncHistory(
            provider_id="instante_justice_md",
            sync_type=SyncType.ON_DEMAND,
            country_code="MD",
        )
        sync.start()
        await self._sync_repo.save(sync)

        try:
            cases = await self._provider.search_cases(query=idno)
            saved_cases = []
            for case in cases:
                case.fetched_at = datetime.utcnow()
                existing_case = await self._case_repo.find_by_case_number(case.case_number)
                if existing_case:
                    case.id = existing_case.id
                    case.created_at = existing_case.created_at
                saved = await self._case_repo.save(case)
                saved_cases.append(saved)

            sync.complete(
                records_total=len(cases),
                records_created=sum(1 for c in saved_cases if c.created_at == c.updated_at),
                records_updated=sum(1 for c in saved_cases if c.created_at != c.updated_at),
                records_unchanged=0,
                records_failed=0,
            )
            sync.file_checksum = f"idno={idno}"
            await self._sync_repo.save(sync)

            return saved_cases

        except Exception as e:
            sync.fail(str(e))
            await self._sync_repo.save(sync)
            raise

    async def search_by_name(self, name: str) -> list[CourtCase]:
        """Search court cases by party name."""
        sync = SyncHistory(
            provider_id="instante_justice_md",
            sync_type=SyncType.ON_DEMAND,
            country_code="MD",
        )
        sync.start()
        await self._sync_repo.save(sync)

        try:
            cases = await self._provider.search_cases(query=name)
            saved_cases = []
            for case in cases:
                case.fetched_at = datetime.utcnow()
                existing_case = await self._case_repo.find_by_case_number(case.case_number)
                if existing_case:
                    case.id = existing_case.id
                    case.created_at = existing_case.created_at
                saved = await self._case_repo.save(case)
                saved_cases.append(saved)

            sync.complete(
                records_total=len(cases),
                records_created=sum(1 for c in saved_cases if c.created_at == c.updated_at),
                records_updated=sum(1 for c in saved_cases if c.created_at != c.updated_at),
                records_unchanged=0,
                records_failed=0,
            )
            sync.file_checksum = f"name={name}"
            await self._sync_repo.save(sync)

            return saved_cases

        except Exception as e:
            sync.fail(str(e))
            await self._sync_repo.save(sync)
            raise

    async def fetch_case_detail(self, case_url: str) -> CourtCase | None:
        """Fetch detailed case information from a specific URL."""
        detail = await self._provider.fetch_case_detail(case_url)

        case_number = detail.get("case_number")
        if not case_number:
            return None

        existing = await self._case_repo.find_by_case_number(case_number)
        if existing:
            existing.update(
                judge_name=detail.get("judge_name") or existing.judge_name,
                plaintiff_name=detail.get("plaintiff_name") or existing.plaintiff_name,
                defendant_name=detail.get("defendant_name") or existing.defendant_name,
                subject_matter=detail.get("subject_matter") or existing.subject_matter,
                raw_data={**existing.raw_data, **detail.get("raw_fields", {})},
                fetched_at=datetime.utcnow(),
            )
            return await self._case_repo.save(existing)

        case = CourtCase(
            case_number=case_number,
            court_name=detail.get("court_name") or "Unknown",
            judge_name=detail.get("judge_name"),
            plaintiff_name=detail.get("plaintiff_name"),
            defendant_name=detail.get("defendant_name"),
            subject_matter=detail.get("subject_matter"),
            source_url=case_url,
            raw_data=detail.get("raw_fields", {}),
            fetched_at=datetime.utcnow(),
        )
        return await self._case_repo.save(case)

    async def sync_hearings(
        self,
        court_slug: str | None = None,
    ) -> list[CourtHearing]:
        """Fetch and store hearing agenda entries."""
        sync = SyncHistory(
            provider_id="instante_justice_md_agenda",
            sync_type=SyncType.INCREMENTAL,
            country_code="MD",
        )
        sync.start()
        await self._sync_repo.save(sync)

        try:
            hearings = await self._provider.fetch_hearings(court_slug=court_slug)
            saved = []
            for hearing in hearings:
                existing = await self._hearing_repo.find_by_id(hearing.id)
                if not existing:
                    saved_hearing = await self._hearing_repo.save(hearing)
                    saved.append(saved_hearing)

            sync.complete(
                records_total=len(hearings),
                records_created=len(saved),
                records_updated=0,
                records_unchanged=len(hearings) - len(saved),
                records_failed=0,
            )
            sync.file_checksum = f"court={court_slug or 'all'}"
            await self._sync_repo.save(sync)

            return saved

        except Exception as e:
            sync.fail(str(e))
            await self._sync_repo.save(sync)
            raise
