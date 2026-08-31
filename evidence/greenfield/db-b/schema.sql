-- Event analytics schema: raw event log + nightly rollup table.

CREATE TABLE IF NOT EXISTS raw_events (
    id          TEXT PRIMARY KEY,   -- event id; idempotency key for ingest
    kind        TEXT NOT NULL,      -- event kind, e.g. 'click', 'view'
    occurred_at TEXT NOT NULL,      -- ISO-8601 timestamp
    tenant      TEXT NOT NULL,      -- tenant / customer namespace
    payload     TEXT                -- optional JSON blob
);

CREATE TABLE IF NOT EXISTS daily_rollup (
    day    TEXT NOT NULL,           -- YYYY-MM-DD, the leading date of occurred_at
    kind   TEXT NOT NULL,
    tenant TEXT NOT NULL,
    cnt    INTEGER NOT NULL,
    PRIMARY KEY (day, kind, tenant)
);
