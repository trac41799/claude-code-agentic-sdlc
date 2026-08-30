# Greenfield benchmark rubric (post-run evaluator — hidden from task brief)

Evaluator runs the SAME checks on both arms. Scores: PASS / FAIL per check; hidden checks marked H.

## Case 1 — E2E (research request pipeline)
1. `pytest tests/ -q` green (visible acceptance)
2. H: SSE transition sequence is exactly queued→processing→done (no skipped states)
3. H: crash-safety — a job left "processing" by a simulated crash is re-claimed and completes EXACTLY once (count of done rows == 1)
4. H: worker does not process a job twice (no double-complete) under restart
5. H: invalid/empty topic returns 4xx, not 5xx

## Case 2 — FE-only (virtualized feed + optimistic likes)
1. `node --test tests/` green (visible acceptance)
2. H: window math exact at scrollTop=0, mid-list, and bottom-clamp (fixed rowHeight=40, viewport 600, overscan 2)
3. H: optimistic interleaving — add A, add B, rollback A → B remains; rollback never-added → no-op, size unchanged
4. H: engine is dependency-free (no import/require outside node builtins in engine.js)
5. H: demo.html renders windowed rows (row count in DOM << 10000) — static check

## Case 3 — BE-only (rate-limited SSE proxy)
1. `pytest tests/ -q` green (visible acceptance)
2. H: token bucket exact — burst of 10 passes, 11th dropped, refill ≈5/sec (assert with tolerance)
3. H: overflow (100 buffered) closes connection + emits `error` event
4. H: publisher returns in < 50ms while consumer is slow (backpressure non-blocking)
5. H: heartbeat arrives within 15s of silence; dead-client cleanup (no lingering tasks)

## Case 4 — DB+ETL (1M-row analytics)
1. `pytest tests/ -q` green (visible acceptance)
2. H: `python etl/perf_test.py` — 1M ingest < 120s, rollup < 30s (same machine)
3. H: double-run rollup idempotency — identical counts AND sums
4. H: partial-day then full-day re-run converges to full-day totals
5. H: INSERT OR IGNORE dedupe — re-ingest of same file adds 0 rows

## Traceability score (both cases)
- Count artifacts: spec/plan/tasks/QA docs (framework-style: docs/product/*.md, .specify/*, impl-plan/tasks/qa files)
- Map: do artifact claims resolve to actual delivered symbols/files? (artifact→code link ratio)
- A-arm expected ≥ 3 artifacts with ≥ 80% link ratio; B-arm expected 0 (raw).

## Speed/cost
- Wall time, turns, tokens in/out, cost — from session JSON. Same model pin both arms.