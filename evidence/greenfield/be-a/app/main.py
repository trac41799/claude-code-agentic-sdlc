"""FastAPI application: the rate-limited live event proxy.

Endpoints
---------
``POST /streams/{stream_id}/events``
    Internal publisher: broadcast a JSON payload to every subscriber on the
    stream. Returns the stream's info document.
``GET /streams/{stream_id}/events``
    SSE consumer: streams the broadcast channel, rate-limited per client by a
    token bucket (10 tokens, 5/s) and a 100-event bounded buffer.
``GET /streams/{stream_id}``
    Stream info: subscriber count, published and dropped event counters.

Configuration
-------------
Passed to :func:`create_app` as keyword arguments, falling back to the
``FROAM_BUCKET_CAPACITY`` / ``FROAM_BUCKET_REFILL`` / ``FROAM_BUFFER_SIZE`` /
``FROAM_HEARTBEAT`` environment variables, then to the defaults.
"""

import os
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from .streams import (
    DEFAULT_BUFFER_SIZE,
    DEFAULT_CAPACITY,
    DEFAULT_HEARTBEAT,
    DEFAULT_REFILL_RATE,
    StreamManager,
    stream_events,
)

_STREAM_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    return int(value) if value is not None else default


def _env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    return float(value) if value is not None else default


def create_app(
    *,
    capacity: Optional[int] = None,
    refill_rate: Optional[float] = None,
    buffer_size: Optional[int] = None,
    heartbeat: Optional[float] = None,
) -> FastAPI:
    manager = StreamManager(
        capacity=_env_int("FROAM_BUCKET_CAPACITY", DEFAULT_CAPACITY) if capacity is None else capacity,
        refill_rate=_env_float("FROAM_BUCKET_REFILL", DEFAULT_REFILL_RATE) if refill_rate is None else refill_rate,
        buffer_size=_env_int("FROAM_BUFFER_SIZE", DEFAULT_BUFFER_SIZE) if buffer_size is None else buffer_size,
        heartbeat=_env_float("FROAM_HEARTBEAT", DEFAULT_HEARTBEAT) if heartbeat is None else heartbeat,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        manager.shutdown()

    app = FastAPI(lifespan=lifespan, title="Rate-limited SSE proxy")
    app.state.manager = manager

    @app.post("/streams/{stream_id}/events")
    async def publish_event(stream_id: str, payload: Any = Body(default=None)):
        manager.publish(stream_id, payload)
        return manager.get_stream(stream_id).info()

    @app.get("/streams/{stream_id}/events")
    async def read_events(stream_id: str):
        return StreamingResponse(
            stream_events(manager, stream_id),
            media_type="text/event-stream",
            headers=_STREAM_HEADERS,
        )

    @app.get("/streams/{stream_id}")
    async def stream_info(stream_id: str):
        stream = manager.get_stream(stream_id, create=False)
        if stream is None:
            raise HTTPException(status_code=404, detail="stream not found")
        return stream.info()

    return app


app = create_app()
