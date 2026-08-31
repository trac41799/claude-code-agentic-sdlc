# Epics — Event Analytics with Nightly Rollup

| Epic | Outcome | Key files |
|---|---|---|
| **E1 — Schema & init** | SQLite DB created from `schema.sql` with `raw_events` (idempotent by `id`) and `daily_rollup` keyed by `(day, kind, tenant)`; init idempotent | `schema.sql`, `etl/init_db.py` |
| **E2 — Idempotent ingest** | `etl/ingest.py` reads JSONL and inserts via `INSERT OR IGNORE`; re-ingest adds 0 rows; returns inserted count | `etl/ingest.py` |
| **E3 — Watermark rollup** | `etl/rollup.py` aggregates `raw_events` → `daily_rollup`; per-day full delete-and-recompute in one transaction; re-runnable with identical totals; supports partial-day backfill | `etl/rollup.py` |
| **E4 — 1M-row scale proof** | `etl/perf_test.py` generates 1,000,000 deterministic events, ingests (<120s), rolls up (<30s), double-run identical counts and sums | `etl/perf_test.py` |
| **E5 — Test suite** | pytest covers dedupe, two-day aggregation, double-run idempotency, partial-day→full-day convergence | `tests/test_ingest.py`, `tests/test_rollup.py`, `tests/test_idempotency.py`, `tests/test_partial_then_full.py` |

## Acceptance
`pytest tests/ -q` green; `python etl/perf_test.py` green.
