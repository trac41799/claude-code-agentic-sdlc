# Implementation Plan — Rate-Limited SSE Proxy

Each task maps to delivered symbols; the "delivered" column is the file/symbol
that satisfies it. All files are in this repo root.

## Phase 1 — Core primitives

| Task | Delivered by |
|------|--------------|
| SSE framing: `data:` events, `event: error`, `: heartbeat`, sentinels | `app/sse.py`: `sse_data`, `error_event`, `heartbeat_event`, `ERROR_SENTINEL`, `SHUTDOWN_SENTINEL`, `OVERFLOW_STATUS`, `OVERFLOW_DETAIL` |
| Token bucket with lazy refill, injectable clock | `app/streams.py`: `TokenBucket` (`try_consume`, `available`, `capacity`, `rate`, `tokens`) |
| Subscriber: bounded queue + bucket + drop counter | `app/streams.py`: `Subscriber` (`queue`, `bucket`, `dropped`, `closed`) |
| Stream registry and counters | `app/streams.py`: `Stream` (`add_subscriber`, `remove_subscriber`, `info`, `published`, `dropped`) |

## Phase 2 — Broadcast engine

| Task | Delivered by |
|------|--------------|
| Stream manager: get/create streams, broadcast | `app/streams.py`: `StreamManager` (`get_stream`, `publish`, `shutdown`, `_mark_overflow`, `_enqueue`) |
| Delivery loop: heartbeat, bucket admission, sentinel handling, cleanup | `app/streams.py`: `stream_loop`, `_flush_remaining` |
| SSE generator endpoint backing | `app/streams.py`: `stream_events` |

## Phase 3 — HTTP surface

| Task | Delivered by |
|------|--------------|
| FastAPI app factory with lifespan + env-overridable config | `app/main.py`: `create_app`, `lifespan`, `_env_int`, `_env_float` |
| Publisher endpoint | `app/main.py`: `publish_event` |
| SSE consumer endpoint | `app/main.py`: `read_events` |
| Stream info endpoint (404 on unknown) | `app/main.py`: `stream_info` |
| Module-level app instance | `app/main.py`: `app` |

## Phase 4 — Test suite

| Task | Delivered by |
|------|--------------|
| Token-bucket unit tests (burst, refill, cap) | `tests/test_bucket.py` |
| HTTP tests via TestClient (counters, 404, shutdown) | `tests/test_http.py` |
| Asyncio engine tests (overflow, drops, heartbeat, shutdown, cleanup) | `tests/test_streams.py` |
| Live uvicorn e2e (burst, refill, heartbeat, dead client, shutdown) | `tests/test_live.py` + `tests/live.py` (`UvicornServer`) |
| Shared fixtures | `tests/conftest.py` (`app_factory`, `make_client`, `client`) |

## Verification

Run `pytest tests/ -q` from the repo root — must be green (24 tests).
