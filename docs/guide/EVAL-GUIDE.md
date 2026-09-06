# Evaluation guide — measuring Agentic SDLC (SPEC-012)

> **When to use:** anyone (human or agent) setting up, running, or interpreting
> an evaluation of the Agentic SDLC framework — observe-mode weekly loops,
> benchmark bake-offs (baseline vs `asdlc-v1` vs `asdlc-next`), or bench-v2
> runs. Read the whole page once before the first run; afterwards use the
> section headers.
>
> **Golden rules:** (1) the model pin is **`open_router/z-ai/glm-5.3-flash`** —
> never run other models, especially Claude models; (2) every value carries a
> status (`measured`/`partial`/`proxy`/`estimate`/`unavailable`) and no claim is
> published without a named human sign-off; (3) never infer from a single run.

---

## 1. Stack map

```
fcc-claude (headless CLI)  →  fcc-server (127.0.0.1:8082, Admin UI holds keys)
                                 ├─ open_router/*  → OpenRouter key  (glm pin uses this)
                                 ├─ deepseek/*     → DEEPSEEK_API_KEY
                                 └─ glm-5.3-flash  → NVIDIA_NIM_API_KEY  (bare id — avoid)
aisdlc-eval (v0.2.0)   — observe loops + benchmark harness (corpus/oracles/cohort/KPI/report)
bench-v2 (this repo)   — N≥5 A/B protocol (stats, cost basis, held-out rubrics, series)
framework arms         — the framework = the `.claude/` overlay (agents+skills+rules)
                         installed into the sandbox before the agent runs
```

Three evaluation targets (the "arms"):

| Arm | What the agent sees | Source checkout |
|---|---|---|
| `baseline` | bare repo, no framework | — |
| `asdlc-v1` | `.claude/` overlay, 17 skills | `main` (v2.10.0) — use the `asdlc-main-bench` worktree |
| `asdlc-next` | `.claude/` overlay, 18 skills (test-freezer, evidence) | `next` (v2.11.0-rc.1) |

## 2. Install

### 2.1 fcc-claude + fcc-server (the proxy)

```bash
# CLI (already on this machine at ~/.local/bin/fcc-claude)
# fcc-server Admin UI at http://127.0.0.1:8082 — keys live there, never in this repo:
#   OpenRouter key (required — serves open_router/z-ai/*) · DeepSeek key (for deepseek/*) · NVIDIA NIM key (for bare glm ids)
fcc-claude --version   # 2.1.218 expected
```

### 2.2 aisdlc-eval (v0.2.0)

```bash
py -m pip install "git+https://git.garage.epam.com/trac_nguyen/aisdlc-eval-package.git"
# REQUIRED patch (framework arms + UTF-8 fix + failure detail) — pending upstream:
git clone https://git.garage.epam.com/trac_nguyen/aisdlc-eval-package $env:TEMP/aisdlc-eval-package
git -C $env:TEMP/aisdlc-eval-package apply <repo>/bench-eval/patches/aisdlc-eval-framework-arms.patch
py -m pip install -e $env:TEMP/aisdlc-eval-package
```

### 2.3 bench-v2 (in this repo)

```bash
py -m pip install pytest
py -m pytest bench-v2/tests/test_v2.py -q    # 7 passed, 1 skipped (series-1 seed-repo missing)
```

## 3. Model pin (enforced)

- The bench-v2 runner **refuses** to start unless `BENCH_CLI=fcc-claude` and `BENCH_MODEL` contains `glm` and is not Claude-family:
  ```bash
  $env:BENCH_CLI="fcc-claude"; $env:BENCH_MODEL="open_router/z-ai/glm-5.3-flash"
  ```
- The aisdlc-eval harness records `benchmark.models.pinned` in every run + annex (set it in `bench-eval/aisdlc-eval.yaml`). It does **not** pass `--model` to the CLI — safe only because the fcc-server default is already the glm pin (verify with a bare `fcc-claude -p "say OK"` and check `modelUsage`).
- Record the pin in every manifest; a run with an unpinned/other model is `PIN VIOLATION` (bench-v2) and not comparable.

## 4. Framework versions — checkouts

```bash
# stable arm (main) — separate worktree so the runner installs v2.10.0, not your working branch
git -C <repo> worktree add <repo>/../asdlc-main-bench main
# next arm — the `next` branch checkout (alpha v2.11.0-rc.1)
```

The overlay is what `/asdlc-adopt` installs: `.claude/agents`, `.claude/skills`, `.claude/rules` copied into the sandbox, plus the activation prompt ("route through the delegation block; produce spec/plan/tasks/TDD/QA artifacts").

## 5. Observe loop (weekly)

```bash
# credentials (never committed): put in .env.local, load by name
#   GITLAB_EVAL_REPO_TOKEN=<PAT with api scope>        (verified 200 OK; the git credential is NOT enough)
aisdlc-eval init && aisdlc-eval doctor                # capability matrix — read it honestly
$env:AISDLC_EVAL_GITLAB_URL="https://git.garage.epam.com"
$env:AISDLC_EVAL_GITLAB_TOKEN=<token>                  # from .env.local
$env:AISDLC_EVAL_GITLAB_PROJECT="<group>/<project>"
aisdlc-eval fetch                                     # tasks/MRs/CI/costs → snapshot
aisdlc-eval cohort assign --framework claude-code
aisdlc-eval kpi compute --window <YYYY-Www>
aisdlc-eval report weekly --window <YYYY-Www>
```

Expect most KPIs `unavailable` with reasons until the observed project meets the eligibility bar (≥50 merged MRs, ≥8-week baseline window). `unavailable` is a feature, not a bug.

## 6. Bench flows

### 6.1 aisdlc-eval bake-off (screening-grade corpus)

```bash
aisdlc-eval bench run --corpus bench/corpus --framework baseline,asdlc-v1,asdlc-next -n 3
aisdlc-eval report comparison --corpus <label>
# matrix + limitation annex → .aisdlc-eval/exports/
```

- Corpus: `bench-eval/bench/corpus/` (FIX-1/2, self-contained, materializing oracles).
- `-n 3` default; costs are small on this corpus (~$5–15 for 18 runs).
- Do **not** add a framework whose binary is missing — the harness falls back to `FakeRunner` and persists fabricated passes.
- Timeouts (harness cap 600s) count as failed runs — decide deliberately whether 600s is a budget KPI or raise it.

### 6.2 bench-v2 (the N≥5 protocol)

```bash
# from the STABLE checkout (asdlc-main-bench) for baseline runs
py bench-v2/benchv2/runner.py hard-greenfield --arms B A --reps 5 --out bench-v2-out/full
# series-1 requires the author-restored seed-repo; report regeneration:
py -c "from benchv2.report import render; from pathlib import Path; render(Path('bench-v2-out/full'), Path('bench-v2-out/full/report.md'))"
```

`bench-v2-out/` is gitignored — copy results into `evidence/baseline/` + `docs/architecture/baseline-status.md` on main to open the SPEC-012 merge gate (baseline-gate CI checks for exactly those files).

## 7. Interpretation rules (read before quoting anything)

1. `unresolved` matrix cells (n too small, p_adj ≥ 0.05) are **excluded from claims** — screening-grade only.
2. **Separate infra failures from oracle failures**: a run that never started (bench-v2 `pin_ok=False`/`is_error`; aisdlc-eval `agent exit -1` + `agent error: TimeoutExpired/OSError`) is not evidence about the framework. The 2026-09 bakeoff's pass-rate gap was entirely infra until re-run cleanly.
3. No single-run causality (SPEC-012 FR-008). No percentage claims without the matched comparison complete.
4. Cross-arm comparability requires the same model pin, corpus, cache policy, and settings fingerprint — all recorded in run manifests/annexes.
5. Human sign-off (eval kit R6) before external publication.

## 8. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `503 <PROVIDER>_API_KEY is not set` | fcc-server Admin UI: add the key for that provider route (OpenRouter / DeepSeek / NVIDIA NIM) |
| bare `glm-5.3-flash` 503s | Use `open_router/z-ai/glm-5.3-flash` (OpenRouter route) |
| `BENCH_MODEL` refusal | Pin guard — set `BENCH_MODEL=open_router/z-ai/glm-5.3-flash`; never Claude-family ids |
| aisdlc-eval agent runs `exit -1, 0s` | Harness catch-all — check the recorded `agent error:` detail (fixed in the patch) |
| Timeouts on framework arms | 600s harness cap; raise (`timeout=` in `runner_cli.py`) or treat as a budget KPI |
| 0 MR rows from GitLab | Correct when the repo has no native MRs (mirror/direct-push) — check the project |
| GitLab API 401 | The git credential is not an API PAT — use `GITLAB_EVAL_REPO_TOKEN` (api scope) |
| FakeRunner "passes" | A framework binary was missing — never trust those cells; verify `shutil.which(binary)` first |

## 9. Current state

- Measured: bench-v2 smoke (N=1), aisdlc-eval pilot, three-arm bakeoff (clean N=3/arm, screening-grade), live observe loop wired.
- Pending: raised-timeout rerun of `asdlc-next`, bench-v2 N=5, series-1 seed-repo, upstream push of the eval-package patches, human sign-off.
- Full numbers and limits: [`docs/benchmarks/EVALUATION-LOG-2026-09.md`](../benchmarks/EVALUATION-LOG-2026-09.md) · workspace: [`bench-eval/`](../../bench-eval/README.md).
