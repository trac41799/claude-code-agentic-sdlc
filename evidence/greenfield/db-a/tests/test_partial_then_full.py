"""Partial-day rollup followed by a full re-run converges to correct totals."""
import sqlite3

from etl.ingest import ingest_events
from etl.rollup import rollup

from .helpers import make_event, rollup_snapshot, write_events


def _daily_rollup_rows(db_path):
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute(
            "SELECT day, kind, tenant, cnt FROM daily_rollup ORDER BY day, kind, tenant"
        ).fetchall()
    finally:
        conn.close()


def test_partial_day_then_full_rerun_fixes_counts(db_path, tmp_path):
    rows = [
        make_event("a", day="2026-01-01", kind="click", tenant="t1"),
        make_event("b", day="2026-01-01", kind="click", tenant="t1"),
        make_event("c", day="2026-01-02", kind="click", tenant="t1"),
        make_event("d", day="2026-01-02", kind="click", tenant="t1"),
        make_event("e", day="2026-01-02", kind="signup", tenant="t2"),
    ]
    path = write_events(tmp_path, rows)
    ingest_events(db_path, path)

    # Partial run: roll up only 2026-01-01.
    rollup(db_path, days=["2026-01-01"])
    partial = _daily_rollup_rows(db_path)
    assert partial == [("2026-01-01", "click", "t1", 2)]
    assert ("2026-01-02",) not in [r[:1] for r in partial]

    # Full re-run: every day is recomputed from scratch, so day 2 now appears
    # and the totals converge to the real per-day counts.
    rollup(db_path)
    full = rollup_snapshot(db_path)
    assert full == [
        ("2026-01-01", "click", "t1", 2),
        ("2026-01-02", "click", "t1", 2),
        ("2026-01-02", "signup", "t2", 1),
    ]
    assert sum(row[3] for row in full) == 5
