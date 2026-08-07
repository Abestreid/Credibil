from __future__ import annotations

import hashlib
import io
from pathlib import Path
from typing import BinaryIO

from credibil.domain.sync.errors import FileStorageError
from credibil.ports.providers.storage import StorageProvider, StoredFile


class LocalStorageProvider(StorageProvider):
    """File storage on local disk — default for development and CKAN sync."""

    def __init__(self, base_path: str = "data/raw") -> None:
        self._base = Path(base_path)
        self._base.mkdir(parents=True, exist_ok=True)

    async def store(
        self,
        file_obj: BinaryIO,
        filename: str,
        directory: str = "",
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> StoredFile:
        target_dir = self._base / directory if directory else self._base
        target_dir.mkdir(parents=True, exist_ok=True)
        filepath = target_dir / filename

        try:
            data = file_obj.read()
            filepath.write_bytes(data)
            checksum = hashlib.sha256(data).hexdigest()
            size = len(data)
        except OSError as e:
            raise FileStorageError(details={"error": str(e)}) from e

        return StoredFile(
            filename=filename,
            path=str(filepath.relative_to(self._base)),
            size_bytes=size,
            checksum_sha256=checksum,
            content_type=content_type,
            metadata=metadata or {},
        )

    async def retrieve(self, path: str) -> BinaryIO:
        filepath = self._base / path
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {path}")
        data = filepath.read_bytes()
        return io.BytesIO(data)

    async def exists(self, path: str) -> bool:
        return (self._base / path).exists()

    async def delete(self, path: str) -> bool:
        filepath = self._base / path
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    async def list_files(self, directory: str = "", pattern: str = "*") -> list[StoredFile]:
        search_dir = self._base / directory if directory else self._base
        if not search_dir.exists():
            return []

        files = []
        for filepath in sorted(search_dir.glob(pattern)):
            if filepath.is_file():
                data = filepath.read_bytes()
                files.append(
                    StoredFile(
                        filename=filepath.name,
                        path=str(filepath.relative_to(self._base)),
                        size_bytes=filepath.stat().st_size,
                        checksum_sha256=hashlib.sha256(data).hexdigest(),
                    )
                )
        return files

    async def get_checksum(self, path: str) -> str | None:
        filepath = self._base / path
        if not filepath.exists():
            return None
        data = filepath.read_bytes()
        return hashlib.sha256(data).hexdigest()
