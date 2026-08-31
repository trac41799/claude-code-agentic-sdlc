# Implementation Plan — GREENFIELD-4 (DB+ETL)

**Feature:** `greenfield-4-db-etl`
**Spec:** `.specify/features/greenfield-4-db-etl/spec.md`
**Effort:** S (small — ~9 files, no external deps)

## Phase 0 — Outline & research

What's in scope:

- SQLite schema + init script (`schema.sql`, `etl/init_db.py`).
- Idempotent JSONL ingest (`etl/ingest.py`).
- Re-runnable daily rollup (`etl/rollup.py`).
- Scale/perf test (`etl/perf_test.py`).
- Correctness suite (`tests/test_ingest.py`, `tests/test_rollup.py`).

Deferred: any API/UI, migrations framework, partitioning, external storage.

Prototype needed? **No.** The only hard unknown is 1M-row performance, and the
budgets (120 s / 30 s) are an order of magnitude above expected SQLite
numbers. We validate empirically in the perf test rather than pre-optimizing.

### Risks & assumptions

| Risk | Mitigation |
|---|---|
| R1: Ingest too slow for 1M rows | Single transaction, chunked `executemany` (10k/batch); no per-row commit. Expected ~5–15 s. |
| R2: Rollup double-counts on re-run | Full-day `DELETE` + recompute inside **one transaction** (watermark). Verified by AC-5/AC-6 tests. |
| R3: `cursor.rowcount` unreliable for `INSERT OR IGNORE` | Compute inserted count as `conn.total_changes` delta across the run — robust across sqlite3 versions (incl. Python 3.14). |
| R4: Import path breaks in tests vs `python etl/perf_test.py` | Root `conftest.py` puts repo root on `sys.path` for pytest; `perf_test.py` inserts parent dir itself before imports. |
| R5: Rollup query scans full table | 1M-row `GROUP BY substr(occurred_at,1,10)` scans in well under 30 s; no index needed to meet budget. |

## Phase 1 — Design & contracts

### System architecture

```
JSONL ──▶ etl/ingest.py ──INSERT OR IGNORE──▶ raw_events
                                                 │
        etl/rollup.py ── DELETE+recompute ───────┤   (one transaction/day)
                                                 ▼
                                            daily_rollup
```

### Component contracts

| Component | Contract |
|---|---|
| `schema.sql` | DDL for `raw_events`, `daily_rollup` (see spec). |
| `etl/init_db.py` | `init_db(db_path) -> sqlite3.Connection`; applies schema, returns open conn. |
| `etl/ingest.py` | `ingest(db_path, jsonl_path) -> int`; returns rows actually inserted. |
| `etl/rollup.py` | `rollup(db_path, day=None) -> int`; returns rollup rows written; re-runnable. |
| `etl/perf_test.py` | Exits 0 on success; prints timing; asserts budgets + idempotency. |
| `tests/*.py` | Cover AC-3 … AC-6; each test cites its AC. |

### Testing strategy

- Unit/integration (real SQLite temp DBs via `tmp_path`): ingest dedupe,
  two-day rollup aggregation, double-run idempotency, partial-day-then-full
  re-run fix.
- Scale: `perf_test.py` as the 1M-row gate (AC-2).
- TDD: tests written first (RED), then minimal implementation (GREEN), then
  refactor — per `dev-tdd`.

## Phase 2 — Tasks (mapped to spec ACs)

| Task | ACs delivered |
|---|---|
| 1.1 Schema + init + pytest import scaffold | AC-4 (enabler) |
| 2.1 Ingest module + tests | AC-3 |
| 2.2 Rollup module + tests | AC-4, AC-5, AC-6 |
| 2.3 Scale perf test | AC-2 |
| 3.1 Full-suite + perf gate | AC-1, AC-2 |

Cross-phase dependencies: Phase 2 tasks all depend on Task 1.1 (schema/init).
Tasks 2.1, 2.2, 2.3 are independent of each other → parallelizable (Wave 1).
