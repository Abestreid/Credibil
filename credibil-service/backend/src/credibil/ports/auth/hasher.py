from __future__ import annotations

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Port for password hashing operations."""

    @abstractmethod
    def hash(self, password: str) -> str: ...

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool: ...
