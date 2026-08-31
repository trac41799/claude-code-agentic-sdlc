#!/usr/bin/env python3
"""Run the A+wave greenfield arms only (B arms stay at the existing frozen
numbers — the wave bundle never touches the bare arm, re-running it would
only burn time and credits)."""

import json
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "bench"))
import benchkit

CASES = {
    "be": ("bench/tasks/greenfield-be-sse.md", "python -m pytest tests/ -q"),
    "e2e": ("bench/tasks/greenfield-e2e-pipeline.md", "python -m pytest tests/ -q"),
    "fe": ("bench/tasks/greenfield-fe-feed.md", "node --test tests/"),
    "db": ("bench/tasks/greenfield-db-etl.md", "python -m pytest tests/ -q"),
}


def main():
    base = pathlib.Path(sys.argv[1])
    only = sys.argv[2:] or list(CASES)
    out = base / "out"
    out.mkdir(parents=True, exist_ok=True)
    for name in only:
        if name not in CASES:
            raise SystemExit(f"unknown case {name}")
        task_rel, gate = CASES[name]
        d = base / f"{name}-wave"
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        (d / "README.md").write_text("# bench repo\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=d, check=True)
        subprocess.run(["git", "config", "user.email", "bench@local"], cwd=d, check=True)
        subprocess.run(["git", "config", "user.name", "Bench"], cwd=d, check=True)
        benchkit.install_framework(str(d), str(REPO), wave=True)
        subprocess.run(["git", "add", "-A"], cwd=d, check=True)
        subprocess.run(["git", "commit", "-qm", "init"], cwd=d, check=True)
        prompt = (REPO / task_rel).read_text(encoding="utf-8")
        print(f"== {name} A+wave ==", flush=True)
        m, _ = benchkit.run_arm(str(d), prompt, str(out / f"{name}-wave.json"),
                                activation=True, wave=True)
        print(json.dumps(m), flush=True)
        print("gate:", benchkit.run_gate(str(d), gate), flush=True)


if __name__ == "__main__":
    main()