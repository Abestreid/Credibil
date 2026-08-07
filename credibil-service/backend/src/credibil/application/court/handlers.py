from __future__ import annotations

from typing import TYPE_CHECKING

from credibil.application.analytics.court_analytics import (
    compute_case_statistics,
    compute_court_distribution,
    compute_judge_frequency,
    compute_timeline,
)
from credibil.application.court.dto import (
    CaseAnalyticsDTO,
    CaseStatisticsDTO,
    CourtCaseDTO,
    CourtDistributionDTO,
    CourtHearingDTO,
    JudgeFrequencyDTO,
    TimelinePointDTO,
)
from credibil.domain.court.errors import CourtCaseNotFoundError

if TYPE_CHECKING:
    from credibil.application.court.commands import (
        GetCaseAnalyticsQuery,
        GetCaseByNumberQuery,
        GetCaseQuery,
        GetCasesByIdnoQuery,
        GetHearingsQuery,
        GetUpcomingHearingsQuery,
        SearchByIdnoCommand,
        SearchByNameCommand,
        SearchCasesCommand,
        SyncHearingsCommand,
    )
    from credibil.countries.moldova.sync.court_orchestrator import CourtSyncOrchestrator
    from credibil.domain.court.entities import CourtCase
    from credibil.ports.repositories.court_case import CourtCaseRepository, CourtHearingRepository


def _case_to_dto(entity: CourtCase) -> CourtCaseDTO:
    return CourtCaseDTO(**entity.__dict__)


class CourtHandlers:
    """Application service for court case operations."""

    def __init__(
        self,
        case_repo: CourtCaseRepository,
        hearing_repo: CourtHearingRepository,
        sync_orchestrator: CourtSyncOrchestrator | None = None,
    ) -> None:
        self._case_repo = case_repo
        self._hearing_repo = hearing_repo
        self._orchestrator = sync_orchestrator

    async def search_by_idno(self, cmd: SearchByIdnoCommand) -> list[CourtCaseDTO]:
        if self._orchestrator:
            cases = await self._orchestrator.search_by_idno(cmd.idno)
        else:
            cases = await self._case_repo.find_by_idno(cmd.idno)
        return [_case_to_dto(c) for c in cases]

    async def search_by_name(self, cmd: SearchByNameCommand) -> list[CourtCaseDTO]:
        if self._orchestrator:
            cases = await self._orchestrator.search_by_name(cmd.name)
        else:
            cases = []
        return [_case_to_dto(c) for c in cases]

    async def search_cases(self, cmd: SearchCasesCommand) -> list[CourtCaseDTO]:
        if self._orchestrator:
            cases = await self._orchestrator.search_by_idno(cmd.query)
        else:
            cases = await self._case_repo.list_cases(limit=cmd.limit)
        return [_case_to_dto(c) for c in cases]

    async def get_case(self, query: GetCaseQuery) -> CourtCaseDTO:
        case = await self._case_repo.find_by_id(query.case_id)
        if not case:
            raise CourtCaseNotFoundError(str(query.case_id))
        return _case_to_dto(case)

    async def get_case_by_number(self, query: GetCaseByNumberQuery) -> CourtCaseDTO:
        case = await self._case_repo.find_by_case_number(query.case_number)
        if not case:
            raise CourtCaseNotFoundError(query.case_number)
        return _case_to_dto(case)

    async def get_cases_by_idno(self, query: GetCasesByIdnoQuery) -> list[CourtCaseDTO]:
        cases = await self._case_repo.find_by_idno(
            query.idno, role=query.role, limit=query.limit, offset=query.offset
        )
        return [_case_to_dto(c) for c in cases]

    async def get_analytics(self, query: GetCaseAnalyticsQuery) -> CaseAnalyticsDTO:
        cases = await self._case_repo.find_by_idno(query.idno)
        stats = compute_case_statistics(cases)
        judges = compute_judge_frequency(cases)
        courts = compute_court_distribution(cases)
        timeline = compute_timeline(cases)

        return CaseAnalyticsDTO(
            idno=query.idno,
            statistics=CaseStatisticsDTO(**stats),
            top_judges=[JudgeFrequencyDTO(**j) for j in judges[:10]],
            court_distribution=[CourtDistributionDTO(**c) for c in courts],
            timeline=[TimelinePointDTO(**t) for t in timeline],
        )

    async def get_hearings(self, query: GetHearingsQuery) -> list[CourtHearingDTO]:
        hearings = await self._hearing_repo.find_by_case_number(
            query.case_number, limit=query.limit, offset=query.offset
        )
        return [CourtHearingDTO(**h.__dict__) for h in hearings]

    async def get_upcoming_hearings(self, query: GetUpcomingHearingsQuery) -> list[CourtHearingDTO]:
        hearings = await self._hearing_repo.find_upcoming_by_idno(query.idno, query.limit)
        return [CourtHearingDTO(**h.__dict__) for h in hearings]

    async def sync_hearings(self, cmd: SyncHearingsCommand) -> list[CourtHearingDTO]:
        if not self._orchestrator:
            raise RuntimeError("Sync orchestrator not configured")
        hearings = await self._orchestrator.sync_hearings(court_slug=cmd.court_slug)
        return [CourtHearingDTO(**h.__dict__) for h in hearings]
