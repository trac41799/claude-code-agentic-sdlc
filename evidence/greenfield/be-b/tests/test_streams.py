import asyncio
import time

from app.sse import ERROR_SENTINEL, SHUTDOWN_SENTINEL
from app.streams import StreamManager, stream_events, stream_loop


def _run(coro):
    return asyncio.run(coro)


def test_publish_broadcasts_to_subscribers():
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


def test_buffer_overflow_closes_with_error_event():
    async def scenario():
        manager = StreamManager(buffer_size=100)
        stream = manager.get_stream("ov")
        sub = stream.add_subscriber()

        for i in range(100):
            manager.publish("ov", {"n": i})
        assert sub.queue.qsize() == 100

        # 101st published event overflows the bounded buffer.
        manager.publish("ov", {"n": 100})
        assert sub.closed is True
        assert sub.queue.qsize() == 100  # 99 events + error sentinel

        chunks = []
        async for chunk in stream_loop(manager, stream, sub):
            chunks.append(chunk)

        errors = [c for c in chunks if "event: error" in c]
        assert len(errors) == 1
        assert '"status": 429' in errors[0]
        assert "buffer overflow" in errors[0]
        # The loop closed and removed the subscriber.
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
        data = []
        try:
            while True:
                chunk = await asyncio.wait_for(gen.__anext__(), 1.0)
                if chunk.startswith("data:"):
                    data.append(chunk)
                    if len(data) == 10:
                        break
            # Resume once more so the loop consumes the 11th (dropped) event.
            await asyncio.wait_for(gen.__anext__(), 1.0)
            assert len(data) == 10
            assert stream.info()["published"] == 11
            assert stream.info()["dropped"] == 1
        finally:
            await gen.aclose()

    _run(scenario())


def test_publisher_is_non_blocking_on_full_buffer():
    async def scenario():
        manager = StreamManager(buffer_size=100)
        stream = manager.get_stream("slow")
        stream.add_subscriber()
        # No consumer loop draining: every publish hits the bounded queue.
        for i in range(100):
            manager.publish("slow", {"n": i})

        start = time.perf_counter()
        n = 500
        for i in range(n):
            manager.publish("slow", {"n": i})
        elapsed = time.perf_counter() - start

        # 500 synchronous publishes (overflow path) must complete far under 50ms.
        assert elapsed < 0.05
        assert stream.info()["dropped"] == 0

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
        manager.shutdown()
        assert manager.shutting_down is True

    _run(scenario())


def test_dead_subscriber_cleanup_on_generator_close():
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
