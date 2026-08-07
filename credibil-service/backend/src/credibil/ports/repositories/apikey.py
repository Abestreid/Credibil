from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.domain.apikey.entities import APIKey


class APIKeyRepository(ABC):
    """Abstract interface for API key data access."""

    @abstractmethod
    async def find_by_id(self, key_id: UUID) -> APIKey | None: ...

    @abstractmethod
    async def find_by_hash(self, key_hash: str) -> APIKey | None: ...

    @abstractmethod
    async def save(self, api_key: APIKey) -> APIKey: ...

    @abstractmethod
    async def delete(self, key_id: UUID) -> None: ...

    @abstractmethod
    async def list_by_tenant(
        self,
        tenant_id: UUID,
        offset: int = 0,
        limit: int = 25,
    ) -> tuple[list[APIKey], int]: ...
