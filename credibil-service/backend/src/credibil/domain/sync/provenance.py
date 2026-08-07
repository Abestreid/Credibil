from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any


class DataSource(StrEnum):
    CKAN_BULK = "ckan_bulk"
    IDNO_MD = "idno_md"
    DATE_GOV_MD = "date_gov_md"
    MANUAL = "manual"


class FieldProvenance:
    """Tracks where a field value came from and when it was last synced."""

    def __init__(
        self,
        field_name: str,
        value: Any,
        source: DataSource,
        source_timestamp: datetime | None = None,
        synced_at: datetime | None = None,
        confidence: float = 1.0,
    ) -> None:
        self.field_name = field_name
        self.value = value
        self.source = source
        self.source_timestamp = source_timestamp
        self.synced_at = synced_at or datetime.utcnow()
        self.confidence = confidence

    def to_dict(self) -> dict[str, Any]:
        value = self.value
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        elif hasattr(value, "value"):
            value = value.value
        return {
            "field_name": self.field_name,
            "value": value,
            "source": self.source,
            "source_timestamp": self.source_timestamp.isoformat()
            if self.source_timestamp
            else None,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FieldProvenance:
        source_ts = data.get("source_timestamp")
        synced_at = data.get("synced_at")
        return cls(
            field_name=data["field_name"],
            value=data["value"],
            source=DataSource(data["source"]),
            source_timestamp=datetime.fromisoformat(source_ts) if source_ts else None,
            synced_at=datetime.fromisoformat(synced_at) if synced_at else None,
            confidence=data.get("confidence", 1.0),
        )

    def __repr__(self) -> str:
        return (
            f"<FieldProvenance field={self.field_name} source={self.source} "
            f"confidence={self.confidence}>"
        )
