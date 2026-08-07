from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.domain.sanctions.entities import SanctionsEntry


class SanctionsRepository(ABC):
    """Repository for sanctions entries."""

    @abstractmethod
    async def find_by_id(self, entry_id: UUID) -> SanctionsEntry | None: ...

    @abstractmethod
    async def find_by_target_idno(self, idno: str) -> list[SanctionsEntry]: ...

    @abstractmethod
    async def find_by_target_idnp(self, idnp: str) -> list[SanctionsEntry]: ...

    @abstractmethod
    async def find_active_by_target(
        self, idno: str | None = None, idnp: str | None = None
    ) -> list[SanctionsEntry]: ...

    @abstractmethod
    async def save(self, entry: SanctionsEntry) -> SanctionsEntry: ...

    @abstractmethod
    async def delete(self, entry_id: UUID) -> None: ...

    @abstractmethod
    async def list_entries(
        self, limit: int = 100, offset: int = 0, filters: dict[str, Any] | None = None
    ) -> list[SanctionsEntry]: ...

    @abstractmethod
    async def count_by_target(self, idno: str | None = None, idnp: str | None = None) -> int: ...

    @abstractmethod
    async def count_by_type(self, sanction_type: str) -> int: ...

    @abstractmethod
    async def count_active(self) -> int: ...
