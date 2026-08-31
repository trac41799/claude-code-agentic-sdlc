"""Background worker: claim -> sleep -> complete, publishing SSE events."""

import asyncio
from datetime import datetime, timezone

from app import db
from app.config import Settings
from app.events import EventBroadcaster


class Worker:
    """Owns a single asyncio task that processes queued research requests."""

    def __init__(self, settings: Settings, broadcaster: EventBroadcaster) -> None:
        self._settings = settings
        self._broadcaster = broadcaster
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        """Start the background loop if it is not already running.

        Synchronous (not ``async def``): tests call ``worker.start()`` without
        ``await``, and the app lifespan uses it during startup.
        """
        if self.is_running():
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run())

    def is_running(self) -> bool:
        """True if the background loop task is alive (started and not done)."""
        return self._task is not None and not self._task.done()

    async def stop(self) -> None:
        """Signal the loop to exit and wait for it to finish promptly."""
        self._stop_event.set()
        task = self._task
        self._task = None
        if task is None or task.done():
            return
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=5)
        except asyncio.TimeoutError:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            job = db.claim_next(self._settings.db_path)
            if job is None:
                # Idle: sleep until the next poll tick or until stop wakes us.
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=self._settings.worker_poll_interval,
                    )
                except asyncio.TimeoutError:
                    pass
                continue
            await self._process(job)

    async def _process(self, job: dict) -> None:
        request_id = job["id"]
        topic = job["topic"]
        # Broadcast the claim first; the claimed row already has status
        # 'processing' and incremented attempts.
        self._broadcaster.publish(request_id, "processing", job)
        try:
            await asyncio.sleep(self._settings.work_delay)
            result = (
                f"Research on '{topic}' completed at "
                f"{datetime.now(timezone.utc).isoformat()}"
            )
            done = db.complete_request(self._settings.db_path, request_id, result)
            self._broadcaster.publish(request_id, "done", done)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - mark the job failed
            failed = db.fail_request(self._settings.db_path, request_id, str(exc))
            self._broadcaster.publish(request_id, "failed", failed)
