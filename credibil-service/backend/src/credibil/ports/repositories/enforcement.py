from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.domain.enforcement.entities import EnforcementProceeding


class EnforcementRepository(ABC):
    """Repository for enforcement proceedings (unej.md somații)."""

    @abstractmethod
    async def find_by_id(self, proceeding_id: UUID) -> EnforcementProceeding | None: ...

    @abstractmethod
    async def find_by_somation_id(self, somation_id: int) -> EnforcementProceeding | None: ...

    @abstractmethod
    async def find_by_idno(
        self,
        idno: str,
        role: str | None = None,
        state: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EnforcementProceeding]:
        """Proceedings where the IDNO appears as debtor and/or creditor.

        ``role`` filters to "debtor"/"creditor"; ``state`` to "active"/"archived".
        """

    @abstractmethod
    async def save(self, proceeding: EnforcementProceeding) -> EnforcementProceeding: ...

    @abstractmethod
    async def delete(self, proceeding_id: UUID) -> None: ...

    @abstractmethod
    async def list_proceedings(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> list[EnforcementProceeding]: ...

    @abstractmethod
    async def count_by_idno(
        self, idno: str, role: str | None = None, state: str | None = None
    ) -> int: ...

    @abstractmethod
    async def all_somation_ids(self) -> set[int]:
        """Every somation_id currently stored (used to detect disappearances)."""

    @abstractmethod
    async def mark_archived(self, somation_ids: list[int]) -> int:
        """Move the given somation_ids to the ARCHIVED state. Returns rows changed."""
