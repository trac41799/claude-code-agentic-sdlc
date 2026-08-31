# Spec — benchmark-v2 (a measurement model that can actually prove value)

Slug: `benchmark-v2` · Status: DRAFT (no implementation yet — protocol approval gate)

## Why this exists (the honest diagnosis of the current suite)

Current evidence (bench/ + evidence/ + BENCHMARK-SUMMARY.md) is **directionally
suggestive, not probative**. Concretely, per claim:

| Current claim | Why it's too lite |
|---|---|
| "4.2× faster" | N=1. One run of each arm; no variance, no significance test. A single model-temperature flip can move runs by more than the claimed gap. |
| "$1.08 vs $2.84" | Provider-cost basis unverified (fcc `costBasis: unknown`); wave runs inflated 5–8× by cache charges. Dollar cells are not trustworthy as-is. |
| "24 vs 22 tests" | Test counts are agent-written + brief-written together; they measure *what the agent wrote*, not *whether the software is right*. No hidden/held-out evaluation. |
| "Traceability 8/8" | Artifact presence, not artifact *quality* (are spec→plan→tasks→code consistent? requirements actually covered by tests?). |
| Case difficulty | 4 synthetic greenfields; nothing touches a realistic existing codebase with tech debt, nothing is multi-session, nothing measures downstream maintenance. |
| "Value in software development" | No human-time, no follow-up-change cost, no quality-drift measurement. The claim the whole pitch rests on is the one this suite measures least. |

## Goal

A measurement model where an independently-reproducing run can convince an
engineer-skeptic: **N≥5 replicates with variance, cost from a verifiable
provider basis, correctness judged by held-out evaluation, and downstream
maintenance cost measured — on realistic development work.**

## Non-goals (dated 2026-09-01)

- Not a general agent benchmark (no SWE-bench floor re-run — documented
  rationale stands). Not a vendor bake-off. Not per-ultra-runtime measurement.
- No changes to the framework design itself; this measures it.
- No live-internet benchmarks (offline-first; deterministic deps pinned).

## Actors

- **Bench harness** (`bench/` v2 runner) — orchestrates arms, collection,
  reconciliation, statistical output.
- **Judge** — a blinded rubric evaluator (deterministic scripted gates +
  LLM-judge with a written rubric, calibrated against one human SME audit).
- **Operator** — approves the protocol (this spec), runs the suite.

## Requirements (EARS)

- R1 · WHEN the suite runs THEN every arm SHALL run ≥5 replicates and the
  report SHALL include median, IQR, and a Wilcoxon signed-rank / Mann-Whitney
  independence test vs the bare arm. *AC: report contains n, med, iqr, p.*
- R2 · WHEN cost is reported THEN token volumes SHALL be primary (input /
  output / cache-read, provider-priced: published $/M per class) and any
  dollar estimate SHALL be labeled with its basis. *AC: cost cells carry
  basis tags; no unlabeled dollars.*
- R3 · FOR each task THEN a held-out rubric SHALL exist (tests/criteria NOT
  visible to the agent) and the suite SHALL report rubric failure rate —
  judged code that behaves wrong = measured, not inferred. *AC: rubric
  score, per task, with judge-human agreement %.*
- R4 · THE suite SHALL include a brownfield series: ≥1 realistic mid-size
  existing codebase (pre-existing tech debt) with a task series of ≥3
  sequential changes (feature, migration, perf fix) in the SAME repo, plus a
  multi-session structure (each task starts with a fresh session — the
  context-loss axis). *AC: task config files exist in bench-v2/tasks/.*
- R5 · AFTER each task in the series THEN a follow-up change task SHALL run on
  the produced code (seeded defect fix + small feature append) and the suite
  SHALL report change latency and regression rate — the downstream-cost axis.
  *AC: follow-up metrics per series task.*
- R6 · THE suite SHALL gate code quality mechanically: lint/type strict
  (ruff+tsc+eslint max strictness), line-coverage %, cyclomatic complexity
  delta vs baseline, and a technical-debt ratio over the series. *AC: per
  task table.*
- R7 · THE suite SHALL meter the process, not just the end state: tool-call
  errors, failed tool-retry counts, agent-session crashes, wall vs compute
  time, and operator active approval/repair minutes (logged by the harness
  protocol). *AC: process metrics per run.*
- R8 · Guardrail effectiveness SHALL be scored: plan-vs-PR file conformance %,
  fragile-file violations per run, gates-that-caught-bugs (pre-merge red
  tests that were fixed / shipped). *AC: conformance % + caught-count.*
- R9 · Every number SHALL be reproducible from the bundled artifacts
  (runner stores raw session JSONs + judge sheets + reconciliation
  calculations; `python bench-v2/report.py` regenerates the report).
  *AC: report regenerates byte-identical from artifacts.*
- R10 · The protocol SHALL declare its own limits: effect size that N≥5 can
  detect, and what remains unmeasured (longevity, team-scale, LLM drift
  across months). *AC: declared limits section in the report template.*

## Edge cases

- E1 · A run that errors (proxy/model/network) → tagged `failed`, excluded
  from stats but listed; never silently dropped.
- E2 · Judge disagreement with human audit >15% → that task's rubric is
  quarantined and reported as uncalibrated.
- E3 · Replicate runs hit differing model behavior (temperature) → reported
  as variance; no cherry-picks.

## Assumptions

- Compute budget: 4 arms × 5 replicates × (~4 greenfield-hard + 3-series
  brownfield) ≈ 70–90 headless runs, ~$40–90 proxy cost at current pins,
  spread over ~2–3 days of wall time. Protocol approval is the gate.
- Judge = scripted gates (deterministic) + rubric-scored LLM judge with one
  human audit per task; audited subset only.
- Multi-session axis uses real session boundaries (fresh claude invocation
  per task step), not faked context truncation.

## Requirements checklist mapping

R1→R10 all observable; each has a report artifact. This spec is the protocol
artifact itself — implementation gets its own tasks.md after approval.