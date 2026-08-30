#!/usr/bin/env python3
"""Brownfield benchmark — project-agnostic, runs on ANY repo the framework is
installed in (team present via /asdlc-adopt, or --install-framework auto).

Arms: A (activated framework) in the given repo; B (bare) in a scratch clone
of the same repo at the same commit. Same frozen task, same model, metered.
"""
import argparse, pathlib, subprocess, tempfile, shutil, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import benchkit


def main():
    ap = argparse.ArgumentParser(description="Brownfield A/B benchmark (project-agnostic)")
    ap.add_argument("--repo", required=True, help="path to the target repo (framework installed)")
    ap.add_argument("--task", required=True, help="frozen task brief .md")
    ap.add_argument("--gate", required=True, help="acceptance gate (shell), e.g. 'pytest tests/ -q'")
    ap.add_argument("--out", default="bench-out", help="output dir for JSONs + report")
    ap.add_argument("--install-framework", default="",
                    help="path to framework repo root to auto-install the team (else assume adopted)")
    args = ap.parse_args()

    repo = pathlib.Path(args.repo).resolve()
    assert (repo / ".git").exists(), f"{repo} is not a git repo"
    if args.install_framework:
        benchkit.install_framework(repo, args.install_framework)
    assert (repo / ".claude" / "agents").exists(), \
        "framework team not present — run /asdlc-adopt first or pass --install-framework"

    task = pathlib.Path(args.task).read_text(encoding="utf-8")
    out = pathlib.Path(args.out); out.mkdir(parents=True, exist_ok=True)

    # Bare arm: scratch clone at same commit, framework stripped
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                          capture_output=True, text=True).stdout.strip()
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="bench-bare-"))
    subprocess.run(["git", "clone", "-q", str(repo), str(scratch)], check=True)
    subprocess.run(["git", "checkout", "-q", head], cwd=scratch, check=True)
    shutil.rmtree(scratch / ".claude", ignore_errors=True)

    print("== B (bare) ==")
    mb, _ = benchkit.run_arm(str(scratch), task, out / "arm-b.json", activation=False)
    print(mb); print("gate:", benchkit.run_gate(str(scratch), args.gate))

    print("== A (framework, activated) ==")
    ma, _ = benchkit.run_arm(str(repo), task, out / "arm-a.json", activation=True)
    print(ma); print("gate:", benchkit.run_gate(str(repo), args.gate))

    benchkit.table(ma, mb)
    print("\nartifacts A:", [str(p.relative_to(repo)) for p in
          (repo / ".specify").rglob("*.md")] if (repo / ".specify").exists() else "none")
    print(f"report dir: {out}")


if __name__ == "__main__":
    main()