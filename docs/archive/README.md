# Archive — superseded and non-canonical docs

Files here are **not canonical**. They are kept for history, provenance, or
recovery — an agent or operator should never follow them as instructions for
the current framework.

| File | What it is | Why archived |
|---|---|---|
| `2026-06-13-restore-auto-update-hook.md` | v1-era plan | Describes the v1 global-install system (SessionStart hooks, `il_telemetry`, 8 agents, `~/.claude/.infiniteleverage-version`). Directly contradicts v2's hard rules: no hooks, no telemetry, nothing installs globally. Kept only as v1 history. |
| `2026-06-21-init-skill-overhaul.md` | v1-era plan | Reworks the retired `infiniteleverage-init/onboard/patch` skills, 8 agents, schedules, Codespaces, Gemini/Resend. None of it exists in v2. Kept only as v1 history. |
| `LARK-CLI-SETUP.md` | Personal machine guide | A machine-specific setup guide (local username paths, broad-access CLI auth) for an unrelated tool. Personal notes, not framework documentation — moved out of `docs/guide/`. |
| `design-system.md` | Orphaned styling reference | Nothing references it, and its agent color map still lists the retired `web-publisher` agent (v2 has 4 agents; publishing is folded into developer). Recover the tokens here if a future styling pass needs them. |

> The raw meeting transcript (`presentation-transcript.md`) was archived here and
> then removed from the repo entirely in the same cleanup — it never should have
> been committed. The curated outputs live in `docs/demo/`.

Rules for this directory:

- Nothing here is loaded, installed, or copied by any skill or the scaffold.
- When archiving a file, move it here with `git mv` (history is preserved) and
  add a row to the table above.
- When deleting an archive entry for good, remove the row too.
