"""Idempotent JSONL event ingestion into raw_events (TDD stub — RED)."""

import json

from .init_db import init_db

_INSERT_SQL = (
    "INSERT OR IGNORE INTO raw_events "
    "(id, kind, occurred_at, tenant, payload) VALUES (?, ?, ?, ?, ?)"
)
_CHUNK_SIZE = 10_000


def ingest(db_path: str, jsonl_path: str) -> int:
    """Read JSONL events from *jsonl_path* and insert them idempotently
    (INSERT OR IGNORE by id) into the SQLite DB at *db_path*.

    Returns the number of rows actually inserted.
    """
    conn = init_db(db_path)
    try:
        before = conn.total_changes
        with open(jsonl_path, "r", encoding="utf-8") as fh:
            batch = []
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                ev = json.loads(line)
                batch.append(
                    (
                        ev["id"],
                        ev["kind"],
                        ev["occurred_at"],
                        ev["tenant"],
                        ev.get("payload"),
                    )
                )
                if len(batch) >= _CHUNK_SIZE:
                    conn.executemany(_INSERT_SQL, batch)
                    batch = []
            if batch:
                conn.executemany(_INSERT_SQL, batch)
        conn.commit()
        return conn.total_changes - before
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
