-- Event analytics schema.
-- raw_events: immutable append-only event log. INSERT OR IGNORE by id makes
-- ingest idempotent (re-ingesting a file adds 0 rows).
CREATE TABLE IF NOT EXISTS raw_events (
    id          TEXT PRIMARY KEY,
    kind        TEXT NOT NULL,
    occurred_at TEXT NOT NULL,           -- ISO-8601 timestamp, e.g. 2026-01-01T09:30:00
    tenant      TEXT NOT NULL,
    payload     TEXT
);

-- daily_rollup: pre-aggregated per (day, kind, tenant) counts. Fully
-- recomputed per day by the rollup job (watermark approach), never appended.
CREATE TABLE IF NOT EXISTS daily_rollup (
    day    TEXT NOT NULL,                -- YYYY-MM-DD
    kind   TEXT NOT NULL,
    tenant TEXT NOT NULL,
    cnt    INTEGER NOT NULL,
    PRIMARY KEY (day, kind, tenant)
);

-- Speeds up day-range scans in rollup (occurred_at >= day_start AND < day_end).
CREATE INDEX IF NOT EXISTS idx_raw_events_occurred_at ON raw_events(occurred_at);
