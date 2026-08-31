# Product Spec — Research Request Pipeline

**Feature slug:** `research-request-pipeline`
**Status:** APPROVED (frozen brief, both arms identical)
**Date:** 2026-08-31
**Owner:** Product Manager (spec capture) → Developer (implementation)

---

## 1. The idea

A **Research Request Pipeline**: a user submits a research request; the system
queues it, processes it in the background, and the user can watch live status
and read the final result.

## 2. Business context

- Single-user / local tool. No auth, no multi-tenant isolation required.
- Runs fully on the operator's machine. No external services, no network
  dependencies at runtime.
- The "research" is simulated: a background worker sleeps briefly and echoes
  the topic with a timestamp. This keeps the pipeline mechanics
  (queue → claim → process → result) the real deliverable.

## 3. Goals / success criteria

- A user can submit a request with a **topic** and an **email**.
- The request is queued and processed asynchronously (never blocking the
  submit call).
- The user can watch the request progress live: `queued → processing → done`.
- The user can read the final result.
- The system is **crash-safe**: a restart mid-job must neither lose the job
  nor complete it twice.
- Tests are automated and runnable with `pytest tests/ -q`.

## 4. Non-goals (out of scope)

- Real research/LLM execution, auth, user accounts, emails actually sent.
- Multi-worker distributed processing, message brokers, external queues.
- A build step or framework for the frontend — static HTML/JS only.

## 5. Personas

- **Submitter** — anyone with a topic and an email address. Wants to drop off
  a request and come back for the result.
- **Operator/Developer** — runs the app locally, reads logs/tests, wants the
  pipeline mechanics to be simple and inspectable.

## 6. Functional requirements (frozen)

### FR-1 — Submit a request
`POST /requests` with JSON body `{ "topic": string, "email": string }`.
- Creates a request with status `queued`.
- **FR-1a:** An empty/whitespace-only topic is rejected (`400`).
- **FR-1b:** An invalid email (no `@`) is rejected (`400`).
- Returns the created request.

### FR-2 — Read a request
`GET /requests/{id}` returns status + result for one request.
- Unknown id → `404`.

### FR-3 — Live status (SSE)
`GET /requests/{id}/events` streams status transitions as Server-Sent Events:
`queued → processing → done | failed`. The stream first emits the current
status, then each subsequent transition.

### FR-4 — List requests
`GET /requests` returns all requests, oldest first (required by the frontend
list + auto-refresh).

### FR-5 — Background worker
A background asyncio loop (started at app startup) claims queued jobs,
simulates work (~0.2s per request), and marks the job `done` with a generated
result that echoes the topic plus a timestamp.

### FR-6 — Crash safety
Claims are persisted status transitions in SQLite. A job left in `processing`
by a crashed process is **re-claimable** on the next worker start. A job is
completed exactly once: a `done` job is never re-processed.

### FR-7 — Frontend
A single static HTML/JS page (no build step):
- form to submit a request (topic + email),
- list of requests with status badges,
- live status via SSE per request,
- auto-refresh fallback (polling).

## 7. Non-functional requirements

- **Stack:** FastAPI + SQLite (file DB in `./data`), asyncio worker, static
  frontend, pytest for tests (temp DB per test).
- **Acceptance commands:**
  - `pytest tests/ -q` passes.
  - `uvicorn app.main:app` boots and `/` serves the frontend page.

## 8. Testing strategy

Unit/integration via httpx ASGI test client against a temp SQLite DB:
- submit → status flow (`queued` → `done`, result echoes topic),
- SSE emits the transition sequence,
- crash-safety: mark a job `processing` (simulate crash), restart the worker,
  job completes exactly once and ends `done`,
- invalid topic rejected.

## 9. Decisions & open questions

- **D1:** Added `GET /requests` (list) beyond the frozen brief — required by
  FR-4/FR-7 (frontend list + auto-refresh). No other endpoints added.
- **D2:** Statuses are `queued`, `processing`, `done`, `failed`.
- **D3:** `failed` status is reserved (worker error path) but not exercised by
  tests; the happy path is the tested contract.
- **D4:** No commit. Deliverable is the working tree only.
