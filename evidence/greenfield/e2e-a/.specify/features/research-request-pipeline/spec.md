# Feature spec — research-request-pipeline

## Summary
A local FastAPI + SQLite app where users submit research requests that are
processed in the background, with live status via SSE and a static frontend.

## Acceptance criteria (mapped to code)

### AC1 — Submit a request
`POST /requests` with `{topic, email}` returns the created request with
`status == "queued"`, an `id`, and `result == null`.
- Implemented: `app/main.py:create_request` → `app/db.py:create_request`.
- Verified: `tests/test_flow.py::test_submit_creates_queued_request`.

### AC2 — Invalid input rejected
Blank or missing `topic` (and `email`) is rejected with a 4xx, never 5xx.
- Implemented: `app/main.py:RequestIn` (`topic_not_blank`, `email_not_blank`).
- Verified: `tests/test_validation.py`.

### AC3 — Background processing
A submitted request transitions `queued → processing → done` on its own, and
`done` rows carry a generated result containing the topic.
- Implemented: `app/worker.py:_loop`, `app/db.py:claim_next_job`,
  `app/db.py:complete_job`, `app/worker.py:generate_result`.
- Verified: `tests/test_flow.py::test_status_flow_reaches_done`.

### AC4 — Live status via SSE
`GET /requests/{id}/events` emits exactly `queued → processing → done` (or
`failed`) with no skipped states, for both live and already-finished requests.
- Implemented: `app/main.py:request_events`, `app/bus.py:EventBus`.
- Verified: `tests/test_sse.py`.

### AC5 — Crash-safety
A job left in `processing` by a crash is re-claimed on the next startup and
completes **exactly once** (`count(done rows) == 1`); a `done` job is never
reprocessed.
- Implemented: `app/db.py:recover_crashed_jobs`, `app/worker.py:start_worker`,
  atomic claim in `app/db.py:claim_next_job`.
- Verified: `tests/test_crash_safety.py`.

### AC6 — Status & result lookup, list
`GET /requests/{id}` returns status + result (404 if unknown);
`GET /requests` lists all requests newest-first.
- Implemented: `app/main.py:get_request`, `app/main.py:list_requests`,
  `app/db.py:get_request`, `app/db.py:list_requests`.
- Verified: `tests/test_flow.py::test_missing_request_returns_404`,
  `tests/test_flow.py::test_list_includes_submitted`.

### AC7 — Frontend loads
`uvicorn app.main:app` boots and `/` serves `app/static/index.html` (form +
live list + auto-refresh).
- Implemented: `app/main.py:index`, `app/static/index.html`.
- Verified: boot smoke test (`GET /` → 200).

## Out of scope
- Real research generation, email delivery, auth, multi-worker scale-out.
