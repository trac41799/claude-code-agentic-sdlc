"""Scale/perf test for the GREENFIELD-4 (DB+ETL) pipeline.

Generates 1,000,000 deterministic synthetic events, ingests them into a
fresh SQLite DB, runs the nightly rollup twice, and asserts:

* exactly 1,000,000 rows were ingested,
* ingest finished within budget,
* the first rollup finished within budget,
* a second rollup is a no-op (identical row count and SUM(cnt)),
* every event was counted exactly once (SUM(cnt) == 1,000,000).

Run from the repo root::

    python etl/perf_test.py

Any failed assertion exits non-zero.
"""

import json
import random
import sqlite3
import sys
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

# Make repo-root imports work when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.ingest import ingest  # noqa: E402
from etl.rollup import rollup  # noqa: E402
from etl.init_db import init_db  # noqa: E402

N_EVENTS = 1_000_000
SEED = 42
KINDS = ("page_view", "click", "signup", "purchase")
TENANTS = ("acme", "globex", "initech", "umbrella", "stark")
N_DAYS = 14
BASE_DATE = date(2026, 8, 17)  # Events span BASE_DATE .. BASE_DATE + N_DAYS - 1.

# Performance budgets (seconds).
INGEST_BUDGET = 120.0
ROLLUP_BUDGET = 30.0


def generate_events(path: str) -> None:
    """Write exactly *N_EVENTS* deterministic JSONL events to *path*."""
    rng = random.Random(SEED)
    days = [(BASE_DATE + timedelta(days=i)).isoformat() for i in range(N_DAYS)]
    with open(path, "w", encoding="utf-8") as fh:
        for i in range(N_EVENTS):
            day = days[rng.randrange(N_DAYS)]
            hour = rng.randrange(24)
            minute = rng.randrange(60)
            second = rng.randrange(60)
            event = {
                "id": f"evt-{SEED}-{i:08d}",
                "kind": rng.choice(KINDS),
                "occurred_at": f"{day}T{hour:02d}:{minute:02d}:{second:02d}Z",
                "tenant": rng.choice(TENANTS),
                "payload": json.dumps(
                    {
                        "seq": i,
                        "value": rng.random(),
                        "session": rng.randrange(10_000),
                    }
                ),
            }
            fh.write(json.dumps(event) + "\n")


def rollup_state(db_path: str) -> tuple[int, int]:
    """Return (row_count, SUM(cnt)) from the daily_rollup table."""
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT COUNT(*) FROM daily_rollup").fetchone()[0]
        total = conn.execute(
            "SELECT COALESCE(SUM(cnt), 0) FROM daily_rollup"
        ).fetchone()[0]
    finally:
        conn.close()
    return rows, total


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "perf.db")
        events_path = str(Path(tmpdir) / "events.jsonl")

        # Schema + data generation (not part of the timed ingest).
        conn = init_db(db_path)
        conn.close()
        generate_events(events_path)

        # 1. Ingest all events, timed.
        t0 = time.monotonic()
        inserted = ingest(db_path, events_path)
        t_ingest = time.monotonic() - t0
        assert inserted == N_EVENTS, (
            f"ingest inserted {inserted:,} rows, expected {N_EVENTS:,}"
        )
        assert t_ingest < INGEST_BUDGET, (
            f"ingest took {t_ingest:.2f}s, budget {INGEST_BUDGET:.0f}s"
        )

        # 2. First rollup, timed.
        t0 = time.monotonic()
        rollup(db_path)
        t_rollup = time.monotonic() - t0
        assert t_rollup < ROLLUP_BUDGET, (
            f"rollup took {t_rollup:.2f}s, budget {ROLLUP_BUDGET:.0f}s"
        )

        # 3. Idempotency: a second rollup must leave the table unchanged.
        rows_1, sum_1 = rollup_state(db_path)
        rollup(db_path)
        rows_2, sum_2 = rollup_state(db_path)
        assert rows_2 == rows_1, (
            f"rollup not idempotent: row count {rows_1:,} -> {rows_2:,}"
        )
        assert sum_2 == sum_1, (
            f"rollup not idempotent: SUM(cnt) {sum_1:,} -> {sum_2:,}"
        )
        assert sum_1 == N_EVENTS, (
            f"rollup SUM(cnt) = {sum_1:,}, expected {N_EVENTS:,}"
        )

        print("=== GREENFIELD-4 scale/perf test PASSED ===")
        print(f"events generated : {N_EVENTS:,}")
        print(f"ingest seconds   : {t_ingest:.2f}")
        print(f"rollup seconds   : {t_rollup:.2f}")
        print(f"rollup rows      : {rows_1:,}")
        print(f"rollup SUM(cnt)  : {sum_1:,}")


if __name__ == "__main__":
    main()
