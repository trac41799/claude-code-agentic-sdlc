"""benchv2.judge — scripted gates + hidden-test harness + rubric bookkeeping."""
import json
import pathlib
import re
import subprocess


def run_hidden(proj: pathlib.Path, cmd: str = "python -m pytest tests/ -q",
               hidden_dir: pathlib.Path | None = None, timeout: int = 600) -> dict:
    """Run the held-out tests NOT visible to the agent during the run."""
    import shutil
    tests_dir = proj / "tests"
    if hidden_dir is None:
        return {"error": "no hidden tests supplied"}
    if tests_dir.exists() and hidden_dir.as_posix() != tests_dir.as_posix():
        hidden_target = pathlib.Path(tests_dir) / "hidden"
        if hidden_target.exists():
            shutil.rmtree(hidden_target)
        shutil.copytree(hidden_dir, hidden_target)
    try:
        r = subprocess.run(cmd, cwd=proj, capture_output=True, text=True, timeout=timeout)
        out = f"{r.stdout}\n{r.stderr}"
        m = re.search(r"(\d+) passed", out)
        return {"passed": int(m.group(1)) if m else 0, "failed": (re.search(r"(\d+) failed", out) or [None, 0])[1] if "failed" in out else (1 if r.returncode else 0), "ok": r.returncode == 0}
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "passed": 0, "ok": False}


def lint(proj: pathlib.Path) -> dict:
    import shutil
    if shutil.which("ruff"):
        r = subprocess.run(["ruff", "check", "--select", "E,F", proj.as_posix()],
                           capture_output=True, text=True)
        return {"tool": "ruff", "errors": r.returncode == 0, "count": len(r.stdout.splitlines())}
    return {"tool": "none", "errors": None, "count": 0}


def coverage(proj: pathlib.Path) -> dict:
    import shutil
    if shutil.which("pytest") and shutil.which("coverage"):
        r = subprocess.run(["coverage", "run", "-m", "pytest", "tests/", "-q",
                            "--co"], cwd=proj, capture_output=True, text=True)
        return {"tool": "coverage", "pct": (re.search(r"(\d+)%", r.stdout) or [None, "n/a"])[1]}
    return {"tool": "none", "pct": "n/a"}


def rubric_summary(hidden_result: dict, lint_res: dict, cov: dict) -> dict:
    return {
        "hidden_passed": hidden_result.get("passed", 0),
        "hidden_ok": hidden_result.get("ok", False),
        "lint": lint_res, "coverage": cov,
    }


def calibration(sheet_rows: list[dict], human_eval: bool = True):
    """Judge-vs-human calibration placeholder — populated by the audit."""
    return {"judge_kappa": None, "human_audit": bool(human_eval)}