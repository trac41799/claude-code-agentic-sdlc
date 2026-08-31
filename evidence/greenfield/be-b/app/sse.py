"""SSE framing helpers and in-queue sentinels."""

import json

# Marker placed in a subscriber's queue when its 100-event buffer overflows.
ERROR_SENTINEL = object()
# Marker placed in a subscriber's queue on app shutdown so the stream can
# flush pending events and close cleanly.
SHUTDOWN_SENTINEL = object()


def sse_data(payload):
    return f"data: {json.dumps(payload)}\n\n"


def error_event(status, detail):
    return f"event: error\ndata: {json.dumps({'status': status, 'detail': detail})}\n\n"
