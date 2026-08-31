"""Scale test: 1,000,000 synthetic events through ingest + rollup.

Asserts (on this machine):
  - ingest of 1M events < 120s
  - re-ingesting the same file adds 0 rows (INSERT OR IGNORE dedupe)
  - rollup < 30s and its total event sum == the number of raw events
  - running rollup a second time yields identical row counts and sums (idempotency)

Run from the repo root:
    python etl/perf_test.py
"""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

if __package__ in (None, ""):  # allow `python etl/perf_test.py`
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.db import connect, init_db  # noqa: E402
from etl.ingest import ingest  # noqa: E402
from etl.rollup import rollup, rollup_totals  # noqa: E402

NUM_EVENTS = 1_000_000
INGEST_LIMIT_S = 120.0
ROLLUP_LIMIT_S = 30.0

KINDS = ("click", "view", "purchase", "signup", "error")
TENANTS = ("acme", "globex", "initech", "umbrella", "stark", "wayne", "wonka", "nimbus")
START = datetime(2026, 1, 1, tzinfo=timezone.utc)


def generate_events(path: Path, count: int = NUM_EVENTS) -> None:
    """Write `count` deterministic synthetic events to `path` as JSONL."""
    span_days = 30
    with open(path, "w", encoding="utf-8") as fh:
        for i in range(count):
            ts = START + timedelta(days=i % span_days, seconds=(i * 37) % 86400)
            ev = {
                "id": f"ev-{i:08d}",
                "kind": KINDS[i % len(KINDS)],
                "occurred_at": ts.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "tenant": TENANTS[(i // 13) % len(TENANTS)],
                "payload": json.dumps({"seq": i, "price": (i % 1000) / 100}, separators=(",", ":")),
            }
            fh.write(json.dumps(ev, separators=(",", ":")))
            fh.write("\n")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "events.db"
        events_path = Path(tmp) / "events.jsonl"

        print(f"generating {NUM_EVENTS} events ...")
        t0 = time.perf_counter()
        generate_events(events_path, NUM_EVENTS)
        gen_s = time.perf_counter() - t0
        print(f"generated in {gen_s:.2f}s")

        init_db(db_path)
        conn = connect(db_path)
        try:
            t0 = time.perf_counter()
            inserted = ingest(conn, events_path)
            ingest_s = time.perf_counter() - t0
            print(f"ingested {inserted} events in {ingest_s:.2f}s")
            assert inserted == NUM_EVENTS, f"expected {NUM_EVENTS} inserted, got {inserted}"
            assert ingest_s < INGEST_LIMIT_S, f"ingest took {ingest_s:.2f}s, limit {INGEST_LIMIT_S}s"

            t0 = time.perf_counter()
            again = ingest(conn, events_path)
            dedup_s = time.perf_counter() - t0
            print(f"re-ingest added {again} rows in {dedup_s:.2f}s")
            assert again == 0, f"re-ingest added {again} rows, expected 0"

            t0 = time.perf_counter()
            days = rollup(conn)
            rollup_s = time.perf_counter() - t0
            print(f"rollup over {len(days)} day(s) in {rollup_s:.2f}s")
            assert rollup_s < ROLLUP_LIMIT_S, f"rollup took {rollup_s:.2f}s, limit {ROLLUP_LIMIT_S}s"

            rows1, sum1 = rollup_totals(conn)
            print(f"rollup rows={rows1}, sum={sum1}")
            assert sum1 == NUM_EVENTS, f"rollup sum {sum1} != {NUM_EVENTS}"

            rollup(conn)  # double-run -> idempotency
            rows2, sum2 = rollup_totals(conn)
            print(f"re-rollup rows={rows2}, sum={sum2}")
            assert (rows2, sum2) == (rows1, sum1), (
                f"idempotency violated: {rows1}/{sum1} -> {rows2}/{sum2}"
            )
        finally:
            conn.close()

    print("PERF + IDEMPOTENCY OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
