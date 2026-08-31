"""SQLite persistence layer for the Research Request Pipeline.

Every function opens a short-lived connection so app instances (each with its
own DB file) never share connection state. All calls are synchronous and short;
in this single-process app they are serialized by the event loop.
"""

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    """ISO-8601 UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


def init_db(db_path: str) -> None:
    """Create the SQLite DB file, its parent directories, schema, and index."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                email TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'queued',
                result TEXT,
                error TEXT,
                claim_token TEXT,
                attempts INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status)"
        )
        conn.commit()
    finally:
        conn.close()


def create_request(db_path: str, topic: str, email: str) -> dict:
    """Insert a queued request and return the full stored row."""
    now = utc_now()
    conn = _connect(db_path)
    try:
        cur = conn.execute(
            """
            INSERT INTO requests
                (topic, email, status, result, error, claim_token, attempts,
                 created_at, updated_at)
            VALUES (?, ?, 'queued', NULL, NULL, NULL, 0, ?, ?)
            """,
            (topic, email, now, now),
        )
        conn.commit()
        rid = cur.lastrowid
    finally:
        conn.close()
    return get_request(db_path, rid)


def get_request(db_path: str, request_id: int):
    """Return the request row as a dict, or None if it does not exist."""
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM requests WHERE id = ?", (request_id,)
        ).fetchone()
        return _to_dict(row) if row else None
    finally:
        conn.close()


def list_requests(db_path: str) -> list[dict]:
    """Return all requests ordered oldest-first by id."""
    conn = _connect(db_path)
    try:
        rows = conn.execute("SELECT * FROM requests ORDER BY id ASC").fetchall()
        return [_to_dict(r) for r in rows]
    finally:
        conn.close()


def claim_next(db_path: str, now: str | None = None, claim_token: str | None = None):
    """Atomically claim the next claimable job.

    Claimable = status IN ('queued', 'processing'). A 'processing' row is an
    orphan left behind by a crashed worker and MUST be re-claimable. A 'done'
    or 'failed' job can never be re-claimed.

    Returns the updated row (status='processing') or None if nothing to claim.
    """
    now = now or utc_now()
    claim_token = claim_token or str(uuid.uuid4())
    conn = _connect(db_path)
    try:
        row = conn.execute(
            """
            UPDATE requests
            SET status = 'processing',
                attempts = attempts + 1,
                claim_token = ?,
                updated_at = ?
            WHERE id = (
                SELECT id FROM requests
                WHERE status IN ('queued', 'processing')
                ORDER BY id ASC
                LIMIT 1
            )
            RETURNING *
            """,
            (claim_token, now),
        ).fetchone()
        conn.commit()
        return _to_dict(row) if row else None
    finally:
        conn.close()


def complete_request(db_path: str, request_id: int, result: str, now: str | None = None) -> dict:
    """Mark a request done and return the updated row."""
    now = now or utc_now()
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            UPDATE requests
            SET status = 'done', result = ?, error = NULL, updated_at = ?
            WHERE id = ?
            """,
            (result, now, request_id),
        )
        conn.commit()
    finally:
        conn.close()
    return get_request(db_path, request_id)


def fail_request(db_path: str, request_id: int, error: str, now: str | None = None) -> dict:
    """Mark a request failed and return the updated row."""
    now = now or utc_now()
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            UPDATE requests
            SET status = 'failed', error = ?, updated_at = ?
            WHERE id = ?
            """,
            (error, now, request_id),
        )
        conn.commit()
    finally:
        conn.close()
    return get_request(db_path, request_id)
