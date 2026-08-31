"""Scale + idempotency test for the event rollup pipeline.

Generates 1,000,000 deterministic synthetic events (seed 42), ingests them
into a fresh SQLite database, runs the nightly rollup, then asserts:

  * ingest completes in under 120s
  * rollup completes in under 30s
  * re-running the rollup yields identical daily_rollup rows (counts AND sums)

Everything runs against a throwaway temp dir, so the test is safe to re-run
on this machine (or the evaluator's) as many times as needed.
"""
import random
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from init_db import init_db  # noqa: E402
from ingest import ingest_events  # noqa: E402
from rollup import rollup  # noqa: E402

NUM_EVENTS = 1_000_000
INGEST_LIMIT_S = 120.0
ROLLUP_LIMIT_S = 30.0
SEED = 42

KINDS = ["page_view", "click", "signup", "purchase", "logout"]
TENANTS = ["tenant_a", "tenant_b", "tenant_c", "tenant_d"]


def generate_events(path, n=NUM_EVENTS, seed=SEED):
    """Write `n` synthetic events (deterministic given `seed`) as JSONL."""
    rng = random.Random(seed)
    kinds, tenants = KINDS, TENANTS
    with open(path, "w", encoding="utf-8") as f:
        for i in range(n):
            day = rng.randint(1, 30)
            hh = rng.randint(0, 23)
            mm = rng.randint(0, 59)
            ss = rng.randint(0, 59)
            kind = kinds[rng.randrange(len(kinds))]
            tenant = tenants[rng.randrange(len(tenants))]
            f.write(
                f'{{"id":"evt-{i:09d}","kind":"{kind}",'
                f'"occurred_at":"2026-01-{day:02d}T{hh:02d}:{mm:02d}:{ss:02d}",'
                f'"tenant":"{tenant}","payload":{{"ok":true}}}}\n'
            )


def rollup_snapshot(db_path):
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute(
            "SELECT day, kind, tenant, cnt FROM daily_rollup ORDER BY day, kind, tenant"
        ).fetchall()
    finally:
        conn.close()


def main():
    with tempfile.TemporaryDirectory(prefix="event-perf-") as tmp:
        tmp = Path(tmp)
        db_path = init_db(tmp / "events.db")
        events_file = tmp / "events.jsonl"

        print(f"Generating {NUM_EVENTS} synthetic events...", flush=True)
        t0 = time.time()
        generate_events(events_file)
        gen_s = time.time() - t0
        print(f"  generated in {gen_s:.2f}s ({events_file.stat().st_size / 1e6:.1f} MB)", flush=True)

        print(f"Ingesting into {db_path} ...", flush=True)
        t0 = time.time()
        inserted = ingest_events(db_path, events_file)
        ingest_s = time.time() - t0
        print(f"  inserted {inserted} events in {ingest_s:.2f}s", flush=True)
        assert inserted == NUM_EVENTS, f"expected {NUM_EVENTS} inserted, got {inserted}"
        assert ingest_s < INGEST_LIMIT_S, f"ingest took {ingest_s:.2f}s, limit is {INGEST_LIMIT_S}s"

        print("Rolling up (first run)...", flush=True)
        t0 = time.time()
        days = rollup(db_path)
        rollup_s = time.time() - t0
        print(f"  rolled up {days} days in {rollup_s:.2f}s", flush=True)
        assert rollup_s < ROLLUP_LIMIT_S, f"rollup took {rollup_s:.2f}s, limit is {ROLLUP_LIMIT_S}s"

        snap1 = rollup_snapshot(db_path)
        total1 = sum(row[3] for row in snap1)
        assert len(snap1) > 0, "rollup produced no rows"
        assert total1 == NUM_EVENTS, f"rollup sum ({total1}) != ingested events ({NUM_EVENTS})"

        print("Rolling up again (idempotency check)...", flush=True)
        rollup(db_path)
        snap2 = rollup_snapshot(db_path)
        total2 = sum(row[3] for row in snap2)
        assert snap1 == snap2, "re-running rollup changed daily_rollup rows (counts or values)"
        assert total1 == total2, f"re-running rollup changed sum: {total1} != {total2}"

    print(
        f"PASS: ingest {ingest_s:.2f}s (<{INGEST_LIMIT_S:.0f}s), "
        f"rollup {rollup_s:.2f}s (<{ROLLUP_LIMIT_S:.0f}s), "
        f"{len(snap1)} rollup rows, idempotent on re-run"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
