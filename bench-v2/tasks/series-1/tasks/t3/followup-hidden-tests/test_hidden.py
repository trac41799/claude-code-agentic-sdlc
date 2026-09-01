"""HELD-OUT rubric — series-1 follow-up 3 (idempotent multi-deduct)."""

def test_replay_is_noop():
    from app.inventory import deduct_many, STOCK_BY_SKU
    n = STOCK_BY_SKU[1024]
    deduct_many({1024: 3}, idempotency_key="k1")
    deduct_many({1024: 3}, idempotency_key="k1")
    assert STOCK_BY_SKU[1024] == n - 3


def test_different_keys_apply():
    from app.inventory import deduct_many, STOCK_BY_SKU
    n = STOCK_BY_SKU[2048]
    deduct_many({2048: 2}, idempotency_key="a")
    deduct_many({2048: 2}, idempotency_key="b")
    assert STOCK_BY_SKU[2048] == n - 4