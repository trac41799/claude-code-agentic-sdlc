"""Shared pytest fixtures for the rate-limited SSE proxy."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app_factory():
    from app.main import create_app

    return create_app


@pytest.fixture
def make_client(app_factory):
    def _make(**kwargs):
        return TestClient(app_factory(**kwargs))

    return _make


@pytest.fixture
def client(make_client):
    with make_client() as c:
        yield c
