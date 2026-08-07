from __future__ import annotations

from typing import Any

from credibil.domain.sanctions.entities import SanctionsEntry
from credibil.domain.sanctions.enums import SanctionStatus
from credibil.ports.repositories.sanctions import SanctionsRepository


class InMemorySanctionsRepository(SanctionsRepository):
    def __init__(self) -> None:
        self._records: dict[Any, SanctionsEntry] = {}

    async def find_by_id(self, entry_id: Any) -> SanctionsEntry | None:
        return self._records.get(entry_id)

    async def find_by_target_idno(self, idno: str) -> list[SanctionsEntry]:
        return [e for e in self._records.values() if e.target_idno == idno]

    async def find_by_target_idnp(self, idnp: str) -> list[SanctionsEntry]:
        return [e for e in self._records.values() if e.target_idnp == idnp]

    async def find_active_by_target(
        self, idno: str | None = None, idnp: str | None = None
    ) -> list[SanctionsEntry]:
        items = list(self._records.values())
        if idno:
            items = [e for e in items if e.target_idno == idno]
        if idnp:
            items = [e for e in items if e.target_idnp == idnp]
        return [e for e in items if e.status == SanctionStatus.ACTIVE]

    async def save(self, entry: SanctionsEntry) -> SanctionsEntry:
        self._records[entry.id] = entry
        return entry

    async def delete(self, entry_id: Any) -> None:
        self._records.pop(entry_id, None)

    async def list_entries(
        self, limit: int = 100, offset: int = 0, filters: dict[str, Any] | None = None
    ) -> list[SanctionsEntry]:
        items = list(self._records.values())
        if filters:
            if "sanction_type" in filters:
                items = [e for e in items if e.sanction_type.value == filters["sanction_type"]]
            if "status" in filters:
                items = [e for e in items if e.status.value == filters["status"]]
            if "country_code" in filters:
                items = [e for e in items if e.country_code == filters["country_code"]]
        items.sort(key=lambda e: e.created_at, reverse=True)
        return items[offset : offset + limit]

    async def count_by_target(self, idno: str | None = None, idnp: str | None = None) -> int:
        items = list(self._records.values())
        if idno:
            items = [e for e in items if e.target_idno == idno]
        if idnp:
            items = [e for e in items if e.target_idnp == idnp]
        return len(items)

    async def count_by_type(self, sanction_type: str) -> int:
        return sum(1 for e in self._records.values() if e.sanction_type.value == sanction_type)

    async def count_active(self) -> int:
        return sum(1 for e in self._records.values() if e.status == SanctionStatus.ACTIVE)
