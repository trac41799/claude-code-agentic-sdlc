"""Re-runnable nightly rollup: raw_events -> daily_rollup.

Watermark delete-and-recompute approach
---------------------------------------
For each day processed, the day's existing rows in ``daily_rollup`` are first
deleted and then recomputed from ``raw_events`` in a single ``INSERT ... SELECT
... GROUP BY`` statement. Both statements run inside one transaction, so a
failed run rolls back cleanly and a successful run is atomic.

This guarantees:
  * re-runs never double-count (the delete removes any prior rows first);
  * partial-day rollups are corrected by the next full run (the whole day is
    recomputed from raw_events, so stale rows vanish and late events count).

If ``day`` is None, every distinct day present in ``raw_events`` is recomputed;
otherwise only that day is processed.
"""

from .init_db import init_db


def rollup(db_path: str, day: str | None = None) -> int:
    """Aggregate raw_events by (day, kind, tenant) into daily_rollup.

    Args:
        db_path: Path to the SQLite database file (created if missing).
        day: An explicit ``YYYY-MM-DD`` day to recompute. If None, all distinct
            days present in raw_events are recomputed.

    Returns:
        The total number of daily_rollup rows written across all processed
        days (the sum of the INSERT ... SELECT row counts).
    """
    conn = init_db(db_path)
    try:
        if day is None:
            days = [
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT substr(occurred_at, 1, 10) FROM raw_events"
                )
            ]
        else:
            days = [day]

        total = 0
        for d in days:
            # First statement opens the implicit transaction; the whole day's
            # recompute is atomic. Delete-then-recompute (watermark) prevents
            # double counting on re-runs and corrects partial-day rollups.
            conn.execute("DELETE FROM daily_rollup WHERE day = ?", (d,))
            cur = conn.execute(
                """
                INSERT INTO daily_rollup (day, kind, tenant, cnt)
                SELECT substr(occurred_at, 1, 10), kind, tenant, COUNT(*)
                FROM raw_events
                WHERE substr(occurred_at, 1, 10) = ?
                GROUP BY 1, 2, 3
                """,
                (d,),
            )
            total += cur.rowcount

        conn.commit()
        return total
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
