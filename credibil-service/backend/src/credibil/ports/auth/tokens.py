from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TokenService(ABC):
    """Port for JWT token operations."""

    @abstractmethod
    def create_access_token(
        self,
        subject: str,
        claims: dict[str, Any] | None = None,
    ) -> str: ...

    @abstractmethod
    def create_refresh_token(
        self,
        subject: str,
        claims: dict[str, Any] | None = None,
    ) -> str: ...

    @abstractmethod
    def decode_token(self, token: str) -> dict[str, Any]: ...

    @abstractmethod
    def decode_refresh_token(self, token: str) -> dict[str, Any]: ...
