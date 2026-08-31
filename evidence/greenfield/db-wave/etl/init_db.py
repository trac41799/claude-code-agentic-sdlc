"""Database initialisation: apply schema.sql to a SQLite file."""

import sqlite3
from pathlib import Path

# Repo-root schema file, located one level above this package.
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"


def init_db(db_path: str) -> sqlite3.Connection:
    """Connect to (creating if needed) the SQLite DB at *db_path* and apply
    ``schema.sql``.

    Returns the open connection with the schema applied. The caller owns the
    connection and is responsible for closing it.
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    except Exception:
        conn.close()
        raise
    return conn
