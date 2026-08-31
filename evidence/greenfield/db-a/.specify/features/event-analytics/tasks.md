# Tasks — event-analytics

| # | Task | Deliverable | Status |
|---|---|---|---|
| 1 | Define `raw_events` + `daily_rollup` DDL + index | `schema.sql` | ✅ |
| 2 | Write idempotent init script | `etl/init_db.py` | ✅ |
| 3 | Implement JSONL ingest w/ INSERT OR IGNORE | `etl/ingest.py` | ✅ |
| 4 | Implement watermark rollup (delete-and-recompute per day, one txn) | `etl/rollup.py` | ✅ |
| 5 | Write 1M-row perf + idempotency test | `etl/perf_test.py` | ✅ |
| 6 | Test: ingest dedupes duplicate ids | `tests/test_ingest.py` | ✅ |
| 7 | Test: rollup aggregates across two days | `tests/test_rollup.py` | ✅ |
| 8 | Test: double-run idempotency | `tests/test_idempotency.py` | ✅ |
| 9 | Test: partial-day then full-day re-run fixes counts | `tests/test_partial_then_full.py` | ✅ |
| 10 | Run acceptance | `pytest tests/ -q` + `python etl/perf_test.py` | ✅ |
