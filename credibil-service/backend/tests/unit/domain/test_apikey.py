from __future__ import annotations

from datetime import datetime, timedelta

from credibil.core.id import new_id
from credibil.domain.apikey.entities import APIKey, APIKeyStatus


def test_generate_key_hash_roundtrip() -> None:
    raw, prefix, key_hash = APIKey.generate_key()
    assert raw.startswith("cb_")
    assert prefix == raw[:11]
    # The stored hash must be reproducible from the raw key (auth relies on this).
    assert APIKey.hash_key(raw) == key_hash
    # Different keys hash differently.
    other_raw, _, other_hash = APIKey.generate_key()
    assert other_hash != key_hash
    assert other_raw != raw


def test_is_valid_status_and_expiry() -> None:
    tenant = new_id()
    active = APIKey(tenant_id=tenant, name="k", status=APIKeyStatus.ACTIVE)
    assert active.is_valid is True

    revoked = APIKey(tenant_id=tenant, name="k", status=APIKeyStatus.ACTIVE)
    revoked.revoke()
    assert revoked.status is APIKeyStatus.REVOKED
    assert revoked.is_valid is False

    expired = APIKey(
        tenant_id=tenant,
        name="k",
        status=APIKeyStatus.ACTIVE,
        expires_at=datetime.utcnow() - timedelta(days=1),
    )
    assert expired.is_valid is False

    future = APIKey(
        tenant_id=tenant,
        name="k",
        status=APIKeyStatus.ACTIVE,
        expires_at=datetime.utcnow() + timedelta(days=1),
    )
    assert future.is_valid is True
