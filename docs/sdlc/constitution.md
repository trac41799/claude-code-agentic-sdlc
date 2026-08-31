# Constitution — Agentic SDLC (fork experiment)

Non-negotiable principles, derived from `CLAUDE.md` hard rules, `AGENTS.md`
routing, and the deck's evidence-grading policy. Every spec, plan, and task is
judged against these.

1. **Nothing installs globally.** No file in this repo may write into
   `~/.claude/` (or `$HOME/.claude/`). All change is project-scoped.
2. **No permissions grants.** No code or skill may touch the `permissions`
   key in any settings file. The `Bash(*)` grant is the reason v2 exists.
3. **Tests first, evidence-gated.** Every behavior change has its failing
   test written before the implementation (RED). "Done" = gates passed with
   pasted evidence, never a bare claim.
4. **Change via PR; experiments on exp branches.** Nothing commits to `main`
   without review. Experimental work lives on `exp/*` branches and never
   contaminates the canonical state.
5. **No telemetry or hooks in the public repo.** That belongs in the private
   telemetry plugin.
6. **Surgical fidelity.** Reintroductions copy the original design verbatim;
   only immature assumptions get closed. No novel improvements, no invented
   features — a flawed design must not be faked.
7. **Honest evidence.** Claims are graded (VERIFIED / CASE STUDY / RATIONALE /
   PLANNED) and gaps are labeled, never hidden.