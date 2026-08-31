# Implementation plan — research-request-pipeline

## Target layout
```
app/                 package root
  main.py            FastAPI app, routes, lifespan, static mount
  db.py              SQLite persistence + atomic claims + recovery
  worker.py          background asyncio worker loop
  bus.py             in-memory event bus for SSE
  static/index.html  dependency-free frontend
tests/               pytest suite (temp DB via REQUESTS_DB env)
data/                SQLite file DB (gitignored, created at runtime)
```

## Steps

1. **Schema & persistence — `app/db.py`**
   - `init_db()` creates table `requests(id TEXT PK, topic, email, status
     CHECK('queued','processing','done','failed'), result, created_at, updated_at)`.
   - `get_db_path()` reads `REQUESTS_DB` env (default `data/requests.db`) so
     tests can point at a temp file.
   - `create_request(topic, email)` inserts `queued` and publishes to the bus.
   - `claim_next_job()` atomically `queued → processing` (SELECT oldest queued,
     UPDATE under a single `threading.Lock`), publishes `processing`.
   - `complete_job(id, result)` / `fail_job(id, error)` → `done`/`failed` only
     from `processing` (guards double-complete), publish transition.
   - `recover_crashed_jobs()` re-queues any rows stuck in `processing`.

2. **Event bus — `app/bus.py`**
   - `EventBus.publish(request_id, status)` appends to a per-request history
     deque and `put_nowait`s to subscribers; terminal statuses also enqueue a
     `None` sentinel so SSE streams close.
   - `subscribe` / `unsubscribe` / `history` power the SSE replay.

3. **Worker — `app/worker.py`**
   - `_loop()`: claim → `asyncio.sleep(0.2)` → complete; on exception → fail;
     `CancelledError` propagates (job stays `processing`, recovered next start).
   - `start_worker()`: run `db.recover_crashed_jobs()` then spawn `_loop`;
     idempotent guard against duplicate tasks.
   - `stop_worker()`: cancel + await, swallowing cancellation on shutdown.
   - `generate_result(topic)` → `"{topic} - completed at {utc iso}"`.

4. **API & lifespan — `app/main.py`**
   - `lifespan` → `db.init_db()` → `worker.start_worker()` → yield → `await
     worker.stop_worker()`.
   - `RequestIn` (Pydantic) validates/strips `topic` and `email`.
   - `POST /requests`, `GET /requests`, `GET /requests/{id}`, and
     `GET /requests/{id}/events` (SSE replay + live via `event_bus`).
   - `GET /` serves `app/static/index.html`; mount `/static`.

5. **Frontend — `app/static/index.html`**
   - Form POSTs JSON; list rendered from `GET /requests`; one `EventSource`
     per request updates status chips live; 3s auto-refresh fallback.

6. **Tests — `tests/`**
   - `conftest.py` `client` fixture: temp `REQUESTS_DB` + `TestClient(app)`.
   - `test_flow.py`, `test_sse.py`, `test_crash_safety.py`,
     `test_validation.py`, shared helpers in `tests/util.py`.
   - Config: `pytest.ini` (`pythonpath = .`, `testpaths = tests`).

## Verification
- `pytest tests/ -q` → 17 passed.
- `uvicorn app.main:app` boots; `GET /` → 200; live SSE shows
  `queued → processing → done` (confirmed via `curl -N`).
