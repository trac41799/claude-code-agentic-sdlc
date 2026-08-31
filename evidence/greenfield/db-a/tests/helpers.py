"""Shared test helpers: event factories and DB snapshot utilities."""
import json
import sqlite3


def make_event(id, day="2026-01-01", kind="click", tenant="t1", hour="10", payload=None):
    return {
        "id": id,
        "kind": kind,
        "occurred_at": f"{day}T{hour}:00:00",
        "tenant": tenant,
        "payload": payload,
    }


def write_events(tmp_path, rows):
    p = tmp_path / f"events-{len(list(tmp_path.glob('events-*.jsonl')))}.jsonl"
    with open(p, "w", encoding="utf-8") as f:
        for evt in rows:
            f.write(json.dumps(evt) + "\n")
    return p


def rollup_snapshot(db_path):
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute(
            "SELECT day, kind, tenant, cnt FROM daily_rollup ORDER BY day, kind, tenant"
        ).fetchall()
    finally:
        conn.close()


def raw_count(db_path):
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute("SELECT COUNT(*) FROM raw_events").fetchone()[0]
    finally:
        conn.close()
