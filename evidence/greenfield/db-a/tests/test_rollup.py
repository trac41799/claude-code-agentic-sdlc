"""Rollup correctness: aggregation across two days."""
import sqlite3

from etl.ingest import ingest_events
from etl.rollup import rollup

from .helpers import make_event, write_events


def test_rollup_aggregates_correctly_across_two_days(db_path, tmp_path):
    rows = [
        make_event("a", day="2026-01-01", kind="click", tenant="t1"),
        make_event("b", day="2026-01-01", kind="click", tenant="t1"),
        make_event("c", day="2026-01-01", kind="click", tenant="t1"),
        make_event("d", day="2026-01-01", kind="signup", tenant="t1"),
        make_event("e", day="2026-01-02", kind="click", tenant="t1"),
        make_event("f", day="2026-01-02", kind="click", tenant="t1"),
        make_event("g", day="2026-01-02", kind="click", tenant="t2"),
    ]
    path = write_events(tmp_path, rows)
    ingest_events(db_path, path)

    rolled_days = rollup(db_path)
    assert rolled_days == 2

    conn = sqlite3.connect(str(db_path))
    try:
        got = {
            (r[0], r[1], r[2]): r[3]
            for r in conn.execute("SELECT day, kind, tenant, cnt FROM daily_rollup")
        }
    finally:
        conn.close()

    assert got == {
        ("2026-01-01", "click", "t1"): 3,
        ("2026-01-01", "signup", "t1"): 1,
        ("2026-01-02", "click", "t1"): 2,
        ("2026-01-02", "click", "t2"): 1,
    }
