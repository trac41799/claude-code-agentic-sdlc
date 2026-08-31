# Tasks — research-request-pipeline

All tasks DONE. Status verified by `pytest tests/ -q` (17 passed) and a live
`uvicorn app.main:app` boot + SSE smoke test.

## Backend

- [x] **T1** Create `requests` table with status CHECK constraint — `app/db.py:init_db`
- [x] **T2** Insert queued request and publish `queued` — `app/db.py:create_request`
- [x] **T3** Atomic claim `queued → processing` — `app/db.py:claim_next_job`
- [x] **T4** Complete/fail `processing → done|failed` guarded by status — `app/db.py:complete_job`, `app/db.py:fail_job`
- [x] **T5** Recover crashed `processing` rows on startup — `app/db.py:recover_crashed_jobs`
- [x] **T6** Configurable DB path for tests — `app/db.py:get_db_path`
- [x] **T7** Event bus with history + subscribers — `app/bus.py:EventBus`
- [x] **T8** Worker loop claim → sleep(0.2) → complete — `app/worker.py:_loop`
- [x] **T9** Worker start (with recovery) / stop — `app/worker.py:start_worker`, `app/worker.py:stop_worker`
- [x] **T10** Result generation (topic + timestamp) — `app/worker.py:generate_result`

## API

- [x] **T11** `POST /requests` with validation — `app/main.py:create_request`, `app/main.py:RequestIn`
- [x] **T12** `GET /requests` list — `app/main.py:list_requests`
- [x] **T13** `GET /requests/{id}` lookup + 404 — `app/main.py:get_request`
- [x] **T14** `GET /requests/{id}/events` SSE (replay + live) — `app/main.py:request_events`
- [x] **T15** Lifespan wiring (init DB, start/stop worker) — `app/main.py:lifespan`

## Frontend

- [x] **T16** Static page with submit form, SSE list, auto-refresh — `app/static/index.html`
- [x] **T17** Serve `/` and `/static` — `app/main.py:index`, `app/main.py` mount

## Tests

- [x] **T18** Submit/status-flow tests — `tests/test_flow.py`
- [x] **T19** SSE transition-sequence tests — `tests/test_sse.py`
- [x] **T20** Crash-safety / exactly-once tests — `tests/test_crash_safety.py`
- [x] **T21** Validation (4xx) tests — `tests/test_validation.py`
- [x] **T22** Shared wait helpers + temp-DB fixture — `tests/util.py`, `tests/conftest.py`
