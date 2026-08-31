# Epics — Rate-Limited Live Event Proxy

## E1 — SSE broadcast plane

`GET /streams/{id}/events` (`read_events` in `app/main.py`) streams a
`text/event-stream` response backed by `stream_events` →
`stream_loop` (both in `app/streams.py`). Each connection is registered as a
`Subscriber` on its `Stream` and is torn down by `Stream.remove_subscriber`
when the generator closes.

**Definition of done:** a connected client receives `data:` events produced by
`sse_data` (in `app/sse.py`); the subscriber is removed after disconnect.
Covered by `tests/test_streams.py::test_publish_broadcasts_to_every_subscriber`
and `tests/test_streams.py::test_closing_the_generator_cleans_up_the_subscriber`.

## E2 — Rate limiting

`TokenBucket` (in `app/streams.py`) enforces capacity 10 / refill 5 per
second. `stream_loop` admits each dequeued event via `TokenBucket.try_consume`;
a denied event increments `Subscriber.dropped` and `Stream.dropped`, surfaced
by `Stream.info` on `GET /streams/{id}` (`stream_info` in `app/main.py`).

**Definition of done:** burst of 10 passes, 11th dropped; refill ≈ 5/sec.
Covered by `tests/test_bucket.py` and the live burst/refill tests in
`tests/test_live.py`.

## E3 — Backpressure & overflow

`StreamManager.publish` pushes onto each subscriber's bounded queue
(`asyncio.Queue(maxsize=100)`). On `QueueFull`, `StreamManager._mark_overflow`
closes the subscriber and queues `ERROR_SENTINEL`; `stream_loop` emits
`error_event(429, "buffer overflow")` and returns, ending the SSE response.
The publisher never blocks (no awaits in `publish`).

**Definition of done:** a full 100-event buffer closes the connection with a
429 error event; the publisher stays under the latency budget.
Covered by `tests/test_streams.py::test_buffer_overflow_closes_connection_with_error_event`
and `tests/test_streams.py::test_publisher_never_blocks_on_a_slow_consumer`.

## E4 — Heartbeat & dead-client hygiene

`stream_loop` uses `asyncio.wait_for(sub.queue.get(), timeout=heartbeat)`; on
timeout it yields `heartbeat_event()` (`: heartbeat`). Closing the generator
(client disconnect) runs the loop's `finally`, removing the subscriber.

**Definition of done:** an idle stream receives a heartbeat comment; a
disconnected client's subscriber is removed.
Covered by `tests/test_streams.py::test_heartbeat_emitted_during_silence`,
`tests/test_live.py::test_heartbeat_during_silence`, and
`tests/test_live.py::test_dead_client_is_cleaned_up`.

## E5 — Graceful shutdown

`StreamManager.shutdown` (`app/streams.py`) marks every subscriber closed and
queues `SHUTDOWN_SENTINEL`. The loop's sentinel branch flushes buffered events
via `_flush_remaining` and returns cleanly. `app/main.py`'s lifespan calls
`manager.shutdown()` after the app stops.

**Definition of done:** shutdown flushes pending events and exits without
exceptions, idempotently.
Covered by `tests/test_streams.py::test_shutdown_flushes_pending_events`,
`tests/test_streams.py::test_shutdown_is_idempotent_and_quiet`, and
`tests/test_http.py::test_shutdown_is_clean`.
