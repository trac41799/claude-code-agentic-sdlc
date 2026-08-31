"""SSE stream tests: the transition sequence must be exactly queued -> processing -> done."""

from __future__ import annotations

import json

from tests.util import wait_for_status_http


def _read_statuses(client, request_id: str) -> list[str]:
    statuses: list[str] = []
    with client.stream("GET", f"/requests/{request_id}/events") as stream:
        for line in stream.iter_lines():
            if line.startswith("data:"):
                payload = json.loads(line[len("data:"):].strip())
                statuses.append(payload["status"])
                if payload["status"] in ("done", "failed"):
                    break
    return statuses


def test_sse_emits_full_transition_sequence(client):
    resp = client.post("/requests", json={"topic": "deep sea", "email": "d@sea.io"})
    req_id = resp.json()["id"]
    assert _read_statuses(client, req_id) == ["queued", "processing", "done"]


def test_sse_replays_history_for_finished_request(client):
    resp = client.post("/requests", json={"topic": "history replay", "email": "h@r.io"})
    req_id = resp.json()["id"]
    wait_for_status_http(client, req_id, "done")
    assert _read_statuses(client, req_id) == ["queued", "processing", "done"]


def test_sse_unknown_request_returns_404(client):
    resp = client.get("/requests/does-not-exist/events")
    assert resp.status_code == 404
