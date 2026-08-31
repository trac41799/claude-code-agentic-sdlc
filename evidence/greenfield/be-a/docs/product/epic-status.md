# Epic Status — Rate-Limited Live Event Proxy

| Epic | Summary | Key symbols | Status | Verified by |
|------|---------|-------------|--------|-------------|
| E1 SSE broadcast plane | SSE endpoint, subscriber registry, cleanup | `read_events` (app/main.py), `stream_events`, `stream_loop`, `Stream.add_subscriber`, `Stream.remove_subscriber` (app/streams.py), `sse_data` (app/sse.py) | **Done** | `test_publish_broadcasts_to_every_subscriber`, `test_closing_the_generator_cleans_up_the_subscriber` (tests/test_streams.py) |
| E2 Rate limiting | Token bucket (10 cap, 5/s refill), drop + count | `TokenBucket.try_consume`, `TokenBucket.available`, `Stream.dropped`, `Stream.info` (app/streams.py), `stream_info` (app/main.py) | **Done** | tests/test_bucket.py; `test_burst_of_10_passes_then_11th_is_dropped`, `test_refill_approximates_5_per_second` (tests/test_live.py) |
| E3 Backpressure & overflow | Bounded queue (100), overflow → 429 error event | `StreamManager.publish`, `StreamManager._mark_overflow`, `Subscriber.queue` (app/streams.py), `error_event` (app/sse.py) | **Done** | `test_buffer_overflow_closes_connection_with_error_event`, `test_publisher_never_blocks_on_a_slow_consumer` (tests/test_streams.py) |
| E4 Heartbeat & hygiene | 15s heartbeat, dead-client cleanup | `stream_loop` wait_for timeout, `heartbeat_event` (app/sse.py), `Stream.remove_subscriber` (app/streams.py) | **Done** | `test_heartbeat_emitted_during_silence` (tests/test_streams.py); `test_heartbeat_during_silence`, `test_dead_client_is_cleaned_up` (tests/test_live.py) |
| E5 Graceful shutdown | Flush + clean exit, idempotent | `StreamManager.shutdown`, `_flush_remaining`, `SHUTDOWN_SENTINEL` (app/streams.py, app/sse.py); lifespan in app/main.py | **Done** | `test_shutdown_flushes_pending_events`, `test_shutdown_is_idempotent_and_quiet` (tests/test_streams.py); `test_shutdown_is_clean` (tests/test_http.py) |

All five epics are implemented and the full suite passes:

```
pytest tests/ -q   ->   24 passed
```
