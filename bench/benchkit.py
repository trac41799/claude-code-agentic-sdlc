#!/usr/bin/env python3
"""Bench kit — shared helpers for the Agentic SDLC benchmark suite.

Cross-platform: runs the `claude` CLI (or `fcc-claude` proxy) headless against
a task brief, meters the session, and evaluates an outcome gate. No framework
dependency in the measurement itself.
"""
import json, os, subprocess, sys, time, tempfile, shutil, pathlib, argparse

CLI = os.environ.get("BENCH_CLI", "claude")          # claude | fcc-claude
MODEL = os.environ.get("BENCH_MODEL", "sonnet")
TOOLS = "Bash Edit Write Read Glob Grep"
MAX_TURNS = int(os.environ.get("BENCH_MAX_TURNS", "60"))

ACTIVATION = (
    "\n\nActivate the project framework for this change: route it through the "
    "delegation block (dev-agent-router skill) and execute it as the developer "
    "agent following the agentic-sdlc workflow: pm spec capture "
    "(docs/product/product.md), dev-feature-plan (impl-plan.md + tasks.md), "
    "dev-tdd (RED evidence), qa-triage. Process artifacts are expected outputs."
)

WAVE_ACTIVATION = (
    " For tasks that can be decomposed into independent work items, use the "
    "dev-multi-agent skill: plan waves from tasks.md with disjoint file scopes, "
    "dispatch agents per wave, verify scopes + git status after each wave, run "
    "the suite after each wave, and write .specify/features/{slug}/wave-report.md "
    "when all waves complete."
)


def activation_text(activation: bool, wave: bool = False) -> str:
    t = ACTIVATION if activation else ""
    if wave:
        t += WAVE_ACTIVATION
    return t


def run_arm(workdir: str, task_prompt: str, out_json: str, activation: bool,
            wave: bool = False, extra_dirs=None):
    """Run one arm headless; returns (metrics_dict, exit_ok)."""
    cmd = [CLI, "-p", task_prompt + activation_text(activation, wave),
           "--output-format", "json", "--model", MODEL,
           "--allowedTools", TOOLS, "--max-turns", str(MAX_TURNS)]
    for d in (extra_dirs or []):
        cmd += ["--add-dir", d]
    t0 = time.time()
    with open(out_json, "w", encoding="utf-8") as f:
        proc = subprocess.run(cmd, cwd=workdir, stdout=f, stderr=subprocess.STDOUT)
    wall = (time.time() - t0) / 60
    try:
        raw = pathlib.Path(out_json).read_text(encoding="utf-8", errors="replace")
        start = raw.find('{"is_error"')  # fcc may prefix warnings + a log line
        j, _ = json.JSONDecoder().raw_decode(raw[start:]) if start >= 0 else ({}, 0)
        m = {
            "wall_min": round(wall, 1),
            "turns": j.get("num_turns"),
            "cost": j.get("total_cost_usd"),
            "in_tokens": (j.get("usage") or {}).get("input_tokens"),
            "out_tokens": (j.get("usage") or {}).get("output_tokens"),
            "terminal": j.get("terminal_reason"),
        }
    except Exception:
        m = {"wall_min": round(wall, 1), "parse": "failed"}
    return m, proc.returncode == 0


def run_gate(workdir: str, gate_cmd: str) -> str:
    """Run the acceptance gate; returns its tail output (<=4 lines)."""
    try:
        r = subprocess.run(gate_cmd, cwd=workdir, shell=True,
                           capture_output=True, text=True, timeout=900)
        out = (r.stdout or "") + (r.stderr or "")
        lines = [l for l in out.splitlines() if l.strip()][-4:]
        return " | ".join(lines)[:300]
    except Exception as e:
        return f"gate error: {e}"


def install_framework(repo: str, framework_root: str, wave: bool = False):
    """Install the project-scoped team (what /asdlc-adopt installs) into repo."""
    fw = pathlib.Path(framework_root)
    dest = pathlib.Path(repo)
    (dest / ".claude" / "rules").mkdir(parents=True, exist_ok=True)
    shutil.copytree(fw / ".claude" / "agents", dest / ".claude" / "agents", dirs_exist_ok=True)
    shutil.copytree(fw / ".claude" / "skills", dest / ".claude" / "skills", dirs_exist_ok=True)
    shutil.copytree(fw / ".claude" / "rules", dest / ".claude" / "rules", dirs_exist_ok=True)
    if wave:
        bundle = fw / "experiments" / "wave-dev-loop" / "skills"
        for s in ("dev-multi-agent", "asdlc-wave-on", "asdlc-wave-off"):
            shutil.copytree(bundle / s, dest / ".claude" / "skills" / s, dirs_exist_ok=True)
    block = (f"-- BEGIN: AGENT-DELEGATION (managed by agentic-sdlc skills -- do not delete this block) --\n"
             "## Agent delegation\n- product-manager: specs/epics/status\n- developer: code/impl\n"
             "- qa: testing/verification\n- devops: CI/CD\nRoute via dev-agent-router.\n-- END --")
    claude_md = dest / "CLAUDE.md"
    if not claude_md.exists():
        claude_md.write_text("# Project Instructions\n\n" + block, encoding="utf-8")


def table(a: dict, b: dict, label_a="A activated", label_b="B bare"):
    rows = [
        ("wall (min)", a.get("wall_min"), b.get("wall_min")),
        ("turns", a.get("turns"), b.get("turns")),
        ("cost", a.get("cost"), b.get("cost")),
        ("in tokens", a.get("in_tokens"), b.get("in_tokens")),
        ("out tokens", a.get("out_tokens"), b.get("out_tokens")),
    ]
    print(f"\n{'metric':<12}{label_a:>14}{label_b:>14}")
    for name, av, bv in rows:
        print(f"{name:<12}{str(av):>14}{str(bv):>14}")


def main():
    ap = argparse.ArgumentParser(description="Agentic SDLC bench arm runner")
    ap.add_argument("--task", required=True, help="frozen task brief .md")
    ap.add_argument("--gate", default="", help="acceptance gate shell command")
    ap.add_argument("--out", default="bench-out", help="output dir")
    ap.add_argument("--activate", action="store_true")
    ap.add_argument("--cwd", default=".")
    args = ap.parse_args()
    prompt = pathlib.Path(args.task).read_text(encoding="utf-8")
    pathlib.Path(args.out).mkdir(parents=True, exist_ok=True)
    m, _ = run_arm(args.cwd, prompt, pathlib.Path(args.out, "arm.json"),
                   activation=args.activate)
    print(json.dumps(m, indent=2))
    if args.gate:
        print("gate:", run_gate(args.cwd, args.gate))


if __name__ == "__main__":
    main()