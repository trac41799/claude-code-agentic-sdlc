# Benchmark evidence — summary

All runs: same model pinned (DeepSeek-chat via FCC proxy since R2; R1 GLM), frozen task briefs,
identical prompts per arm, metered via session JSON (turns, tokens in/out, cost), offline acceptance
gates, non-merge branches. Full protocols: `docs/benchmarks/` on the Froam experiment branch
(`exp/asdlc-bench` in the traveling-friend project clones) — files below live there, not in this repo
(this repo hosts the framework; evidence repos host the runs).

## Incremental suite (existing codebase — travelbuddy-agentic-be / froam FE)

| Run | B bare | A′ passive | A activated |
|---|---|---|---|
| R1 · add-tests (trivial) | $0.63 · 6 tests | $0.62 · 7 tests | $0.47 · 10 tests · 2.5× turns |
| R2 · DB migration + RLS | $0.22 · 11 tests | $0.27 · 11 tests | $0.67 · 11 tests + plan/QA |
| R4 · fragile refactor | refused (restraint pass) | — | violated (guardrail advisory); prod-correct when approved |
| R3 · vertical FE+BE | $0.94 · 4 tests | — | $0.98 · 4 tests + plan/tasks |

Findings: passive ≈ bare (no idle cost) · activation tax scales with ceremony, benefit with risk ·
restraint is advisory, not structural — fragile files need mechanical protection · QA lane is the
differentiator on approved risky change.

## Greenfield suite (implement-from-idea, 4 cases, fresh repos)

| Case | B bare | A activated |
|---|---|---|
| E2E crash-safe job pipeline | 11.0m · $1.77 · 13 tests | 7.8m · $1.24 · 17 tests + spec/plan/tasks |
| FE virtualized feed + optimistic rollback | 7.4m · $0.97 · 24 tests | 7.3m · $1.18 · 22 tests + artifacts |
| BE rate-limited SSE proxy (hard) | 27.4m · $2.84 · 22 tests | 6.5m · $1.08 · 24 tests + artifacts |
| DB+ETL 1M rows, idempotent | 4.4m · $0.58 · 8 tests · perf ✓ | 5.8m · $1.08 · 6 tests · perf ✓ |

Each case also has a third arm (W — parallel dev-review "wave" loop) with
runnable projects and session JSONs in `evidence/`; the experiment verdict was
negative in the headless proxy and the wave loop is **not** part of the
canonical framework (see `docs/slides/GAP-ANALYSIS.md`, deliberate exclusions).

## Answers the evidence supports

1. **Value position**: the framework's benefit concentrates where difficulty lives — plan-first
   discipline collapses agent churn on hard engineering (4.2× faster, 2.6× cheaper, more passing
   tests on the SSE/backpressure case). On simple tasks it is parity-to-small-tax.
2. **Traceability**: A produced spec → plan → tasks → QA trails in 8/8 framework runs (incremental +
   greenfield); bare produced zero process artifacts. Multi-agent team = planning + QA lanes, measured.
3. **Gaps (documented, not hidden)**: guardrail adherence is advisory (R4 inversion) · headless-harness
   agent registration gap (fixed via `dev-agent-router`; native path intact) · token economy unmanaged
   (baseline pending) · case studies confounded (model drift, n=2, no cost tracking at the time).
4. **SWE-bench floor check: not run.** The question it would answer — "does the framework degrade
   capability?" — is answered by acceptance parity across the 12 metered greenfield runs (and the
   4 earlier incremental runs): the framework arm was never below bare on risky tasks. SWE-bench
   measures model capability on isolated bugs, a dimension the framework
   does not claim to change; its cost (docker, days of runs) is not justified by marginal information.

## Reproduce (one-command kit)

`bench/` ships with this repo: `bench/brownfield.py` (any repo, project-agnostic,
A/B on a scratch clone) and `bench/greenfield.py` (fresh folders). Usage and
frozen task templates: [bench/README.md](../../bench/README.md).

Commands:
- Brownfield: `python bench/brownfield.py --repo <your-repo> --task bench/tasks/brownfield-add-tests.md --gate "<test cmd>" --out bench-out/x`
- Greenfield: `python bench/greenfield.py --base /tmp/gf --name r1 --task bench/tasks/greenfield-e2e-pipeline.md --gate "pytest tests/ -q" --out bench-out/x`

## Reproduce (reference runs)

- **Evidence bundle (this repo)**: `evidence/` — 12 metered session JSONs
  (`evidence/sessions/`), 12 runnable project folders (`evidence/greenfield/`),
  tree captures (`evidence/tree/`), and the claim→evidence map
  (`evidence/manifest.md`). `python evidence/validate.py` reruns every acceptance
  gate and regenerates `evidence/validation-report.md` (12/12).
- **Incremental runs R1–R4**: ran against the Froam project clones
  (`travelbuddy-agentic-be` / `froam-journey-platform-fe`); protocol docs and
  session JSONs live on the `exp/asdlc-bench` branch of those clones.
- **Wave arms**: `evidence/greenfield/*-wave/` + `evidence/sessions/*-wave-a.json`;
  experiment writeup on the `exp/wave-dev-loop` branch.