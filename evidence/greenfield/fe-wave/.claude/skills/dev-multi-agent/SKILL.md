---
name: dev-multi-agent
description: >-
  Breaks a large, complex task into independent pieces and works on multiple parts simultaneously, then brings the results together. Use for big features or refactors that touch many files — it dramatically reduces the time needed for large tasks.
---

# Developer: Multi-Agent Delegation

Use for complex tasks that can be decomposed into independent work items.

## Wave Execution Model

```
Wave 1: [Agent A] [Agent B] [Agent C]   ← independent, parallel
           ↓          ↓          ↓
         done        done        done
                     ↓
Wave 2: [Agent D] [Agent E]            ← depends on Wave 1 outputs
```

Waves are sequential — Wave 2 starts only after Wave 1 is fully resolved. Within a wave, all agents run concurrently and independently.

## Sub-Agent Prompt Template

Every sub-agent prompt must include:

```
You are working on [specific scope]. Your goal: [single deliverable].

Context:
- [relevant background]
- [error messages / failing tests / requirements]

Constraints:
- Do NOT modify [files/systems outside scope]
- Do NOT ask clarifying questions — make the best call and document your reasoning

When done, return:
- Decision made / root cause
- Files created or modified (path + one-line description)
- Any caveats or follow-up items
```

## When to Use Parallel Dispatch

| Situation | Action |
|-----------|--------|
| 2+ independent failures/tasks | Dispatch one agent per domain |
| Tasks share state or depend on each other | Sequential agents or single agent |
| Single problem, unclear root cause | Single agent investigates first |
| Agents would edit the same files | Do NOT dispatch in parallel |

## Coordinator Responsibilities
- Decompose task into independent domains before Wave 1
- Craft complete, self-contained agent prompts before each wave
- Collect and synthesize all agent outputs after each wave
- Check for conflicts between agent changes
- Decide whether a Wave 2 is needed
- Write unified summary after all waves complete

## Integration Check
After all agents complete, produce a unified summary:
- Conflicts found: none / [list]
- Follow-up waves needed: none / [describe]

---

## [V2-REINTRO R4] Wave plan gate — derived from tasks.md

The coordinator derives the wave plan from the project's
`.specify/features/{slug}/tasks.md` (dev-feature-plan output). Group tasks
into waves so that every wave contains only tasks with DISJOINT file scopes —
no file may appear in two scopes in the same wave. Present the wave plan
(waves, scopes, per-wave agents) to the operator and wait for approval before
Wave 1. A wave with zero independent tasks runs as one sequential wave.

## [V2-REINTRO R5] Post-wave conflict check

After each wave: (1) verify every sub-agent's reported files are within its
declared scope; (2) run `git status --porcelain` and check every changed or
untracked path against the wave's scope map; (3) revert or re-queue
out-of-scope changes into a later wave. No wave starts until the previous
wave's checks are clean.

## [V2-REINTRO R6] Sub-agent failure path

If a sub-agent fails to return, returns without its contract, or its work does
not verify: the coordinator re-runs that item SEQUENTIALLY (single agent, same
scope) in a later wave, or aborts the run with a written reason in the wave
report. Never proceed silently; never auto-approve a failed item.

## [V2-REINTRO R7] Unified summary location

When all waves complete, write the unified summary (conflicts found /
follow-up waves needed) to `.specify/features/{slug}/wave-report.md`.

## [V2-REINTRO R8] Suite gate per wave

After each wave, run the project test suite. If it is red, fix it before the
next wave starts.