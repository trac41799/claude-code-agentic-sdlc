"""FastAPI service: a rate-limited live event proxy.

POST /streams/{id}/events      internal publisher
GET  /streams/{id}/events      SSE consumer (token bucket + bounded buffer)
GET  /streams/{id}             stream info (published / dropped / subscribers)
"""

import os
from contextlib import asynccontextmanager
from typing import Any

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


def _env_int(name, default):
    value = os.environ.get(name)
    return int(value) if value is not None else default


def _env_float(name, default):
    value = os.environ.get(name)
    return float(value) if value is not None else default


def create_app(
    *,
    capacity: int | None = None,
    refill_rate: float | None = None,
    buffer_size: int | None = None,
    heartbeat: float | None = None,
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
