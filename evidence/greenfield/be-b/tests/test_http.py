"""HTTP tests via TestClient (non-streaming endpoints + clean shutdown)."""


def test_post_event_creates_stream_and_counts(client):
    resp = client.post("/streams/s/events", json={"n": 1})
    assert resp.status_code == 200
    assert resp.json() == {"id": "s", "subscribers": 0, "published": 1, "dropped": 0}

    resp = client.post("/streams/s/events", json={"n": 2})
    assert resp.json()["published"] == 2


def test_stream_info_reports_published_and_dropped(client):
    client.post("/streams/s/events", json={"n": 1})
    client.post("/streams/s/events", json={"n": 2})
    info = client.get("/streams/s").json()
    assert info["id"] == "s"
    assert info["published"] == 2
    assert info["dropped"] == 0
    assert info["subscribers"] == 0


def test_unknown_stream_returns_404(client):
    assert client.get("/streams/does-not-exist").status_code == 404


def test_post_accepts_arbitrary_json(client):
    for payload in ({"a": 1}, [1, 2, 3], "hello", 42, None):
        resp = client.post("/streams/any/events", json=payload)
        assert resp.status_code == 200, payload


def test_shutdown_is_clean(client):
    # Entering/exiting the TestClient context runs lifespan startup/shutdown;
    # a clean exit means no exceptions from manager.shutdown().
    with client:
        client.post("/streams/s/events", json={"n": 1})
        assert client.get("/streams/s").status_code == 200
