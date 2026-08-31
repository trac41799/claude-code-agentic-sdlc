# Architecture Plan — Rate-Limited SSE Proxy

## Overview

Single FastAPI process. `app/main.py` exposes the HTTP surface; `app/streams.py`
holds the broadcast engine; `app/sse.py` owns wire framing. No external
storage or background processes.

```
publisher ──POST /streams/{id}/events──► StreamManager.publish
                                            │  (synchronous, put_nowait)
                                            ▼
                        per-subscriber asyncio.Queue (maxsize=100)
                                            │
                          stream_loop  ◄────┘  (async generator, per SSE client)
                          ├─ wait_for(get, heartbeat) → ": heartbeat"
                          ├─ TokenBucket.try_consume() → drop & count
                          ├─ ERROR_SENTINEL    → event:error 429, close
                          └─ SHUTDOWN_SENTINEL → flush, close
                                            │
GET /streams/{id}/events ◄──StreamingResponse ◄─ chunks
```

## Data flow

1. `read_events` (app/main.py) calls `stream_events(manager, stream_id)`
   (app/streams.py), which registers a `Subscriber` on the `Stream` and
   yields chunks from `stream_loop`.
2. `publish_event` calls `StreamManager.publish`, which increments
   `Stream.published` and pushes the payload into each subscriber's bounded
   queue with `put_nowait` — never blocking the caller.
3. `stream_loop` dequeues items. A `TokenBucket.try_consume()` pass yields
   `sse_data(payload)`; a denial increments `Subscriber.dropped` /
   `Stream.dropped`. A full queue at publish time triggers
   `StreamManager._mark_overflow` → `ERROR_SENTINEL` → 429 error event and
   generator return.
4. The loop's `finally` calls `Stream.remove_subscriber`, so every exit path
   (disconnect, overflow, shutdown) tears the client down.

## Key decisions

- **Synchronous publish** (`put_nowait`, no `await`): guarantees the publisher
  cannot be blocked by slow consumers; satisfies the ~10ms backpressure budget.
- **Bounded queues + drop-on-full**: bounded memory; overflow is surfaced to
  the client as a 429-style SSE error rather than silently dropping the
  connection.
- **Lazy token bucket** (refill computed from `time.monotonic` on access): no
  background task, deterministic under load, and unit-testable with an injected
  clock (`TokenBucket(capacity=…, refill_rate=…, now=fake_clock)`).
- **Async-generator delivery loop**: resource cleanup is scoped to the
  generator's `finally`, so client disconnect (Starlette `aclose`) and app
  shutdown both run the same teardown path.
- **Sentinels over queues**: `ERROR_SENTINEL` / `SHUTDOWN_SENTINEL`
  (app/sse.py) are plain object markers, so the queue stays homogeneous and
  the loop remains single-drain.

## Failure handling

| Failure | Response |
|---------|----------|
| Slow consumer fills buffer | `_mark_overflow` → 429 error event, connection closed |
| Bucket empty at delivery | Event dropped, `dropped` counter incremented |
| Client disconnects mid-stream | Generator `finally` removes subscriber |
| App shutdown | `StreamManager.shutdown` queues `SHUTDOWN_SENTINEL`; loops flush and exit |
| Unknown stream info | `stream_info` returns 404 |

## Dependencies

`requirements.txt`: `fastapi`, `uvicorn`, `pytest`, `httpx` (test client /
live e2e). Runtime needs only `fastapi` + `uvicorn`.
