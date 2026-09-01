"""HELD-OUT rubric — series-1 follow-up 1 (double-coupon guard).

Runs on task-1 delivered code + follow-up. Asserts the exact bug report
semantics from followup.md.
"""

def test_coupon_applies_once():
    from app.orders import OrderStore
    s = OrderStore()
    o = s.create(1024, 1)
    first = o["total"]
    s.apply_coupon(o["id"], "SAVE10")
    half = o["total"]
    s.apply_coupon(o["id"], "SAVE10")
    assert o["total"] == half
    assert half < first


def test_coupon_used_flag():
    from app.orders import OrderStore
    s = OrderStore()
    o = s.create(2048, 1)
    s.apply_coupon(o["id"], "SAVE10")
    assert o.get("coupon_used") is True