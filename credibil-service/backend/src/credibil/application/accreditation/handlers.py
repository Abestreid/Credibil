from __future__ import annotations

import logging
from collections import Counter
from typing import TYPE_CHECKING

from credibil.application.accreditation.dto import (
    AccreditationDTO,
    AccreditationStatisticsDTO,
    AccreditationSyncResultDTO,
)
from credibil.domain.accreditation.errors import AccreditationNotFoundError

if TYPE_CHECKING:
    from credibil.application.accreditation import (
        GetAccreditationQuery,
        GetAccreditationStatisticsQuery,
        ListAccreditationsQuery,
        SyncAccreditationsCommand,
    )
    from credibil.countries.moldova.sync.moldac_orchestrator import MoldacSyncOrchestrator
    from credibil.ports.repositories.accreditation import AccreditationRepository

logger = logging.getLogger(__name__)


class AccreditationHandlers:
    """Handlers for accreditation commands and queries."""

    def __init__(
        self,
        accreditation_repo: AccreditationRepository,
        orchestrator: MoldacSyncOrchestrator | None = None,
    ) -> None:
        self._repo = accreditation_repo
        self._orchestrator = orchestrator

    async def sync(self, command: SyncAccreditationsCommand) -> AccreditationSyncResultDTO:
        """Trigger MOLDAC sync."""
        if not self._orchestrator:
            raise ValueError("Orchestrator not configured")

        if command.category:
            sync = await self._orchestrator.sync_category(command.category)
        else:
            sync = await self._orchestrator.sync_all_categories()

        return AccreditationSyncResultDTO(
            sync_id=sync.id,
            status=sync.status.value,
            records_created=sync.records_created,
            records_updated=sync.records_updated,
            records_unchanged=sync.records_unchanged,
            records_failed=sync.records_failed,
        )

    async def get(self, query: GetAccreditationQuery) -> AccreditationDTO:
        """Get a single accreditation by ID or certificate number."""
        acc = None
        if query.accreditation_id:
            acc = await self._repo.find_by_id(query.accreditation_id)
        elif query.certificate_number:
            acc = await self._repo.find_by_certificate_number(query.certificate_number)

        if not acc:
            identifier = query.certificate_number or str(query.accreditation_id)
            raise AccreditationNotFoundError(identifier)

        return AccreditationDTO(
            id=acc.id,
            organization_name=acc.organization_name,
            director_name=acc.director_name,
            address=acc.address,
            phone=acc.phone,
            fax=acc.fax,
            email=acc.email,
            certificate_number=acc.certificate_number,
            category=acc.category.value,
            standard=acc.standard,
            status=acc.status.value,
            issue_date=acc.issue_date.isoformat() if acc.issue_date else None,
            expiry_date=acc.expiry_date.isoformat() if acc.expiry_date else None,
            scope=acc.scope,
            certificate_url=acc.certificate_url,
            annex_urls=acc.annex_urls,
            remarks=acc.remarks,
            country_code=acc.country_code,
            source_url=acc.source_url,
            last_synced=acc.last_synced.isoformat() if acc.last_synced else None,
            created_at=acc.created_at.isoformat() if acc.created_at else None,
            updated_at=acc.updated_at.isoformat() if acc.updated_at else None,
        )

    async def list(self, query: ListAccreditationsQuery) -> list[AccreditationDTO]:
        """List accreditations with optional filters."""
        filters: dict[str, str] = {}
        if query.category:
            filters["category"] = query.category.value
        if query.status:
            filters["status"] = query.status.value
        if query.keyword:
            filters["keyword"] = query.keyword

        accreditations = await self._repo.list_accreditations(
            limit=query.limit, offset=query.offset, filters=filters if filters else None
        )

        return [
            AccreditationDTO(
                id=acc.id,
                organization_name=acc.organization_name,
                director_name=acc.director_name,
                address=acc.address,
                phone=acc.phone,
                fax=acc.fax,
                email=acc.email,
                certificate_number=acc.certificate_number,
                category=acc.category.value,
                standard=acc.standard,
                status=acc.status.value,
                issue_date=acc.issue_date.isoformat() if acc.issue_date else None,
                expiry_date=acc.expiry_date.isoformat() if acc.expiry_date else None,
                scope=acc.scope,
                certificate_url=acc.certificate_url,
                annex_urls=acc.annex_urls,
                remarks=acc.remarks,
                country_code=acc.country_code,
                source_url=acc.source_url,
                last_synced=acc.last_synced.isoformat() if acc.last_synced else None,
                created_at=acc.created_at.isoformat() if acc.created_at else None,
                updated_at=acc.updated_at.isoformat() if acc.updated_at else None,
            )
            for acc in accreditations
        ]

    async def get_statistics(
        self, query: GetAccreditationStatisticsQuery
    ) -> AccreditationStatisticsDTO:
        """Get accreditation statistics."""
        if query.category:
            accreditations = await self._repo.find_by_category(query.category, limit=10000)
        else:
            accreditations = await self._repo.list_accreditations(limit=10000)

        total = len(accreditations)
        by_status = Counter(a.status.value for a in accreditations)
        by_category = Counter(a.category.value for a in accreditations)
        by_standard = Counter(a.standard for a in accreditations)

        return AccreditationStatisticsDTO(
            total=total,
            by_status=dict(by_status),
            by_category=dict(by_category),
            by_standard=dict(by_standard),
        )

    async def search(self, keyword: str, limit: int = 100) -> list[AccreditationDTO]:
        """Search accreditations by keyword."""
        accreditations = await self._repo.search_by_keyword(keyword, limit=limit)

        return [
            AccreditationDTO(
                id=acc.id,
                organization_name=acc.organization_name,
                director_name=acc.director_name,
                address=acc.address,
                phone=acc.phone,
                fax=acc.fax,
                email=acc.email,
                certificate_number=acc.certificate_number,
                category=acc.category.value,
                standard=acc.standard,
                status=acc.status.value,
                issue_date=acc.issue_date.isoformat() if acc.issue_date else None,
                expiry_date=acc.expiry_date.isoformat() if acc.expiry_date else None,
                scope=acc.scope,
                certificate_url=acc.certificate_url,
                annex_urls=acc.annex_urls,
                remarks=acc.remarks,
                country_code=acc.country_code,
                source_url=acc.source_url,
                last_synced=acc.last_synced.isoformat() if acc.last_synced else None,
                created_at=acc.created_at.isoformat() if acc.created_at else None,
                updated_at=acc.updated_at.isoformat() if acc.updated_at else None,
            )
            for acc in accreditations
        ]
