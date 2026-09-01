"""HELD-OUT rubric — series-1 follow-up 2 (blank env fallback)."""

def test_blank_env_falls_back(tmp_path, monkeypatch):
    monkeypatch.setenv("SHIP_FLAT", "")
    import importlib
    from app import config
    importlib.reload(config)
    assert config.get_pricing()["SHIP_FLAT"] == 499


def test_missing_env_falls_back(tmp_path, monkeypatch):
    monkeypatch.delenv("TAX_RATE", raising=False)
    import importlib
    from app import config
    importlib.reload(config)
    assert config.get_pricing()["TAX_RATE"] == 0.08