# QA Triage — GREENFIELD-3 Rate-Limited Live Event Proxy

**Date:** 2026-08-31
**Triage performed by:** qa lane (after developer multi-agent waves)
**Verdict:** ✅ **PASS — approve for handoff**

## Scope reviewed

`app/rate_limit.py`, `app/streams.py`, `app/main.py`, `app/config.py` and the
full test suite under `tests/`.

## Acceptance gate

```
$ python -m pytest tests/ -q
19 passed in 6.01s
```

## Acceptance-criteria mapping

| AC | Criterion | Evidence |
|---|---|---|
| AC-1 | Bucket enforces 10-token burst, then drops | `test_rate_limit.py::test_burst_capacity_enforced_then_drops`, `test_refill_capped_at_capacity`, `test_streams.py::test_bucket_gates_delivery_and_tracks_dropped` |
| AC-2 | Refill rate ≈ 5/s over 2s | `test_rate_limit.py::test_refill_rate_approx_5_per_second_over_2s`, `test_refill_exact_with_fake_clock` |
| AC-3 | Buffer overflow → connection closed with 429-ish error event | `test_streams.py::test_overflow_closes_connection_and_emits_error`, `test_api.py::test_sse_overflow_emits_error_and_closes` |
| AC-4 | Heartbeat comment arrives during silence | `test_streams.py::test_heartbeat_arrives_during_silence`, `test_api.py::test_sse_heartbeat_during_silence` |
| AC-5 | Publisher never blocks on a slow consumer | `test_streams.py::test_publisher_non_blocking_under_slow_consumer` (2000 publishes ≪10ms bound) |
| AC-6 | Graceful shutdown, pending events flush, no exceptions | `test_streams.py::test_shutdown_flushes_pending_events_and_exits_cleanly`, `test_api.py::test_lifespan_shutdown_cleans_registry` |
| — | Dropped counter surfaced on stream info; 404 for missing stream | `test_api.py::test_info_endpoint_surfaces_dropped_counter`, `test_info_404_for_missing_stream` |
| — | Dead-client detection cleans up resources | `test_streams.py::test_disconnect_cleans_up_subscription`, `test_unsubscribe_removes_subscriber` |

## Findings

- **P0/P1 bugs: none.**
- **One post-implementation defect found and fixed in integration (P2):**
  The Wave-2 API layer initially reformatted every SSE frame in `main.py`
  (`_reformat_sse_frame`), producing a non-standard single-line
  `event: error data: {...}` error event — a real SSE client (`EventSource`)
  would parse that line as the `event` field, swallowing the payload — and
  paying a redundant `json.loads`/`json.dumps` round-trip per data frame.
  Root cause: a test assertion that demanded `event: error` and `429` on the
  same line, over-constraining the wire format.
  **Fix:** wire format moved into the stream layer (`streams.py` emits
  spec-standard `data: {...}` with default separators and a two-line
  `event: error` / `data:` error event); `main.py` is now a thin
  pass-through; the over-constrained API test was corrected to accept the
  two-line error event. Full suite re-verified green.

## Test-correction note (traceability)

- `tests/test_api.py::test_sse_overflow_emits_error_and_closes` — changed
  from "first line containing `event: error` must also contain `429`" to
  "collect lines until both `event: error` and `429` are seen". This is a
  legitimate de-constraining of an implementation-detail assertion (the error
  event is intentionally spec-standard two-line SSE), not a relaxation of the
  acceptance criterion (AC-3 still requires an error event carrying 429 that
  closes the connection).

## Regression risk

Low. Stream-level unit tests are deterministic (injected clocks, direct
queue/registry inspection); the API layer adds three real-socket SSE tests.
No flaky timing assertions beyond generous bounds (2s refill window, 0.5s
non-blocking bound, 3–5s timeouts).

## Recommendation

**Approve.** Changes remain uncommitted in the working tree per the task
brief.
