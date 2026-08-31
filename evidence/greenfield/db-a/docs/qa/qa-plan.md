# QA Plan — Event Analytics DB + ETL

## Scope
Verify the acceptance criteria and the hidden behavioral checks for the DB+ETL arm.

## Test pyramid
| Layer | What | Where |
|---|---|---|
| Unit (ingest) | INSERT OR IGNORE dedupe; field storage; returned inserted count | `tests/test_ingest.py` |
| Unit (rollup) | Two-day aggregation correctness | `tests/test_rollup.py` |
| Integration (rollup) | Double-run idempotency (counts + sums) | `tests/test_idempotency.py` |
| Integration (rollup) | Partial-day → full-day convergence | `tests/test_partial_then_full.py` |
| Scale | 1M ingest <120s, rollup <30s, double-run identical snapshot | `etl/perf_test.py` |

## Manual check mapping (hidden checks)
1. **1M perf on this machine** → `python etl/perf_test.py` times ingest and rollup, asserts limits.
2. **Double-run idempotency, identical counts AND sums** → perf test compares full
   `daily_rollup` snapshots after two rollups, plus sum equality.
3. **Partial-day then full-day re-run converges** → `tests/test_partial_then_full.py`.
4. **Re-ingest of same file adds 0 rows** → `tests/test_ingest.py::test_ingest_dedupes_duplicate_ids`.

## Sign-off
- [x] `pytest tests/ -q` — 6 passed
- [x] `python etl/perf_test.py` — perf + idempotency asserts pass
