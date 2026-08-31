"""API contract tests — AC-1..AC-4, AC-8, FR-4 (see spec.md)."""

import asyncio

from tests.helpers import wait_for_status


async def test_submit_creates_queued_request(client):
    """AC-1: POST /requests creates a request with status 'queued'."""
    resp = await client.post(
        "/requests", json={"topic": "quantum error correction", "email": "a@b.com"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] >= 1
    assert body["topic"] == "quantum error correction"
    assert body["email"] == "a@b.com"
    assert body["status"] == "queued"
    assert body["result"] is None


async def test_submit_to_done_flow(client):
    """AC-1 + AC-6: a submitted request is processed by the worker to 'done',
    with a result echoing the topic."""
    resp = await client.post(
        "/requests", json={"topic": "coral reef resilience", "email": "a@b.com"}
    )
    rid = resp.json()["id"]

    get = await client.get(f"/requests/{rid}")
    assert get.status_code == 200
    assert get.json()["status"] == "queued"

    body = await wait_for_status(client, rid, "done")
    assert body["status"] == "done"
    assert body["result"] is not None
    assert "coral reef resilience" in body["result"]


async def test_invalid_topic_rejected(client):
    """AC-2: empty / whitespace-only topic is rejected with 400."""
    resp = await client.post("/requests", json={"topic": "", "email": "a@b.com"})
    assert resp.status_code == 400

    resp = await client.post("/requests", json={"topic": "   ", "email": "a@b.com"})
    assert resp.status_code == 400


async def test_invalid_email_rejected(client):
    """AC-3: email without '@' is rejected with 400."""
    resp = await client.post("/requests", json={"topic": "ok", "email": "not-an-email"})
    assert resp.status_code == 400


async def test_missing_fields_rejected(client):
    """AC-1/AC-2: missing topic field → 422 (Pydantic)."""
    resp = await client.post("/requests", json={"email": "a@b.com"})
    assert resp.status_code == 422


async def test_get_missing_request_returns_404(client):
    """AC-4: unknown request id → 404."""
    resp = await client.get("/requests/99999")
    assert resp.status_code == 404


async def test_list_requests(client):
    """FR-4: GET /requests lists all requests, oldest first."""
    await client.post("/requests", json={"topic": "first", "email": "a@b.com"})
    await client.post("/requests", json={"topic": "second", "email": "b@b.com"})
    resp = await client.get("/requests")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    assert [r["topic"] for r in body] == ["first", "second"]


async def test_frontend_served(client):
    """AC-8: GET / serves the static frontend page."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Research" in resp.text


async def test_submit_does_not_block_on_worker(client_no_worker):
    """AC-1: submission returns immediately (queued) even with the worker off."""
    resp = await client_no_worker.post(
        "/requests", json={"topic": "no worker", "email": "a@b.com"}
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "queued"
