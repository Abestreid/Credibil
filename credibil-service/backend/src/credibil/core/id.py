from __future__ import annotations

import uuid

from ulid import ULID


def new_id() -> uuid.UUID:
    """Generate a time-sortable UUID (ULID-based)."""
    return uuid.UUID(bytes=ULID().bytes)
