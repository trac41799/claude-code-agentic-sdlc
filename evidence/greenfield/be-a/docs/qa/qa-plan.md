# QA Plan — Rate-Limited Live Event Proxy

## Scope

Verify the service meets the acceptance criteria: `pytest tests/ -q` green,
plus the behavioral guarantees around rate limiting, backpressure, heartbeats,
overflow, and shutdown.

## Test pyramid

| Layer | File | Covers |
|-------|------|--------|
| Unit | `tests/test_bucket.py` | TokenBucket burst of 10 then drop, refill ≈ 5/s, capping at capacity, injectable clock |
| Unit | `tests/test_streams.py` | Broadcast fan-out, overflow → 429 error event + close, bucket drops counted, publisher non-blocking, heartbeat, shutdown flush, idempotent shutdown, generator-close cleanup, sentinel distinctness |
| Integration | `tests/test_http.py` | Endpoints via TestClient: publish counters, stream info, 404, arbitrary JSON payloads, clean lifespan shutdown |
| E2E | `tests/test_live.py` | Real uvicorn socket: burst drop, 5/s refill over 2s, heartbeat during silence, dead-client cleanup, clean shutdown |

## Regression checklist

- [x] `POST /streams/{id}/events` returns 200 with `Stream.info()` body.
- [x] 11 rapid events → 10 delivered, 1 dropped, `dropped` counter = 1.
- [x] After ~2s silence, refilled bucket delivers a second burst of 10.
- [x] 101 events with an undrained consumer → connection closed, `event: error` with `status: 429` and `detail: "buffer overflow"`.
- [x] Publisher stays synchronous (no awaits) → well under the 50ms budget for 500 overflow publishes.
- [x] Heartbeat comment (`: heartbeat`) arrives during silence.
- [x] Disconnected client's subscriber removed (no lingering resources).
- [x] Shutdown flushes pending events and exits without exceptions; `manager.shutdown()` is idempotent.
- [x] Unknown stream → 404.
- [x] Full suite green: `pytest tests/ -q` → 24 passed.

## Known limitations

- Events are best-effort: dropped on empty bucket or full buffer by design.
- No persistence/auth; single-process in-memory model.
