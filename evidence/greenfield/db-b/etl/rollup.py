"""Aggregate raw_events into daily_rollup.

Re-runnable (idempotent): rollup never increments existing counters. It uses a
"watermark" strategy — the day being recomputed acts as the watermark. For each
day it deletes that day's existing rollup rows and recomputes them from
raw_events inside a single transaction. A crash or a partial run leaves no
partial counts: the next run for that day simply wipes and rebuilds the whole
day, so totals converge to the full-day values regardless of how many times the
job re-runs.

Usage:
    python -m etl.rollup [--day YYYY-MM-DD]     # or: python etl/rollup.py [--day ...]
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

if __package__ in (None, ""):  # allow `python etl/rollup.py`
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.db import connect, init_db  # noqa: E402

# The "day" is the leading date of the ISO-8601 timestamp.
_DAY = "substr(occurred_at, 1, 10)"

_INSERT_DAY = f"""
    INSERT INTO daily_rollup (day, kind, tenant, cnt)
    SELECT {_DAY}, kind, tenant, COUNT(*)
    FROM raw_events
    WHERE {_DAY} = ?
    GROUP BY {_DAY}, kind, tenant
"""

_INSERT_ALL = f"""
    INSERT INTO daily_rollup (day, kind, tenant, cnt)
    SELECT {_DAY}, kind, tenant, COUNT(*)
    FROM raw_events
    GROUP BY {_DAY}, kind, tenant
"""


def rollup(conn: sqlite3.Connection, day: str | None = None) -> list[str]:
    """Recompute rollup rows for one day, or for every day present in raw_events.

    Each day is handled as delete-then-recompute inside a single transaction, so
    re-running the rollup never double-counts (watermark approach).

    Returns the list of days that were recomputed.
    """
    cur = conn.cursor()
    days = [day] if day is not None else [
        r[0] for r in cur.execute(f"SELECT DISTINCT {_DAY} FROM raw_events")
    ]

    with conn:  # one transaction: deletes + inserts commit (or roll back) together
        for d in days:
            cur.execute("DELETE FROM daily_rollup WHERE day = ?", (d,))
        if day is not None:
            cur.execute(_INSERT_DAY, (day,))
        else:
            cur.execute(_INSERT_ALL)
    return days


def rollup_totals(conn: sqlite3.Connection) -> tuple[int, int]:
    """Return (number of daily_rollup rows, sum of cnt) for idempotency checks."""
    row = conn.execute("SELECT COUNT(*), COALESCE(SUM(cnt), 0) FROM daily_rollup").fetchone()
    return int(row[0]), int(row[1])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate raw_events into daily_rollup (idempotent).")
    parser.add_argument(
        "--day",
        default=None,
        metavar="YYYY-MM-DD",
        help="Recompute only this day (default: every day present in raw_events)",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="SQLite DB path (default: data/events.db or $FROAM_DB)",
    )
    args = parser.parse_args(argv)

    init_db(args.db)
    conn = connect(args.db)
    try:
        days = rollup(conn, day=args.day)
        rows, total = rollup_totals(conn)
    finally:
        conn.close()

    print(f"recomputed {len(days)} day(s): {', '.join(sorted(days)) or '(none)'}")
    print(f"daily_rollup rows={rows}, total events={total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
