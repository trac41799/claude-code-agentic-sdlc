# Task Checklist — GREENFIELD-4 (DB+ETL)

**Feature:** `greenfield-4-db-etl`
**Spec:** `.specify/features/greenfield-4-db-etl/spec.md`
**Plan:** `.specify/features/greenfield-4-db-etl/impl-plan.md`

> `[P]` = may run in parallel. Dependencies govern ordering.

## Phase 1: Foundation

### Task 1.1: Scaffold schema, init script, and pytest import path
**Description**: Create `schema.sql` (raw_events + daily_rollup), `etl/init_db.py`
(`init_db(db_path)` applies schema and returns a connection), `etl/__init__.py`,
and a root `conftest.py` so `import etl.*` works under pytest.
**Acceptance Criteria**:
- [ ] `schema.sql` defines `raw_events(id TEXT PK, kind TEXT, occurred_at TEXT, tenant TEXT, payload TEXT)` and `daily_rollup(day TEXT, kind TEXT, tenant TEXT, cnt INTEGER, PRIMARY KEY(day,kind,tenant))` — spec AC-4 (enabler)
- [ ] `init_db()` applies the schema idempotently (CREATE TABLE IF NOT EXISTS)
- [ ] `pytest tests/ -q` can import `etl` modules from repo root
**Effort**: S
**Dependencies**: None

## Phase 2: ETL modules (independent → parallel wave)

### Task 2.1: [P] Implement idempotent JSONL ingest
**Description**: `etl/ingest.py` with `ingest(db_path, jsonl_path) -> int`: reads
JSONL events, `INSERT OR IGNORE` by id, one transaction, returns rows actually
inserted (tracked via `total_changes` delta).
**Acceptance Criteria**:
- [ ] Duplicate ids within a file are inserted once — spec AC-3
- [ ] Re-ingesting the same file returns 0 inserted — spec AC-3
- [ ] Returns correct inserted count on a fresh file
**Effort**: S
**Dependencies**: Task 1.1

### Task 2.2: [P] Implement re-runnable daily rollup
**Description**: `etl/rollup.py` with `rollup(db_path, day=None) -> int`: per day,
`DELETE` that day's `daily_rollup` rows then recompute from `raw_events` grouped
by `(day, kind, tenant)`, all in one transaction. Watermark approach documented
in the module docstring.
**Acceptance Criteria**:
- [ ] Aggregates correctly across two days — spec AC-4
- [ ] Double-run is idempotent (same row count + SUM(cnt)) — spec AC-5
- [ ] Partial-day rollup then full-day re-run fixes counts — spec AC-6
**Effort**: S
**Dependencies**: Task 1.1

### Task 2.3: [P] Write 1M-row scale/perf test
**Description**: `etl/perf_test.py` standalone script: deterministic 1M-event
generation (seeded RNG), ingest, double rollup; asserts ingest < 120 s,
rollup < 30 s, identical row counts and `SUM(cnt)` across the two rollup runs.
**Acceptance Criteria**:
- [ ] `python etl/perf_test.py` exits 0 — spec AC-2
- [ ] Timing + idempotency assertions present
**Effort**: M
**Dependencies**: Task 1.1

## Phase 3: Gates

### Task 3.1: Full-suite + perf gate
**Description**: Run `pytest tests/ -q` (AC-1) and `python etl/perf_test.py`
(AC-2) end-to-end; fix any failures; capture evidence.
**Acceptance Criteria**:
- [ ] `pytest tests/ -q` green — spec AC-1
- [ ] `python etl/perf_test.py` passes — spec AC-2
**Effort**: S
**Dependencies**: Tasks 2.1, 2.2, 2.3
