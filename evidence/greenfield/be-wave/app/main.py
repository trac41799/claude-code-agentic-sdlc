"""FastAPI application for the rate-limited live event proxy.

Wave 2 (API): publisher endpoint, SSE consumer endpoint, info endpoint, and
lifespan-managed registry shutdown.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.config import Settings
from app.streams import StreamRegistry


def create_app(
    registry: StreamRegistry | None = None,
    settings: Settings | None = None,
) -> FastAPI:
    """Build the FastAPI app with publisher, SSE consumer and info endpoints."""
    registry = registry or StreamRegistry(settings=settings or Settings())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            # Graceful shutdown: drain/flush every stream, no exceptions on exit.
            await registry.shutdown_all()

    app = FastAPI(title="Rate-limited live event proxy", lifespan=lifespan)

    @app.post("/streams/{stream_id}/events")
    async def publish_event(stream_id: str, request: Request):
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                status_code=400, content={"error": "invalid JSON body"}
            )
        stream = registry.get_or_create(stream_id)
        result = stream.publish(body)
        return JSONResponse(
            status_code=202,
            content={
                "status": "accepted",
                "stream_id": stream_id,
                "events_published": stream.events_published,
                "delivered": result.delivered,
                "dropped": result.dropped,
                "overflowed": result.overflowed,
            },
        )

    @app.get("/streams/{stream_id}/events")
    async def stream_events(stream_id: str, request: Request):
        stream = registry.get_or_create(stream_id)
        sub = stream.subscribe()
        return StreamingResponse(
            sub.aiter_sse(is_disconnected=request.is_disconnected),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.get("/streams/{stream_id}")
    async def stream_info(stream_id: str):
        stream = registry.get(stream_id)
        if stream is None:
            return JSONResponse(
                status_code=404, content={"error": "stream not found"}
            )
        return stream.info()

    return app


app = create_app()  # module-level instance for uvicorn
