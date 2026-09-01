"""HELD-OUT rubric — series-1 task 3 (atomic multi-deduct)."""

def test_atomic_partial_failure_leaves_state():
    from app.inventory import deduct_many, STOCK_BY_SKU
    before = dict(STOCK_BY_SKU)
    try:
        deduct_many({1024: 10, 8192: 9999})
    except RuntimeError:
        pass
    assert STOCK_BY_SKU == before


def test_shim_parity():
    from app.inventory import deduct_all
    before = None
    from app.inventory import STOCK_BY_SKU
    n = STOCK_BY_SKU[1024]
    deduct_all(1024, 5)
    assert STOCK_BY_SKU[1024] == n - 5


def test_multi_ok():
    from app.inventory import deduct_many, STOCK_BY_SKU
    n1, n4 = STOCK_BY_SKU[2048], STOCK_BY_SKU[4096]
    deduct_many({2048: 1, 4096: 2})
    assert STOCK_BY_SKU[2048] == n1 - 1
    assert STOCK_BY_SKU[4096] == n4 - 2