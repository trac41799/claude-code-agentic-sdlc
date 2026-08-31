---
name: dev-agent-router
description: >
  Adopts a specialist agent persona and routes execution for a request whose
  class belongs to one of the four lanes (product-manager, developer, qa,
  devops). Use when the request spans an agent lane, when subagent
  registration is unavailable (e.g. `--agent` not found for a project agent),
  when the delegation block cannot reach the agent tool, or when the operator
  says "route this", "adopt the X agent", or "@developer"-style delegation.
  Always falls back to reading the agent card file and following the lane
  rules in-context — delegation is persona adoption, not just dispatch.
---

# Agent Router — lane delegation without registration

The delegation block in `CLAUDE.md` lists the four lanes. **This skill is the
mechanical fallback that makes delegation work even when subagents are not
registered** (some harnesses cannot load project agents).

## Steps

1. **Identify the lane.** Read `CLAUDE.md`'s agent-delegation block; pick
   exactly one lane (or ask the operator if ambiguous).

2. **Read the agent card.** Load `.claude/agents/<lane>.md` — the persona,
   hard rules, and skill index are the source of truth for HOW to execute.

3. **Adopt the persona in-context.** Run the request as that agent: its
   rules, its skills, its output conventions. Report the adopted lane and the
   evidence trail.

4. **Delegation for real.** If subagents ARE registered (`--agent developer`
   resolves, or the agent tool lists the lane), dispatch to the registered
   agent instead — this skill only fills the gap, never replaces native
   delegation when it works.

5. **Hard rules always**: no start without an approved plan · nothing
   committed without the operator · all change via PR · no self-merge · QA
   verifies before merge.

## Cross-checks the router must enforce per lane

| Lane | When invoked | Must produce |
|---|---|---|
| product-manager | roadmap/spec/epic work | decision-complete spec + operator approval |
| developer | implementation/bugs/publishing | plan → RED proof → GREEN → refactor evidence |
| qa | verification/regression | triage verdict or regression-suite evidence |
| devops | CI/CD/infra | pipeline state + guardrail check |
