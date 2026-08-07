from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SanctionsProvider(ABC):
    """External sanctions data provider port.

    Implementations fetch from OFAC, EU, UN, or other sanctions lists.
    """

    @abstractmethod
    async def search_by_name(self, name: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search sanctions lists by name."""
        ...

    @abstractmethod
    async def search_by_idno(self, idno: str) -> list[dict[str, Any]]:
        """Search sanctions lists by company IDNO."""
        ...

    @abstractmethod
    async def search_by_idnp(self, idnp: str) -> list[dict[str, Any]]:
        """Search sanctions lists by person IDNP."""
        ...

    @abstractmethod
    async def get_latest_entries(self, since: str | None = None) -> list[dict[str, Any]]:
        """Get latest sanctions entries since a given date (ISO format)."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is reachable."""
        ...
