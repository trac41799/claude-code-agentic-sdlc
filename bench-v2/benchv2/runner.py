"""benchv2.runner — replicate-based benchmark runner (protocol v2).

Runs `--reps` replicates of each arm for a case, reusing the v1 benchkit arms.
Each replicate: fresh repo (bare or framework-installed), one headless session
via the pinned CLI, session JSON archived, gates + hidden-rubric run by the
judge, then a run-record appended to <out>/runs/runs.json.

Usage:
  python bench-v2/benchv2/runner.py hard-greenfield --arms B A --reps 5 --out bench-v2-out/full
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent.parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "bench"))
import benchkit  # noqa: E402

try:
    from . import costs, judge, score  # noqa: E402
except ImportError:  # direct script execution
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    import benchv2.costs as costs  # noqa: E402,F401
    import benchv2.judge as judge  # noqa: E402
    import benchv2.score as score  # noqa: E402

CASES = {
    "hard-greenfield": {
        "task": "bench/tasks/greenfield-be-sse.md",
        "gate": "python -m pytest tests/ -q",
        "hidden": "bench-v2/tasks/hard-greenfield/rubric-hidden-tests",
        "series": False,
    },
    "series-1": {
        "task": "bench-v2/tasks/series-1/tasks/t1/task.md",
        "gate": "python -m pytest tests/ -q",
        "hidden": "bench-v2/tasks/series-1/tasks/t1/rubric-hidden-tests",
        "series": True,
    },
}


def parse_args(argv):
    ap = argparse.ArgumentParser(prog="runner v2")
    ap.add_argument("case", choices=list(CASES))
    ap.add_argument("--arms", nargs="+", default=["B", "A"], choices=["B", "A"])
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--out", default=str(HERE.parent / "bench-v2-out"))
    return ap.parse_args(argv)


def is_failed(session: dict) -> bool:
    return bool(session.get("is_error")) or bool(session.get("errors"))


def process_metrics(session: dict, wall_min: float) -> dict:
    return score.process_metrics(session, wall_min)


def fresh_repo(d: pathlib.Path, framework: bool, wave: bool = False):
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    (d / "README.md").write_text("# bench repo\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=d, check=True)
    subprocess.run(["git", "config", "user.email", "bench@local"], cwd=d, check=True)
    subprocess.run(["git", "config", "user.name", "Bench"], cwd=d, check=True)
    if framework:
        benchkit.install_framework(str(d), str(REPO))
    subprocess.run(["git", "add", "-A"], cwd=d, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=d, check=True)


PIN_ALIAS = ["glm"]

def verify_pin(session: dict) -> bool:
    mus = session.get("modelUsage") or {}
    if not mus:
        return False
    for model in mus:
        if any(a in model.lower() for a in PIN_ALIAS):
            return True
    return False


SERIES = ["t1", "t2", "t3"]  # task dirs under bench-v2/tasks/series-1/tasks/


def run_series_replicate(arm: str, rep: int, out: pathlib.Path) -> list:
    """Series-1: seed repo → t1 → followup → t2 → followup → t3 → followup."""
    series_root = REPO / "bench-v2" / "tasks" / "series-1"
    d = out / "projects" / f"series-1-{arm}-r{rep}"
    fresh_repo(d, framework=(arm == "A"))
    # seed repo files copied into the fresh repo (no .git issues — clean copy)
    shutil.copytree(series_root / "seed-repo", d, dirs_exist_ok=True)
    subprocess.run(["git", "add", "-A"], cwd=d, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=d, check=True)
    recs = []
    for t in SERIES:
        task_dir = series_root / "tasks" / t
        for step in ["task.md", "followup.md"]:
            brief = (task_dir / step).read_text(encoding="utf-8")
            session_json = out / "sessions" / f"series-1-{arm}-r{rep}-{t}-{step.split('.')[0]}.json"
            t0 = time.time()
            benchkit.run_arm(str(d), brief, str(session_json), activation=(arm == "A"))
            wall = (time.time() - t0) / 60
            try:
                raw = session_json.read_text(encoding="utf-8", errors="replace")
                s, _ = json.JSONDecoder().raw_decode(raw[raw.find('{"is_error"'):])
            except Exception:
                s = {}
            hidden = task_dir / "rubric-hidden-tests"
            if step == "task.md":
                hidden = task_dir / ("rubric-hidden-tests")
            recs.append({
                "case": "series-1", "arm": arm, "rep": rep, "step": f"{t}/{step[:-2]}",
                "wall_min": wall, "process": process_metrics(s, wall),
                "failed": is_failed(s), "pin_ok": verify_pin(s),
                "models": list((s.get("modelUsage") or {}).keys()),
                "cost_breakdown": costs.breakdown(s), "cost": s.get("total_cost_usd"),
                "terminal": s.get("terminal_reason"),
            })
            if not recs[-1]["failed"] and recs[-1]["pin_ok"] and not recs[-1]["process"]["is_error"]:
                recs[-1]["hidden_gate"] = judge.run_hidden(d, hidden_dir=hidden)
            if step == "task.md":
                pass  # followup keeps same repo/tree
    return recs


def run_replicate(case: str, arm: str, rep: int, out: pathlib.Path) -> dict:
    cfg = CASES[case]
    d = out / "projects" / f"{case}-{arm}-r{rep}"
    fresh_repo(d, framework=(arm == "A"))
    task = (REPO / cfg["task"]).read_text(encoding="utf-8")
    session_json = out / "sessions" / f"{case}-{arm}-r{rep}.json"
    session_json.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    benchkit.run_arm(str(d), task, str(session_json), activation=(arm == "A"))
    wall_min = (time.time() - t0) / 60
    try:
        raw = session_json.read_text(encoding="utf-8", errors="replace")
        s, _ = json.JSONDecoder().raw_decode(raw[raw.find('{"is_error"'):])
    except Exception:
        s = {}
    proc = process_metrics(s, wall_min)
    fail = is_failed(s)
    pin_ok = verify_pin(s)
    rec = {
        "case": case, "arm": arm, "rep": rep, "wall_min": wall_min,
        "process": proc, "failed": fail, "pin_ok": pin_ok,
        "models": list((s.get("modelUsage") or {}).keys()),
        "cost_breakdown": costs.breakdown(s),
        "cost": s.get("total_cost_usd"),
        "is_error": s.get("is_error"),
        "terminal": s.get("terminal_reason"),
    }
    if not pin_ok:
        rec["note"] = "PIN VIOLATION \u2014 run metered on " + ", ".join(rec["models"] or ["none"]) + "; not comparable"
        return rec
    if not fail:
        from . import judge as j
        rec["hidden_gate"] = j.run_hidden(d, hidden_dir=REPO / cfg["hidden"])
        rec["lint"] = j.lint(d)
        rec["coverage"] = j.coverage(d)
    return rec


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    # Operator pin (2026-09-05): pilot everything with glm-5.3-flash via
    # fcc-claude. Refuse anything else — especially Claude-family models.
    cli = os.environ.get("BENCH_CLI", "")
    model = os.environ.get("BENCH_MODEL", "")
    if cli != "fcc-claude":
        raise SystemExit("BENCH_CLI must be fcc-claude — refusing to run with any other CLI")
    if not model:
        raise SystemExit("BENCH_MODEL must be set — pilot pin is glm-5.3-flash")
    low = model.lower()
    if any(x in low for x in ("claude", "opus", "sonnet", "haiku")):
        raise SystemExit(f"BENCH_MODEL={model} is a Claude-family model — refused (operator pin: glm-5.3-flash only)")
    if "glm" not in low:
        raise SystemExit(f"BENCH_MODEL={model} is not a glm model — pilot runs use glm-5.3-flash only")
    out = pathlib.Path(args.out)
    runs_dir = out / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    (out / "projects").mkdir(exist_ok=True)
    (out / "sessions").mkdir(exist_ok=True)
    manifest_path = out / "manifest.json"
    manifest = {
        "case": args.case, "arms": args.arms, "reps": args.reps,
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "status": "running",
        "pin_env": {"BENCH_CLI": cli, "BENCH_MODEL": model},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    runs_path = runs_dir / "runs.json"
    runs = json.loads(runs_path.read_text(encoding="utf-8")) if runs_path.exists() else []
    for arm in args.arms:
        for rep in range(1, args.reps + 1):
            print(f"== {args.case} {arm} rep {rep} ==", flush=True)
            rec = run_replicate(args.case, arm, rep, out)
            runs.append(rec)
            runs_path.write_text(json.dumps(runs, indent=2), encoding="utf-8")
            print(json.dumps({k: rec[k] for k in ("wall_min", "terminal", "failed")}), flush=True)
    manifest["status"] = "done"
    manifest["ended"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("done:", runs_path)


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
    from benchv2.runner import main as _main
    _main()