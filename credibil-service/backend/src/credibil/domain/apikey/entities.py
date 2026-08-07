from __future__ import annotations

import hashlib
import secrets
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class APIKeyStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class APIKey:
    """API key entity for programmatic access."""

    def __init__(
        self,
        *,
        key_id: UUID | None = None,
        tenant_id: UUID,
        name: str,
        key_prefix: str = "",
        key_hash: str = "",
        scopes: list[str] | None = None,
        rate_limit: int = 1000,
        status: APIKeyStatus = APIKeyStatus.ACTIVE,
        expires_at: datetime | None = None,
        last_used_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = key_id or new_id()
        self.tenant_id = tenant_id
        self.name = name
        self.key_prefix = key_prefix
        self.key_hash = key_hash
        self.scopes = scopes or []
        self.rate_limit = rate_limit
        self.status = status
        self.expires_at = expires_at
        self.last_used_at = last_used_at
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @staticmethod
    def hash_key(raw_key: str) -> str:
        """Deterministic hash used both at issuance and on every lookup."""
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_key() -> tuple[str, str, str]:
        """Generate a new API key. Returns (raw_key, prefix, hash).

        Only the hash is persisted; the raw key is shown to the client once.
        The prefix (e.g. ``cb_ab12cd``) is stored for display/identification.
        """
        raw_key = f"cb_{secrets.token_urlsafe(32)}"
        prefix = raw_key[:11]
        key_hash = APIKey.hash_key(raw_key)
        return raw_key, prefix, key_hash

    def revoke(self) -> None:
        self.status = APIKeyStatus.REVOKED
        self.updated_at = datetime.utcnow()

    def record_usage(self) -> None:
        self.last_used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @property
    def is_valid(self) -> bool:
        return self.status == APIKeyStatus.ACTIVE and (
            not self.expires_at or self.expires_at >= datetime.utcnow()
        )

    def __repr__(self) -> str:
        return f"<APIKey id={self.id} name={self.name!r} prefix={self.key_prefix!r}>"
