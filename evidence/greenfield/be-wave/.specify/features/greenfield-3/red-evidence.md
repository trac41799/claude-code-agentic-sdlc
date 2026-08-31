# RED Evidence — GREENFIELD-3 Rate-Limited Live Event Proxy

**Date:** 2026-08-31
**Method:** dev-tdd — every test written before any implementation. Stub
modules provide real signatures (`app/rate_limit.py`, `app/streams.py`,
`app/main.py`) so collection succeeds and failures are `NotImplementedError`
(the *right* reason — feature missing — not import errors).

## Baseline run (before any implementation)

```
$ python -m pytest tests/ -q
11 failed, 8 errors in 1.36s
```

Every failure/error is `NotImplementedError` from a stub:

| Test | Spec criterion | Failure |
|---|---|---|
| `test_rate_limit.py::test_burst_capacity_enforced_then_drops` | AC-1 | NotImplementedError |
| `test_rate_limit.py::test_refill_rate_approx_5_per_second_over_2s` | AC-2 | NotImplementedError |
| `test_rate_limit.py::test_refill_exact_with_fake_clock` | AC-2 | NotImplementedError |
| `test_rate_limit.py::test_refill_capped_at_capacity` | (cap) | NotImplementedError |
| `test_streams.py::test_bucket_gates_delivery_and_tracks_dropped` | AC-1 + info | NotImplementedError |
| `test_streams.py::test_overflow_closes_connection_and_emits_error` | AC-3 | NotImplementedError |
| `test_streams.py::test_heartbeat_arrives_during_silence` | AC-4 | NotImplementedError |
| `test_streams.py::test_publisher_non_blocking_under_slow_consumer` | AC-5 | NotImplementedError |
| `test_streams.py::test_shutdown_flushes_pending_events_and_exits_cleanly` | AC-6 | NotImplementedError |
| `test_streams.py::test_disconnect_cleans_up_subscription` | (dead clients) | NotImplementedError |
| `test_streams.py::test_unsubscribe_removes_subscriber` | (cleanup) | NotImplementedError |
| `test_api.py::*` (8 tests) | AC-1…AC-6 + wiring | NotImplementedError (create_app) |

## Why this is a valid RED

- Tests target the acceptance criteria from `spec.md` (cited in names/comments).
- Failures are *behavioural* (feature not implemented), never import/collection
  errors — the stubs exist and are importable.
- No test is skipped, commented out, or marked `.only`.

## GREEN gate

After the multi-agent implementation waves, `pytest tests/ -q` must be fully
green. See `wave-report.md` for per-wave evidence.
