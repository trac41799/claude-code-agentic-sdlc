"""Pytest setup: put the project root and etl/ on sys.path, expose db_path fixture."""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "etl"))

from etl.init_db import init_db  # noqa: E402


@pytest.fixture()
def db_path(tmp_path):
    """A fresh, initialized SQLite database for each test."""
    return init_db(tmp_path / "test.db")
