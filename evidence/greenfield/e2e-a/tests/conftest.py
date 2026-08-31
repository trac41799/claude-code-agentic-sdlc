from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """An HTTP client against a fresh temp DB with the worker running."""
    monkeypatch.setenv("REQUESTS_DB", str(tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client
