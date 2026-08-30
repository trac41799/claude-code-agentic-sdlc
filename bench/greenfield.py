#!/usr/bin/env python3
"""Greenfield benchmark — implement-from-idea on freshly created folders.

Creates two fresh repos (A framework-installed, B bare) from scratch, runs the
same frozen idea brief in both, meters, and prints the comparison.
"""
import argparse, pathlib, subprocess, shutil, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import benchkit


def fresh_repo(root: pathlib.Path, framework_root: str | None):
    root.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text("# bench repo\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "bench@local"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Bench"], cwd=root, check=True)
    if framework_root:
        benchkit.install_framework(root, framework_root)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=root, check=True)


def main():
    ap = argparse.ArgumentParser(description="Greenfield A/B benchmark (fresh folders)")
    ap.add_argument("--base", required=True, help="parent dir for the fresh repos")
    ap.add_argument("--name", required=True, help="run name, e.g. run1")
    ap.add_argument("--task", required=True, help="frozen idea brief .md")
    ap.add_argument("--gate", required=True, help="acceptance gate (shell)")
    ap.add_argument("--framework", default=str(pathlib.Path(__file__).parent.parent),
                    help="framework repo root (default: this repo)")
    ap.add_argument("--out", default="bench-out")
    args = ap.parse_args()

    base = pathlib.Path(args.base)
    a_dir = base / f"{args.name}-a"
    b_dir = base / f"{args.name}-b"
    for d in (a_dir, b_dir):
        if d.exists():
            shutil.rmtree(d)
    fresh_repo(a_dir, args.framework)
    fresh_repo(b_dir, None)

    task = pathlib.Path(args.task).read_text(encoding="utf-8")
    out = pathlib.Path(args.out); out.mkdir(parents=True, exist_ok=True)

    print("== B (bare, fresh folder) ==")
    mb, _ = benchkit.run_arm(str(b_dir), task, out / f"{args.name}-b.json", activation=False)
    print(mb); print("gate:", benchkit.run_gate(str(b_dir), args.gate))

    print("== A (framework, fresh folder) ==")
    ma, _ = benchkit.run_arm(str(a_dir), task, out / f"{args.name}-a.json", activation=True)
    print(ma); print("gate:", benchkit.run_gate(str(a_dir), args.gate))

    benchkit.table(ma, mb)
    print("\nartifacts A:", sorted(str(p.relative_to(a_dir)) for p in
          (a_dir / ".specify").rglob("*.md")) if (a_dir / ".specify").exists() else "none")
    print(f"report dir: {out}")


if __name__ == "__main__":
    main()