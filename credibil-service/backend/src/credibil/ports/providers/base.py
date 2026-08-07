from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseProvider(ABC, Generic[T]):
    """Base interface for all external data providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str: ...

    @property
    @abstractmethod
    def country_code(self) -> str: ...

    @property
    @abstractmethod
    def data_source_name(self) -> str: ...

    @abstractmethod
    async def health_check(self) -> bool: ...

    @abstractmethod
    async def fetch_by_identifier(self, identifier: str, id_type: str = "idno") -> T | None: ...

    @abstractmethod
    async def fetch_batch(self, identifiers: list[str], id_type: str = "idno") -> list[T]: ...

    @abstractmethod
    async def fetch_all(
        self,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[T]: ...
