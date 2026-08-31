"""API tests — endpoints, info/dropped counter, lifespan shutdown, and
end-to-end SSE streaming against a real in-process uvicorn server."""

from __future__ import annotations

import asyncio
import contextlib
from typing import AsyncIterator

import httpx
import pytest
import uvicorn
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.streams import StreamRegistry


# ---------------------------------------------------------------------------
# In-process real server (ASGI transports buffer full bodies; an infinite SSE
# stream needs a real socket).
# ---------------------------------------------------------------------------


class _Server:
    def __init__(self, app) -> None:
        config = uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning")
        self.server = uvicorn.Server(config)
        self.server.install_signal_handlers = lambda: None
        self.port: int | None = None
        self._task: asyncio.Task | None = None

    async def __aenter__(self) -> "_Server":
        self._task = asyncio.create_task(self.server.serve())
        for _ in range(200):
            if self.server.started:
                break
            await asyncio.sleep(0.01)
        assert self.server.started, "uvicorn did not start"
        self.port = self.server.servers[0].sockets[0].getsockname()[1]
        return self

    async def __aexit__(self, *exc) -> None:
        self.server.should_exit = True
        if self._task is not None:
            await asyncio.wait_for(self._task, timeout=5.0)

    @property
    def url(self) -> str:
        assert self.port is not None
        return f"http://127.0.0.1:{self.port}"


async def first_matching(
    resp: httpx.Response, predicate, timeout: float = 5.0
) -> str | None:
    """Return the first SSE line matching ``predicate``, else None on timeout."""

    async def run() -> str | None:
        async for line in resp.aiter_lines():
            if predicate(line):
                return line
        return None

    return await asyncio.wait_for(run(), timeout=timeout)


@pytest.fixture
def fast_settings() -> Settings:
    """Fast heartbeat + permissive bucket so SSE tests run quickly."""
    return Settings(
        heartbeat_seconds=0.1,
        bucket_capacity=10_000,
        bucket_refill_rate=10_000.0,
    )


@pytest.fixture
def fast_registry(fast_settings: Settings) -> StreamRegistry:
    return StreamRegistry(settings=fast_settings)


# ---------------------------------------------------------------------------
# Sync TestClient tests (non-streaming requests).
# ---------------------------------------------------------------------------


def test_post_publishes_and_returns_202(registry: StreamRegistry) -> None:
    with TestClient(create_app(registry=registry)) as client:
        resp = client.post("/streams/demo/events", json={"type": "tick", "n": 1})
        assert resp.status_code == 202
        body = resp.json()
        assert body["status"] == "accepted"
        assert body["events_published"] == 1
        assert registry.get("demo") is not None


def test_post_invalid_json_returns_400(registry: StreamRegistry) -> None:
    with TestClient(create_app(registry=registry)) as client:
        resp = client.post(
            "/streams/demo/events",
            content=b"not json",
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 400
        assert "invalid" in resp.json()["error"]


def test_info_endpoint_surfaces_dropped_counter(registry: StreamRegistry) -> None:
    with TestClient(create_app(registry=registry)) as client:
        client.post("/streams/demo/events", json={"a": 1})
        stream = registry.get("demo")
        assert stream is not None
        sub = stream.subscribe()
        # 13 publishes against a default bucket (10/5): 10 delivered, 3 dropped.
        for i in range(13):
            stream.publish({"n": i})
        assert sub.dropped == 3

        resp = client.get("/streams/demo")
        assert resp.status_code == 200
        info = resp.json()
        assert info["stream_id"] == "demo"
        assert info["dropped"] == 3
        assert info["events_published"] == 14  # POST + 13 direct publishes


def test_info_404_for_missing_stream(registry: StreamRegistry) -> None:
    with TestClient(create_app(registry=registry)) as client:
        resp = client.get("/streams/nope")
        assert resp.status_code == 404


def test_lifespan_shutdown_cleans_registry(registry: StreamRegistry) -> None:
    """AC-6 at the app level: shutdown drains streams, no exception on exit."""
    with TestClient(create_app(registry=registry)) as client:
        client.post("/streams/demo/events", json={"a": 1})
        assert registry.get("demo") is not None
    assert registry.get("demo") is None


# ---------------------------------------------------------------------------
# Async end-to-end SSE tests against a real uvicorn server.
# ---------------------------------------------------------------------------


async def test_sse_delivers_published_event(fast_registry: StreamRegistry) -> None:
    app = create_app(registry=fast_registry)
    async with _Server(app) as server:
        async with httpx.AsyncClient(base_url=server.url) as client:
            async with client.stream("GET", "/streams/demo/events") as resp:
                assert resp.status_code == 200
                assert resp.headers["content-type"].startswith("text/event-stream")

                # Wait until the consumer is subscribed before publishing.
                for _ in range(100):
                    stream = fast_registry.get("demo")
                    if stream and stream.subscribers:
                        break
                    await asyncio.sleep(0.01)
                assert fast_registry.get("demo") is not None

                post = await client.post("/streams/demo/events", json={"n": 42})
                assert post.status_code == 202

                line = await first_matching(resp, lambda l: l.startswith("data:"))
                assert line is not None
                assert '"n": 42' in line


async def test_sse_heartbeat_during_silence(fast_registry: StreamRegistry) -> None:
    """AC-4 end-to-end: heartbeat comment arrives while no events flow."""
    app = create_app(registry=fast_registry)
    async with _Server(app) as server:
        async with httpx.AsyncClient(base_url=server.url) as client:
            async with client.stream("GET", "/streams/hb/events") as resp:
                line = await first_matching(resp, lambda l: l.startswith(":"))
                assert line is not None
                assert "heartbeat" in line


async def test_sse_overflow_emits_error_and_closes(
    fast_registry: StreamRegistry,
) -> None:
    """AC-3 end-to-end: an overflowed subscriber gets the 429 error frame."""
    app = create_app(registry=fast_registry)
    async with _Server(app) as server:
        async with httpx.AsyncClient(base_url=server.url) as client:
            async with client.stream("GET", "/streams/ov/events") as resp:
                stream = None
                for _ in range(100):
                    stream = fast_registry.get("ov")
                    if stream and stream.subscribers:
                        break
                    await asyncio.sleep(0.01)
                assert stream is not None
                sub = next(iter(stream.subscribers.values()))
                # Simulate the slow-consumer case: the publisher overflowed the
                # bounded buffer. Deterministic regardless of socket buffering.
                sub.mark_overflow()

                # The error event is spec-standard SSE: an "event: error" line
                # followed by a "data:" line carrying the 429 status. Collect
                # lines until both markers arrive.
                text = ""

                async def collect() -> None:
                    nonlocal text
                    async for line in resp.aiter_lines():
                        text += line + "\n"
                        if "event: error" in text and "429" in text:
                            return

                await asyncio.wait_for(collect(), timeout=5.0)
                assert "event: error" in text
                assert "429" in text
