# Bench V2 — measurement protocol implementation

Implements `docs/specs/002-benchmark-v2/spec.md`. Reproduces what the v1 suite
was missing: replicates + variance + significance, verifiable cost basis,
held-out rubric evaluation, brownfield multi-session series with follow-up
change tasks, process metering, guardrail conformance — with self-declared
limits.

## Layout

```
bench-v2/
├── benchv2/            # package: stats · costs · judge · score · report · runner
├── tasks/
│   ├── hard-greenfield/        # the v1 hard case + held-out rubric tests
│   └── series-1/               # seed repo (debt) + t1..t3 + follow-ups + hidden tests
├── tests/test_v2.py            # unit tests (8) — python -m pytest bench-v2/tests
└── README.md
```

## Run

```bash
# unit tests
python -m pytest bench-v2/tests/test_v2.py -q

# one case, N replicates, arms (subset check first)
python bench-v2/benchv2/runner.py hard-greenfield --arms B A --reps 5 --out bench-v2-out/full
python bench-v2/benchv2/runner.py series-1     --arms B A --reps 5 --out bench-v2-out/full

# regenerate the report from artifacts (byte-identical)
python -c "from benchv2.report import render; from pathlib import Path; render(Path('bench-v2-out/full'), Path('bench-v2-out/full/report.md'))"
```

## What it measures (protocol R-number → output row)

| Requirement | Output |
|---|---|
| R1 replicates | median / IQR / min / max + Mann-Whitney p vs bare |
| R2 cost basis | token volumes per class + basis label (unverified vs provider-priced) |
| R3 held-out rubric | hidden-test pass count (tests the agent never saw) |
| R6 quality | lint (ruff strict, optional) + coverage pct |
| R7 process | terminal, errors, turns, subagents, compute vs wall |
| R8 guardrails | plan-vs-PR conformance (score module) |
| R9/R10 reproducibility/limits | regenerable from artifacts + stated limits |

## Pins

CLI = `fcc-claude`, model = **`glm-5.3-flash`** — pilot pin, operator decision
2026-09-05. The runner **refuses** any other model (non-glm and Claude-family
pins are hard errors), and the run manifest records the actual `BENCH_MODEL`.
NOTE: this differs from the v1 suite pin (`deepseek/deepseek-chat`), so v1 runs
are NOT comparable on the model axis — compare within this pilot only.
~$40–90 total for the full suite; ~2–3 days wall (v1-estimated; glm pricing may
differ — the smoke run establishes the new per-run cost).