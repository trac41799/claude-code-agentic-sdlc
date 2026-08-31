"""In-memory event bus that fans request status transitions out to SSE subscribers.

The SQLite database is the source of truth; this bus only provides a live
notification channel so SSE clients react immediately instead of polling. Each
request keeps a small append-only history so a client connecting late can replay
the full queued -> processing -> done|failed sequence.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque

TERMINAL_STATUSES = ("done", "failed")


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue]] = defaultdict(set)
        self._history: dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

    def publish(self, request_id: str, status: str) -> None:
        """Record a transition and wake every subscriber of that request."""
        self._history[request_id].append(status)
        subscribers = tuple(self._subscribers.get(request_id, ()))
        for queue in subscribers:
            queue.put_nowait(status)
        if status in TERMINAL_STATUSES:
            for queue in subscribers:
                queue.put_nowait(None)  # sentinel: close the stream

    def subscribe(self, request_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers[request_id].add(queue)
        return queue

    def unsubscribe(self, request_id: str, queue: asyncio.Queue) -> None:
        self._subscribers.get(request_id, set()).discard(queue)

    def history(self, request_id: str) -> list[str]:
        return list(self._history[request_id])


event_bus = EventBus()
