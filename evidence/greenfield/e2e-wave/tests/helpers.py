"""Shared test helpers."""

import asyncio
import json


async def read_sse_event(lines):
    """Read one SSE event from an httpx ``aiter_lines()`` stream.

    Collects the ``data:`` payload lines until the blank-line terminator and
    returns the parsed JSON object.
    """
    data_lines = []
    async for line in lines:
        line = line.strip()
        if not line:
            if data_lines:
                return json.loads("\n".join(data_lines))
            continue
        if line.startswith("data:"):
            data_lines.append(line[len("data:"):].strip())


async def wait_for_status(client, request_id, target, timeout=5.0):
    """Poll ``GET /requests/{id}`` until the request reaches ``target`` status.

    Returns the request body; raises AssertionError on timeout.
    """
    import time

    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        resp = await client.get(f"/requests/{request_id}")
        assert resp.status_code == 200
        last = resp.json()
        if last["status"] == target:
            return last
        await asyncio.sleep(0.02)
    raise AssertionError(
        f"request {request_id} did not reach '{target}' within {timeout}s "
        f"(last status: {last and last['status']})"
    )
