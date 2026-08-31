# Product — Research Request Pipeline

## One-liner
A user submits a research request; the system queues it, processes it in the
background, and the user can watch live status and read the final result.

## Users
- **Requester** — submits a topic + email and watches the job move
  `queued → processing → done`.

## Core features
1. **Request intake** — `POST /requests` accepts `{topic, email}`, validates
   input, and creates a request in `queued` status. Blank or missing topics are
   rejected with a 4xx (`app/main.py:create_request`, `app/db.py:create_request`).
2. **Background processing** — an asyncio worker claims queued jobs one at a
   time, simulates ~0.2s of work, and marks each `done` with a generated result
   (topic + timestamp) (`app/worker.py:_loop`, `app/db.py:claim_next_job`,
   `app/db.py:complete_job`).
3. **Live status via SSE** — `GET /requests/{id}/events` streams the exact
   transition sequence `queued → processing → done|failed`; late joiners replay
   the full history with no skipped states (`app/main.py:request_events`,
   `app/bus.py:EventBus`).
4. **Status + result lookup** — `GET /requests/{id}` returns the current
   request row (`app/main.py:get_request`, `app/db.py:get_request`).
5. **Request list** — `GET /requests` returns all requests, newest first, used
   by the frontend list (`app/main.py:list_requests`, `app/db.py:list_requests`).
6. **Static frontend** — a dependency-free single page (`app/static/index.html`)
   with a submit form, a live-updating list via SSE, and auto-refresh.

## Non-functional requirements
- **Crash-safety**: a job interrupted mid-`processing` is re-claimed on restart
  and completes exactly once — never lost, never double-completed
  (`app/db.py:recover_crashed_jobs`, `app/worker.py:start_worker`).
- **Local, zero infra**: FastAPI + SQLite file DB under `./data` (path overridable
  via the `REQUESTS_DB` env var for tests; `app/db.py:get_db_path`).

## Acceptance criteria
- `pytest tests/ -q` passes.
- `uvicorn app.main:app` boots and the frontend page loads at `/`.
