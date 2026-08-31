"""Stream / Subscriber / Registry behaviour — AC-3 overflow, AC-4 heartbeat,
AC-5 non-blocking publisher, AC-6 clean shutdown, dropped counter surfacing."""

from __future__ import annotations

import asyncio
import time

import pytest

from app.config import Settings
from app.streams import Stream, StreamRegistry

# A bucket permissive enough that it never gates delivery — isolates
# buffer/overflow behaviour from rate-limiting.
PERMISSIVE = dict(bucket_capacity=1_000_000, bucket_refill_rate=1_000_000.0)


@pytest.fixture
def settings() -> Settings:
    return Settings()


async def test_bucket_gates_delivery_and_tracks_dropped(settings: Settings) -> None:
    """AC-1 via streams: default bucket (10/5) delivers 10, drops the rest,
    and the dropped counter is surfaced on the stream info endpoint."""
    stream = Stream("s4", settings=settings)
    sub = stream.subscribe()
    for i in range(15):
        stream.publish({"n": i})

    assert sub.queue.qsize() == 10
    assert sub.dropped == 5
    assert stream.dropped_total == 5

    info = stream.info()
    assert info["stream_id"] == "s4"
    assert info["dropped"] == 5
    assert info["subscribers"] == 1
    assert info["events_published"] == 15


async def test_overflow_closes_connection_and_emits_error(settings: Settings) -> None:
    """AC-3: queue maxsize 100 → 150 events overflow → error frame + close."""
    stream = Stream("s1", settings=settings, queue_size=100, **PERMISSIVE)
    sub = stream.subscribe()
    for i in range(150):
        stream.publish({"n": i})

    assert sub.overflowed is True
    assert sub.queue.qsize() == 100  # bounded, never grew beyond maxsize

    text = "\n".join([line async for line in sub.aiter_sse()])
    assert "event: error" in text
    assert "429" in text


async def test_heartbeat_arrives_during_silence(settings: Settings) -> None:
    """AC-4: with no events, an SSE comment heartbeat arrives after the interval."""
    stream = Stream("s2", settings=settings, heartbeat_seconds=0.05, **PERMISSIVE)
    sub = stream.subscribe()

    lines: list[str] = []

    async def run() -> None:
        async for line in sub.aiter_sse():
            lines.append(line)
            if len(lines) >= 2:
                break

    await asyncio.wait_for(run(), timeout=3.0)
    assert any(line.startswith(":") for line in lines)


async def test_publisher_non_blocking_under_slow_consumer(settings: Settings) -> None:
    """AC-5: publishing into a full buffer never blocks (synchronous path)."""
    stream = Stream("s3", settings=settings, queue_size=100, **PERMISSIVE)
    sub = stream.subscribe()
    for i in range(100):
        stream.publish({"n": i})
    assert sub.queue.qsize() == 100

    start = time.perf_counter()
    for i in range(2000):
        stream.publish({"n": i})
    elapsed = time.perf_counter() - start

    assert sub.overflowed is True
    # 2000 publishes at ≪10ms each; bound is generous for loaded CI.
    assert elapsed < 0.5


async def test_shutdown_flushes_pending_events_and_exits_cleanly(
    settings: Settings,
) -> None:
    """AC-6: shutdown closes subscribers, flushes queued events, no exceptions."""
    registry = StreamRegistry(settings=settings)
    stream = registry.get_or_create("s5")
    sub = stream.subscribe()
    for i in range(5):
        stream.publish({"n": i})

    collected: list[str] = []

    async def consume() -> None:
        async for line in sub.aiter_sse():
            collected.append(line)

    task = asyncio.create_task(consume())
    await asyncio.sleep(0.01)  # let the consumer start draining
    await registry.shutdown_all()
    await asyncio.wait_for(task, timeout=3.0)

    data_lines = [line for line in collected if line.startswith("data:")]
    assert len(data_lines) == 5  # pending events flushed before closing
    assert registry.get("s5") is None  # stream removed from the registry


async def test_disconnect_cleans_up_subscription(settings: Settings) -> None:
    """Dead-client detection: a disconnected consumer is removed and its
    resources released."""
    stream = Stream("s7", settings=settings, heartbeat_seconds=0.05)
    sub = stream.subscribe()
    assert len(stream.subscribers) == 1

    async def disconnected() -> bool:
        return True

    lines = [line async for line in sub.aiter_sse(is_disconnected=disconnected)]
    assert lines == []
    assert len(stream.subscribers) == 0


async def test_unsubscribe_removes_subscriber(settings: Settings) -> None:
    stream = Stream("s6", settings=settings)
    sub = stream.subscribe()
    assert len(stream.subscribers) == 1
    stream.unsubscribe(sub)
    assert len(stream.subscribers) == 0
