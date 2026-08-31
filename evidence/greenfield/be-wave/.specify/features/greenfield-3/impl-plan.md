# Implementation Plan — GREENFIELD-3 Rate-Limited Live Event Proxy

**Status:** COMPLETE (dev-feature-plan)
**Date:** 2026-08-31
**Spec:** .specify/features/greenfield-3/spec.md

---

## Phase 0 — Outline & Research

### What's in this build

A single-process FastAPI service. All stream state lives in memory in a
registry; there is no persistence. The build is fully covered by the
acceptance criteria in `spec.md` (AC-1 … AC-6).

### Deferred (explicitly out of scope)

- AuthN/AuthZ on the publisher endpoint (it is explicitly internal).
- Multi-process / multi-node fan-out.
- Persistence/replay of events.
- Client backpressure in the HTTP/SSE layer beyond the bounded queue.

### Prototype answers already found (research spike)

An in-process spike proved that **both `httpx.ASGITransport` and Starlette's
`TestClient` buffer the full response before returning** — they cannot exercise
a long-lived (infinite) SSE stream. Therefore:

- Behavioural tests (bucket, refill, overflow→error, heartbeat, non-blocking
  publish, shutdown) run **directly against the stream layer** with asyncio.
- End-to-end SSE tests run against a **real in-process uvicorn server** on a
  free port (verified working on this machine: real streaming, clean shutdown).

### Risks & Assumptions

| Risk | Mitigation |
|---|---|
| Cancellation noise on client disconnect (Python 3.14 `asyncio.wait_for` quirk) | Generator uses `get_nowait()` + `asyncio.wait` on tasks, never `wait_for` on the queue; `finally` cleans up the subscription. |
| Flaky real-time refill test on loaded CI | Test asserts a tolerant bound (≥8/10 tokens after ~2s) and a fake-clock test pins exact arithmetic. |
| API SSE tests flaky on socket bind | Use `port=0` (ephemeral), wait for `server.started`, always `should_exit` + `await` the serve task. |
| Publisher accidentally blocking on slow consumer | `publish()` is fully synchronous (no `await`) and uses `put_nowait`; measured far under the 10ms budget. |
| Unbounded memory growth | Every per-client queue is bounded (`maxsize=100`); overflow drops/closes instead of growing. |

---

## Phase 1 — Design & Contracts

### Architecture

```
POST /streams/{id}/events          GET /streams/{id}/events          GET /streams/{id}
      │                                  │                                 │
      ▼                                  ▼                                 ▼
┌────────────┐   publish()   ┌──────────────────────┐   info()        ┌────────────┐
│  FastAPI   │ ────────────▶ │     Stream           │ ──────────────▶ │  Stream    │
│   app      │               │  (per stream_id)     │                 │  Registry  │
└────────────┘               │  - subscribers map   │                 └────────────┘
                             │  - events_published  │
                             │  - dropped_total     │
                             └─────────┬────────────┘
                                       │ subscribe()
                              ┌────────▼─────────┐      ┌──────────────────────┐
                              │    Subscriber    │─────▶│  TokenBucket          │
                              │  - bounded queue │      │  capacity=10          │
                              │    (max 100)     │      │  refill=5/sec         │
                              │  - dropped       │      └──────────────────────┘
                              │  - overflowed    │
                              │  - aiter_sse()   │  → yields SSE strings
                              └──────────────────┘
```

- **TokenBucket** (`app/rate_limit.py`): pure logic, injectable clock.
- **Stream / Subscriber / Registry** (`app/streams.py`): broadcast + bounded
  per-client queues + heartbeat + overflow/shutdown events + SSE formatting.
- **FastAPI app** (`app/main.py`): endpoints, lifespan shutdown, wiring.
- **Settings** (`app/config.py`): tunable defaults (capacity 10, refill 5,
  buffer 100, heartbeat 15s).

### API contracts

#### `POST /streams/{stream_id}/events`
- **Body:** any JSON value (event payload).
- **Behaviour:** `registry.get_or_create(stream_id)`, then `stream.publish(body)`.
- **Responses:**
  - `202` `{"status":"accepted","stream_id":…,"events_published":…,
    "delivered":…,"dropped":…,"overflowed":…}`
  - `400` `{"error":"invalid JSON body"}` on malformed JSON.

#### `GET /streams/{stream_id}/events`
- **Response:** `200` `text/event-stream`, `Cache-Control: no-cache`.
- **Frames:**
  - event: `data: {json}\n\n`
  - heartbeat (idle ≥ heartbeat interval): `: heartbeat\n\n`
  - buffer overflow: `event: error\ndata: {"error":"buffer_overflow","status":429,…}\n\n` then close.
- On client disconnect (`request.is_disconnected()`), the subscription is
  removed in `finally`.

#### `GET /streams/{stream_id}` (info endpoint)
- `200` — `{"stream_id":…,"events_published":…,"subscribers":…,"dropped":…,
  "subscribers_detail":[{"id":…,"dropped":…,"queued":…,"overflowed":…}]}`
- `404` — `{"error":"stream not found"}`.

### Data model (in-memory)

```python
@dataclass(frozen=True)
class Settings:
    bucket_capacity: int = 10
    bucket_refill_rate: float = 5.0
    buffer_size: int = 100
    heartbeat_seconds: float = 15.0

class TokenBucket:            # capacity, refill_rate, clock
    def try_consume(n=1) -> bool
    @property tokens -> float

class Subscriber:             # queue(maxsize=buffer_size), bucket, dropped,
                              # overflowed, closed, _overflow_event, _shutdown_event
    def mark_overflow()       # set overflowed + _overflow_event (called by publish)
    def close()               # set closed + _shutdown_event (called by shutdown)
    async def aiter_sse(is_disconnected=None) -> AsyncIterator[str]

class Stream:                 # stream_id, subscribers{}, events_published, dropped_total
    subscribe() -> Subscriber
    unsubscribe(sub)
    publish(event) -> PublishResult   # synchronous, non-blocking
    async shutdown()
    info() -> dict

class StreamRegistry:         # _streams{id: Stream}
    get_or_create(stream_id, **overrides) -> Stream
    get(stream_id) -> Stream | None
    remove(stream_id)
    async shutdown_all()
```

### Interaction contract (publisher → subscribers)

`publish(event)`:
1. `events_published += 1`
2. for each live subscriber:
   - skip if `overflowed` or `closed`;
   - `bucket.try_consume(1)` — on **empty bucket**: `sub.dropped += 1`,
     `dropped_total += 1`, **drop the event**;
   - else `queue.put_nowait(event)` — on **`QueueFull`**: set `overflowed`,
     set `_overflow_event`, mark result overflowed.
3. returns `PublishResult(delivered, dropped, overflowed)`.
4. **No `await` anywhere** → publisher never blocks (well under the ~10ms
   budget).

### Consumer loop contract (`aiter_sse`)

```
loop:
  if overflowed:        yield error frame; break
  if closed and queue empty: break
  drain queue via get_nowait → yield data frames
  if is_disconnected(): break
  wait on {overflow_event, shutdown_event}, timeout=heartbeat_seconds
    - event set  → loop (top handles overflow / shutdown)
    - timeout    → yield ": heartbeat\n\n"
finally: stream.unsubscribe(subscriber)
```

Graceful shutdown sets `closed` + `_shutdown_event` per subscriber; the loop
drains remaining queued events (flush) then breaks.

### Testing strategy

| File | Scope | Approach |
|---|---|---|
| `tests/test_rate_limit.py` | TokenBucket | Direct unit: burst, real-time refill (~2s, tolerant), fake-clock exact refill. |
| `tests/test_streams.py` | Stream/Subscriber/Registry | asyncio unit: bucket gating + dropped counter, overflow→error, heartbeat during silence, non-blocking publish, shutdown flush. |
| `tests/test_api.py` | FastAPI endpoints | Sync TestClient for POST/info/lifespan; real in-process uvicorn for SSE delivery/heartbeat/overflow. |

---

## Phase 2 — Verification & Handoff

- Run `pytest tests/ -q` — must be green.
- Multi-agent waves (see `tasks.md`): Wave 1 foundation, Wave 2 API; suite gate
  after each wave; scope + `git status` verification after each wave.
- QA lane: `qa-triage` report + verification evidence in `docs/qa/`.
- Do **not** commit — leave changes in the working tree.

## Effort summary

| Phase | Effort |
|---|---|
| Phase 0 — Outline & research | S (spike done) |
| Phase 1 — Design & contracts | S |
| Wave 1 — Foundation (`rate_limit.py` + `streams.py`) | M |
| Wave 2 — API (`main.py`) | M |
| QA / triage / reports | S |
