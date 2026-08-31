import asyncio
import json

import aiosqlite
import pytest

from app.worker import process_one_job


def _run(coro):
    return asyncio.run(coro)


def test_submit_creates_queued_request(client):
    resp = client.post("/requests", json={"topic": "quantum computing", "email": "a@b.com"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "queued"
    assert body["topic"] == "quantum computing"
    assert body["email"] == "a@b.com"
    assert body["id"] > 0


def test_full_flow_to_done(client, db_path):
    resp = client.post("/requests", json={"topic": "solar panels", "email": "x@y.com"})
    rid = resp.json()["id"]

    assert _run(process_one_job(db_path)) is True

    body = client.get(f"/requests/{rid}").json()
    assert body["status"] == "done"
    assert body["result"]
    assert "solar panels" in body["result"]


def test_sse_emits_exact_transition_sequence(live_client):
    resp = live_client.post("/requests", json={"topic": "sse test", "email": "s@e.com"})
    rid = resp.json()["id"]

    statuses = []
    with live_client.stream("GET", f"/requests/{rid}/events") as stream:
        for line in stream.iter_lines():
            if not line or not line.startswith("data:"):
                continue
            statuses.append(json.loads(line[len("data:"):].strip())["status"])
            if statuses and statuses[-1] in ("done", "failed"):
                break

    assert statuses == ["queued", "processing", "done"]


def test_crash_safety_reclaims_and_completes_exactly_once(client, db_path):
    resp = client.post("/requests", json={"topic": "crash recovery", "email": "c@d.com"})
    rid = resp.json()["id"]

    async def _simulate_crash():
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                "UPDATE requests SET status='processing', updated_at=datetime('now') WHERE id=?",
                (rid,),
            )
            await db.commit()

    _run(_simulate_crash())

    # Restart the worker: a job stuck in 'processing' must be re-claimed and finished.
    assert _run(process_one_job(db_path)) is True

    body = client.get(f"/requests/{rid}").json()
    assert body["status"] == "done"
    assert body["result"]

    async def _count_done():
        async with aiosqlite.connect(db_path) as db:
            cur = await db.execute("SELECT COUNT(*) FROM requests WHERE status='done'")
            (n,) = await cur.fetchone()
            return n

    assert _run(_count_done()) == 1

    # Nothing is left to claim -> no double processing after recovery.
    assert _run(process_one_job(db_path)) is False


def test_worker_does_not_reprocess_done_job_after_restart(client, db_path):
    resp = client.post("/requests", json={"topic": "already done", "email": "d@e.com"})
    rid = resp.json()["id"]

    _run(process_one_job(db_path))
    assert client.get(f"/requests/{rid}").json()["status"] == "done"

    # A restarted worker must not pick up the completed job again.
    assert _run(process_one_job(db_path)) is False
    assert client.get(f"/requests/{rid}").json()["status"] == "done"


@pytest.mark.parametrize(
    "payload",
    [
        {"topic": "", "email": "a@b.com"},
        {"topic": "   ", "email": "a@b.com"},
        {"topic": "ok", "email": ""},
        {"topic": "ok", "email": "   "},
        {"topic": "ok"},
        {"email": "a@b.com"},
        {"topic": None, "email": "a@b.com"},
        {"topic": "ok", "email": None},
    ],
)
def test_invalid_requests_rejected_with_4xx(client, payload):
    resp = client.post("/requests", json=payload)
    assert resp.status_code in (400, 422), (resp.status_code, payload)
