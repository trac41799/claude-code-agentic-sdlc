GREENFIELD-4 (DB+ETL) TASK BRIEF (frozen, identical for both arms)

Idea: "Event analytics with nightly rollup at scale" — ingest raw events into a database and roll them up nightly, correct even when the job re-runs, and fast enough for 1M rows.

Build it locally (SQLite, no external services):
- Schema (`schema.sql`, applied by an init script): `raw_events` (id TEXT PK, kind TEXT, occurred_at TEXT (ISO), tenant TEXT, payload TEXT) + `daily_rollup` (day TEXT, kind TEXT, tenant TEXT, cnt INTEGER, PRIMARY KEY (day, kind, tenant)).
- Ingest (`etl/ingest.py`): reads a JSONL file of events, inserts with INSERT OR IGNORE (idempotent by id) and returns inserted count.
- Rollup (`etl/rollup.py`): aggregates raw_events by (day, kind, tenant) into daily_rollup. MUST be re-runnable: re-running the rollup for the same day must produce identical totals (no double-count) — implement via full-day delete-and-recompute of the day's rollup rows in one transaction (watermark approach), and note it.
- Scale test (`etl/perf_test.py`): generates 1,000,000 synthetic events (deterministic seed), ingests them, runs rollup; asserts ingest < 120s and rollup < 30s on this machine; asserts double-run of rollup yields identical row counts and sums (idempotency).
- Tests (pytest): ingest dedupes duplicate ids; rollup aggregates correctly across two days; double-run idempotency; rollup of a partial day then full day re-run fixes counts.

Acceptance: `pytest tests/ -q` passes; `python etl/perf_test.py` passes the 1M-row perf + idempotency asserts.

Do not commit. Leave changes in the working tree.