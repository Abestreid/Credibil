from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class ChangeCategory(StrEnum):
    """Category of a detected company change (drives notification grouping)."""

    STATUS = "status"
    TAX_DEBT = "tax_debt"
    MANAGEMENT = "management"  # founders / directors / beneficiaries
    ADDRESS = "address"
    COURT = "court"
    ENFORCEMENT = "enforcement"
    GENERAL = "general"


class MonitoredCompany:
    """A user's subscription to monitoring of one company (by IDNO)."""

    def __init__(
        self,
        *,
        monitored_id: UUID | None = None,
        user_id: UUID,
        idno: str,
        company_id: UUID | None = None,
        company_name: str | None = None,
        is_active: bool = True,
        created_at: datetime | None = None,
        last_checked_at: datetime | None = None,
        last_change_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = monitored_id or new_id()
        self.user_id = user_id
        self.idno = idno
        self.company_id = company_id
        self.company_name = company_name
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.last_checked_at = last_checked_at
        self.last_change_at = last_change_at
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self) -> str:
        return f"<MonitoredCompany user={self.user_id} idno={self.idno} active={self.is_active}>"


class CompanyChangeEvent:
    """One detected field-level change for a company (append-only journal).

    Entity-scoped (keyed by IDNO, not user): one change fans out to N
    per-user notifications.
    """

    def __init__(
        self,
        *,
        event_id: UUID | None = None,
        idno: str,
        category: ChangeCategory = ChangeCategory.GENERAL,
        field: str,
        description: str,
        old_value: str | None = None,
        new_value: str | None = None,
        batch_id: str | None = None,
        detected_at: datetime | None = None,
    ) -> None:
        self.id = event_id or new_id()
        self.idno = idno
        self.category = category
        self.field = field
        self.description = description
        self.old_value = old_value
        self.new_value = new_value
        self.batch_id = batch_id
        self.detected_at = detected_at or datetime.utcnow()

    def __repr__(self) -> str:
        return f"<CompanyChangeEvent idno={self.idno} field={self.field!r}>"


class MonitoringNotification:
    """Per-user delivery record for a batch of changes on a monitored company."""

    def __init__(
        self,
        *,
        notification_id: UUID | None = None,
        user_id: UUID,
        idno: str,
        company_name: str | None = None,
        change_count: int = 0,
        change_event_ids: list[str] | None = None,
        summary: str | None = None,
        categories: list[str] | None = None,
        is_read: bool = False,
        email_sent: bool = False,
        created_at: datetime | None = None,
        read_at: datetime | None = None,
    ) -> None:
        self.id = notification_id or new_id()
        self.user_id = user_id
        self.idno = idno
        self.company_name = company_name
        self.change_count = change_count
        self.change_event_ids = change_event_ids or []
        self.summary = summary
        self.categories = categories or []
        self.is_read = is_read
        self.email_sent = email_sent
        self.created_at = created_at or datetime.utcnow()
        self.read_at = read_at

    def mark_read(self) -> None:
        self.is_read = True
        self.read_at = datetime.utcnow()

    def to_metadata(self) -> dict[str, Any]:
        return {"change_event_ids": self.change_event_ids, "categories": self.categories}

    def __repr__(self) -> str:
        return f"<MonitoringNotification user={self.user_id} idno={self.idno} read={self.is_read}>"
