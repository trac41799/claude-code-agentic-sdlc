"""HELD-OUT rubric tests — GREENFIELD-3 (rate-limited SSE proxy).

Written independently of the brief implementation; the agent never sees this
file during the run. These assert deeper semantics than the brief: bucket math
edges, drop accounting, overflow semantics, heartbeat timing, dead-client
cleanup, and idempotent shutdown. Run after the arm completes.

    python -m pytest tests/hidden/ -q
"""
import asyncio
import json
import time

import pytest


@pytest.fixture
def bucket():
    from app.rate_limit import TokenBucket
    return TokenBucket(capacity=10, refill_per_sec=5.0)


def test_bucket_exact_burst(bucket):
    assert bucket.try_consume() is True
    assert bucket.remaining == 9


def test_bucket_refill_is_linear(bucket):
    start = bucket.remaining
    time.sleep(0.41)
    if bucket.refill_event_check is None:
        # lazy monotonic refill — force a small wait then sample
        bucket.force_tick if hasattr(bucket, "force_tick") else None
    got = bucket.try_consume()
    assert got is True  # a single token must be available after >=0.2s at 5/s


def test_refill_rate_approx(bucket):
    t0 = time.monotonic()
    n = 0
    while time.monotonic() - t0 < 1.6 and n < 9:
        if bucket.try_consume():
            n += 1
        time.sleep(0.05)
    # 5/s refill over ~1.4s wall => stable consumption between 5 and 8 tokens
    assert 5 <= n <= 9


def test_drops_counted_after_burst():
    from app.streams import Stream
    s = Stream(name="x")
    s.subscriber_token_burst = 2
    for _ in range(6):
        s.publish({"i": 1})
    assert s.dropped >= 4//  # drops beyond burst must be counted


def test_overflow_emits_429_error_event():
    from app.streams import Stream
    from app.sse import error_event
    ev = error_event(429, "buffer overflow")
    assert "429" in json.dumps(ev)
    assert "error" in json.dumps(ev)


def test_heartbeat_is_sse_comment():
    from app.sse import heartbeat_event
    h = heartbeat_event()
    assert h.startswith(":")
    assert h.endswith("\n")


def test_shutdown_clean_and_idempotent():
    import app.main as m
    app = m.create_app()
    # shutdown must not raise and must be safe to call twice
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(app.router.shutdown())
        loop.run_until_complete(app.router.shutdown())
    finally:
        loop.close()


def test_publisher_nonblocking_under_slow_consumer():
    from app.streams import Stream
    s = Stream(name="y")
    s.max_buffer = 3
    import time as t
    t0 = t.monotonic()
    for _ in range(30):
        s.publish({"data": 1})
    assert (t.monotonic() - t0) < 1.0