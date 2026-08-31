"""FastAPI application for the Research Request Pipeline.

Endpoints:
- POST /requests                     submit {topic, email} -> queued request
- GET  /requests                     list all requests (newest first)
- GET  /requests/{id}                status + result for one request
- GET  /requests/{id}/events         SSE stream of status transitions
- GET  /                             static frontend page
"""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from app import db, worker
from app.bus import event_bus

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TERMINAL_STATUSES = ("done", "failed")


class RequestIn(BaseModel):
    topic: str
    email: str

    @field_validator("topic")
    @classmethod
    def topic_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("topic must not be blank")
        return value

    @field_validator("email")
    @classmethod
    def email_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("email must not be blank")
        return value


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    worker.start_worker()
    try:
        yield
    finally:
        await worker.stop_worker()


app = FastAPI(title="Research Request Pipeline", lifespan=lifespan)


@app.post("/requests")
async def create_request(payload: RequestIn) -> dict:
    return db.create_request(payload.topic, payload.email)


@app.get("/requests")
async def list_requests() -> list[dict]:
    return db.list_requests()


@app.get("/requests/{request_id}")
async def get_request(request_id: str) -> dict:
    row = db.get_request(request_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return row


@app.get("/requests/{request_id}/events")
async def request_events(request_id: str, request: Request) -> StreamingResponse:
    row = db.get_request(request_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Request not found")

    queue = event_bus.subscribe(request_id)

    def encode(status: str) -> str:
        payload = json.dumps({"id": request_id, "status": status})
        return f"event: status\ndata: {payload}\n\n"

    async def event_generator():
        try:
            # Replay the recorded sequence first so late joiners still see every
            # transition (queued -> processing -> done|failed) with no gaps.
            history = event_bus.history(request_id)
            if not history:
                current = db.get_request(request_id)
                history = [current["status"]] if current else []
            for status in history:
                yield encode(status)
                if status in TERMINAL_STATUSES:
                    return
            while True:
                status = await queue.get()
                if status is None:
                    break
                yield encode(status)
                if status in TERMINAL_STATUSES:
                    break
                if await request.is_disconnected():
                    break
        finally:
            event_bus.unsubscribe(request_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
