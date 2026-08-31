# Implementation Plan — Research Request Pipeline

**Feature:** `research-request-pipeline`
**Spec:** `.specify/features/research-request-pipeline/spec.md`
**Status:** APPROVED → in build
**Date:** 2026-08-31

---

## Phase 0 — Outline & research

- **What's in Phase 1:** the full MVP — scaffolding, RED tests, backend
  (persistence, worker, SSE, API), static frontend.
- **What's deferred:** real research execution, auth, distributed
  multi-worker processing, emails actually sent, deployment.
- **Needs a prototype first?** No. The single risky mechanic — crash-safe
  claim — is de-risked by an atomic conditional `UPDATE ... WHERE status IN
  ('queued','processing')` (see R1).

### Risks & assumptions

| ID | Risk | Mitigation |
|----|------|------------|
| R1 | Two workers could claim the same job (double-complete). | Single worker per app; claims are a single atomic `UPDATE … RETURNING` restricted to `status IN ('queued','processing')`, so a `done` job can never be re-claimed. |
| R2 | SSE subscriber leaks / connection left open after client disconnects. | Per-job subscriber set; unsubscribe in `finally`; 15s keep-alive heartbeat; generator cancellation handled by Starlette on disconnect. |
| R3 | Tests share DB state / pollute each other. | `create_app(db_path=…)` factory; each test uses a `tmp_path` SQLite file; worker tied to lifespan (start/stop). |
| R4 | Background worker task leaks across tests. | Worker owned by app state; `Worker.start()`/`stop()`; lifespan teardown cancels the task. |
| R5 | `RETURNING` requires recent SQLite. | Python 3.14 bundles SQLite ≥ 3.35; verified during RED/green runs. |

**Effort (whole feature): S.**

---

## Phase 1 — Design & contracts

### 1.1 System architecture

```
Browser (static/index.html)
   │  POST /requests · GET /requests · GET /requests/{id} · GET /requests/{id}/events (SSE)
   ▼
FastAPI app (create_app factory)
   │  app.state.{settings,broadcaster,worker}
   ▼
app/db.py  ── SQLite (./data/app.db, or temp path in tests)
   ▲
app/worker.py (asyncio task started at lifespan startup)
   │  claim → sleep(work_delay≈0.2s) → complete
   ▼
app/events.py (EventBroadcaster: per-request asyncio.Queue fan-out to SSE)
```

- **Single process.** One event loop; worker is one asyncio task. FastAPI
  endpoints run in the same process (sync sqlite calls are short-lived).
- **Factory:** `create_app(db_path=None, work_delay=None, worker_enabled=None)`
  builds an isolated app (own DB, own broadcaster, own worker). Module-level
  `app = create_app()` for `uvicorn app.main:app`.

### 1.2 API contracts

From the spec — see `.specify/features/research-request-pipeline/spec.md`
"Interface contract". Request JSON shape:
`{id, topic, email, status, result, attempts, created_at, updated_at}`.

SSE framing: `event: status\ndata: {json}\n\n` where data is
`{"status": "...", "request": {...}}`.

### 1.3 Data model

`requests` table as specified in the spec. Crash-safety relies on the status
column + `claim_token` + `attempts`. Claims:

- claim next: `UPDATE requests SET status='processing', attempts=attempts+1,
  claim_token=<uuid>, updated_at=<now> WHERE id = (SELECT id FROM requests
  WHERE status IN ('queued','processing') ORDER BY id LIMIT 1) RETURNING *`
- complete: `UPDATE requests SET status='done', result=<result>,
  updated_at=<now> WHERE id=<id>`
- fail: `UPDATE requests SET status='failed', error=<msg>, updated_at=<now>
  WHERE id=<id>`

### 1.4 UI/UX flow

- Form (topic + email) → `POST /requests` → prepend card to list.
- Each card: topic, email, status badge, result (when done).
- Per-card `EventSource('/requests/{id}/events')` updates the badge live.
- `setInterval(loadRequests, 5000)` polling as auto-refresh fallback.

### 1.5 Testing strategy

- pytest + pytest-asyncio (auto mode), httpx `ASGITransport`, asgi-lifespan
  `LifespanManager`.
- Each test gets a temp SQLite DB via `create_app(db_path=tmp_path / "x.db")`.
- Tests written **first** (RED), then implementation (GREEN).

---

## Phase 2+ — Later milestones

None. This feature is the full MVP; follow-ups (real research backend,
emails) are new features, not phases.
