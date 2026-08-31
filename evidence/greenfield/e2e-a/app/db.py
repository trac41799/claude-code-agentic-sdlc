"""SQLite persistence layer for research requests.

Every write goes through a single process-wide lock and claims are atomic
(queued -> processing happens in one UPDATE guarded by the lock), so a job can
only ever be claimed by one worker at a time. A job left in 'processing' by a
crashed process is recovered back to 'queued' by ``recover_crashed_jobs`` at
worker startup, which makes it re-claimable without ever double-completing it.
"""

from __future__ import annotations

import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone

from app.bus import event_bus

_lock = threading.Lock()


def get_db_path() -> str:
    return os.environ.get("REQUESTS_DB", os.path.join("data", "requests.db"))


def get_conn() -> sqlite3.Connection:
    path = get_db_path()
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db() -> None:
    with _lock:
        conn = get_conn()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    email TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'queued'
                        CHECK (status IN ('queued', 'processing', 'done', 'failed')),
                    result TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()


def create_request(topic: str, email: str) -> dict:
    req_id = uuid.uuid4().hex
    now = _now()
    with _lock:
        conn = get_conn()
        try:
            conn.execute(
                "INSERT INTO requests (id, topic, email, status, result, created_at, updated_at) "
                "VALUES (?, ?, ?, 'queued', NULL, ?, ?)",
                (req_id, topic, email, now, now),
            )
            conn.commit()
        finally:
            conn.close()
    event_bus.publish(req_id, "queued")
    return get_request(req_id)


def get_request(req_id: str) -> dict | None:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, topic, email, status, result, created_at, updated_at "
            "FROM requests WHERE id = ?",
            (req_id,),
        ).fetchone()
        return dict(row) if row is not None else None
    finally:
        conn.close()


def list_requests() -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id, topic, email, status, result, created_at, updated_at "
            "FROM requests ORDER BY created_at DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def claim_next_job() -> dict | None:
    """Atomically move the oldest queued job to 'processing' and return it."""
    now = _now()
    job: dict | None = None
    with _lock:
        conn = get_conn()
        try:
            row = conn.execute(
                "SELECT id, topic, email, status, result, created_at, updated_at "
                "FROM requests WHERE status = 'queued' ORDER BY created_at ASC, id ASC LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            conn.execute(
                "UPDATE requests SET status = 'processing', updated_at = ? WHERE id = ?",
                (now, row["id"]),
            )
            conn.commit()
            job = dict(row)
            job["status"] = "processing"
        finally:
            conn.close()
    event_bus.publish(job["id"], "processing")
    return job


def complete_job(req_id: str, result: str) -> None:
    now = _now()
    with _lock:
        conn = get_conn()
        try:
            conn.execute(
                "UPDATE requests SET status = 'done', result = ?, updated_at = ? "
                "WHERE id = ? AND status = 'processing'",
                (result, now, req_id),
            )
            conn.commit()
        finally:
            conn.close()
    event_bus.publish(req_id, "done")


def fail_job(req_id: str, error: str) -> None:
    now = _now()
    with _lock:
        conn = get_conn()
        try:
            conn.execute(
                "UPDATE requests SET status = 'failed', result = ?, updated_at = ? "
                "WHERE id = ? AND status = 'processing'",
                (error, now, req_id),
            )
            conn.commit()
        finally:
            conn.close()
    event_bus.publish(req_id, "failed")


def recover_crashed_jobs() -> int:
    """Re-queue jobs stuck in 'processing' from a previously crashed process."""
    now = _now()
    with _lock:
        conn = get_conn()
        try:
            cur = conn.execute(
                "UPDATE requests SET status = 'queued', updated_at = ? WHERE status = 'processing'",
                (now,),
            )
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()


def count_status(status: str) -> int:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM requests WHERE status = ?", (status,)
        ).fetchone()
        return int(row["n"])
    finally:
        conn.close()
