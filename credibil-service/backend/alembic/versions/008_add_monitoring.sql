-- Migration 008: Company monitoring (subscriptions, snapshots, change journal, notifications).
--
-- Users subscribe companies to monitoring; a daily job snapshots each monitored
-- company's canonical state, diffs against the previous snapshot, and fans out
-- in-app notifications on any change. Snapshots exist only for monitored IDNOs.
-- Idempotent. ORM source of truth: infrastructure/database/models_monitoring.py.

CREATE TABLE IF NOT EXISTS monitored_companies (
    id              UUID PRIMARY KEY,
    user_id         UUID NOT NULL,
    idno            VARCHAR(13) NOT NULL,
    company_id      UUID,
    company_name    VARCHAR(500),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_checked_at TIMESTAMPTZ,
    last_change_at  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_monitored_user_idno UNIQUE (user_id, idno)
);
CREATE INDEX IF NOT EXISTS ix_monitored_user ON monitored_companies (user_id);
CREATE INDEX IF NOT EXISTS ix_monitored_idno ON monitored_companies (idno);
CREATE INDEX IF NOT EXISTS ix_monitored_active ON monitored_companies (is_active);

CREATE TABLE IF NOT EXISTS company_snapshots (
    idno               VARCHAR(13) PRIMARY KEY,
    snapshot_hash      VARCHAR(64) NOT NULL,
    snapshot_json      JSONB NOT NULL DEFAULT '{}'::jsonb,
    snapshot_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    prev_snapshot_json JSONB,
    prev_snapshot_at   TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS company_change_events (
    id          UUID PRIMARY KEY,
    idno        VARCHAR(13) NOT NULL,
    category    VARCHAR(30) NOT NULL DEFAULT 'general',
    field       VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    old_value   TEXT,
    new_value   TEXT,
    batch_id    VARCHAR(40),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_change_event_idno ON company_change_events (idno);
CREATE INDEX IF NOT EXISTS ix_change_event_detected ON company_change_events (detected_at);
CREATE INDEX IF NOT EXISTS ix_change_event_batch ON company_change_events (batch_id);

CREATE TABLE IF NOT EXISTS monitoring_notifications (
    id           UUID PRIMARY KEY,
    user_id      UUID NOT NULL,
    idno         VARCHAR(13) NOT NULL,
    company_name VARCHAR(500),
    change_count INTEGER NOT NULL DEFAULT 0,
    summary      TEXT,
    metadata     JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_read      BOOLEAN NOT NULL DEFAULT FALSE,
    email_sent   BOOLEAN NOT NULL DEFAULT FALSE,
    read_at      TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_notification_user ON monitoring_notifications (user_id);
CREATE INDEX IF NOT EXISTS ix_notification_user_unread ON monitoring_notifications (user_id, is_read);
