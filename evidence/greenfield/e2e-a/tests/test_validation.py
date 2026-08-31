"""Input validation: blank/missing topics must be rejected with 4xx."""

from __future__ import annotations

import pytest


@pytest.mark.parametrize("topic", ["", "   ", "\t\n", None])
def test_blank_or_null_topic_rejected(client, topic):
    resp = client.post("/requests", json={"topic": topic, "email": "a@b.c"})
    assert 400 <= resp.status_code < 500


def test_missing_topic_rejected(client):
    resp = client.post("/requests", json={"email": "a@b.c"})
    assert 400 <= resp.status_code < 500


def test_missing_email_rejected(client):
    resp = client.post("/requests", json={"topic": "valid topic"})
    assert 400 <= resp.status_code < 500


def test_whitespace_padded_topic_is_stripped(client):
    resp = client.post("/requests", json={"topic": "  trimmed topic  ", "email": "a@b.c"})
    assert resp.status_code == 200
    assert resp.json()["topic"] == "trimmed topic"
