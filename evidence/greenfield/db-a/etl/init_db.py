"""Apply schema.sql to create the SQLite database (idempotent)."""
import argparse
import sqlite3
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "events.db"


def init_db(db_path=DEFAULT_DB_PATH):
    """Create (if missing) the database at db_path and apply schema.sql.

    Safe to call repeatedly: CREATE TABLE IF NOT EXISTS / CREATE INDEX IF NOT
    EXISTS make it idempotent.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()
    return db_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize the event analytics database from schema.sql")
    parser.add_argument("db_path", nargs="?", default=str(DEFAULT_DB_PATH), help="path to SQLite database file")
    args = parser.parse_args()
    path = init_db(args.db_path)
    print(f"Initialized database at {path}")
    sys.exit(0)
