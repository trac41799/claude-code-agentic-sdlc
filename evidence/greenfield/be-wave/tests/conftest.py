"""Shared fixtures for the GREENFIELD-3 test suite."""

from __future__ import annotations

import pytest

from app.config import Settings
from app.streams import StreamRegistry


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
def registry(settings: Settings) -> StreamRegistry:
    return StreamRegistry(settings=settings)


@pytest.fixture
def app(registry: StreamRegistry):
    """FastAPI app backed by the shared registry fixture."""
    from app.main import create_app

    return create_app(registry=registry)
