# Tasks — benchmark-v2

Baseline: none (new harness; existing suite stays as-is). Spec: `002-benchmark-v2`.

## T1 [P] stats module — files: bench-v2/stats.py — acceptance: spec R1
— test: tests/test_v2.py::test_stats_median_iqr_and_mwu
- task: failing test FIRST (median/IQR correct, Mann-Whitney U small-n with known answer), then implement.

## T2 [P] cost basis tagging — files: bench-v2/costs.py — acceptance: spec R2
— test: tests/test_v2.py::test_cost_basis_tagging
- task: failing test FIRST (token volumes extracted per class from fcc session JSON, dollar cells labeled basis or `none`), then implement.

## T3 process metering — files: bench-v2/runner.py — acceptance: spec R7
— test: tests/test_v2.py::test_runner_process_metrics
- task: failing test FIRST (tool errors/retries/crashes parsed from session JSON, wall+compute recorded), then implement.

## T4 [P] judge + hidden tests — files: bench-v2/judge.py, bench-v2/tasks/hard-greenfield/ (task.md frozen, rubric.md hidden) — acceptance: spec R3, R6
— test: tests/test_v2.py::test_judge_hidden_gate (fake project passes/fails hidden tests)
- task: failing test FIRST, then implement judge (pytest hidden + strict lint + coverage + complexity delta) and the held-out rubric/tests for the hard case.

## T5 [P] brownfield series task set — files: bench-v2/tasks/series-1/ (seed repo + t1..t3 + f1..f3 + rubrics + hidden tests) — acceptance: spec R4
— test: tests/test_v2.py::test_series_task_set_exists (structure + frozen files + rubric/hidden/test triplets resolve)
- task: failing test FIRST (all files exist per manifest), then author the seed repo (realistic debt: monolith, no tests, magic constants, no types) + 3 sequential task briefs + follow-up tasks.

## T6 [P] guardrail/process scoring — files: bench-v2/score.py — acceptance: spec R8
— test: tests/test_v2.py::test_guardrail_conformance (plan-vs-PR file conformance + violations on fake git states)
- task: failing test FIRST, then implement.

## T7 report generator (R9/R10) — files: bench-v2/report.py — acceptance: spec R9, R10
— test: tests/test_v2.py::test_report_reproducible (regenerates byte-identical from artifacts; limits section present)
- task: failing test FIRST, then implement (stats + cost + process + judge + guardrail sections + declared limits).

## T8 runner CLI — files: bench-v2/runner.py (--case/--arms/--reps/--out) — acceptance: R1, E1
— test: tests/test_v2.py::test_runner_cli_and_failed_tagging
- task: failing test FIRST (CLI parses; failed runs tagged, excluded, listed), then implement.

## T9 [P] pipeline live smoke — run hard-greenfield B+A × 1 rep — acceptance: R1..R10 end-to-end
- task: execute smoke run; paste runner + report excerpts; triage any pipeline bug via TDD loop.

## T10 full suite — all cases × N≥5 × arms — acceptance: production report + artifacts
- task: launch detached full run (manifest + monitoring); collect report when done.

## T11 docs — bench-v2/README.md (how to run, limits, what's measured) — acceptance: spec checklist
- task: write README.