"""SSE streaming tests — AC-5 (spec.md)."""

import asyncio

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from tests.helpers import read_sse_event


async def test_sse_emits_transition_sequence(tmp_path):
    """AC-5: GET /requests/{id}/events streams queued → processing → done."""
    db_path = str(tmp_path / "test.db")
    application = create_app(db_path=db_path, work_delay=0.05, worker_enabled=False)

    async with LifespanManager(application):
        async with AsyncClient(
            transport=ASGITransport(app=application), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/requests", json={"topic": "sse topic", "email": "a@b.com"}
            )
            rid = resp.json()["id"]

            statuses = []
            async with client.stream("GET", f"/requests/{rid}/events") as sresp:
                assert sresp.status_code == 200
                lines = sresp.aiter_lines()

                # First event = current status. Worker is off, so it is 'queued'.
                ev = await asyncio.wait_for(read_sse_event(lines), timeout=3)
                assert ev["status"] == "queued"
                statuses.append(ev["status"])

                # Attach the worker now that the subscriber is listening.
                application.state.worker.start()

                ev = await asyncio.wait_for(read_sse_event(lines), timeout=3)
                assert ev["status"] == "processing"
                statuses.append(ev["status"])

                ev = await asyncio.wait_for(read_sse_event(lines), timeout=3)
                assert ev["status"] == "done"
                assert ev["request"]["result"] is not None
                statuses.append(ev["status"])

            assert statuses == ["queued", "processing", "done"]


async def test_sse_404_for_unknown_request(tmp_path):
    """AC-4: events endpoint for an unknown request → 404."""
    application = create_app(db_path=str(tmp_path / "test.db"), worker_enabled=False)
    async with LifespanManager(application):
        async with AsyncClient(
            transport=ASGITransport(app=application), base_url="http://test"
        ) as client:
            resp = await client.get("/requests/12345/events")
            assert resp.status_code == 404
