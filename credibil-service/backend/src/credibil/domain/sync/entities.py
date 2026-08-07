from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class SyncStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SyncType(StrEnum):
    FULL = "full"
    INCREMENTAL = "incremental"
    ON_DEMAND = "on_demand"


class SyncHistory:
    """Tracks every sync operation — one record per run."""

    def __init__(
        self,
        *,
        sync_id: UUID | None = None,
        provider_id: str,
        sync_type: SyncType,
        country_code: str,
        status: SyncStatus = SyncStatus.PENDING,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        records_total: int = 0,
        records_created: int = 0,
        records_updated: int = 0,
        records_unchanged: int = 0,
        records_failed: int = 0,
        error_message: str | None = None,
        file_checksum: str | None = None,
        file_path: str | None = None,
        duration_seconds: float | None = None,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = sync_id or new_id()
        self.provider_id = provider_id
        self.sync_type = sync_type
        self.country_code = country_code
        self.status = status
        self.started_at = started_at
        self.finished_at = finished_at
        self.records_total = records_total
        self.records_created = records_created
        self.records_updated = records_updated
        self.records_unchanged = records_unchanged
        self.records_failed = records_failed
        self.error_message = error_message
        self.file_checksum = file_checksum
        self.file_path = file_path
        self.duration_seconds = duration_seconds
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def start(self) -> None:
        self.status = SyncStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def complete(
        self,
        records_total: int,
        records_created: int,
        records_updated: int,
        records_unchanged: int,
        records_failed: int,
    ) -> None:
        self.status = SyncStatus.COMPLETED
        self.finished_at = datetime.utcnow()
        self.records_total = records_total
        self.records_created = records_created
        self.records_updated = records_updated
        self.records_unchanged = records_unchanged
        self.records_failed = records_failed
        if self.started_at:
            self.duration_seconds = (self.finished_at - self.started_at).total_seconds()
        self.updated_at = datetime.utcnow()

    def fail(self, error_message: str) -> None:
        self.status = SyncStatus.FAILED
        self.finished_at = datetime.utcnow()
        self.error_message = error_message
        if self.started_at:
            self.duration_seconds = (self.finished_at - self.started_at).total_seconds()
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<SyncHistory id={self.id} provider={self.provider_id} "
            f"type={self.sync_type} status={self.status}>"
        )
