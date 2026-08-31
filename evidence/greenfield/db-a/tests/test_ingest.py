"""Ingest behavior: idempotency by id, and field storage."""
import json
import sqlite3

from etl.ingest import ingest_events

from .helpers import make_event, raw_count, write_events


def test_ingest_inserts_all_rows(db_path, tmp_path):
    path = write_events(tmp_path, [
        make_event("a"),
        make_event("b"),
        make_event("c"),
    ])
    assert ingest_events(db_path, path) == 3
    assert raw_count(db_path) == 3


def test_ingest_dedupes_duplicate_ids(db_path, tmp_path):
    rows = [make_event("a"), make_event("b")]
    path = write_events(tmp_path, rows)

    assert ingest_events(db_path, path) == 2
    assert raw_count(db_path) == 2

    # Re-ingesting the exact same file adds 0 rows.
    assert ingest_events(db_path, path) == 0
    assert raw_count(db_path) == 2

    # A file that overlaps existing ids adds only the new ones.
    path2 = write_events(tmp_path, rows + [make_event("c")])
    assert ingest_events(db_path, path2) == 1
    assert raw_count(db_path) == 3


def test_ingest_stores_all_fields(db_path, tmp_path):
    payload = {"ok": True, "n": 1}
    path = write_events(tmp_path, [make_event("a", payload=payload)])
    ingest_events(db_path, path)

    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT id, kind, occurred_at, tenant, payload FROM raw_events"
        ).fetchone()
    finally:
        conn.close()

    assert row[0] == "a"
    assert row[1] == "click"
    assert row[2] == "2026-01-01T10:00:00"
    assert row[3] == "t1"
    assert json.loads(row[4]) == payload
