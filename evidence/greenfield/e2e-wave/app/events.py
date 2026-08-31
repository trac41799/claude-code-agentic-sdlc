"""Per-request SSE fan-out via asyncio.Queue."""

import asyncio
import json


def build_event_frame(request_data: dict, status: str | None = None) -> str:
    """Build an SSE frame: ``event: status\\ndata: <json>\\n\\n``.

    The data payload is ``{"status": ..., "request": {...}}``.
    """
    status = status or request_data["status"]
    payload = {"status": status, "request": request_data}
    return f"event: status\ndata: {json.dumps(payload)}\n\n"


class EventBroadcaster:
    """Fan out published transitions to per-request subscriber queues."""

    def __init__(self) -> None:
        self._subscribers: dict[int, list[asyncio.Queue]] = {}

    def subscribe(self, request_id: int) -> asyncio.Queue:
        """Register a new subscriber queue for a request and return it."""
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(request_id, []).append(q)
        return q

    def unsubscribe(self, request_id: int, q: asyncio.Queue) -> None:
        """Remove a subscriber queue; drop the request entry when empty."""
        subs = self._subscribers.get(request_id)
        if not subs:
            return
        try:
            subs.remove(q)
        except ValueError:
            pass
        if not subs:
            self._subscribers.pop(request_id, None)

    def publish(self, request_id: int, status: str, request_data: dict) -> None:
        """Queue a status frame to every subscriber of ``request_id``."""
        frame = build_event_frame(request_data, status)
        for q in self._subscribers.get(request_id, []):
            q.put_nowait(frame)
