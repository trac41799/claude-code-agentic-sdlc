"""Asyncio-level tests for StreamManager, the delivery loop, and shutdown."""

import asyncio
import time

from app.sse import ERROR_SENTINEL, SHUTDOWN_SENTINEL
from app.streams import StreamManager, stream_events, stream_loop


def _run(coro):
    return asyncio.run(coro)


def test_publish_broadcasts_to_every_subscriber():
    async def scenario():
        manager = StreamManager()
        stream = manager.get_stream("s")
        sub = stream.add_subscriber()
        manager.publish("s", {"n": 1})
        manager.publish("s", {"n": 2})
        assert stream.published == 2
        assert sub.queue.qsize() == 2
        assert await sub.queue.get() == {"n": 1}
        assert await sub.queue.get() == {"n": 2}

    _run(scenario())


def test_buffer_overflow_closes_connection_with_error_event():
    async def scenario():
        manager = StreamManager(buffer_size=100)
        stream = manager.get_stream("ov")
        sub = stream.add_subscriber()

        for i in range(100):
            manager.publish("ov", {"n": i})
        assert sub.queue.qsize() == 100

        # The 101st event overflows the bounded buffer: the subscriber is
        # marked closed and an error sentinel is queued.
        manager.publish("ov", {"n": 100})
        assert sub.closed is True

        chunks = []
        async for chunk in stream_loop(manager, stream, sub):
            chunks.append(chunk)

        errors = [c for c in chunks if "event: error" in c]
        assert len(errors) == 1
        assert '"status": 429' in errors[0]
        assert "buffer overflow" in errors[0]
        assert stream.info()["subscribers"] == 0

    _run(scenario())


def test_token_bucket_drops_when_empty_and_counts():
    async def scenario():
        manager = StreamManager(heartbeat=0.01)
        stream = manager.get_stream("burst")
        sub = stream.add_subscriber()
        for i in range(11):
            manager.publish("burst", {"n": i})

        gen = stream_loop(manager, stream, sub)
        delivered = []
        try:
            while len(delivered) < 10:
                chunk = await asyncio.wait_for(gen.__anext__(), 1.0)
                if chunk.startswith("data:"):
                    delivered.append(chunk)
            # Consume one more chunk so the 11th (dropped) event is processed.
            await asyncio.wait_for(gen.__anext__(), 1.0)
            assert len(delivered) == 10
            assert stream.info()["published"] == 11
            assert stream.info()["dropped"] == 1
        finally:
            await gen.aclose()

    _run(scenario())


def test_publisher_never_blocks_on_a_slow_consumer():
    async def scenario():
        manager = StreamManager(buffer_size=100)
        stream = manager.get_stream("slow")
        stream.add_subscriber()  # registered but never drained

        for i in range(100):
            manager.publish("slow", {"n": i})  # fill the buffer

        start = time.perf_counter()
        for i in range(500):
            manager.publish("slow", {"n": i})  # all take the overflow path
        elapsed = time.perf_counter() - start

        assert elapsed < 0.05  # 500 synchronous publishes << 50ms budget
        assert stream.info()["dropped"] == 0

    _run(scenario())


def test_heartbeat_emitted_during_silence():
    async def scenario():
        manager = StreamManager(heartbeat=0.02)
        stream = manager.get_stream("hb")
        sub = stream.add_subscriber()

        gen = stream_loop(manager, stream, sub)
        try:
            chunk = await asyncio.wait_for(gen.__anext__(), 1.0)
            assert chunk == ": heartbeat\n\n"
        finally:
            await gen.aclose()

    _run(scenario())


def test_shutdown_flushes_pending_events():
    async def scenario():
        manager = StreamManager()
        stream = manager.get_stream("flush")
        sub = stream.add_subscriber()
        manager.publish("flush", {"a": 1})
        manager.publish("flush", {"a": 2})

        manager.shutdown()
        assert stream.subscribers[sub.id].closed is True

        chunks = []
        async for chunk in stream_loop(manager, stream, sub):
            chunks.append(chunk)

        data = [c for c in chunks if c.startswith("data:")]
        assert len(data) == 2
        assert stream.info()["subscribers"] == 0

    _run(scenario())


def test_shutdown_is_idempotent_and_quiet():
    async def scenario():
        manager = StreamManager()
        manager.get_stream("empty")
        manager.shutdown()
        manager.shutdown()  # second call must not raise
        assert manager.shutting_down is True

    _run(scenario())


def test_closing_the_generator_cleans_up_the_subscriber():
    async def scenario():
        manager = StreamManager(heartbeat=0.05)
        stream = manager.get_stream("dead")

        async def consume():
            async for _ in stream_events(manager, "dead"):
                pass

        task = asyncio.create_task(consume())
        for _ in range(100):
            if stream.info()["subscribers"] == 1:
                break
            await asyncio.sleep(0.005)
        assert stream.info()["subscribers"] == 1

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert stream.info()["subscribers"] == 0

    _run(scenario())


def test_sentinels_are_distinct():
    assert ERROR_SENTINEL is not SHUTDOWN_SENTINEL
