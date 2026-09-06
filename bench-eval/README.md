# `bench-eval/` — evaluation workspace (aisdlc-eval)

Durable home for the aisdlc-eval evaluation that ran 2026-09-05/06. The live
runs happened in a scratch workspace; the evidence was copied here so any agent
or human can reproduce the analysis without rerunning anything.

| Path | What it is |
|---|---|
| `aisdlc-eval.yaml` | The configured workspace config — pin, GitLab sources, `framework_roots` (overlay arms) |
| `bench/corpus/` | The benchmark corpus (FIX-1, FIX-2 — self-contained fib tasks with materializing oracles) |
| `.aisdlc-eval/store.sqlite` | The evidence store: snapshots, runs, KPIs, pipeline rows (committed as evidence) |
| `.aisdlc-eval/exports/` | Generated reports: `comparison_matrix.csv`, `limitation_annex.md`, `weekly_metrics.*` |
| `patches/aisdlc-eval-framework-arms.patch` | Record of the overlay-arm changes (framework arms, sidecar files, artifact capture, `BENCH_TIMEOUT`, UTF-8 fix, failure detail) — **merged upstream** on the package repo's `main` (2026-09-06); kept here for reference and for installing against the registry wheel |

## How to use

```bash
# rerun the bench in this workspace (uses the committed store — commit new snapshots as evidence)
pip install -e <clone of https://git.garage.epam.com/trac_nguyen/aisdlc-eval-package>
git -C <clone> apply bench-eval/patches/aisdlc-eval-framework-arms.patch
aisdlc-eval bench run --corpus bench/corpus --framework baseline,asdlc-v1,asdlc-next -n 3
aisdlc-eval report comparison --corpus <label>
```

Full procedure, pin rules, and interpretation: [`docs/guide/EVAL-GUIDE.md`](../docs/guide/EVAL-GUIDE.md).
The results so far: [`docs/benchmarks/EVALUATION-LOG-2026-09.md`](../docs/benchmarks/EVALUATION-LOG-2026-09.md).

## Evidence policy

- The store is committed **as evidence** — new runs append snapshots; commit them with a message naming the run (arm set, n, date).
- Bench sandboxes are ephemeral (`%TEMP%\asdlc-bench-*`) and never committed; the store's run rows are stripped of sandbox paths.
- Never edit committed evidence; a corrected run is a new snapshot, not an edit.
