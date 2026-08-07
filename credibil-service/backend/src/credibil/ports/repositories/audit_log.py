from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from credibil.domain.audit.entities import AuditLogEntry


class AuditLogRepository(ABC):
    @abstractmethod
    async def create(self, entry: AuditLogEntry) -> AuditLogEntry: ...

    @abstractmethod
    async def find_by_request_id(self, request_id: str) -> AuditLogEntry | None: ...

    @abstractmethod
    async def list_recent(self, limit: int = 100) -> list[AuditLogEntry]: ...

    @abstractmethod
    async def list_by_user(self, user_id: str, limit: int = 100) -> list[AuditLogEntry]: ...

    @abstractmethod
    async def list_by_path(self, path: str, limit: int = 100) -> list[AuditLogEntry]: ...

    @abstractmethod
    async def list_by_date_range(self, start: datetime, end: datetime) -> list[AuditLogEntry]: ...

    @abstractmethod
    async def count_total(self) -> int: ...

    @abstractmethod
    async def purge_before(self, cutoff: datetime) -> int: ...
