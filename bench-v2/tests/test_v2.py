import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import benchv2.stats as st
import benchv2.costs as c
import benchv2.judge as j
import benchv2.score as sc
import benchv2.report as rep
import benchv2.runner as runners

V2 = pathlib.Path(__file__).resolve().parents[2] / "bench-v2"


def test_stats_median_iqr_and_mwu():
    a = [6.2, 7.1, 6.8, 7.4, 6.9]
    b = [11.0, 27.4, 13.2, 9.8, 25.0]
    m = st.summarize(a)
    assert abs(m["median"] - 6.9) < 1e-9
    assert abs(m["iqr"] - (7.1 - 6.8)) < 1e-9
    p = st.mann_whitney(a, b)
    assert p < 0.05, "two clearly separated samples must be significant"


def test_cost_basis_tagging():
    raw = {
        "usage": {"input_tokens": 100, "output_tokens": 50, "cache_read_input_tokens": 900},
        "total_cost_usd": 1.0,
        "modelUsage": {"deepseek/deepseek-chat": {"costBasis": "unknown", "costUSD": 1.0}},
    }
    t = c.breakdown(raw)
    assert t["in"] == 100 and t["out"] == 50 and t["cache_read"] == 900
    assert t["basis"] == "unknown" and t["cents_k"] == "unverified"


def test_runner_process_metrics():
    raw = {
        "terminal_reason": "max_turns", "is_error": True, "num_turns": 61,
        "duration_ms": 1662052, "errors": ["Reached maximum number of turns (60)"],
        "subagent_stats": {"spawned": 2, "failed": 0},
    }
    m = runners.process_metrics(raw, wall_min=30.0)
    assert m["terminal"] == "max_turns" and m["errors"] == 1 and m["compute_min"] == 27.7


def test_judge_hidden_gate(tmp_path):
    proj = tmp_path / "p"
    (proj / "tests").mkdir(parents=True)
    hidden = tmp_path / "hidden"
    hidden.mkdir()
    (hidden / "test_hidden_pass.py").write_text(
        "def test_ok():\n    assert 1 == 1\n", encoding="utf-8")
    r = j.run_hidden(proj, hidden_dir=hidden)
    assert r["passed"] >= 1


def test_series_task_set_exists():
    se = V2 / "tasks" / "series-1"
    if not (se / "seed-repo").is_dir():
        # Removed in 1d99e72 ("embedded repos removed") and never re-added; the
        # runner copies it at runtime (runner.run_series_replicate), so series-1
        # cannot execute until the author restores it. Kept visible as a skip,
        # not a pass, so the gap cannot silently rot.
        pytest.skip("series-1/seed-repo is missing — not in git history; restore it to run the brownfield series")
    assert (se / "seed-repo" / "app").is_dir()
    for t in ["t1", "t2", "t3"]:
        assert (se / "tasks" / t / "task.md").exists()
        assert (se / "tasks" / t / "rubric-hidden-tests" / "test_hidden.py").exists()
        assert (se / "tasks" / t / "followup.md").exists()
    print("series set OK")


def test_guardrail_conformance(tmp_path):
    repo = tmp_path / "g"
    (repo / "app").mkdir(parents=True)
    (repo / ".git").mkdir()
    planned = {"app/": {"app/a.py", "app/b.py"}}
    sc._git(repo)  # noop
    out = sc.conformance_simple(planned, changed={"app/a.py", "app/c.py"})
    assert out["conform"] is False and out["violations"] == {"app/c.py"}


def test_report_reproducible(tmp_path):
    art = tmp_path / "art"
    (art / "runs").mkdir(parents=True)
    runs = [{"case": "hard-greenfield", "arm": "A", "rep": 1, "wall_min": 7.0,
             "terminal": "completed", "cost": 1.0, "basis": "unknown",
             "in": 100, "out": 50, "hidden": 24, "judge_kap": 0.9}]
    (art / "runs" / "runs.json").write_text(json.dumps(runs), encoding="utf-8")
    rep.render(art, out_md=tmp_path / "report.md")
    rep.render(art, out_md=tmp_path / "report2.md")
    assert (tmp_path / "report.md").read_text(encoding="utf-8") == \
           (tmp_path / "report2.md").read_text(encoding="utf-8")
    assert "Declared limits" in (tmp_path / "report.md").read_text(encoding="utf-8")


def test_runner_cli_and_failed_tagging():
    import argparse
    import benchv2.runner as runners
    r = runners.parse_args(["hard-greenfield", "--arms", "A", "--reps", "1"])
    assert r.case == "hard-greenfield" and r.reps == 1
    assert runners.is_failed({"is_error": True}) is True
    assert runners.is_failed({"is_error": False}) is False