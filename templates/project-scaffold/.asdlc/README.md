# `.asdlc/` — governed-task runtime artifacts (SPEC-012)

This directory holds machine-readable artifacts produced by the governed
workflows. Files here are **generated at runtime**, not authored by hand.

| Artifact | Produced by | Purpose |
|---|---|---|
| `test-lock.json` | `dev-tdd` test-freezer (`test-lock.mjs create`) | SHA-256 digest of the locked test suite; `verify` fails on any change, added/deleted/renamed file, or symlink until a human-approved `relock` |
| `evidence/<task-id>.json` | `dev-evidence` manifest (`evidence.mjs record` / `finalize`) | One canonical machine-readable evidence manifest per governed task: gates, test-lock status, review verdict, cost provenance, handoff |
| `task-budget.json` | effort/cost governance (later phase) | Declared effort profile and USD budget per task |

Rules:

- Task IDs are immutable after the first evidence artifact is written.
- Locks, manifests, and budgets are namespaced by task ID and may not be
  overwritten by another task.
- Files here store digests and statuses — never credentials, prompts, or raw
  private model output.
- CI validates any committed artifacts (see the asdlc-evidence workflow).
