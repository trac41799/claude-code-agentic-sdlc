# Feature Spec: GREENFIELD-4 (DB+ETL) — Event Analytics with Nightly Rollup

**Slug:** `greenfield-4-db-etl`
**Status:** Approved (frozen brief)
**Source:** `docs/product/product.md` (PM spec capture)

## Summary

Build a local SQLite event-analytics pipeline: ingest raw JSONL events
idempotently, aggregate them nightly into per-(day, kind, tenant) counts, and
prove correctness + 1M-row performance with a pytest suite and a scale test.

## User-visible behaviours / acceptance criteria

- **AC-1** Running `pytest tests/ -q` from the repo root passes (all tests
  green).
- **AC-2** Running `python etl/perf_test.py` passes: generates 1,000,000
  deterministic synthetic events, ingests them, runs the rollup twice;
  asserts ingest < 120 s, rollup < 30 s, and that the second rollup run
  yields identical `daily_rollup` row counts and `SUM(cnt)`.
- **AC-3** Ingest dedupes duplicate event `id`s: a JSONL file containing
  duplicate ids inserts each unique id once, and re-ingesting the same file
  inserts nothing (returned inserted count reflects actual inserts).
- **AC-4** Rollup aggregates `raw_events` by `(day, kind, tenant)` across
  two days, producing correct per-group counts in `daily_rollup`.
- **AC-5** Double-running the rollup is idempotent: row count and `SUM(cnt)`
  are identical after the second run.
- **AC-6** Rollup of a partial day followed by a full-day re-run fixes the
  counts (delete-and-recompute of the day in one transaction).
- **AC-7** Process artifacts exist (product doc, impl-plan, tasks, TDD RED
  evidence, QA triage, wave report).
- **AC-8** Changes are left uncommitted in the working tree.

## Data contracts

### `schema.sql`
- `raw_events(id TEXT PK, kind TEXT NOT NULL, occurred_at TEXT NOT NULL,
  tenant TEXT NOT NULL, payload TEXT)`.
- `daily_rollup(day TEXT, kind TEXT, tenant TEXT, cnt INTEGER NOT NULL,
  PRIMARY KEY (day, kind, tenant))`.

### `etl/init_db.py`
- `init_db(db_path)` — connects to (creating) the SQLite DB and applies
  `schema.sql`; returns the open connection.

### `etl/ingest.py`
- `ingest(db_path, jsonl_path) -> int` — reads JSONL (one JSON object per
  line with keys `id`, `kind`, `occurred_at`, `tenant`, `payload`),
  `INSERT OR IGNORE` into `raw_events`, commits once, returns the number of
  rows actually inserted.

### `etl/rollup.py`
- `rollup(db_path, day=None) -> int` — for each day processed (`day` given,
  or every distinct day present in `raw_events`), deletes that day's
  `daily_rollup` rows and re-inserts `SELECT day, kind, tenant, COUNT(*) ...
  GROUP BY day, kind, tenant`, all in one transaction. Returns the number of
  rollup rows written. Re-runnable without double-counting.

### `etl/perf_test.py`
- Standalone script (`python etl/perf_test.py`): deterministic 1M-event
  workload, ingest + double rollup, timing and idempotency assertions.

## Out of scope
- No network/external services, no migrations framework, no API/UI.
