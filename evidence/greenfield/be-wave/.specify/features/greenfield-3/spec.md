# GREENFIELD-3 — Rate-Limited Live Event Proxy (BE-only)

**Status:** APPROVED (frozen task brief — no operator revision requested)
**Date:** 2026-08-31
**Slug:** `greenfield-3`
**Source:** docs/product/product.md

## Idea

A service that relays a live event stream to clients while enforcing
per-client rate limits, handling slow clients and dying connections.

## Requirements

### API surface

- `POST /streams/{id}/events` — internal publisher: pushes an event to the
  stream's broadcast channel.
- `GET /streams/{id}/events` — consumer: SSE stream.
- Stream info endpoint — surfaces the `dropped` counter (aggregate + per
  subscriber).

### Per-client rate limiting

- Token bucket per client: **capacity 10, refill 5 tokens/sec**.
- Events that arrive when the bucket is empty are **dropped**; a `dropped`
  counter is surfaced on the stream info endpoint.

### Buffer & overflow

- Bounded per-client buffer of **max 100 undelivered events**.
- On buffer overflow, the connection is **closed with a 429-ish SSE `error`
  event**.

### Backpressure

- Publisher must **never block more than ~10ms** on slow consumers.
- Use **bounded queues + drop-on-full**; never unbounded memory.

### Heartbeat & dead clients

- If no event flows for **15s**, send an SSE **comment heartbeat**.
- Detect dead clients (recv timeout) and clean up their resources.

### Graceful shutdown

- On app shutdown, all streams close cleanly, **pending events flush**, no
  exceptions on exit.

## Acceptance criteria

`pytest tests/ -q` passes. Tests (pytest + asyncio):

- **AC-1** Bucket enforces a 10-token burst, then drops.
- **AC-2** Refill rate ≈ 5/sec over 2s.
- **AC-3** Buffer overflow closes the connection and emits an `error` event.
- **AC-4** Heartbeat arrives during silence.
- **AC-5** Publisher non-blocking under a slow consumer.
- **AC-6** Shutdown is clean.

## Constraints

- FastAPI service, Python backend only.
- Do not commit — leave changes in the working tree.
