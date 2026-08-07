from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class DomainEvent:
    """Base class for all domain events."""

    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = ""

    def __post_init__(self) -> None:
        if not self.event_type:
            self.event_type = type(self).__name__


@dataclass
class CompanyCreated(DomainEvent):
    company_id: UUID = field(default_factory=UUID)
    idno: str = ""
    tenant_id: UUID | None = None


@dataclass
class CompanyUpdated(DomainEvent):
    company_id: UUID = field(default_factory=UUID)
    changes: dict[str, Any] = field(default_factory=dict)
    tenant_id: UUID | None = None


@dataclass
class CompanyDeleted(DomainEvent):
    company_id: UUID = field(default_factory=UUID)
    tenant_id: UUID | None = None
