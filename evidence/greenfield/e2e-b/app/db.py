import os
import sqlite3
from contextlib import asynccontextmanager

import aiosqlite

from .sse import publish

DEFAULT_DB_PATH = os.path.join("data", "requests.db")


def db_path_from_env():
    return os.environ.get("FROAM_DB_PATH", DEFAULT_DB_PATH)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    email TEXT NOT NULL,
    status TEXT NOT NULL,
    result TEXT,
    error TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (request_id) REFERENCES requests(id)
);
"""


@asynccontextmanager
async def open_db(db_path):
    db = aiosqlite.connect(db_path)
    try:
        await db
        db.row_factory = sqlite3.Row
        await db.execute("PRAGMA busy_timeout=5000")
        yield db
    finally:
        await db.close()


async def init_db(db_path):
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    async with open_db(db_path) as db:
        await db.executescript(_SCHEMA)


async def create_request(db, topic, email, bus=None):
    cur = await db.execute(
        "INSERT INTO requests (topic, email, status) VALUES (?, ?, 'queued')",
        (topic, email),
    )
    rid = cur.lastrowid
    await db.execute("INSERT INTO events (request_id, status) VALUES (?, 'queued')", (rid,))
    await db.commit()
    if bus is not None:
        publish(bus, rid, "queued")
    return rid


async def transition(db, rid, new_status, bus=None, result=None, error=None, log=True):
    await db.execute(
        "UPDATE requests SET status=?, result=?, error=?, updated_at=datetime('now') WHERE id=?",
        (new_status, result, error, rid),
    )
    if log:
        await db.execute("INSERT INTO events (request_id, status) VALUES (?, ?)", (rid, new_status))
    await db.commit()
    if log and bus is not None:
        publish(bus, rid, new_status)


async def get_request(db, rid):
    cur = await db.execute("SELECT * FROM requests WHERE id = ?", (rid,))
    row = await cur.fetchone()
    return dict(row) if row else None


async def list_requests(db):
    cur = await db.execute("SELECT * FROM requests ORDER BY id DESC")
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_events(db, rid):
    cur = await db.execute("SELECT * FROM events WHERE request_id = ? ORDER BY id", (rid,))
    rows = await cur.fetchall()
    return [dict(r) for r in rows]
