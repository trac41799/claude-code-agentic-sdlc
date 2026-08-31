-- GREENFIELD-4 (DB+ETL) schema
-- Applied by etl/init_db.py; idempotent (CREATE TABLE IF NOT EXISTS).

CREATE TABLE IF NOT EXISTS raw_events (
    id          TEXT PRIMARY KEY,
    kind        TEXT NOT NULL,
    occurred_at TEXT NOT NULL,          -- ISO-8601 timestamp (YYYY-MM-DDTHH:MM:SSZ)
    tenant      TEXT NOT NULL,
    payload     TEXT
);

CREATE TABLE IF NOT EXISTS daily_rollup (
    day    TEXT NOT NULL,               -- YYYY-MM-DD (prefix of occurred_at)
    kind   TEXT NOT NULL,
    tenant TEXT NOT NULL,
    cnt    INTEGER NOT NULL,
    PRIMARY KEY (day, kind, tenant)
);
