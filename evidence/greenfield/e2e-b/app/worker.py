import asyncio
from datetime import datetime, timezone

from .db import open_db, transition

WORK_SLEEP = 0.2


async def _has_event(db, rid, status):
    cur = await db.execute(
        "SELECT 1 FROM events WHERE request_id = ? AND status = ? LIMIT 1", (rid, status)
    )
    return await cur.fetchone() is not None


async def _claim(db, bus):
    # Fresh work first: queued -> processing (persisted atomically with the event).
    cur = await db.execute(
        "SELECT * FROM requests WHERE status = 'queued' ORDER BY id LIMIT 1"
    )
    row = await cur.fetchone()
    if row is not None:
        await transition(db, row["id"], "processing", bus=bus)
        return dict(row)

    # Crash recovery: a job left mid-flight as 'processing' is stale (previous
    # worker died) and is safe to re-claim.
    cur = await db.execute(
        "SELECT * FROM requests WHERE status = 'processing' ORDER BY id LIMIT 1"
    )
    row = await cur.fetchone()
    if row is not None:
        rid = row["id"]
        await transition(db, rid, "processing", bus=bus, log=not await _has_event(db, rid, "processing"))
        return dict(row)

    return None


async def process_one_job(db_path, bus=None):
    async with open_db(db_path) as db:
        job = await _claim(db, bus)
        if job is None:
            return False
        rid = job["id"]
        try:
            await asyncio.sleep(WORK_SLEEP)
            result = (
                f"Research on '{job['topic']}' completed at "
                f"{datetime.now(timezone.utc).isoformat()}"
            )
            await transition(db, rid, "done", bus=bus, result=result)
        except Exception as exc:  # noqa: BLE001
            await transition(db, rid, "failed", bus=bus, error=str(exc))
        return True


async def worker_loop(db_path, bus=None, idle_sleep=0.1):
    while True:
        try:
            worked = await process_one_job(db_path, bus)
            if not worked:
                await asyncio.sleep(idle_sleep)
        except asyncio.CancelledError:
            break
        except Exception:  # noqa: BLE001
            await asyncio.sleep(idle_sleep)
