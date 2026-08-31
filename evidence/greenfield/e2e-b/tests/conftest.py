import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def app(db_path):
    from app.main import create_app

    return create_app(db_path=db_path, autostart_worker=False)


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def live_app(db_path):
    from app.main import create_app

    return create_app(db_path=db_path, autostart_worker=True)


@pytest.fixture
def live_client(live_app):
    with TestClient(live_app) as c:
        yield c
