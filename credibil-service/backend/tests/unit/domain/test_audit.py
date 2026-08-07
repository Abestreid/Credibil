from __future__ import annotations

import uuid

from credibil.domain.audit.entities import AuditLogEntry


class TestAuditLogEntry:
    def test_create_entry(self):
        entry = AuditLogEntry(
            request_id="req-123",
            method="GET",
            path="/api/companies",
            status_code=200,
            client_ip="127.0.0.1",
            duration_ms=42.5,
        )
        assert entry.request_id == "req-123"
        assert entry.method == "GET"
        assert entry.status_code == 200
        assert entry.duration_ms == 42.5
        assert isinstance(entry.id, uuid.UUID)
        assert entry.created_at.tzinfo is not None

    def test_to_dict(self):
        entry = AuditLogEntry(
            request_id="req-456",
            method="POST",
            path="/api/auth/login",
            status_code=401,
            client_ip="10.0.0.1",
            user_agent="Mozilla/5.0",
            duration_ms=12.3,
        )
        d = entry.to_dict()
        assert d["request_id"] == "req-456"
        assert d["method"] == "POST"
        assert d["status_code"] == 401
        assert d["user_agent"] == "Mozilla/5.0"
        assert isinstance(d["created_at"], str)

    def test_optional_fields(self):
        entry = AuditLogEntry()
        assert entry.request_id == ""
        assert entry.user_id is None
        assert entry.error_message is None
        assert entry.request_body is None
