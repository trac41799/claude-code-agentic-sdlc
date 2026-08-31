# Product: Rate-Limited Live Event Proxy

## One-liner

A FastAPI service that relays a live event stream to many clients while
enforcing per-client rate limits, absorbing slow consumers, and cleaning up
after dying connections.

## Problem

A single publisher wants to broadcast live events to many HTTP clients.
Naive fan-out blocks the publisher on the slowest client, and unmanaged
connections leak memory and tasks. Clients also need predictable, bounded
throughput rather than an unbounded burst.

## Goals

1. **Non-blocking broadcast.** `StreamManager.publish` (in `app/streams.py`)
   never `await`s; it pushes onto bounded per-client queues with
   `put_nowait`, so a slow consumer cannot stall the publisher.
2. **Per-client rate limiting.** Each SSE client owns a `TokenBucket`
   (capacity 10, refill 5/sec). Events admitted by the bucket are delivered;
   events that arrive while the bucket is empty are dropped and counted.
3. **Bounded buffers.** Each client buffers at most 100 undelivered events.
   Overflow closes that client's connection with a 429-style SSE `error`
   event via `error_event` in `app/sse.py`.
4. **Keepalive & hygiene.** Idle connections receive an SSE comment heartbeat
   (`heartbeat_event`) every 15s; dead clients are removed by the delivery
   loop's cleanup (`stream_loop`'s `finally` → `Stream.remove_subscriber`).
5. **Clean shutdown.** `StreamManager.shutdown` marks subscribers closed and
   queues a `SHUTDOWN_SENTINEL` so active streams flush pending events and
   exit without exceptions.

## Non-goals

- No persistence, auth, or multi-host distribution. This is an in-memory
  proxy for a single process.
- No delivery guarantees beyond the token-bucket admission policy; events are
  best-effort by design (drop-on-empty, drop-on-full).

## Users / consumers

- **Publishers** call `POST /streams/{id}/events` (`publish_event` in
  `app/main.py`) with any JSON payload.
- **Consumers** call `GET /streams/{id}/events` (`read_events` in
  `app/main.py`) and receive an SSE stream.

## Delivery

- Source layout: `app/` (package), `tests/` (suite), `requirements.txt`.
- Acceptance: `pytest tests/ -q` green (24 tests).
