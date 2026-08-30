# Bench kit — reproduce the benchmarks

The measured numbers on the deck's results slide come from this kit. Everything is
project-agnostic for brownfield (run it on ANY repo the framework is installed in)
and fresh-folder for greenfield. Cross-platform Python; runs the `claude` CLI
(or `fcc-claude` proxy — set `BENCH_CLI`).

## Setup

```bash
# In the framework repo (this directory IS bench/)
export BENCH_CLI=claude            # or fcc-claude
export BENCH_MODEL=sonnet          # same pin for both arms of a run
```

## Brownfield (any repo with the framework installed)

On the target repo, first install the team if not already present:
`/asdlc-adopt` (or auto-install via `--install-framework .`).

```bash
# Task template: add unit tests to an untested function
python bench/brownfield.py \
  --repo /path/to/your-repo \
  --task bench/tasks/brownfield-add-tests.md \
  --gate "pytest tests/ -q" \
  --out bench-out/brown-a \
  --install-framework .

# Task template: convention cleanup (three evidence-backed fixes)
python bench/brownfield.py \
  --repo /path/to/your-repo \
  --task bench/tasks/brownfield-convention-cleanup.md \
  --gate "pytest tests/ -q" \
  --out bench-out/brown-b
```

The gate must match your repo's test runner (pytest/node/npm test/go test/...).
The runner: creates a scratch clone at the same commit for the bare arm (framework
stripped), runs both arms with the identical frozen brief, meters (turns/tokens/
cost/wall), runs the gate, prints the A-vs-B table and the A-arm's `.specify/`
traceability artifacts.

## Greenfield (fresh folders, idea briefs)

```bash
python bench/greenfield.py \
  --base /tmp/gf-runs --name run1 \
  --task bench/tasks/greenfield-e2e-pipeline.md \
  --gate "pytest tests/ -q" \
  --out bench-out/gf-run1

python bench/greenfield.py \
  --base /tmp/gf-runs --name run2 \
  --task bench/tasks/greenfield-fe-feed.md \
  --gate "node --test tests/" \
  --out bench-out/gf-run2

python bench/greenfield.py \
  --base /tmp/gf-runs --name run3 \
  --task bench/tasks/greenfield-be-sse.md \
  --gate "pytest tests/ -q" \
  --out bench-out/gf-run3

python bench/greenfield.py \
  --base /tmp/gf-runs --name run4 \
  --task bench/tasks/greenfield-db-etl.md \
  --gate "pytest tests/ -q && python etl/perf_test.py" \
  --out bench-out/gf-run4
```

Creates `{base}/{name}-a` (framework team installed) and `{base}/{name}-b`
(bare), both fresh `git init` folders — nothing else on disk is touched.

## Methodology (read before trusting numbers)

- Same model pin, identical frozen task text per arm, same tooling flags, isolated
  config dirs (set `CLAUDE_CONFIG_DIR` yourself if you need isolation).
- Arms: B bare · A framework activated (routing + lanes, the framework's own directive).
- Metering from session JSON: turns, tokens in/out, cost, wall time; outcome gate run
  verbatim.
- A-arm process artifacts (`.specify/*`) = traceability evidence; B-arm should have none.
- Known confounds: model pin changes between epochs invalidate cross-epoch token totals;
  trivial tasks show ceremony tax; guardrail adherence is advisory (R4 finding).

## Reference runs

The deck's numbers: R1–R4 incremental on the Froam project + 4 greenfield cases
(E2E pipeline / FE feed / BE SSE proxy / DB+ETL 1M rows). Full docs and session
JSONs: `docs/benchmarks/` and the Froam exp-branch clones.