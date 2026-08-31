"""Stream broadcast, per-client bounded queues, heartbeat, graceful shutdown."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import AsyncIterator, Awaitable, Callable

from app.config import Settings
from app.rate_limit import TokenBucket

DisconnectCheck = Callable[[], Awaitable[bool]]


@dataclass
class PublishResult:
    """Outcome of a single ``Stream.publish`` call across all subscribers."""

    delivered: int = 0
    dropped: int = 0
    overflowed: int = 0


class Subscriber:
    """One SSE client attached to a stream."""

    def __init__(
        self,
        stream: "Stream",
        *,
        queue_size: int = 100,
        bucket_capacity: int = 10,
        bucket_refill_rate: float = 5.0,
        heartbeat_seconds: float = 15.0,
    ) -> None:
        self.stream = stream
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self.bucket = TokenBucket(bucket_capacity, bucket_refill_rate)
        self.heartbeat_seconds = heartbeat_seconds
        self.dropped = 0
        self.overflowed = False
        self.closed = False
        self._overflow_event = asyncio.Event()
        self._shutdown_event = asyncio.Event()
        self._id = 0  # assigned by the owning Stream's per-stream id counter

    def mark_overflow(self) -> None:
        """Set the overflow flag and wake any waiting consumer loop."""
        self.overflowed = True
        self._overflow_event.set()

    def close(self) -> None:
        """Mark the subscriber closed and wake any waiting consumer loop."""
        self.closed = True
        self._shutdown_event.set()

    def _data_frame(self, event: object) -> str:
        return "data: " + json.dumps(event, ensure_ascii=False) + "\n\n"

    def _error_frame(self) -> str:
        payload = {
            "error": "buffer_overflow",
            "status": 429,
            "stream_id": self.stream.stream_id,
        }
        return (
            "event: error\ndata: "
            + json.dumps(payload, ensure_ascii=False)
            + "\n\n"
        )

    async def aiter_sse(
        self, is_disconnected: DisconnectCheck | None = None
    ) -> AsyncIterator[str]:
        """Yield SSE frames until overflow / shutdown / disconnect."""
        try:
            while True:
                if self.overflowed:
                    yield self._error_frame()
                    break
                if self.closed and self.queue.empty():
                    break

                # Drain whatever is queued right now, yielding one frame each.
                while True:
                    try:
                        event = self.queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                    yield self._data_frame(event)

                # On QueueEmpty: if closed, stop flushing and exit.
                if self.closed:
                    break

                if is_disconnected is not None:
                    try:
                        if await is_disconnected():
                            break
                    except Exception:
                        break

                ot = asyncio.ensure_future(self._overflow_event.wait())
                st = asyncio.ensure_future(self._shutdown_event.wait())
                done, _ = await asyncio.wait(
                    {ot, st},
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=self.heartbeat_seconds,
                )
                for task in (ot, st):
                    if not task.done():
                        task.cancel()
                await asyncio.gather(ot, st, return_exceptions=True)

                if not done:
                    yield ": heartbeat\n\n"
        finally:
            self.stream.unsubscribe(self)


class Stream:
    """Broadcast channel for one stream id."""

    def __init__(
        self,
        stream_id: str,
        *,
        settings: Settings | None = None,
        queue_size: int | None = None,
        bucket_capacity: int | None = None,
        bucket_refill_rate: float | None = None,
        heartbeat_seconds: float | None = None,
    ) -> None:
        resolved = settings if settings is not None else Settings()
        self.stream_id = stream_id
        self.queue_size = (
            queue_size if queue_size is not None else resolved.buffer_size
        )
        self.bucket_capacity = (
            bucket_capacity
            if bucket_capacity is not None
            else resolved.bucket_capacity
        )
        self.bucket_refill_rate = (
            bucket_refill_rate
            if bucket_refill_rate is not None
            else resolved.bucket_refill_rate
        )
        self.heartbeat_seconds = (
            heartbeat_seconds
            if heartbeat_seconds is not None
            else resolved.heartbeat_seconds
        )
        self.subscribers: dict[int, Subscriber] = {}
        self.events_published = 0
        self.dropped_total = 0
        self._next_sub_id = 0

    def subscribe(self) -> Subscriber:
        subscriber = Subscriber(
            self,
            queue_size=self.queue_size,
            bucket_capacity=self.bucket_capacity,
            bucket_refill_rate=self.bucket_refill_rate,
            heartbeat_seconds=self.heartbeat_seconds,
        )
        sub_id = self._next_sub_id
        self._next_sub_id += 1
        subscriber._id = sub_id
        self.subscribers[sub_id] = subscriber
        return subscriber

    def unsubscribe(self, subscriber: Subscriber) -> None:
        for key, sub in list(self.subscribers.items()):
            if sub is subscriber:
                del self.subscribers[key]
                return

    def publish(self, event: object) -> PublishResult:
        """Broadcast ``event`` to subscribers. Never blocks."""
        self.events_published += 1
        result = PublishResult()
        for sub in list(self.subscribers.values()):
            if sub.closed or sub.overflowed:
                continue
            if not sub.bucket.try_consume(1):
                sub.dropped += 1
                self.dropped_total += 1
                result.dropped += 1
                continue
            try:
                sub.queue.put_nowait(event)
                result.delivered += 1
            except asyncio.QueueFull:
                sub.mark_overflow()
                result.overflowed += 1
        return result

    async def shutdown(self) -> None:
        """Close all subscribers, flushing queued events."""
        for sub in list(self.subscribers.values()):
            sub.close()
        self.subscribers.clear()

    def info(self) -> dict:
        """Stream info including the aggregate ``dropped`` counter."""
        return {
            "stream_id": self.stream_id,
            "events_published": self.events_published,
            "subscribers": len(self.subscribers),
            "dropped": self.dropped_total,
            "subscribers_detail": [
                {
                    "id": sub._id,
                    "dropped": sub.dropped,
                    "queued": sub.queue.qsize(),
                    "overflowed": sub.overflowed,
                }
                for sub in self.subscribers.values()
            ],
        }


class StreamRegistry:
    """Owns all streams keyed by stream id."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings if settings is not None else Settings()
        self._streams: dict[str, Stream] = {}

    def get_or_create(self, stream_id: str, **overrides: object) -> Stream:
        if stream_id not in self._streams:
            self._streams[stream_id] = Stream(
                stream_id, settings=self._settings, **overrides
            )
        return self._streams[stream_id]

    def get(self, stream_id: str) -> Stream | None:
        return self._streams.get(stream_id)

    def remove(self, stream_id: str) -> None:
        self._streams.pop(stream_id, None)

    async def shutdown_all(self) -> None:
        for stream in list(self._streams.values()):
            await stream.shutdown()
        self._streams.clear()
