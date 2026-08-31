# Feature Spec — Rate-Limited SSE Proxy

## Summary

Expose a live event broadcast over Server-Sent Events where each client is
rate-limited by a token bucket, slow clients are absorbed by bounded queues,
overflows close the connection with a 429-style SSE error, idle connections
receive heartbeats, and shutdown is clean.

## API contract

Implemented by `app/main.py`.

| Method | Path                     | Function            | Behavior |
|--------|--------------------------|---------------------|----------|
| POST   | `/streams/{stream_id}/events` | `publish_event` | Broadcasts an arbitrary JSON body to all subscribers; returns `Stream.info()` |
| GET    | `/streams/{stream_id}/events` | `read_events`   | `text/event-stream`; yields chunks from `stream_events` |
| GET    | `/streams/{stream_id}`   | `stream_info`       | Returns `Stream.info()` or 404 if unknown |

`Stream.info()` (`app/streams.py`) returns `{id, subscribers, published, dropped}`.

## SSE wire format

Defined in `app/sse.py`:

- data event: `data: {json}\n\n` — `sse_data(payload)`
- overflow error: `event: error\ndata: {"status": 429, "detail": "buffer overflow"}\n\n` — `error_event(OVERFLOW_STATUS, OVERFLOW_DETAIL)`
- heartbeat: `: heartbeat\n\n` — `heartbeat_event()`

## Rate limiting (per client)

- `TokenBucket(capacity=10, refill_rate=5.0)` in `app/streams.py`, refilled
  lazily from `time.monotonic`.
- `stream_loop` dequeues an event and calls `TokenBucket.try_consume()`; on
  denial it increments `Subscriber.dropped` and `Stream.dropped`.
- Bucket starts full, so a 10-event burst passes before drops begin.

## Buffering & overflow (per client)

- Each `Subscriber` has `asyncio.Queue(maxsize=100)`.
- `StreamManager.publish` uses `put_nowait` (never blocks). On `QueueFull`
  it calls `StreamManager._mark_overflow`: mark closed, evict oldest, queue
  `ERROR_SENTINEL`. `stream_loop` then emits the 429 error event and returns.

## Heartbeat & cleanup

- `stream_loop` waits with `asyncio.wait_for(sub.queue.get(), timeout=heartbeat)`
  (default 15s) and yields `heartbeat_event()` on timeout.
- The loop's `finally` calls `Stream.remove_subscriber(sub)` so disconnects
  (generator close) and errors clean up immediately.

## Shutdown

- `StreamManager.shutdown()` (`app/streams.py`) sets `shutting_down`, marks all
  subscribers closed, and queues `SHUTDOWN_SENTINEL`.
- The sentinel branch drains buffered events via `_flush_remaining` then returns.
- The app lifespan in `app/main.py` calls `manager.shutdown()` after `yield`.

## Configuration

`create_app(...)` accepts `capacity`, `refill_rate`, `buffer_size`, `heartbeat`,
falling back to env vars `FROAM_BUCKET_CAPACITY`, `FROAM_BUCKET_REFILL`,
`FROAM_BUFFER_SIZE`, `FROAM_HEARTBEAT`, then defaults in `app/streams.py`
(`DEFAULT_CAPACITY=10`, `DEFAULT_REFILL_RATE=5.0`, `DEFAULT_BUFFER_SIZE=100`,
`DEFAULT_HEARTBEAT=15.0`).

## Acceptance

`pytest tests/ -q` green. Tests live in `tests/` and cover bucket burst/refill,
overflow error event, publisher non-blocking, heartbeat, dead-client cleanup,
and shutdown.
