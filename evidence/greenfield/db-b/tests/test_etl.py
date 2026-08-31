"""Tests for the event-analytics ETL pipeline (schema, ingest, rollup)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from etl.db import connect, init_db
from etl.ingest import ingest
from etl.rollup import rollup, rollup_totals


@pytest.fixture()
def db(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = connect(db_path)
    yield conn
    conn.close()


def write_events(path: Path, events: list[dict]) -> Path:
    with open(path, "w", encoding="utf-8") as fh:
        for ev in events:
            fh.write(json.dumps(ev) + "\n")
    return path


def ev(
    id: str,
    kind: str = "click",
    occurred_at: str = "2026-08-01T10:00:00.000Z",
    tenant: str = "acme",
    payload: str | None = None,
) -> dict:
    return {
        "id": id,
        "kind": kind,
        "occurred_at": occurred_at,
        "tenant": tenant,
        "payload": payload,
    }


def test_init_db_creates_schema_and_is_idempotent(tmp_path):
    db_path = tmp_path / "x.db"
    init_db(db_path)
    init_db(db_path)  # running twice must not error
    conn = connect(db_path)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {"raw_events", "daily_rollup"} <= tables


def test_ingest_dedupes_duplicate_ids(db, tmp_path):
    path = write_events(tmp_path / "dup.jsonl", [ev("e1"), ev("e2"), ev("e1"), ev("e3"), ev("e2")])
    assert ingest(db, path) == 3
    assert db.execute("SELECT COUNT(*) FROM raw_events").fetchone()[0] == 3


def test_reingest_same_file_adds_zero_rows(db, tmp_path):
    path = write_events(tmp_path / "f.jsonl", [ev("e1"), ev("e2")])
    assert ingest(db, path) == 2
    assert ingest(db, path) == 0
    assert db.execute("SELECT COUNT(*) FROM raw_events").fetchone()[0] == 2


def test_ingest_normalizes_dict_payload(db, tmp_path):
    path = write_events(
        tmp_path / "p.jsonl",
        [{"id": "e1", "kind": "click", "occurred_at": "2026-08-01T10:00:00Z", "tenant": "acme",
          "payload": {"k": 1}}],
    )
    assert ingest(db, path) == 1
    row = db.execute("SELECT payload FROM raw_events WHERE id='e1'").fetchone()
    assert json.loads(row[0]) == {"k": 1}


def test_rollup_aggregates_correctly_across_two_days(db, tmp_path):
    path = write_events(tmp_path / "events.jsonl", [
        ev("a1", kind="click", occurred_at="2026-08-01T10:00:00Z", tenant="acme"),
        ev("a2", kind="click", occurred_at="2026-08-01T11:00:00Z", tenant="acme"),
        ev("a3", kind="view", occurred_at="2026-08-01T12:00:00Z", tenant="acme"),
        ev("b1", kind="click", occurred_at="2026-08-02T10:00:00Z", tenant="globex"),
        ev("b2", kind="click", occurred_at="2026-08-02T11:00:00Z", tenant="acme"),
    ])
    ingest(db, path)

    days = rollup(db)
    assert sorted(days) == ["2026-08-01", "2026-08-02"]

    rows = db.execute(
        "SELECT day, kind, tenant, cnt FROM daily_rollup ORDER BY day, kind, tenant"
    ).fetchall()
    assert [tuple(r) for r in rows] == [
        ("2026-08-01", "click", "acme", 2),
        ("2026-08-01", "view", "acme", 1),
        ("2026-08-02", "click", "acme", 1),
        ("2026-08-02", "click", "globex", 1),
    ]


def test_double_run_rollup_is_idempotent(db, tmp_path):
    path = write_events(tmp_path / "events.jsonl", [
        ev("a1", kind="click", occurred_at="2026-08-01T10:00:00Z", tenant="acme"),
        ev("a2", kind="click", occurred_at="2026-08-01T11:00:00Z", tenant="acme"),
        ev("b1", kind="view", occurred_at="2026-08-02T10:00:00Z", tenant="globex"),
    ])
    ingest(db, path)

    rollup(db)
    before = db.execute("SELECT day, kind, tenant, cnt FROM daily_rollup ORDER BY day, kind, tenant").fetchall()
    rows1, sum1 = rollup_totals(db)

    rollup(db)
    after = db.execute("SELECT day, kind, tenant, cnt FROM daily_rollup ORDER BY day, kind, tenant").fetchall()
    rows2, sum2 = rollup_totals(db)

    assert [tuple(r) for r in before] == [tuple(r) for r in after]
    assert (rows2, sum2) == (rows1, sum1)
    assert sum1 == 3


def test_partial_day_then_full_day_rerun_fixes_counts(db, tmp_path):
    first = write_events(tmp_path / "first.jsonl", [
        ev("a1", kind="click", occurred_at="2026-08-01T10:00:00Z", tenant="acme"),
        ev("a2", kind="click", occurred_at="2026-08-01T11:00:00Z", tenant="acme"),
    ])
    ingest(db, first)
    rollup(db, day="2026-08-01")
    assert db.execute(
        "SELECT cnt FROM daily_rollup WHERE day=? AND kind=? AND tenant=?",
        ("2026-08-01", "click", "acme"),
    ).fetchone()[0] == 2

    # Later events arrive for the same day; a full-day re-run must fix the counts.
    later = write_events(tmp_path / "later.jsonl", [
        ev("a3", kind="click", occurred_at="2026-08-01T12:00:00Z", tenant="acme"),
        ev("a4", kind="view", occurred_at="2026-08-01T13:00:00Z", tenant="acme"),
    ])
    ingest(db, later)
    rollup(db, day="2026-08-01")

    rows = {
        (r["day"], r["kind"], r["tenant"]): r["cnt"]
        for r in db.execute("SELECT day, kind, tenant, cnt FROM daily_rollup")
    }
    assert rows == {("2026-08-01", "click", "acme"): 3, ("2026-08-01", "view", "acme"): 1}


def test_rollup_scoped_to_one_day_leaves_other_days_untouched(db, tmp_path):
    path = write_events(tmp_path / "events.jsonl", [
        ev("a1", kind="click", occurred_at="2026-08-01T10:00:00Z", tenant="acme"),
        ev("b1", kind="click", occurred_at="2026-08-02T10:00:00Z", tenant="acme"),
    ])
    ingest(db, path)
    rollup(db)
    rollup(db, day="2026-08-01")  # touch only day 1 again

    rows = db.execute("SELECT day, cnt FROM daily_rollup ORDER BY day").fetchall()
    assert [tuple(r) for r in rows] == [("2026-08-01", 1), ("2026-08-02", 1)]
