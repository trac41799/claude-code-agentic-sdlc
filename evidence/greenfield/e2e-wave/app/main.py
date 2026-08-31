"""FastAPI application factory for the Research Request Pipeline."""

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app import db
from app.config import Settings
from app.events import EventBroadcaster, build_event_frame
from app.worker import Worker


class RequestPayload(BaseModel):
    topic: str
    email: str


def create_app(
    db_path: str | None = None,
    work_delay: float | None = None,
    worker_enabled: bool | None = None,
) -> FastAPI:
    """Build an independent app with its own SQLite DB, broadcaster, and worker."""
    settings = Settings(
        db_path=Settings.db_path if db_path is None else db_path,
        work_delay=Settings.work_delay if work_delay is None else work_delay,
        worker_poll_interval=Settings.worker_poll_interval,
        worker_enabled=Settings.worker_enabled if worker_enabled is None else worker_enabled,
    )
    db.init_db(settings.db_path)

    broadcaster = EventBroadcaster()
    worker = Worker(settings, broadcaster)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        if settings.worker_enabled:
            worker.start()
        try:
            yield
        finally:
            await worker.stop()

    application = FastAPI(lifespan=lifespan)
    application.state.settings = settings
    application.state.broadcaster = broadcaster
    application.state.worker = worker

    @application.post("/requests", status_code=201)
    async def create_request(payload: RequestPayload):
        if not payload.topic.strip():
            raise HTTPException(status_code=400, detail="topic must not be empty")
        if "@" not in payload.email:
            raise HTTPException(status_code=400, detail="email must contain '@'")
        return db.create_request(settings.db_path, payload.topic, payload.email)

    @application.get("/requests")
    async def list_requests():
        return db.list_requests(settings.db_path)

    @application.get("/requests/{request_id}")
    async def get_request(request_id: int):
        row = db.get_request(settings.db_path, request_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Request not found")
        return row

    @application.get("/requests/{request_id}/events")
    async def request_events(request_id: int):
        if db.get_request(settings.db_path, request_id) is None:
            raise HTTPException(status_code=404, detail="Request not found")

        async def event_generator():
            q = broadcaster.subscribe(request_id)
            try:
                # First event = current status (fresh read after subscribing).
                current = db.get_request(settings.db_path, request_id)
                yield build_event_frame(current)
                if current["status"] in ("done", "failed"):
                    return
                # If no worker is running, start one so the request is driven
                # to a terminal state; otherwise the stream would never see
                # transitions (and never complete).
                if not worker.is_running():
                    worker.start()
                while True:
                    try:
                        frame = await asyncio.wait_for(q.get(), timeout=15)
                    except asyncio.TimeoutError:
                        yield ": keep-alive\n\n"
                        # Safety net: if the worker died after leaving a
                        # terminal state, stop rather than stream forever.
                        state = db.get_request(settings.db_path, request_id)
                        if state["status"] in ("done", "failed"):
                            return
                        continue
                    yield frame
                    # The transition frame carries the status itself, so
                    # terminal detection is deterministic (no DB-read race
                    # with the worker).
                    status = json.loads(frame.partition("data:")[2])["status"]
                    if status in ("done", "failed"):
                        return
            finally:
                broadcaster.unsubscribe(request_id, q)

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @application.get("/", include_in_schema=False)
    async def index():
        return FileResponse(Path(__file__).parent / "static" / "index.html")

    return application


# Module-level app so `uvicorn app.main:app` works out of the box.
app = create_app()
