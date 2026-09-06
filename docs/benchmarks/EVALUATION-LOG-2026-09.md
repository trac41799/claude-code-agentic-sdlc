# Evaluation log — 2026-09 (SPEC-012 pilot)

> **When to read:** anyone reviewing what has been measured about the Agentic
> SDLC framework (stable vs the `next` improvements), before quoting a number
> from this repo. This is the **living record**; every entry states its status
> (`measured` / `partial` / `unresolved`) and its limits. No cell here is a
> published claim — SPEC-012 FR-008 and the eval kit's R5/R6/R7 rules apply.

## Pin (all runs)

- CLI: `fcc-claude` 2.1.218 (headless Claude-Code-compatible proxy via fcc-server at 127.0.0.1:8082)
- Model: **`open_router/z-ai/glm-5.3-flash`** — operator decision 2026-09-05:
  *pilot everything with glm-5.3-flash, no other models, especially Claude models.*
- The bare id `glm-5.3-flash` routes to the NVIDIA NIM provider on the fcc-server and 503s; the `open_router/z-ai/`-qualified id uses the configured OpenRouter key.
- `bench-v2` runner **refuses** unset/non-glm/Claude-family pins mechanically (commit `5c98203`); the aisdlc-eval harness records the pin in every run and the limitation annex.

## 1. bench-v2 smoke — hard-greenfield, N=1 (status: partial — single run, no claims)

Ran 2026-09-05 from the `main` checkout (`asdlc-main-bench`), arms B (bare) / A (framework v2.10.0), out: `bench-v2-out/smoke` (gitignored; manifest + sessions on disk).

| Arm | Wall | Turns | Cost | Pin | Hidden gate |
|---|---|---|---|---|---|
| B (bare) | 24.1m | 59 | $2.84 | ✅ | 0/1 |
| A (framework) | 45.7m | 86 | $6.30 | ✅ | 0/1 |

- Both sessions metered on the pinned model only. Held-out test failed in both arms.
- Per-rep cost $2.8–6.3 → full N=5 suite ≈ **$90–100+** (glm pricing; v1's deepseek estimate was $40–90).
- **Not comparable to v1 runs** — the pin changed from `deepseek/deepseek-chat` (recorded in bench-v2/README.md).

## 2. aisdlc-eval pilot — 2-item corpus, claude-code arm, N=1 (status: partial)

`bench run --framework claude-code -n 1` on `bench/corpus` (FIX-1, FIX-2). Result: **2 runs, 1 oracle-passed**. Matrix cells `unresolved` (n too small).

## 3. Three-arm bakeoff — baseline vs asdlc-v1 vs asdlc-next (status: screening-grade, unresolved)

Corpus: FIX-1/FIX-2 × 3 arms × 3 reps. Arms: `baseline` (no overlay), `asdlc-v1` (`.claude/` from `main` @ v2.10.0 — 17 skills), `asdlc-next` (`.claude/` from `next` @ v2.11.0-rc.1 — 18 skills incl. test-freezer + evidence). Model pin identical across arms.

### Incident (recorded for honesty)
The first launch was "canceled" by the operator but its Python child **survived and ran to completion**; a second launch then ran again → 36 runs (two full benches), not 18. Decomposition showed all pass-rate differences were explained by **infra no-start failures** (`exit -1, 0s`) in the framework arms, not oracle outcomes. The run was re-executed cleanly (single process) — only the clean run below is used.

### Clean run (single process, 18 runs, 2026-09-06T06:36Z)

| Arm | Oracle pass | Median agent time (finished runs) | Failure signature |
|---|---|---|---|
| baseline | **6/6** | 70s | — |
| asdlc-v1 | **6/6** | 326s (4.7× baseline) | — |
| asdlc-next | **2/6** | 301s | **`TimeoutExpired` at the harness's 600s cap** ×4 |

- Every arm that **finished** passed the oracle (next: 2/2 finished). The four next-arm failures are **timeouts** — the Phase-1 ceremony (spec → plan → tasks → TDD + test-freezer → evidence → QA) exceeds a 10-minute budget on a trivial two-function task.
- Matrix (B-01/B-03): all cells **`unresolved`** (p_adj 0.75–1.0, n=6) — screening-grade only, no claims.
- **Read:** on small tasks, the framework's activation tax is large and grows with each control (v1 ≈ 4.7× bare time; next misses the budget entirely). On hard tasks the framework's value hypothesis is **unmeasured for the new changes** — the bench-v2 N=5 hard-greenfield run is the pending arbiter (arm A completed the SSE task in 45.7m in the smoke, so the ceremony fits a real-task budget).

## 4. Live observe loop (status: wired, sample too small)

- Token: `GITLAB_EVAL_REPO_TOKEN` (in `.env.local`, never committed) — **verified 200 OK** on `git.garage.epam.com/api/v4`; wired as `AISDLC_EVAL_GITLAB_TOKEN`. The cached *git* credential lacks API scope (401) — do not use it for the API.
- `fetch` live: CI rows fetched (5 for `aisdlc-eval-package`, 4 for `asdlc-improved`); **0 MR rows** — correct: neither repo has native GitLab MRs (one is a GitHub mirror; the other was direct-pushed). MR-based KPIs need a repo with native MRs (or the GitHub adapter + `AISDLC_EVAL_GITHUB_TOKEN`).
- `cohort assign` → `kpi compute` (15 values, all `unavailable` with reasons) → `report weekly` — the loop works end-to-end; value claims wait for a qualifying project (kit eligibility: ≥50 merged MRs, ≥8-week baseline window).

## 5. Tooling findings (fixes pending or applied)

| Finding | Status |
|---|---|
| `aisdlc-eval` not on PyPI | Install from `git+https://git.garage.epam.com/trac_nguyen/aisdlc-eval-package.git` (v0.2.0 @ `3cc773b5`) |
| Harness has no framework-overlay arms | **Patched** locally (bench-eval/patches/) — sandbox `.claude/` install + activation + `framework_roots` config + RUNNER_MAP entries; **not yet pushed upstream** |
| Windows UTF-8 bug — stdout reader thread crashed on non-Latin-1 bytes | **Patched** locally (`encoding="utf-8", errors="replace"`); same patch file |
| Agent failures recorded as bare `exit -1` | **Patched** — `agent error: <Type>: <detail>` now captured (this is how the timeouts were diagnosed) |
| `FakeRunner` trap | If a framework binary is missing, `bench run` silently persists **fabricated passes** (notes say "fake runner"; matrix can't distinguish) — do not run arms whose binary is absent |
| `codemie` arm blocked | `codemie-claude` wraps the Claude agent (ACP) — running it would attempt Claude models, violating the pin |
| "Recorded golden fixtures" fallback in README | Not implemented — `fetch` fail-opens without creds |

## Artifacts

- `bench-eval/` — workspace: config, corpus, **evidence store** (all snapshots), exports, required patch
- `docs/guide/EVAL-GUIDE.md` — full procedure from install to framework arms to interpretation
- `bench-v2-out/smoke` (gitignored) — bench-v2 smoke manifest/sessions
- fcc-server/gateway state, `.env.local` keys — never committed

## Next steps (pending operator decisions)

1. Re-run `asdlc-next` with a raised harness timeout (600s → 1800s) — distinguishes true completion rate from budget-miss (~$5–10).
2. bench-v2 **N=5 hard-greenfield** (~$30–40, one case) — the hard-task arbiter for the merge decision.
3. Restore `bench-v2/tasks/series-1/seed-repo` (author's copy) — unblocks the brownfield series case.
4. Push the eval-package patches upstream (EPAM GitLab) so the guide's install is patch-free.
5. Human sign-off (eval kit R6) before anything here is quoted externally.
