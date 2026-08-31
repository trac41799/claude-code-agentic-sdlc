"""Shared helpers for the test suite."""

from __future__ import annotations

import time


def wait_for_status_http(client, request_id: str, status: str, timeout: float = 5.0) -> dict:
    """Poll GET /requests/{id} until it reaches ``status``."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = client.get(f"/requests/{request_id}")
        if resp.status_code == 200 and resp.json()["status"] == status:
            return resp.json()
        time.sleep(0.02)
    raise AssertionError(
        f"request {request_id} did not reach status {status!r} within {timeout}s"
    )


def wait_for_status_db(request_id: str, status: str, timeout: float = 5.0) -> dict:
    """Poll the database directly until ``request_id`` reaches ``status``."""
    from app import db

    deadline = time.time() + timeout
    while time.time() < deadline:
        row = db.get_request(request_id)
        if row is not None and row["status"] == status:
            return row
        time.sleep(0.02)
    raise AssertionError(
        f"request {request_id} did not reach status {status!r} within {timeout}s"
    )
