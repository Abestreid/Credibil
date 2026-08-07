-- Migration 007: Add enforcement_proceedings table (unej.md "Somații" board).
--
-- Stores enforcement summons matched to companies by fiscal code (IDNO), with
-- debtor/creditor roles and an active/archived lifecycle relative to the source.
-- Idempotent: safe to re-run. The ORM model in
-- infrastructure/database/models_enforcement.py is the source of truth.

CREATE TABLE IF NOT EXISTS enforcement_proceedings (
    id                    UUID PRIMARY KEY,
    somation_id           BIGINT NOT NULL,
    debtor_name           VARCHAR(500),
    debtor_idno           VARCHAR(13),
    debtor_idno_masked    VARCHAR(20),
    creditor_name         VARCHAR(500),
    creditor_idno         VARCHAR(13),
    executory_doc_number  VARCHAR(200),
    court_name            VARCHAR(300),
    case_number           VARCHAR(100),
    amount                FLOAT,
    currency              VARCHAR(10) NOT NULL DEFAULT 'MDL',
    publication_date      DATE,
    state                 VARCHAR(20) NOT NULL DEFAULT 'active',
    source_url            TEXT,
    raw_data              JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata              JSONB NOT NULL DEFAULT '{}'::jsonb,
    first_seen_at         TIMESTAMPTZ,
    last_seen_at          TIMESTAMPTZ,
    fetched_at            TIMESTAMPTZ,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_enforcement_somation_id
    ON enforcement_proceedings (somation_id);
CREATE INDEX IF NOT EXISTS ix_enforcement_debtor_idno
    ON enforcement_proceedings (debtor_idno);
CREATE INDEX IF NOT EXISTS ix_enforcement_creditor_idno
    ON enforcement_proceedings (creditor_idno);
CREATE INDEX IF NOT EXISTS ix_enforcement_state
    ON enforcement_proceedings (state);
CREATE INDEX IF NOT EXISTS ix_enforcement_publication_date
    ON enforcement_proceedings (publication_date);
