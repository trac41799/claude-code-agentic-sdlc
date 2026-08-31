"""Shared fixtures: per-test temp-DB FastAPI app instances.

Each test gets an isolated SQLite database via ``create_app(db_path=...)``.
The worker is started/stopped by the app lifespan (asgi-lifespan).
"""

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest_asyncio.fixture
async def app(tmp_path):
    """App with the background worker enabled, over a temp SQLite DB."""
    application = create_app(db_path=str(tmp_path / "test.db"), work_delay=0.02)
    async with LifespanManager(application):
        yield application


@pytest_asyncio.fixture
async def app_no_worker(tmp_path):
    """App with the worker NOT started — deterministic control for SSE/crash tests."""
    application = create_app(
        db_path=str(tmp_path / "test.db"), work_delay=0.02, worker_enabled=False
    )
    async with LifespanManager(application):
        yield application


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def client_no_worker(app_no_worker):
    async with AsyncClient(transport=ASGITransport(app=app_no_worker), base_url="http://test") as c:
        yield c
