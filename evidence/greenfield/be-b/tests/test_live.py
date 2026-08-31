"""End-to-end tests over a real uvicorn socket (true SSE streaming)."""

import asyncio
import json

import httpx
import pytest

from app.main import create_app
from tests.live import UvicornServer


def _run(coro):
    return asyncio.run(coro)


async def _read_data(it, n, timeout=5.0):
    """Pull up to n `data:` lines from a shared SSE line iterator.

    Uses ``anext`` rather than ``async for`` so an early stop does not close
    the underlying response stream.
    """
    lines = []
    async with asyncio.timeout(timeout):
        while len(lines) < n:
            line = await anext(it)
            if line.startswith("data:"):
                lines.append(line)
    return lines


async def _wait_for(predicate, timeout=3.0, interval=0.02):
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        if predicate():
            return True
        await asyncio.sleep(interval)
    return predicate()


def test_burst_10_passes_11th_dropped(app_factory):
    async def scenario():
        server = UvicornServer(app_factory())
        port = server.start()
        try:
            base = f"http://127.0.0.1:{port}/streams/burst"
            async with httpx.AsyncClient(timeout=5.0) as client:
                async with client.stream("GET", f"{base}/events") as resp:
                    assert resp.status_code == 200
                    for i in range(11):
                        r = await client.post(f"{base}/events", json={"n": i})
                        assert r.status_code == 200
                    await asyncio.sleep(0.1)  # let the server process the burst
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


def test_refill_approximates_5_per_second(app_factory):
    async def scenario():
        server = UvicornServer(app_factory())
        port = server.start()
        try:
            base = f"http://127.0.0.1:{port}/streams/refill"
            async with httpx.AsyncClient(timeout=5.0) as client:
                async with client.stream("GET", f"{base}/events") as resp:
                    assert resp.status_code == 200
                    it = resp.aiter_lines()
                    # First burst of 10 -> all delivered.
                    for i in range(10):
                        await client.post(f"{base}/events", json={"n": i})
                    first = await _read_data(it, 10)
                    assert len(first) == 10

                    # 11th event -> bucket empty, dropped.
                    await client.post(f"{base}/events", json={"n": 10})

                    # Wait ~2s: 5/sec refill gives ~10 tokens (capped at 10).
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


def test_heartbeat_during_silence(app_factory):
    async def scenario():
        server = UvicornServer(app_factory(heartbeat=0.1))
        port = server.start()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                async with client.stream("GET", f"http://127.0.0.1:{port}/streams/hb/events") as resp:
                    assert resp.status_code == 200
                    async for line in resp.aiter_lines():
                        if line.startswith(": "):
                            assert "heartbeat" in line
                            break
        finally:
            server.stop()

    _run(scenario())


def test_dead_client_cleanup(app_factory):
    async def scenario():
        app = app_factory(heartbeat=0.05)
        server = UvicornServer(app)
        port = server.start()
        manager = app.state.manager
        try:
            base = f"http://127.0.0.1:{port}/streams/cleanup"
            async with httpx.AsyncClient(timeout=5.0) as client:
                stream_url = f"{base}/events"
                async with client.stream("GET", stream_url) as resp:
                    assert resp.status_code == 200
                    ok = await _wait_for(
                        lambda: manager.get_stream("cleanup", create=False) is not None
                        and manager.get_stream("cleanup").info()["subscribers"] == 1
                    )
                    assert ok, "subscriber was never registered"

                # Leaving the stream context closes the socket; the server must
                # notice and tear the subscriber down (no lingering tasks).
                ok = await _wait_for(
                    lambda: manager.get_stream("cleanup", create=False) is None
                    or manager.get_stream("cleanup").info()["subscribers"] == 0
                )
                assert ok, "subscriber was not cleaned up after disconnect"
        finally:
            server.stop()

    _run(scenario())


def test_shutdown_is_clean_over_http(app_factory):
    async def scenario():
        server = UvicornServer(app_factory())
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
