# Epics — Research Request Pipeline

## Epic 1 — Request intake & validation
Owns the `POST /requests` endpoint and the `requests` SQLite table.
- Pydantic model `RequestIn` rejects blank/missing `topic` and `email` with 4xx
  (`app/main.py:RequestIn`).
- `app/db.py:create_request` inserts the row in `queued` status and publishes
  the first transition on the event bus.
- Tests: `tests/test_validation.py`.

## Epic 2 — Background worker
Drains the queue with exactly-once completion.
- `app/worker.py:_loop` claims one job per cycle, sleeps ~0.2s, then completes.
- `app/db.py:claim_next_job` atomically moves `queued → processing` under a
  process-wide lock so only one worker ever claims a job.
- `app/db.py:complete_job` / `app/db.py:fail_job` transition `processing → done|failed`.
- Tests: `tests/test_flow.py::test_status_flow_reaches_done`.

## Epic 3 — Crash-safety & recovery
Guarantees no lost and no double-completed jobs across restarts.
- `app/db.py:recover_crashed_jobs` re-queues any job stuck in `processing`
  (left by a killed process).
- `app/worker.py:start_worker` runs recovery before the loop starts; the
  idempotent guard prevents duplicate workers.
- Tests: `tests/test_crash_safety.py`.

## Epic 4 — Live status via SSE
Streams the transition sequence with no skipped states.
- `app/main.py:request_events` replays recorded history then streams live events.
- `app/bus.py:EventBus` keeps per-request history and fans out to subscribers.
- Tests: `tests/test_sse.py`.

## Epic 5 — Static frontend
Dependency-free single page served from the FastAPI app.
- `app/static/index.html` — submit form, live status list via SSE, 3s auto-refresh.
- Served at `/` and `/static` (`app/main.py:index`, `app/main.py` mount).
- Smoke-verified by booting `uvicorn app.main:app` (acceptance).
