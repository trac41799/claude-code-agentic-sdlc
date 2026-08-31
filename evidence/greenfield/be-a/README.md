# Rate-limited live event proxy

A FastAPI service that relays a live event stream to clients while enforcing
per-client rate limits, handling slow clients and dying connections.

## Endpoints

| Method | Path                        | Purpose                                        |
|--------|-----------------------------|------------------------------------------------|
| POST   | `/streams/{id}/events`      | Internal publisher: broadcast a JSON event     |
| GET    | `/streams/{id}/events`      | SSE consumer: rate-limited live event stream   |
| GET    | `/streams/{id}`             | Stream info: published / dropped / subscribers |

## Behavior

- **Token bucket**: each SSE client gets a bucket (capacity 10, refill 5/sec).
  Events that arrive when the bucket is empty are dropped and counted on the
  stream's `dropped` counter.
- **Bounded buffer**: each client buffers up to 100 undelivered events; on
  overflow the connection is closed with a 429-style SSE `error` event.
- **Backpressure**: the publisher never blocks — it uses bounded queues and
  drop-on-full, so a slow consumer cannot stall the broadcast.
- **Heartbeat**: idle connections receive an SSE comment (`: heartbeat`) after
  15s of silence; dead clients are detected and cleaned up.
- **Graceful shutdown**: on app shutdown streams flush pending events and close
  without exceptions.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```bash
pytest tests/ -q
```

Configuration defaults can be overridden via `create_app(...)` keyword
arguments or the `FROAM_BUCKET_CAPACITY`, `FROAM_BUCKET_REFILL`,
`FROAM_BUFFER_SIZE`, and `FROAM_HEARTBEAT` environment variables.
