# Epic Status

Updated: 2026-08-29

| Epic | Status | Notes |
|---|---|---|
| E1 — Schema & init | ✅ Done | `schema.sql` + `etl/init_db.py` applied; idempotent |
| E2 — Idempotent ingest | ✅ Done | `INSERT OR IGNORE`, returns inserted count |
| E3 — Watermark rollup | ✅ Done | Per-day delete-and-recompute, single transaction |
| E4 — 1M-row scale proof | ✅ Done | `etl/perf_test.py` passes on this machine |
| E5 — Test suite | ✅ Done | 6 tests green via `pytest tests/ -q` |
