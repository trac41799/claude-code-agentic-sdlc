GREENFIELD-3 (BE-only) TASK BRIEF (frozen, identical for both arms)

Idea: "Rate-limited live event proxy" — a service that relays a live event stream to clients while enforcing per-client rate limits, handling slow clients and dying connections.

Build it as a FastAPI service:
- `POST /streams/{id}/events` (internal publisher): pushes an event to the stream's broadcast channel.
- `GET /streams/{id}/events` (consumer): SSE stream; each client has a token bucket (capacity 10, refill 5/sec); events that arrive when the bucket is empty are DROPPED (with a `dropped` counter surfaced on the stream info endpoint); when a client's buffer (max 100 undelivered events) overflows, the connection is closed with a 429-ish SSE `error` event.
- Backpressure: publisher must never block more than ~10ms on slow consumers; use bounded queues + drop-on-full (not unbounded memory).
- Heartbeat: if no event flows for 15s, send an SSE comment heartbeat; detect dead clients (recv timeout) and clean up their resources.
- Graceful shutdown: on app shutdown, all streams close cleanly, pending events flush, no exceptions on exit.
- Tests (pytest, asyncio): bucket enforces 10-token burst then drops; refill rate ≈ 5/sec over 2s; buffer overflow closes connection and emits error; heartbeat arrives during silence; publisher non-blocking under a slow consumer; shutdown is clean.

Acceptance: `pytest tests/ -q` passes.

Do not commit. Leave changes in the working tree.