"""Nightly rollup of raw_events into daily_rollup.

Approach (watermark / full-day delete-and-recompute):
--------------------------------------------------------
For every day present in raw_events, we DELETE that day's existing rollup rows
and then recompute them from raw_events by GROUP BY (kind, tenant). The whole
day's delete-and-recompute happens inside a single transaction.

Because rollup rows are never appended — each day's rows are always rebuilt
from the source of truth — re-running the rollup for the same day produces
identical totals (no double counting). This is what makes the job safe to run
nightly even when it crashes partway or is re-invoked for the same window.

Partial days: callers may pass an explicit `days` list to roll up only a
subset (e.g. backfill one day). A later full run (days=None) recomputes every
day, so a partial-day run followed by a full re-run converges to the correct
full-day totals.
"""
import argparse
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

try:
    from .init_db import DEFAULT_DB_PATH  # imported as etl.rollup
except ImportError:  # pragma: no cover - running as a script with etl/ on sys.path
    from init_db import DEFAULT_DB_PATH


def _day_bounds(day):
    """Return [start, end) ISO range covering the calendar day `day`."""
    end = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    return day, end


def rollup(db_path, days=None):
    """Aggregate raw_events into daily_rollup, re-runnable without double counting.

    Parameters
    ----------
    db_path : str | os.PathLike
        Path to the SQLite database.
    days : iterable[str] | None
        Days (YYYY-MM-DD) to roll up. If None, every day present in raw_events
        is rolled up.

    Returns
    -------
    int
        The number of days that were (re)computed.
    """
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("BEGIN")
        if days is None:
            days = [
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT substr(occurred_at, 1, 10) FROM raw_events"
                )
            ]
        for day in days:
            start, end = _day_bounds(day)
            conn.execute("DELETE FROM daily_rollup WHERE day = ?", (day,))
            conn.execute(
                """
                INSERT INTO daily_rollup (day, kind, tenant, cnt)
                SELECT ?, kind, tenant, COUNT(*)
                FROM raw_events
                WHERE occurred_at >= ? AND occurred_at < ?
                GROUP BY kind, tenant
                """,
                (day, start, end),
            )
        conn.commit()
    finally:
        conn.close()
    return len(days)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Roll raw_events up into daily_rollup (idempotent)")
    parser.add_argument("db_path", nargs="?", default=str(DEFAULT_DB_PATH), help="path to SQLite database file")
    parser.add_argument("--day", action="append", help="roll up only this day (YYYY-MM-DD); repeatable; default: all days")
    args = parser.parse_args()
    count = rollup(args.db_path, days=args.day)
    print(f"Rolled up {count} day(s)")
    sys.exit(0)
