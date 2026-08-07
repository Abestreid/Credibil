from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.domain.user.entities import User


class UserRepository(ABC):
    """Abstract interface for user data access."""

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user_id: UUID) -> None: ...

    @abstractmethod
    async def list_users(
        self,
        tenant_id: UUID | None = None,
        offset: int = 0,
        limit: int = 25,
    ) -> tuple[list[User], int]: ...

    @abstractmethod
    async def count_by_email(self, email: str) -> int: ...

    @abstractmethod
    async def exists(self, user_id: UUID) -> bool: ...
