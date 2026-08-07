from __future__ import annotations

from datetime import datetime

import pytest

from credibil.countries.moldova.sync.moldac_orchestrator import MoldacSyncOrchestrator
from credibil.domain.accreditation.entities import (
    Accreditation,
    AccreditationCategory,
    AccreditationStatus,
)
from credibil.domain.sync.entities import SyncStatus, SyncType
from tests.in_memory_repos import InMemoryAccreditationRepository, InMemorySyncHistoryRepository


class FakeMOLDACProvider:
    """Fake MOLDAC provider for testing."""

    def __init__(self, accreditations: list[Accreditation] | None = None):
        self._accreditations = accreditations or []

    async def fetch_all_categories(self) -> list[Accreditation]:
        return self._accreditations

    async def fetch_by_category(self, category: AccreditationCategory) -> list[Accreditation]:
        return [a for a in self._accreditations if a.category == category]


@pytest.fixture
def provider():
    return FakeMOLDACProvider()


@pytest.fixture
def accreditation_repo():
    return InMemoryAccreditationRepository()


@pytest.fixture
def sync_repo():
    return InMemorySyncHistoryRepository()


@pytest.fixture
def orchestrator(provider, accreditation_repo, sync_repo):
    return MoldacSyncOrchestrator(
        provider=provider,
        accreditation_repo=accreditation_repo,
        sync_repo=sync_repo,
    )


def _make_accreditation(
    cert_number: str = "LI-001",
    org_name: str = "Test Lab SRL",
    category: AccreditationCategory = AccreditationCategory.TESTING_LAB,
    status: AccreditationStatus = AccreditationStatus.ACTIVE,
) -> Accreditation:
    return Accreditation(
        organization_name=org_name,
        certificate_number=cert_number,
        category=category,
        standard="SM EN ISO/IEC 17025:2018",
        status=status,
    )


class TestMoldacSyncOrchestrator:
    @pytest.mark.anyio
    async def test_sync_all_creates_records(self, orchestrator):
        acc1 = _make_accreditation(cert_number="LI-001")
        acc2 = _make_accreditation(cert_number="LI-002", org_name="Other Lab")
        orchestrator._provider = FakeMOLDACProvider([acc1, acc2])

        result = await orchestrator.sync_all_categories()

        assert result.status == SyncStatus.COMPLETED
        assert result.records_created == 2
        assert result.records_updated == 0
        assert result.records_failed == 0

    @pytest.mark.anyio
    async def test_sync_all_idempotent(self, orchestrator, accreditation_repo):
        acc = _make_accreditation(cert_number="LI-001")
        await accreditation_repo.save(acc)

        orchestrator._provider = FakeMOLDACProvider([acc])
        result = await orchestrator.sync_all_categories()

        assert result.records_created == 0
        assert result.records_unchanged == 1

    @pytest.mark.anyio
    async def test_sync_all_updates_changed_status(self, orchestrator, accreditation_repo):
        acc = _make_accreditation(
            cert_number="LI-001",
            status=AccreditationStatus.ACTIVE,
        )
        await accreditation_repo.save(acc)

        updated_acc = _make_accreditation(
            cert_number="LI-001",
            status=AccreditationStatus.WITHDRAWN,
        )
        orchestrator._provider = FakeMOLDACProvider([updated_acc])

        result = await orchestrator.sync_all_categories()
        assert result.records_updated == 1

        stored = await accreditation_repo.find_by_certificate_number("LI-001")
        assert stored.status == AccreditationStatus.WITHDRAWN

    @pytest.mark.anyio
    async def test_sync_category(self, orchestrator):
        acc = _make_accreditation(
            cert_number="LM-001",
            category=AccreditationCategory.MEDICAL_LAB,
        )
        orchestrator._provider = FakeMOLDACProvider([acc])

        result = await orchestrator.sync_category(AccreditationCategory.MEDICAL_LAB)
        assert result.status == SyncStatus.COMPLETED
        assert result.records_created == 1

    @pytest.mark.anyio
    async def test_concurrent_sync_returns_existing(self, orchestrator, sync_repo):
        from credibil.domain.sync.entities import SyncHistory

        running = SyncHistory(
            provider_id="moldac",
            sync_type=SyncType.FULL,
            country_code="MD",
            status=SyncStatus.RUNNING,
            started_at=datetime.now(),
        )
        await sync_repo.save(running)

        result = await orchestrator.sync_all_categories()
        assert result.id == running.id

    @pytest.mark.anyio
    async def test_sync_creates_sync_history(self, orchestrator, sync_repo):
        orchestrator._provider = FakeMOLDACProvider([])

        await orchestrator.sync_all_categories()

        history = await sync_repo.list_by_provider("moldac")
        assert len(history) == 1
        assert history[0].status == SyncStatus.COMPLETED
