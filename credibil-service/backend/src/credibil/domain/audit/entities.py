from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class AuditLogEntry:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    request_id: str = ""
    method: str = ""
    path: str = ""
    status_code: int = 0
    client_ip: str = ""
    user_id: str | None = None
    api_key_prefix: str | None = None
    user_agent: str = ""
    request_body: str | None = None
    duration_ms: float = 0.0
    error_message: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "request_id": self.request_id,
            "method": self.method,
            "path": self.path,
            "status_code": self.status_code,
            "client_ip": self.client_ip,
            "user_id": self.user_id,
            "api_key_prefix": self.api_key_prefix,
            "user_agent": self.user_agent,
            "request_body": self.request_body,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
        }
