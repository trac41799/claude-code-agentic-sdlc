# Tasks — Rate-Limited SSE Proxy

All tasks complete. Status verified by `pytest tests/ -q` (24 passed).

| # | Task | Delivered symbol/file | Status |
|---|------|------------------------|--------|
| 1 | SSE frame helpers + sentinels | `app/sse.py`: `sse_data`, `error_event`, `heartbeat_event`, `ERROR_SENTINEL`, `SHUTDOWN_SENTINEL` | Done |
| 2 | Token bucket (10 cap, 5/s) | `app/streams.py`: `TokenBucket` | Done |
| 3 | Subscriber with bounded queue + bucket | `app/streams.py`: `Subscriber` | Done |
| 4 | Stream registry + counters | `app/streams.py`: `Stream` | Done |
| 5 | Non-blocking broadcast + overflow close | `app/streams.py`: `StreamManager.publish`, `StreamManager._mark_overflow` | Done |
| 6 | Graceful shutdown | `app/streams.py`: `StreamManager.shutdown`, `_flush_remaining` | Done |
| 7 | Delivery loop (heartbeat, bucket, cleanup) | `app/streams.py`: `stream_loop`, `stream_events` | Done |
| 8 | App factory + lifespan + env config | `app/main.py`: `create_app`, `lifespan` | Done |
| 9 | POST /streams/{id}/events | `app/main.py`: `publish_event` | Done |
| 10 | GET /streams/{id}/events (SSE) | `app/main.py`: `read_events` | Done |
| 11 | GET /streams/{id} info + 404 | `app/main.py`: `stream_info` | Done |
| 12 | Bucket unit tests | `tests/test_bucket.py` | Done |
| 13 | HTTP tests | `tests/test_http.py` | Done |
| 14 | Engine asyncio tests | `tests/test_streams.py` | Done |
| 15 | Live e2e tests | `tests/test_live.py`, `tests/live.py` | Done |
| 16 | Fixtures | `tests/conftest.py` | Done |
| 17 | Dependencies + ignore + readme | `requirements.txt`, `.gitignore`, `README.md` | Done |
