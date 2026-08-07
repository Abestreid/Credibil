from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.domain.monitoring.entities import (
        CompanyChangeEvent,
        MonitoredCompany,
        MonitoringNotification,
    )


class MonitoringRepository(ABC):
    """Repository for company monitoring: subscriptions, snapshots, events, notifications."""

    # --- subscriptions ---
    @abstractmethod
    async def add_monitored(self, monitored: MonitoredCompany) -> MonitoredCompany: ...

    @abstractmethod
    async def remove_monitored(self, user_id: UUID, idno: str) -> bool: ...

    @abstractmethod
    async def find_monitored(self, user_id: UUID, idno: str) -> MonitoredCompany | None: ...

    @abstractmethod
    async def list_monitored(self, user_id: UUID) -> list[MonitoredCompany]: ...

    @abstractmethod
    async def distinct_monitored_idnos(self) -> list[str]:
        """Every IDNO watched by at least one active subscription."""

    @abstractmethod
    async def watchers_of(self, idno: str) -> list[MonitoredCompany]:
        """Active subscriptions for a given IDNO (for notification fan-out)."""

    @abstractmethod
    async def touch_checked(self, idno: str, changed: bool) -> None:
        """Update last_checked_at (and last_change_at when changed) for all watchers."""

    # --- snapshots (2-slot rolling buffer, keyed by idno) ---
    @abstractmethod
    async def get_snapshot(self, idno: str) -> dict[str, Any] | None:
        """Return {'hash', 'snapshot', 'snapshot_at'} or None."""

    @abstractmethod
    async def save_snapshot(self, idno: str, snapshot_hash: str, snapshot: dict[str, Any]) -> None:
        """Upsert current snapshot, rotating the old current into prev."""

    # --- change events ---
    @abstractmethod
    async def add_change_events(self, events: list[CompanyChangeEvent]) -> None: ...

    @abstractmethod
    async def list_change_events(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[CompanyChangeEvent]: ...

    # --- notifications ---
    @abstractmethod
    async def add_notifications(self, notifications: list[MonitoringNotification]) -> None: ...

    @abstractmethod
    async def list_notifications(
        self, user_id: UUID, unread_only: bool = False, limit: int = 50, offset: int = 0
    ) -> list[MonitoringNotification]: ...

    @abstractmethod
    async def count_unread(self, user_id: UUID) -> int: ...

    @abstractmethod
    async def mark_notification_read(self, user_id: UUID, notification_id: UUID) -> bool: ...

    @abstractmethod
    async def mark_all_read(self, user_id: UUID) -> int: ...
