"""Crash-safety tests — AC-7 (spec.md)."""

import asyncio
import sqlite3

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from tests.helpers import wait_for_status


async def test_crash_restart_recovers_job_exactly_once(tmp_path):
    """AC-7: a job left in 'processing' by a crashed worker is re-claimed on
    restart, completes exactly once, and ends in status 'done'."""
    db_path = str(tmp_path / "test.db")

    # Phase 1 — submit a request, then simulate the crash: the worker had
    # claimed the job (status='processing') but died before completing it.
    app1 = create_app(db_path=db_path, work_delay=0.02, worker_enabled=False)
    async with LifespanManager(app1):
        async with AsyncClient(
            transport=ASGITransport(app=app1), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/requests", json={"topic": "crash topic", "email": "a@b.com"}
            )
            rid = resp.json()["id"]
            assert resp.json()["status"] == "queued"

        # Simulate the crashed worker's persisted in-flight state.
        conn = sqlite3.connect(db_path)
        conn.execute(
            "UPDATE requests SET status='processing', attempts=1, "
            "claim_token='dead-beef' WHERE id=?",
            (rid,),
        )
        conn.commit()
        conn.close()

    # Phase 2 — "restart": a fresh app instance (new worker) over the same DB.
    app2 = create_app(db_path=db_path, work_delay=0.02, worker_enabled=True)
    async with LifespanManager(app2):
        async with AsyncClient(
            transport=ASGITransport(app=app2), base_url="http://test"
        ) as client:
            body = await wait_for_status(client, rid, "done")
            assert body["status"] == "done"
            assert body["result"] is not None
            assert "crash topic" in body["result"]

            # Exactly once: a 'done' job is never touched again by the worker.
            await asyncio.sleep(0.15)
            again = (await client.get(f"/requests/{rid}")).json()
            assert again["status"] == "done"
            assert again["result"] == body["result"]


async def test_queued_job_survives_restart(tmp_path):
    """AC-7: a never-claimed 'queued' job is processed after a restart."""
    db_path = str(tmp_path / "test.db")

    app1 = create_app(db_path=db_path, worker_enabled=False)
    async with LifespanManager(app1):
        async with AsyncClient(
            transport=ASGITransport(app=app1), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/requests", json={"topic": "still queued", "email": "a@b.com"}
            )
            rid = resp.json()["id"]

    app2 = create_app(db_path=db_path, work_delay=0.02, worker_enabled=True)
    async with LifespanManager(app2):
        async with AsyncClient(
            transport=ASGITransport(app=app2), base_url="http://test"
        ) as client:
            body = await wait_for_status(client, rid, "done")
            assert body["status"] == "done"
            assert "still queued" in body["result"]
