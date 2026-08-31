# Gap analysis — what the framework lacks, and what it deliberately excludes

Analysis date: 2026-08-31. Inputs: all measured runs so far (R1–R4 incremental,
4-case greenfield suite, 4-case A+wave experiment), the deck's evidence grades,
the constitution, and documented decisions. Rule used throughout: a **gap** is
something evidence shows we should be able to do and cannot (or do
unreliably); a **deliberate exclusion** is a design choice with documented
reasoning — these are surfaced separately so neither masquerades as the other.

## 1. Gaps (evidence-backed, ranked by impact)

### G1 · Cost: no trusted metering, no feedback loop, no budget — HIGH
Evidence:
- The bench's cost cells come from the provider client's `total_cost_usd`,
  with `costBasis: "unknown"` (fcc) — the basis is not independently
  verified.
- The A+wave runs proved the basis drifts: identical pin + brief produced
  costs 5–8× the A arm ($8.88 vs $1.08, $9.91 vs $1.24) dominated by
  `cache_read_input_tokens` (2.0M–5.8M per run) charged at full rate — a
  metering artifact, not real usage (waves/cache semantics differ).
- No per-task or per-skill cost attribution exists; no budget guard; the
  only brake in a run is `--max-turns`.
- **Consequence we actually hit:** one probe session silently ran on the
  wrong model (claude-opus-5, $0.17/turn) instead of the deepseek pin — we
  caught it only because we eyeballed the JSON. Nothing in the harness
  verifies the effective model against the expected pin.
Fix path: session-JSON ingestion into a per-run/per-task cost table (bench
side), a canonical model-pin assertion (reject runs where `canonicalModel ≠`
expected), the pending token baseline, and per-task budgets as a gate input.

### G2 · Enforcement is advisory, not mechanical — HIGH
Evidence: R4 (fragile refactor) — the activated arm violated the guardrail
when the operator approved the change; it landed prod-correct, but "don't
touch fragile files without evidence" was a preference, not a wall. The
constitution forbids `permissions` grants, so the fix must be mechanical
CI/checker-side (fragile-path scanner, plan-vs-PR file contract), never
Claude-permission-side.
Fix path: CI job asserting the PR touches only files listed in the approved
plan (blast-radius, the plan.mjs engine already ships an engine for this) +
a fragile-file deny-list with an evidence-required message.

### G3 · Every benchmark cell is N=1 — MED
Evidence: each arm ran once per case; nothing measures run-to-run variance.
The headline claim ("4.2× faster") rests on a single measurement. Model
temperature/nondeterminism makes the likely variance non-trivial (we saw
turns 26–74 across the four wave cases at identical settings).
Fix path: headline cells ×3 with variance reported; claims re-graded
(VERIFIED → VERIFIED* until N≥3).

### G4 · Devops lanes are offline-unmeasurable — MED
Evidence: bench gates are offline acceptance; `devops-cicd`, `devops-ops`,
rollback, and git guardrails never fire in a lab run. Their claims are
tested only on live client projects — no reproducible cell, no regression
signal when the skills change.
Fix path: a staging smoke harness (GH Actions run + Vercel preview + one
rollback drill) that the bench can gate against.

### G5 · Human-hour ratio: method exists, evidence pending — MED
Evidence: hooks + PR-window measurement is implemented in the private
telemetry plugin; the public evidence trail has no human-hour cell, so the
"one week POC" claims stay at CASE STUDY/RATIONALE.
Fix path: publish the method as a reproducible doc (public method, private
data), run it on one project, grade the result.

### G6 · Model-sensitivity and context pressure unmeasured — MED
Evidence: R1 ran GLM, R2+ deepseek (a documented mix); the framework's
benefit is claimed on one model family. Wave runs showed cache-read token
explosion — context pressure per task is invisible in the metrics.
Fix path: headline cells on a second model; add context-read metrics to the
bench table.

## 2. Deliberate exclusions (design choices with reasoning — not defects)

1. **No hooks / no auto-runtime / no silent telemetry** — the v1 lesson;
   nothing runs without a human trigger (constitution, CI-enforced).
2. **No auto-approve; every gate is a human decision** — v1's overnight
   autonomy produced drift, not leverage (slides 16–17).
3. **No marketing agent lanes** — writer/designer/email removed in v2.6.0;
   they carried maintenance load with no measurement (slide 16 shows them in
   the 10 scheduled routines).
4. **No permissions grants** — the `Bash(*)` grant is the reason v2 exists
   (CLAUDE.md hard rule). Mechanical enforcement lives in CI, not Claude.
5. **No SWE-bench floor check** — deliberately not run; rationalized in
   BENCHMARK-SUMMARY (capability-floor question, docker + days of runs,
   marginal information low vs cost).
6. **No global memory / no auto-context restoration** — repo artifacts
   (spec/plan/tasks/QA) are the memory; re-reading them is the discipline.
7. **No wave loop in the canonical set** — the experiment verdict was honest
   and negative in a headless proxy (parallelism can't materialize there);
   kept as an opt-in experiment with clean removal (exp/wave-dev-loop).
8. **No fleet-wide agent management** — per-project install by design; the
   marketplace + `/asdlc-adopt` refresh is the update mechanism.

## 3. Focus list (what we'd do first, scoped)

1. **Trusted cost loop** (G1): pin assertion + session ingestion + baseline +
   per-task budget hooks. Headline gap the user flagged — it also made a
   real incident (wrong-model probe).
2. **Mechanical enforcement** (G2): CI plan-vs-PR file contract + fragile-file
   scanner, reusing the plan engine.
3. **N≥3 headlines** (G3): variance for the two most-told claims; regrade.
4. **Devops staging smoke** (G4): one reproducible offline-ish cell.
5. **Second-model matrix** (G6): stability of the benefit claim across model
   families.

## 4. Claims currently PLANNED/N-VERIFIED (audit)

- Human-hour ratio: PLANNED (blocked on G5).
- SWE-bench-style floor: deliberately not claimed.
- Cost comparisons: VERIFIED-with-caveat (basis unverified, G1) — the deck
  must say so.
- "4.2× faster": single-run (G3) — state N=1 when presented.