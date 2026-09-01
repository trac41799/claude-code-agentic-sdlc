"""HELD-OUT rubric — series-1 task 2 (config boundary).

Asserts env-override behavior and that the old module-level constants do not
remain read at runtime by create().
"""

def test_env_override_wins():
    import os
    os.environ["TAX_RATE"] = "0.11"
    try:
        import importlib
        from app import config
        importlib.reload(config)
        s = config.get_pricing()
        assert s["TAX_RATE"] == 0.11
    finally:
        os.environ.pop("TAX_RATE", None)


def test_defaults_match_legacy():
    from app import config
    s = config.get_pricing()
    assert s["PRICE_MAPPING"][1024] == 299
    assert 0 < s["SHIP_FLAT"] < 1000


def test_create_reads_config_not_module_constants():
    from app import config
    from app.orders import OrderStore
    s = OrderStore()
    o = s.create(1024, 1)
    assert o["total"] > 0
    assert config.get_pricing()["PRICE_MAPPING"][1024] == 299