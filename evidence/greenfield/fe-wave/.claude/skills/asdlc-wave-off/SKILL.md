---
name: asdlc-wave-off
description: Removes the wave-based dev loop and restores the original agentic-sdlc project state — 17 canonical skills, no wave artifacts. Use when the operator says "wave loop off", "remove dev-multi-agent", or wants to recover the canonical state.
---
# asdlc-wave-off — remove the wave dev loop

1. Locate the bundle: the framework fork repo clone on this machine, or clone
   it to a temp dir if absent:
   `git clone https://github.com/trac41799/claude-code-agentic-sdlc <tmp>`
   The bundle is at `<repo>/experiments/wave-dev-loop/`.
2. Run the remover from this project root:
   `bash <bundle>/scripts/wave-remove.sh .`
3. Verify: `.claude/skills/` holds exactly the 17 canonical skills, and no
   `wave-report.md` remains under `.specify/`.
4. Report what was removed — or "nothing installed" if the project was
   already at the original state.

Never write outside this project.