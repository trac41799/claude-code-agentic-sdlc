"""Crash-safety tests: jobs interrupted mid-processing are recovered and complete exactly once."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app import db
from app.main import app
from tests.util import wait_for_status_db, wait_for_status_http


def test_processing_job_reclaimed_and_completes_once(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUESTS_DB", str(tmp_path / "crash.db"))

    # A previous run submitted a request and claimed it, then crashed mid-job:
    # the row is left in 'processing'.
    db.init_db()
    req_id = db.create_request("crash topic", "c@rash.io")["id"]
    job = db.claim_next_job()
    assert job["id"] == req_id
    assert db.get_request(req_id)["status"] == "processing"

    # "Restart": the lifespan startup recovers crashed jobs and starts the worker.
    with TestClient(app) as client:
        row = wait_for_status_db(req_id, "done")
        assert row["status"] == "done"
        assert db.count_status("done") == 1

    assert db.count_status("done") == 1
    assert db.count_status("processing") == 0


def test_done_job_not_reprocessed_on_restart(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUESTS_DB", str(tmp_path / "restart.db"))

    with TestClient(app) as client:
        resp = client.post("/requests", json={"topic": "stable topic", "email": "s@t.io"})
        req_id = resp.json()["id"]
        first_result = wait_for_status_http(client, req_id, "done")["result"]

    # Restart the app: a 'done' job must stay done, untouched by recovery.
    with TestClient(app) as client:
        row = client.get(f"/requests/{req_id}").json()
        assert row["status"] == "done"
        assert row["result"] == first_result
        assert db.count_status("done") == 1


def test_worker_completes_each_job_exactly_once(client):
    # Multiple queued jobs drain in order, each exactly one done row.
    ids = []
    for topic in ("one", "two", "three"):
        resp = client.post("/requests", json={"topic": topic, "email": "n@once.io"})
        ids.append(resp.json()["id"])
    for req_id in ids:
        wait_for_status_http(client, req_id, "done")
    assert db.count_status("done") == 3
    assert db.count_status("processing") == 0
    assert db.count_status("failed") == 0
