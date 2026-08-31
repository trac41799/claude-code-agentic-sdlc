"""End-to-end submission and status-flow tests over HTTP."""

from __future__ import annotations

from tests.util import wait_for_status_http


def test_submit_creates_queued_request(client):
    resp = client.post("/requests", json={"topic": "quantum computing", "email": "a@b.c"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"]
    assert data["topic"] == "quantum computing"
    assert data["email"] == "a@b.c"
    assert data["status"] == "queued"
    assert data["result"] is None


def test_list_includes_submitted(client):
    resp = client.post("/requests", json={"topic": "marine biology", "email": "x@y.z"})
    req_id = resp.json()["id"]
    items = client.get("/requests").json()
    assert any(item["id"] == req_id for item in items)


def test_status_flow_reaches_done(client):
    resp = client.post("/requests", json={"topic": "urban farming", "email": "u@f.io"})
    req_id = resp.json()["id"]
    row = wait_for_status_http(client, req_id, "done")
    assert row["status"] == "done"
    assert row["result"] is not None
    assert "urban farming" in row["result"]


def test_missing_request_returns_404(client):
    resp = client.get("/requests/nonexistent")
    assert resp.status_code == 404
