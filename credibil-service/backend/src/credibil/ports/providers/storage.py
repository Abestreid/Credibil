from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import BinaryIO


@dataclass
class StoredFile:
    """Metadata about a stored file."""

    filename: str
    path: str
    size_bytes: int
    checksum_sha256: str
    content_type: str = "application/octet-stream"
    stored_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, str] = field(default_factory=dict)


class StorageProvider(ABC):
    """Abstract interface for file storage (local, S3, GCS, etc.)."""

    @abstractmethod
    async def store(
        self,
        file_obj: BinaryIO,
        filename: str,
        directory: str = "",
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> StoredFile:
        """Store a file and return metadata about it."""
        ...

    @abstractmethod
    async def retrieve(self, path: str) -> BinaryIO:
        """Retrieve a file by path. Raises FileNotFoundError if missing."""
        ...

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if a file exists at the given path."""
        ...

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Delete a file. Returns True if deleted, False if not found."""
        ...

    @abstractmethod
    async def list_files(self, directory: str = "", pattern: str = "*") -> list[StoredFile]:
        """List files in a directory matching a pattern."""
        ...

    @abstractmethod
    async def get_checksum(self, path: str) -> str | None:
        """Get the SHA-256 checksum of a stored file. Returns None if not found."""
        ...
