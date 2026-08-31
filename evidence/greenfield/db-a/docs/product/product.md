# Product — Event Analytics with Nightly Rollup

## Problem
Teams need daily event analytics (counts of events by `kind` and `tenant`) without
paying per-query scan costs on a large, growing raw-event log. Raw events are
ingested continuously; the analytics answer is served from a pre-aggregated
`daily_rollup` table rebuilt nightly.

## Scope
Local, dependency-free analytics pipeline on SQLite (no external services):
idempotent raw-event ingest, a nightly rollup that is safe to re-run, and a
1M-row scale test proving it on this machine.

## Non-goals
- No web UI / API / service layer (out of scope for the DB+ETL brief).
- No incremental/streaming rollup; nightly full-day recompute is the contract.
- No event enrichment or schema evolution.

## Users
- **Data analyst** — queries `daily_rollup` for per-day, per-kind, per-tenant counts.
- **Platform operator** — runs the nightly job; must be safe to re-run after a
  crash or a partial-day backfill.

## Success criteria
1. `pytest tests/ -q` passes.
2. `python etl/perf_test.py` passes 1M-row ingest (<120s) + rollup (<30s) + idempotency.

## Deliverables
| Deliverable | Path |
|---|---|
| Database schema (raw_events, daily_rollup) | `schema.sql` |
| Schema init script | `etl/init_db.py` |
| Idempotent JSONL ingest | `etl/ingest.py` |
| Watermark-based nightly rollup | `etl/rollup.py` |
| 1M-row scale + idempotency test | `etl/perf_test.py` |
| Pytest suite | `tests/test_*.py` |
