---
name: asdlc-wave-on
description: Installs the v1 wave-based parallel implementation loop (dev-multi-agent) into this project — exactly three skills, nothing else changes. Use when the operator says "wave loop on", "install dev-multi-agent", or wants wave dispatch for a large task.
---
# asdlc-wave-on — install the wave dev loop

The wave loop is an experiment shipped from the fork's
`experiments/wave-dev-loop/` bundle. Installing it adds exactly three skills
to this project's `.claude/skills/` — `dev-multi-agent`, `asdlc-wave-on`,
`asdlc-wave-off` — and modifies nothing else.

1. Locate the bundle: the framework fork repo clone on this machine, or clone
   it to a temp dir if absent:
   `git clone https://github.com/trac41799/claude-code-agentic-sdlc <tmp>`
   The bundle is at `<repo>/experiments/wave-dev-loop/`.
2. Run the installer from this project root:
   `bash <bundle>/scripts/wave-install.sh <bundle> .`
3. Verify: `ls .claude/skills/` shows the 17 canonical skills plus
   `dev-multi-agent`, `asdlc-wave-on`, `asdlc-wave-off`. Report the count.
4. To remove later, run `/asdlc-wave-off`.

Never write outside this project.