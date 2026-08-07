-- Migration 009: API keys for the public client-facing API.
--
-- The APIKeyModel already existed in models_organization.py but had no explicit
-- migration. This creates the table (idempotent) so the public API's X-API-Key
-- authentication works on a freshly-migrated database.
-- ORM source of truth: infrastructure/database/models_organization.py::APIKeyModel.

CREATE TABLE IF NOT EXISTS api_keys (
    id           UUID PRIMARY KEY,
    tenant_id    UUID NOT NULL,
    name         VARCHAR(255) NOT NULL,
    key_prefix   VARCHAR(20) NOT NULL,
    key_hash     VARCHAR(255) NOT NULL UNIQUE,
    scopes       JSONB NOT NULL DEFAULT '[]'::jsonb,
    rate_limit   INTEGER NOT NULL DEFAULT 1000,
    status       VARCHAR(50) NOT NULL DEFAULT 'active',
    expires_at   TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    metadata     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_api_keys_tenant_id ON api_keys (tenant_id);
CREATE INDEX IF NOT EXISTS ix_api_keys_key_prefix ON api_keys (key_prefix);
CREATE INDEX IF NOT EXISTS ix_api_keys_status ON api_keys (status);
