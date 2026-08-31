"""Shared database helpers: locate the DB file, connect, apply the schema."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

# Repo root: parent of the etl/ package.
ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema.sql"
DEFAULT_DB_PATH = ROOT / "data" / "events.db"


def default_db_path() -> Path:
    """Return the DB path, honoring the FROAM_DB env override."""
    return Path(os.environ.get("FROAM_DB", str(DEFAULT_DB_PATH)))


def init_db(db_path: str | os.PathLike[str] | None = None) -> Path:
    """Create the DB file (if needed) and apply schema.sql. Idempotent."""
    path = Path(db_path) if db_path is not None else default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()
    return path


def connect(db_path: str | os.PathLike[str] | None = None) -> sqlite3.Connection:
    """Open a connection to an initialized database."""
    path = Path(db_path) if db_path is not None else default_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn
