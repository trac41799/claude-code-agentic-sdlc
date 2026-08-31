"""Ingest raw events from a JSONL file, idempotent by event id.

Each line is one event object: {"id": ..., "kind": ..., "occurred_at": ...,
"tenant": ..., "payload": ...}. Rows are inserted with INSERT OR IGNORE, so
re-ingesting a file (or a file whose ids partly overlap an already-ingested
one) adds 0 rows for the ids already present.
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

try:
    from .init_db import DEFAULT_DB_PATH  # imported as etl.ingest
except ImportError:  # pragma: no cover - running as a script with etl/ on sys.path
    from init_db import DEFAULT_DB_PATH

BATCH_SIZE = 10_000

_INSERT_SQL = (
    "INSERT OR IGNORE INTO raw_events (id, kind, occurred_at, tenant, payload) "
    "VALUES (?, ?, ?, ?, ?)"
)


def _payload_to_text(payload):
    if payload is None or isinstance(payload, str):
        return payload
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def ingest_events(db_path, jsonl_path):
    """Read a JSONL file and insert its events, ignoring duplicate ids.

    Returns the number of rows actually inserted (events whose id was not
    already present in raw_events). Runs in a single transaction so the whole
    file is applied atomically.
    """
    conn = sqlite3.connect(str(db_path))
    total = 0
    try:
        conn.execute("BEGIN")
        with open(jsonl_path, "r", encoding="utf-8") as f:
            batch = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                evt = json.loads(line)
                batch.append((
                    evt["id"],
                    evt["kind"],
                    evt["occurred_at"],
                    evt["tenant"],
                    _payload_to_text(evt.get("payload")),
                ))
                if len(batch) >= BATCH_SIZE:
                    total += conn.executemany(_INSERT_SQL, batch).rowcount
                    batch = []
            if batch:
                total += conn.executemany(_INSERT_SQL, batch).rowcount
        conn.commit()
    finally:
        conn.close()
    return total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a JSONL file of raw events (idempotent by id)")
    parser.add_argument("jsonl_path", help="path to JSONL file of events")
    parser.add_argument("db_path", nargs="?", default=str(DEFAULT_DB_PATH), help="path to SQLite database file")
    args = parser.parse_args()
    count = ingest_events(args.db_path, args.jsonl_path)
    print(f"Inserted {count} events from {args.jsonl_path}")
    sys.exit(0)
