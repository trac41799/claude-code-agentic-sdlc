# Product — Rate-Limited Live Event Proxy

**Status:** Spec captured (GREENFIELD-3, BE-only)
**Date:** 2026-08-31
**Scope:** Backend service only — no frontend, no database.

## 1. What we are building

A **rate-limited live event proxy**: a service that relays a live event stream
to clients while enforcing per-client rate limits, handling slow clients and
dying connections gracefully.

The service is a FastAPI application with two primary surfaces:

- an **internal publisher** endpoint that pushes events into a stream's
  broadcast channel, and
- a **consumer** endpoint that streams events to clients over Server-Sent
  Events (SSE).

## 2. Functional requirements

1. **Publisher — `POST /streams/{id}/events`** (internal): pushes an event to
   the stream's broadcast channel.
2. **Consumer — `GET /streams/{id}/events`** (SSE): a live event stream per
   client, with:
   - a **token bucket** per client — capacity 10, refill 5 tokens/sec;
   - events that arrive when the bucket is empty are **dropped**, and a
     `dropped` counter is surfaced on the stream info endpoint;
   - a **bounded buffer** of max 100 undelivered events per client; when the
     buffer overflows, the connection is **closed with a 429-ish SSE `error`
     event**.
3. **Backpressure**: the publisher must **never block more than ~10ms** on slow
   consumers — bounded queues + drop-on-full (never unbounded memory).
4. **Heartbeat**: if no event flows for **15s**, send an SSE **comment
   heartbeat** (`: ...`); detect dead clients (recv timeout) and clean up their
   resources.
5. **Graceful shutdown**: on app shutdown, all streams close cleanly, pending
   events flush, no exceptions on exit.

## 3. Non-functional requirements

- Built as a FastAPI service.
- Tested with pytest + asyncio.
- Bounded memory: no unbounded queues; drop-on-full everywhere.
- Deterministic, non-flaky tests.

## 4. Acceptance criteria

`pytest tests/ -q` passes, with tests covering:

| # | Behaviour tested |
|---|---|
| AC-1 | Token bucket enforces a 10-token burst, then drops |
| AC-2 | Token bucket refills at ≈5 tokens/sec over 2s |
| AC-3 | Buffer overflow closes the connection and emits an `error` event |
| AC-4 | Heartbeat arrives during silence |
| AC-5 | Publisher is non-blocking under a slow consumer |
| AC-6 | Shutdown is clean |

## 5. Out of scope

- No authentication/authorization (publisher endpoint is explicitly internal).
- No persistence — in-memory broadcast only.
- No cross-node distribution (single-process service).
- No frontend/consumer UI.
