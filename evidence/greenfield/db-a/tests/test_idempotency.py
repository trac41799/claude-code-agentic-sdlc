"""Rollup idempotency: re-running for the same days must not double-count."""
from etl.ingest import ingest_events
from etl.rollup import rollup

from .helpers import make_event, rollup_snapshot, write_events


def test_double_run_rollup_is_idempotent(db_path, tmp_path):
    rows = [
        make_event("a", day="2026-01-01", kind="click", tenant="t1"),
        make_event("b", day="2026-01-01", kind="click", tenant="t1"),
        make_event("c", day="2026-01-01", kind="signup", tenant="t1"),
        make_event("d", day="2026-01-02", kind="click", tenant="t1"),
        make_event("e", day="2026-01-02", kind="purchase", tenant="t2"),
    ]
    path = write_events(tmp_path, rows)
    ingest_events(db_path, path)

    rollup(db_path)
    snap1 = rollup_snapshot(db_path)

    rollup(db_path)
    snap2 = rollup_snapshot(db_path)

    assert snap1 == snap2
    assert sum(row[3] for row in snap2) == 5  # every event counted exactly once
