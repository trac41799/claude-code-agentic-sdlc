# db-a bench repo

GREENFIELD-4 (DB+ETL): **Event analytics with nightly rollup at scale** —
ingest raw events into SQLite and roll them up nightly, correct when the job
re-runs, and fast enough for 1M rows.

## Layout
- `schema.sql` — DDL: `raw_events` (idempotent by `id`) + `daily_rollup` keyed by `(day, kind, tenant)`.
- `etl/init_db.py` — applies `schema.sql` (idempotent).
- `etl/ingest.py` — JSONL ingest via `INSERT OR IGNORE`; returns inserted count.
- `etl/rollup.py` — watermark rollup: per-day full delete-and-recompute in one transaction.
- `etl/perf_test.py` — 1M-event scale + idempotency test.
- `tests/` — pytest suite (dedupe, two-day aggregation, double-run idempotency, partial→full convergence).

## Run
```bash
python etl/init_db.py                 # create data/events.db from schema.sql
python etl/ingest.py events.jsonl     # ingest (idempotent by id)
python etl/rollup.py                  # nightly rollup (re-runnable)
python etl/rollup.py --day 2026-01-01 # backfill a single day

pytest tests/ -q                      # acceptance: 6 passed
python etl/perf_test.py               # acceptance: 1M ingest <120s, rollup <30s, idempotent
```
