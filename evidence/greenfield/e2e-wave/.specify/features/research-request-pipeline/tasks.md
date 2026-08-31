# Task Checklist — Research Request Pipeline

**Feature:** `research-request-pipeline`
**Spec:** `.specify/features/research-request-pipeline/spec.md`
`[P]` = can run in parallel. Order by dependency.

---

## Phase 1: MVP

### Task 1.1: Scaffold the project
**Description:** Create `requirements.txt` (fastapi, uvicorn, pytest,
pytest-asyncio, httpx, asgi-lifespan), `pytest.ini` (`asyncio_mode = auto`,
`pythonpath = .`, `testpaths = tests`), and `.gitignore` (`__pycache__/`,
`.pytest_cache/`, `data/`). No application code.
**Acceptance Criteria:**
- [ ] `pip install -r requirements.txt` succeeds.
- [ ] `pytest --version` runs (AC-9 scaffold).
**Effort:** S
**Dependencies:** None

### Task 1.2: Write failing tests (RED)
**Description:** Write `tests/` covering AC-1…AC-9: submit → status flow,
SSE transition sequence, crash-safety recovery, invalid topic/email rejection,
frontend served. Tests import `create_app` from `app.main` (does not exist
yet → RED). Use temp SQLite DB per test.
**Acceptance Criteria:**
- [ ] `pytest tests/ -q` fails with `ModuleNotFoundError: app` (RED evidence captured).
- [ ] Each test cites the AC it validates.
**Effort:** S
**Dependencies:** Task 1.1

### Task 1.3 [P]: Implement backend
**Description:** Write `app/__init__.py`, `app/config.py`, `app/db.py`,
`app/events.py`, `app/worker.py`, `app/main.py` per `impl-plan.md`
Phase 1 contracts. `create_app(db_path=None, work_delay=None,
worker_enabled=None)` factory; module-level `app = create_app()`.
Endpoints: `POST /requests` (201, 400 for empty topic/invalid email),
`GET /requests` (list), `GET /requests/{id}` (200/404),
`GET /requests/{id}/events` (SSE). Worker claims `queued` **or** orphaned
`processing` jobs atomically, sleeps `work_delay`, completes to `done` with a
result echoing the topic + timestamp. Broadcast transitions to SSE subscribers.
**Acceptance Criteria:**
- [ ] `pytest tests/test_api.py tests/test_sse.py tests/test_crash_safety.py -q` passes (AC-1…AC-7, AC-9).
**Effort:** M
**Dependencies:** Task 1.2

### Task 1.4 [P]: Implement frontend
**Description:** Write `app/static/index.html` — single static page, no build
step: submit form (topic + email), request list with status badges, per-request
SSE live updates, polling auto-refresh fallback.
**Acceptance Criteria:**
- [ ] `GET /` serves the page; page fetches `/requests` and opens EventSource per request (AC-8).
**Effort:** S
**Dependencies:** Task 1.2

### Task 1.5: Integrate and green
**Description:** Verify both agents' scopes are disjoint and clean (`git status
--porcelain`), run the full suite, fix any integration issues (R8: suite must
be green before the next wave).
**Acceptance Criteria:**
- [ ] `pytest tests/ -q` passes fully (AC-9).
- [ ] `git status --porcelain` shows only in-scope files.
**Effort:** S
**Dependencies:** Task 1.3, Task 1.4

### Task 1.6: Boot verification
**Description:** Boot `uvicorn app.main:app`, fetch `/`, confirm the frontend
page loads, shut down.
**Acceptance Criteria:**
- [ ] uvicorn boots with no errors; `GET /` returns `200 text/html` (NFR).
**Effort:** S
**Dependencies:** Task 1.5

---

## Follow-up (not in this scope)

- Real research execution / email delivery.
- Auth and multi-user isolation.
- Multi-worker horizontal scaling.
