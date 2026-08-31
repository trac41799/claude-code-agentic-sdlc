"""Ingest JSONL events into raw_events.

Idempotent by event id: a row whose id already exists is skipped
(INSERT OR IGNORE), so re-ingesting a file adds 0 rows. Returns the
number of newly inserted rows.

Usage:
    python -m etl.ingest events.jsonl            # or: python etl/ingest.py events.jsonl
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

if __package__ in (None, ""):  # allow `python etl/ingest.py`
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.db import connect, init_db  # noqa: E402

_BATCH = 5_000

_INSERT = (
    "INSERT OR IGNORE INTO raw_events (id, kind, occurred_at, tenant, payload) "
    "VALUES (?, ?, ?, ?, ?)"
)


def ingest(conn: sqlite3.Connection, jsonl_path: str | Path) -> int:
    """Insert every event from the JSONL file, skipping duplicate ids.

    Returns the number of rows actually inserted.
    """
    cur = conn.cursor()
    inserted = 0
    batch: list[tuple[str, str, str, str, str | None]] = []

    with open(jsonl_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            payload = ev.get("payload")
            if payload is not None and not isinstance(payload, str):
                payload = json.dumps(payload, separators=(",", ":"))
            batch.append((ev["id"], ev["kind"], ev["occurred_at"], ev["tenant"], payload))
            if len(batch) >= _BATCH:
                cur.executemany(_INSERT, batch)
                inserted += cur.rowcount
                batch.clear()

    if batch:
        cur.executemany(_INSERT, batch)
        inserted += cur.rowcount

    conn.commit()
    return inserted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest a JSONL file of events (idempotent by id).")
    parser.add_argument("jsonl_path", help="Path to the events file (.jsonl)")
    parser.add_argument(
        "--db",
        default=None,
        help="SQLite DB path (default: data/events.db or $FROAM_DB)",
    )
    args = parser.parse_args(argv)

    init_db(args.db)
    conn = connect(args.db)
    try:
        inserted = ingest(conn, args.jsonl_path)
    finally:
        conn.close()

    print(f"inserted {inserted} events")
    return 0


if __name__ == "__main__":
    sys.exit(main())
