"""Tests for etl.rollup — re-runnable daily aggregation (spec AC-4/5/6)."""

import json
import sqlite3

from etl.ingest import ingest
from etl.rollup import rollup


def _write_jsonl(path, events):
    with open(path, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")


def _event(i, day, kind, tenant):
    return {
        "id": f"{tenant}-{kind}-{day}-{i}",
        "kind": kind,
        "occurred_at": f"{day}T10:00:{i % 60:02d}Z",
        "tenant": tenant,
        "payload": json.dumps({"seq": i}),
    }


def _rows(db_path):
    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            "SELECT day, kind, tenant, cnt FROM daily_rollup ORDER BY day, kind, tenant"
        ).fetchall()


def _sum_cnt(db_path):
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT COALESCE(SUM(cnt), 0) FROM daily_rollup").fetchone()[0]


def test_rollup_aggregates_correctly_across_two_days(tmp_path):
    """AC-4: rollup aggregates raw_events by (day, kind, tenant) across two
    days."""
    db = tmp_path / "events.db"
    src = tmp_path / "events.jsonl"
    _write_jsonl(src, [
        _event(1, "2026-08-30", "page_view", "acme"),
        _event(2, "2026-08-30", "page_view", "acme"),
        _event(3, "2026-08-30", "click", "acme"),
        _event(4, "2026-08-31", "page_view", "acme"),
        _event(5, "2026-08-31", "page_view", "globex"),
        _event(6, "2026-08-31", "click", "globex"),
    ])
    ingest(str(db), str(src))

    written = rollup(str(db))

    assert written == 5  # (30,page_view,acme), (30,click,acme),
    # (31,page_view,acme), (31,page_view,globex), (31,click,globex)
    assert _rows(str(db)) == [
        ("2026-08-30", "click", "acme", 1),
        ("2026-08-30", "page_view", "acme", 2),
        ("2026-08-31", "click", "globex", 1),
        ("2026-08-31", "page_view", "acme", 1),
        ("2026-08-31", "page_view", "globex", 1),
    ]
    assert _sum_cnt(str(db)) == 6


def test_rollup_double_run_is_idempotent(tmp_path):
    """AC-5: running rollup twice yields identical row counts and sums."""
    db = tmp_path / "events.db"
    src = tmp_path / "events.jsonl"
    _write_jsonl(src, [
        _event(1, "2026-08-30", "page_view", "acme"),
        _event(2, "2026-08-31", "click", "globex"),
        _event(3, "2026-08-31", "click", "globex"),
    ])
    ingest(str(db), str(src))

    rollup(str(db))
    rows_1, sum_1 = _rows(str(db)), _sum_cnt(str(db))

    written = rollup(str(db))
    rows_2, sum_2 = _rows(str(db)), _sum_cnt(str(db))

    assert written == len(rows_1)
    assert rows_2 == rows_1
    assert sum_2 == sum_1
    assert sum_2 == 3


def test_rollup_partial_day_then_full_day_fixes_counts(tmp_path):
    """AC-6: a partial-day rollup followed by a full-day re-run fixes the
    counts (no double counting, no stale rows)."""
    db = tmp_path / "events.db"

    # First file: 3 events on 2026-08-30 (1 click, 2 page_view).
    a = tmp_path / "a.jsonl"
    _write_jsonl(a, [
        _event(1, "2026-08-30", "page_view", "acme"),
        _event(2, "2026-08-30", "page_view", "acme"),
        _event(3, "2026-08-30", "click", "acme"),
    ])
    ingest(str(db), str(a))
    rollup(str(db), day="2026-08-30")
    assert _sum_cnt(str(db)) == 3
    assert _rows(str(db)) == [
        ("2026-08-30", "click", "acme", 1),
        ("2026-08-30", "page_view", "acme", 2),
    ]

    # Second file: 2 more events land on the same day (late data).
    b = tmp_path / "b.jsonl"
    _write_jsonl(b, [
        _event(4, "2026-08-30", "page_view", "acme"),
        _event(5, "2026-08-30", "click", "globex"),
    ])
    ingest(str(db), str(b))

    # Full-day re-run must recompute the whole day from raw_events.
    rollup(str(db))
    assert _rows(str(db)) == [
        ("2026-08-30", "click", "acme", 1),
        ("2026-08-30", "click", "globex", 1),
        ("2026-08-30", "page_view", "acme", 3),
    ]
    assert _sum_cnt(str(db)) == 5


def test_rollup_single_day_argument_recomputes_only_that_day(tmp_path):
    """AC-6: rollup(day=...) targets one day; other days' rollups untouched."""
    db = tmp_path / "events.db"
    src = tmp_path / "events.jsonl"
    _write_jsonl(src, [
        _event(1, "2026-08-30", "page_view", "acme"),
        _event(2, "2026-08-31", "click", "globex"),
    ])
    ingest(str(db), str(src))
    rollup(str(db))

    # Late event on the 30th.
    late = tmp_path / "late.jsonl"
    _write_jsonl(late, [_event(3, "2026-08-30", "page_view", "acme")])
    ingest(str(db), str(late))

    rollup(str(db), day="2026-08-30")

    assert _rows(str(db)) == [
        ("2026-08-30", "page_view", "acme", 2),
        ("2026-08-31", "click", "globex", 1),
    ]
