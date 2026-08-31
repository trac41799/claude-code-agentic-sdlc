# Feature Spec — event-analytics

Idea: ingest raw events into a database and roll them up nightly, correct even
when the job re-runs, and fast enough for 1M rows. Local SQLite, no external
services.

## Schema
- `raw_events`: `id TEXT PK`, `kind TEXT`, `occurred_at TEXT (ISO)`, `tenant TEXT`, `payload TEXT`
- `daily_rollup`: `day TEXT`, `kind TEXT`, `tenant TEXT`, `cnt INTEGER`, `PRIMARY KEY (day, kind, tenant)`
- Applied idempotently by an init script from `schema.sql`.

## Behavior
- **Ingest** (`etl/ingest.py`): read JSONL, `INSERT OR IGNORE` (idempotent by `id`), return inserted count.
- **Rollup** (`etl/rollup.py`): aggregate `raw_events` by `(day, kind, tenant)` into
  `daily_rollup`. Re-runnable without double counting — per-day
  **full-day delete-and-recompute in one transaction** (watermark approach).
  Supports explicit day list for partial/backfill runs; full re-run recomputes every day.
- **Scale test** (`etl/perf_test.py`): 1,000,000 deterministic events (seed 42),
  assert ingest < 120s and rollup < 30s on this machine, assert double-run yields
  identical counts and sums.
- **Tests** (pytest): duplicate-id dedupe; two-day aggregation; double-run
  idempotency; partial-day then full-day re-run fixes counts.

## Acceptance
1. `pytest tests/ -q` passes.
2. `python etl/perf_test.py` passes perf + idempotency asserts.

## Delivered symbols
- `schema.sql` — DDL for `raw_events`, `daily_rollup`, index on `occurred_at`
- `etl/init_db.init_db(db_path)` — applies schema.sql (idempotent)
- `etl/ingest.ingest_events(db_path, jsonl_path) -> int` — inserted count
- `etl/rollup.rollup(db_path, days=None) -> int` — days recomputed
- `etl/perf_test.generate_events` / `rollup_snapshot` / `main`
- `tests/*` — pytest coverage per acceptance
