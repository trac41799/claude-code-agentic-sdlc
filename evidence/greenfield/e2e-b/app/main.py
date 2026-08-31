import asyncio
import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .db import (
    db_path_from_env,
    create_request,
    get_events,
    get_request,
    init_db,
    list_requests,
    open_db,
)
from .sse import make_bus, subscribe, unsubscribe
from .worker import worker_loop


class RequestIn(BaseModel):
    topic: str
    email: str


def _sse_event(request_id, status, result=None, error=None):
    data = {"request_id": request_id, "status": status}
    if result is not None:
        data["result"] = result
    if error is not None:
        data["error"] = error
    return f"event: status\ndata: {json.dumps(data)}\n\n"


def create_app(db_path=None, autostart_worker=True):
    db_path = os.path.abspath(db_path) if db_path else os.path.abspath(db_path_from_env())
    bus = make_bus()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await init_db(db_path)
        task = None
        if autostart_worker:
            task = asyncio.create_task(worker_loop(db_path, bus))
        yield
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    app = FastAPI(lifespan=lifespan, title="Research Request Pipeline")
    app.state.db_path = db_path
    app.state.bus = bus

    @app.post("/requests", status_code=201)
    async def post_request(payload: RequestIn):
        topic = payload.topic.strip()
        email = payload.email.strip()
        if not topic or not email:
            raise HTTPException(status_code=400, detail="topic and email are required")
        async with open_db(db_path) as db:
            rid = await create_request(db, topic, email, bus)
        async with open_db(db_path) as db:
            return await get_request(db, rid)

    @app.get("/requests/{request_id}")
    async def read_request(request_id: int):
        async with open_db(db_path) as db:
            req = await get_request(db, request_id)
        if req is None:
            raise HTTPException(status_code=404, detail="request not found")
        return req

    @app.get("/requests")
    async def read_requests():
        async with open_db(db_path) as db:
            return await list_requests(db)

    @app.get("/requests/{request_id}/events")
    async def request_events(request_id: int):
        async with open_db(db_path) as db:
            req = await get_request(db, request_id)
        if req is None:
            raise HTTPException(status_code=404, detail="request not found")

        async def event_stream():
            q = subscribe(bus, request_id)
            sent = set()
            try:
                async with open_db(db_path) as db:
                    events = await get_events(db, request_id)
                for ev in events:
                    st = ev["status"]
                    if st in sent:
                        continue
                    sent.add(st)
                    yield _sse_event(request_id, st)
                    if st in ("done", "failed"):
                        return

                while True:
                    try:
                        st = await asyncio.wait_for(q.get(), timeout=15.0)
                    except asyncio.TimeoutError:
                        yield ": keepalive\n\n"
                        continue
                    if st in sent:
                        continue
                    sent.add(st)
                    result = error = None
                    async with open_db(db_path) as db:
                        cur = await get_request(db, request_id)
                        if cur is not None:
                            result = cur.get("result")
                            error = cur.get("error")
                    yield _sse_event(request_id, st, result=result, error=error)
                    if st in ("done", "failed"):
                        return
            finally:
                unsubscribe(bus, request_id, q)

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def index():
        return FileResponse(os.path.join(static_dir, "index.html"))

    return app


app = create_app()
