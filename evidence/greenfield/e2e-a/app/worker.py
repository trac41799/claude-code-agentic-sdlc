"""Background worker that drains the queued-request queue.

Started from the app lifespan. Each cycle claims one queued job (queued ->
processing, persisted to SQLite), simulates work with a short sleep, then marks
it done with a generated result. If the process is killed mid-job the row is
left 'processing'; ``recover_crashed_jobs`` (run on the next startup) re-queues
it so it completes exactly once.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app import db

WORK_DELAY = 0.2
IDLE_POLL_SECONDS = 0.1

_worker_task: asyncio.Task | None = None


def generate_result(topic: str) -> str:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return f"{topic} - completed at {now}"


async def _loop() -> None:
    while True:
        job = db.claim_next_job()
        if job is None:
            await asyncio.sleep(IDLE_POLL_SECONDS)
            continue
        try:
            await asyncio.sleep(WORK_DELAY)
            db.complete_job(job["id"], generate_result(job["topic"]))
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - a failure must not kill the loop
            db.fail_job(job["id"], str(exc))


def start_worker() -> None:
    """Recover crashed jobs and start the processing loop (idempotent)."""
    global _worker_task
    if _worker_task is not None and not _worker_task.done():
        return
    db.recover_crashed_jobs()
    _worker_task = asyncio.create_task(_loop())


async def stop_worker() -> None:
    global _worker_task
    if _worker_task is None:
        return
    task = _worker_task
    _worker_task = None
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    except Exception:  # noqa: BLE001 - shutdown must never raise
        pass
