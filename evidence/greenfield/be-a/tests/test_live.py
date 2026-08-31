"""End-to-end tests over a real uvicorn socket (true SSE streaming)."""

import asyncio
import json

import httpx

from app.main import create_app
from tests.live import UvicornServer


def _run(coro):
    return asyncio.run(coro)


async def _read_data(it, n, timeout=5.0):
    """Pull up to ``n`` ``data:`` lines from a shared SSE line iterator.

    Uses ``anext`` (not ``async for``) so an early stop does not close the
    underlying response stream.
    """
    lines = []
    async with asyncio.timeout(timeout):
        while len(lines) < n:
            line = await anext(it)
            if line.startswith("data:"):
                lines.append(line)
    return lines


async def _wait_for(predicate, timeout=3.0, interval=0.02):
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if predicate():
            return True
        await asyncio.sleep(interval)
    return predicate()


def test_burst_of_10_passes_then_11th_is_dropped():
    async def scenario():
        server = UvicornServer(create_app())
        port = server.start()
        try:
            base = f"http://127.0.0.1:{port}/streams/burst"
            async with httpx.AsyncClient(timeout=5.0) as client:
                async with client.stream("GET", f"{base}/events") as resp:
                    assert resp.status_code == 200
                    for i in range(11):
                        r = await client.post(f"{base}/events", json={"n": i})
                        assert r.status_code == 200
                    await asyncio.sleep(0.1)  # let the server drain the burst
                    it = resp.aiter_lines()
                    delivered = await _read_data(it, 10)
                    assert len(delivered) == 10
                    assert json.loads(delivered[0][len("data:"):]) == {"n": 0}
                info = (await client.get(base)).json()
                assert info["published"] == 11
                assert info["dropped"] == 1
        finally:
            server.stop()

    _run(scenario())


def test_refill_approximates_5_per_second():
    async def scenario():
        server = UvicornServer(create_app())
        port = server.start()
        try:
            base = f"http://127.0.0.1:{port}/streams/refill"
            async with httpx.AsyncClient(timeout=5.0) as client:
                async with client.stream("GET", f"{base}/events") as resp:
                    assert resp.status_code == 200
                    it = resp.aiter_lines()

                    # First burst of 10 -> all delivered, bucket drained.
                    for i in range(10):
                        await client.post(f"{base}/events", json={"n": i})
                    first = await _read_data(it, 10)
                    assert len(first) == 10

                    # 11th event -> bucket empty, dropped.
                    await client.post(f"{base}/events", json={"n": 10})

                    # ~2s at 5/s refills the bucket to its 10-token cap.
                    await asyncio.sleep(2.1)
                    for i in range(10):
                        await client.post(f"{base}/events", json={"n": 100 + i})
                    second = await _read_data(it, 10)
                    assert len(second) == 10
                info = (await client.get(base)).json()
                assert info["published"] == 21
                assert info["dropped"] == 1
        finally:
            server.stop()

    _run(scenario())


def test_heartbeat_during_silence():
    async def scenario():
        server = UvicornServer(create_app(heartbeat=0.1))
        port = server.start()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                async with client.stream(
                    "GET", f"http://127.0.0.1:{port}/streams/hb/events"
                ) as resp:
                    assert resp.status_code == 200
                    async for line in resp.aiter_lines():
                        if line.startswith(": "):
                            assert "heartbeat" in line
                            break
        finally:
            server.stop()

    _run(scenario())


def test_dead_client_is_cleaned_up():
    async def scenario():
        app = create_app(heartbeat=0.05)
        server = UvicornServer(app)
        port = server.start()
        manager = app.state.manager
        try:
            base = f"http://127.0.0.1:{port}/streams/cleanup"
            async with httpx.AsyncClient(timeout=5.0) as client:
                async with client.stream("GET", f"{base}/events") as resp:
                    assert resp.status_code == 200
                    ok = await _wait_for(
                        lambda: manager.get_stream("cleanup", create=False) is not None
                        and manager.get_stream("cleanup").info()["subscribers"] == 1
                    )
                    assert ok, "subscriber was never registered"

                # Leaving the stream context closes the socket; the server must
                # notice and tear the subscriber down (no lingering resources).
                ok = await _wait_for(
                    lambda: manager.get_stream("cleanup", create=False) is None
                    or manager.get_stream("cleanup").info()["subscribers"] == 0
                )
                assert ok, "subscriber was not cleaned up after disconnect"
        finally:
            server.stop()

    _run(scenario())


def test_shutdown_is_clean_over_http():
    async def scenario():
        server = UvicornServer(create_app())
        port = server.start()
        try:
            base = f"http://127.0.0.1:{port}/streams/sd"
            async with httpx.AsyncClient(timeout=5.0) as client:
                for i in range(3):
                    assert (await client.post(f"{base}/events", json={"n": i})).status_code == 200
                assert (await client.get(base)).status_code == 200
            # Stop with no open streams: graceful exit must not raise.
            server.stop()
            assert server.thread is not None and not server.thread.is_alive()
        finally:
            server.stop()

    _run(scenario())
