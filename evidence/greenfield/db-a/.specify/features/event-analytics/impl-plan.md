# Implementation Plan — event-analytics

## Phases
1. **Schema + init** — write `schema.sql`; `etl/init_db.py` reads it and applies
   via `executescript` (idempotent). Creates `data/events.db` by default.
2. **Ingest** — `etl/ingest.py`: stream JSONL in 10k-row batches, `executemany`
   with `INSERT OR IGNORE` in one transaction; `cursor.rowcount` accumulates the
   actually-inserted count. Payload dict → compact JSON text.
3. **Rollup** — `etl/rollup.py`: discover days via
   `SELECT DISTINCT substr(occurred_at,1,10)`; per day, `DELETE` the day's rollup
   rows then `INSERT ... GROUP BY kind, tenant` from the `[day, day+1)` ISO range
   (uses the `occurred_at` index); all inside one `BEGIN`/`COMMIT`.
4. **Scale test** — `etl/perf_test.py`: deterministic generator (seed 42,
   1M events over 30 days, 5 kinds, 4 tenants), temp-dir DB so it is re-runnable,
   timing asserts + double-run snapshot equality.
5. **Tests** — `tests/` pytest suite (see tasks).

## Key decisions
- **Watermark = full-day delete-and-recompute in one transaction**: rollup rows
  are never appended, so a re-run for the same day reproduces identical totals.
  A crash mid-transaction rolls back the whole day — no partial double count.
- **ISO range predicate** (`occurred_at >= day AND < day+1`) instead of
  `substr(...)` in `WHERE`, to leverage the index and keep 1M-row rollup fast.
- **`executemany` batch inserts + single transaction** for ingest throughput.
- **Temp dir in perf test** so the evaluator can re-run it on an already-tested tree.

## Risks
- 1M-row ingest under 120s → mitigated by batching + single transaction.
- Rollup under 30s → mitigated by index + range predicate.
