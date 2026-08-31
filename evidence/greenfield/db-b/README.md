# db-b bench repo

Event analytics with nightly rollup (SQLite only, no external services).

```
python -m etl.init_db                # apply schema.sql -> data/events.db
python -m etl.ingest events.jsonl    # idempotent ingest (INSERT OR IGNORE by id)
python -m etl.rollup                 # recompute all days (idempotent)
python -m etl.rollup --day 2026-08-01
python etl/perf_test.py              # 1M-event scale test + idempotency asserts
pytest tests/ -q                     # unit tests
```
