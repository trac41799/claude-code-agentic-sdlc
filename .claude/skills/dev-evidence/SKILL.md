---
name: dev-evidence
description: Produces and validates the machine-readable evidence manifest for a governed task (SPEC-012 FR-003). Use when a task has an approved plan, when verification gates run, when a handoff or PR is being prepared, when the operator says "record evidence", "finalize handoff", "evidence manifest", or when CI reports an invalid manifest. Every governed task ends with exactly one manifest at .asdlc/evidence/<task-id>.json; prose summaries link to it instead of duplicating measurements.
---

# Dev Evidence — manifest per governed task

One machine-readable evidence manifest per governed task. The manifest is the
authoritative index for the task handoff; human-readable handoff summaries link
to it. A governed task is one with an approved implementation plan (or a task
explicitly marked `governed: true`).

Engine: `.claude/skills/dev-evidence/assets/evidence.mjs` (dependency-free,
`node:` builtins). Schema: `assets/evidence-manifest.schema.json` (versioned).

## Workflow

```
1. First gate result — manifest is created automatically:
   node .claude/skills/dev-evidence/assets/evidence.mjs record --task <task-id> \
     --gate <name> --status <passed|failed|skipped|not-run> [--command <cmd>] [--reason <text>]
2. Record the task metadata as it becomes known:
   node .claude/skills/dev-evidence/assets/evidence.mjs meta --task <task-id> \
     [--head-commit <sha>] [--changed-paths <csv>] [--plan-path <p>] [--plan-status <s>] \
     [--test-freeze <status>] [--review <status>] [--reviewer <x>] [--handoff <p>] \
     [--cost <measured|estimated|unavailable>] [--actual <usd>] [--cost-source <x>]
3. At handoff, finalize — this stamps provenance and validates everything:
   node .claude/skills/dev-evidence/assets/evidence.mjs finalize --task <task-id> \
     [--plugin-version <v>]
4. CI validates any committed manifest (template: `.github/workflows/asdlc-evidence.yml`):
   node .claude/skills/dev-evidence/assets/evidence.mjs validate --task <task-id> [--strict]
```
`validate` without `--strict` checks structural rules (statuses, skip reasons,
cost states) — safe for work-in-progress manifests. `--strict` additionally
requires the full minimum schema (headCommit, changedPaths, plan, review) and is
what CI runs on finalized manifests (those claiming governed completion).

## Hard rules

- Every gate status is one of `passed`, `failed`, `skipped`, `not-run`.
- `skipped` always carries a reason. `not-run` is a failure for mandatory gates
  and an explicit limitation for optional ones.
- Cost status is `measured`, `estimated`, or `unavailable`. Unknown cost is
  `unavailable` — never zero and never a fabricated estimate.
- `measured` cost requires `actualUsd`; `unavailable` requires `actualUsd: null`.
- The manifest stores digests, paths, statuses, and reasons — never prompts,
  credentials, or raw private model output.
- Exactly one manifest path per task (`.asdlc/evidence/<task-id>.json`); task
  IDs are immutable after the first artifact; concurrent tasks never overwrite
  each other.
- A handoff that cannot point at a valid manifest is not a handoff — fix or
  record the limitation before claiming completion.
