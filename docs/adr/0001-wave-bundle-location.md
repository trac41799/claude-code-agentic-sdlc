# ADR-0001 — Wave bundle location

## Context

Reintroducing the v1 `dev-multi-agent` skill into V2 as an experiment requires
a home that (a) keeps the canonical 17-skill set untouched, (b) makes
one-command removal structurally trivial, and (c) never re-installs via
`/asdlc-adopt`. Candidates: the plugin payload, `.claude/skills/`, or a
standalone experiments directory.

## Decision

Ship the bundle under `experiments/wave-dev-loop/` in the framework repo.
Toggle skills (`asdlc-wave-on` / `asdlc-wave-off`) copy/remove the skills into
a project's `.claude/skills/` via deterministic scripts. Nothing else in the
repo references the bundle.

## Status

Accepted (exp branch only).

## Consequences

- Canonical structure is structurally guaranteed: `.claude/skills/` (17) and
  `plugin/` (4 commands) never change.
- Removal is a fixed-path delete (skills + `wave-report.md` artifacts);
  no agent-file patching.
- Cost: the wave loop is not discoverable by default — operators opt in per
  project; the developer agent does not list it (matches v1 fidelity: invoked
  on demand).
- `/asdlc-adopt` refreshes will never resurrect the experiment — which is
  exactly the clean-recovery property required.