"""SSE wire-format helpers and the in-queue control sentinels.

The SSE output format is plain text. The two sentinels are object markers
pushed through a subscriber's bounded queue to steer the delivery loop:

- ``ERROR_SENTINEL``    buffer overflow -> emit a 429-style error event, close
- ``SHUTDOWN_SENTINEL`` graceful shutdown -> flush buffered events, then close
"""

import json

ERROR_SENTINEL = object()
SHUTDOWN_SENTINEL = object()

OVERFLOW_STATUS = 429
OVERFLOW_DETAIL = "buffer overflow"


def sse_data(payload) -> str:
    """Frame ``payload`` as an SSE ``data:`` event (JSON encoded)."""
    return f"data: {json.dumps(payload)}\n\n"


def error_event(status: int, detail: str) -> str:
    """Frame an SSE ``event: error`` message carrying a JSON body."""
    return f"event: error\ndata: {json.dumps({'status': status, 'detail': detail})}\n\n"


def heartbeat_event() -> str:
    """SSE comment used to keep idle connections alive."""
    return ": heartbeat\n\n"
