from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.domain.sync.entities import SyncHistory, SyncType


class SyncHistoryRepository(ABC):
    """Repository for sync operation history."""

    @abstractmethod
    async def find_by_id(self, sync_id: UUID) -> SyncHistory | None: ...

    @abstractmethod
    async def save(self, sync: SyncHistory) -> SyncHistory: ...

    @abstractmethod
    async def find_running_by_provider(self, provider_id: str) -> SyncHistory | None: ...

    @abstractmethod
    async def find_latest_completed(
        self, provider_id: str, sync_type: SyncType
    ) -> SyncHistory | None: ...

    @abstractmethod
    async def list_by_provider(
        self,
        provider_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[SyncHistory]: ...

    @abstractmethod
    async def count_by_provider(self, provider_id: str) -> int: ...

    @abstractmethod
    async def delete(self, sync_id: UUID) -> None: ...
