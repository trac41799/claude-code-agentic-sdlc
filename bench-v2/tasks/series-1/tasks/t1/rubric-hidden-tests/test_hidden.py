"""HELD-OUT rubric — series-1 task 1 (status machine + notifications).

The agent never sees this file; it runs AFTER the arm completes, against the
delivered code. Asserts semantics beyond the brief (edge transitions,
cancel-before-pay, notify exactly once across a double-ship attempt, history
ordering).
"""
import pytest


@pytest.fixture
def store():
    from app.orders import OrderStore
    return OrderStore()


def test_cancel_before_pay(store):
    o = store.create(1024, 1)
    o = store.apply_coupon(o["id"], "SAVE10")
    assert store.transition(o["id"], "CANCELLED") is True
    assert store.get(o["id"])["status"] == "CANCELLED"


def test_double_ship_does_not_double_notify(store):
    from app import notifications
    o = store.create(2048, 1)
    store.transition(o["id"], "PAID")
    store.transition(o["id"], "SHIPPED")
    n1 = len([x for x in notifications.SENT if x["kind"] == "notify"])
    with pytest.raises(ValueError):
        store.transition(o["id"], "SHIPPED")
    n2 = len([x for x in notifications.SENT if x["kind"] == "notify"])
    assert n2 == n1


def test_history_is_ordered(store):
    o = store.create(4096, 1)
    for st in ("PAID", "SHIPPED", "DELIVERED"):
        store.transition(o["id"], st)
    assert store.history(o["id"]) == ["CREATED", "PAID", "SHIPPED", "DELIVERED"]


def test_invalid_transition_raises_and_state_untouched(store):
    o = store.create(8192, 1)
    with pytest.raises(ValueError):
        store.transition(o["id"], "DELIVERED")
    assert store.get(o["id"])["status"] == "CREATED"