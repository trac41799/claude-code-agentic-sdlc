"""Tests for etl.ingest — idempotent JSONL ingestion (spec AC-3)."""

import json
import sqlite3

from etl.ingest import ingest


def _write_jsonl(path, events):
    with open(path, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")


def _event(i, day="2026-08-30"):
    return {
        "id": f"evt-{i}",
        "kind": "page_view" if i % 2 == 0 else "click",
        "occurred_at": f"{day}T12:0{i % 10}:00Z",
        "tenant": "acme" if i % 3 == 0 else "globex",
        "payload": json.dumps({"seq": i}),
    }


def _count(db_path):
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM raw_events").fetchone()[0]


def test_ingest_returns_inserted_count_on_fresh_file(tmp_path):
    """AC-3: ingest returns the number of rows actually inserted."""
    db = tmp_path / "events.db"
    src = tmp_path / "events.jsonl"
    _write_jsonl(src, [_event(i) for i in range(5)])

    inserted = ingest(str(db), str(src))

    assert inserted == 5
    assert _count(str(db)) == 5


def test_ingest_dedupes_duplicate_ids(tmp_path):
    """AC-3: duplicate ids within a file are inserted once; re-ingesting the
    same file inserts nothing."""
    db = tmp_path / "events.db"
    events = [_event(i) for i in range(5)]
    # evt-0 and evt-1 each appear twice -> 5 unique ids in a 7-line file.
    events += [events[0], events[1]]
    src = tmp_path / "events.jsonl"
    _write_jsonl(src, events)

    inserted = ingest(str(db), str(src))
    assert inserted == 5
    assert _count(str(db)) == 5

    # Re-ingest the same file: everything is ignored.
    assert ingest(str(db), str(src)) == 0
    assert _count(str(db)) == 5


def test_ingest_appends_new_ids_to_existing_db(tmp_path):
    """AC-3: ingesting new ids into an already-populated db only adds the new
    ones."""
    db = tmp_path / "events.db"
    _write_jsonl(tmp_path / "a.jsonl", [_event(i) for i in range(3)])
    ingest(str(db), str(tmp_path / "a.jsonl"))

    # Overlapping ids (0,1) plus new ones (3,4).
    _write_jsonl(tmp_path / "b.jsonl", [_event(i) for i in range(5)])
    inserted = ingest(str(db), str(tmp_path / "b.jsonl"))

    assert inserted == 2
    assert _count(str(db)) == 5
