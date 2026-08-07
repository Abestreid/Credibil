from __future__ import annotations

import pytest

from credibil.domain.sync.entities import SyncHistory, SyncStatus, SyncType


class TestSyncHistoryEntity:
    def test_create_pending(self) -> None:
        sync = SyncHistory(
            provider_id="ckan_bulk",
            sync_type=SyncType.FULL,
            country_code="MD",
        )
        assert sync.status == SyncStatus.PENDING
        assert sync.provider_id == "ckan_bulk"
        assert sync.country_code == "MD"
        assert sync.records_total == 0
        assert sync.id is not None

    def test_start_sets_running(self) -> None:
        sync = SyncHistory(
            provider_id="ckan_bulk",
            sync_type=SyncType.INCREMENTAL,
            country_code="MD",
        )
        sync.start()
        assert sync.status == SyncStatus.RUNNING
        assert sync.started_at is not None

    def test_complete(self) -> None:
        sync = SyncHistory(
            provider_id="ckan_bulk",
            sync_type=SyncType.FULL,
            country_code="MD",
        )
        sync.start()
        sync.complete(
            records_total=100,
            records_created=50,
            records_updated=30,
            records_unchanged=15,
            records_failed=5,
        )
        assert sync.status == SyncStatus.COMPLETED
        assert sync.finished_at is not None
        assert sync.records_total == 100
        assert sync.records_created == 50
        assert sync.records_failed == 5
        assert sync.duration_seconds is not None
        assert sync.duration_seconds >= 0

    def test_fail(self) -> None:
        sync = SyncHistory(
            provider_id="ckan_bulk",
            sync_type=SyncType.FULL,
            country_code="MD",
        )
        sync.start()
        sync.fail("Network timeout")
        assert sync.status == SyncStatus.FAILED
        assert sync.error_message == "Network timeout"
        assert sync.duration_seconds is not None

    def test_repr(self) -> None:
        sync = SyncHistory(
            provider_id="test_provider",
            sync_type=SyncType.ON_DEMAND,
            country_code="RO",
        )
        r = repr(sync)
        assert "test_provider" in r
        assert "on_demand" in r


class TestSyncHistoryRepository:
    @pytest.mark.asyncio
    async def test_save_and_find(self, sync_repo: "InMemorySyncHistoryRepository") -> None:
        sync = SyncHistory(
            provider_id="ckan_bulk",
            sync_type=SyncType.FULL,
            country_code="MD",
        )
        await sync_repo.save(sync)
        found = await sync_repo.find_by_id(sync.id)
        assert found is not None
        assert found.provider_id == "ckan_bulk"

    @pytest.mark.asyncio
    async def test_find_running(self, sync_repo: "InMemorySyncHistoryRepository") -> None:
        sync = SyncHistory(
            provider_id="ckan_bulk",
            sync_type=SyncType.FULL,
            country_code="MD",
        )
        sync.start()
        await sync_repo.save(sync)
        running = await sync_repo.find_running_by_provider("ckan_bulk")
        assert running is not None
        assert running.id == sync.id

    @pytest.mark.asyncio
    async def test_find_latest_completed(self, sync_repo: "InMemorySyncHistoryRepository") -> None:
        sync = SyncHistory(
            provider_id="ckan_bulk",
            sync_type=SyncType.FULL,
            country_code="MD",
        )
        sync.start()
        sync.complete(100, 50, 30, 15, 5)
        await sync_repo.save(sync)

        latest = await sync_repo.find_latest_completed("ckan_bulk", SyncType.FULL)
        assert latest is not None
        assert latest.records_total == 100

    @pytest.mark.asyncio
    async def test_count(self, sync_repo: "InMemorySyncHistoryRepository") -> None:
        for _i in range(3):
            sync = SyncHistory(
                provider_id="ckan_bulk",
                sync_type=SyncType.FULL,
                country_code="MD",
            )
            await sync_repo.save(sync)
        count = await sync_repo.count_by_provider("ckan_bulk")
        assert count == 3

    @pytest.mark.asyncio
    async def test_delete(self, sync_repo: "InMemorySyncHistoryRepository") -> None:
        sync = SyncHistory(
            provider_id="ckan_bulk",
            sync_type=SyncType.FULL,
            country_code="MD",
        )
        await sync_repo.save(sync)
        await sync_repo.delete(sync.id)
        found = await sync_repo.find_by_id(sync.id)
        assert found is None
