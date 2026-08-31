import asyncio


def make_bus():
    return {}


def subscribe(bus, request_id):
    q = asyncio.Queue()
    bus.setdefault(request_id, []).append(q)
    return q


def unsubscribe(bus, request_id, q):
    try:
        bus[request_id].remove(q)
        if not bus[request_id]:
            del bus[request_id]
    except (KeyError, ValueError):
        pass


def publish(bus, request_id, status):
    for q in list(bus.get(request_id, [])):
        q.put_nowait(status)
