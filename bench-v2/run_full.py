import os
import subprocess
import sys

BASE = r"D:\TRANSFER DATA\Coding\claude-code-agentic-sdlc"
env = dict(os.environ)
env["BENCH_CLI"] = "fcc-claude"
env["BENCH_MODEL"] = "deepseek/deepseek-chat"

jobs = [
    ["python", "bench-v2/benchv2/runner.py", "hard-greenfield", "--arms", "B", "A", "--reps", "5", "--out", "bench-v2-out/full"],
    ["python", "bench-v2/benchv2/runner.py", "series-1", "--arms", "B", "A", "--reps", "5", "--out", "bench-v2-out/full"],
]
for j in jobs:
    print(">>", " ".join(j), flush=True)
    r = subprocess.run(j, cwd=BASE, env=env)
    print(">> exit", r.returncode, flush=True)
print("ALL JOBS DONE", flush=True)