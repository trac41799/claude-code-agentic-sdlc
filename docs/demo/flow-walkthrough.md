# Flow walkthrough — "One request: first command → merged PR"

**Deck:** slide 10 (the three-lane flow diagram: OPERATOR / PRODUCT MANAGER /
DEVELOPER·QA·DEVOPS). Use this file to present the diagram confidently and to
answer whatever the audience throws at you. Cite the deck's evidence slide
numbers where noted.

The diagram tells one story: **the human decides, the team executes, gates
hold.** Everything across the middle lane is produced by agents; everything
that crosses the top lane requires a human.

---

## The flow in ~90 seconds (script)

1. **Human first command** (top lane, green start). You say one thing — "let's
   plan the first feature" — and the team starts.
2. **Empty repo?** (first diamond). New idea → `/asdlc-project` scaffolds the
   project *and* installs the 4-agent team into it. Existing repo →
   `/asdlc-adopt` installs the team into your already-established repository.
   Installation is per-project: nothing lives globally, nothing runs without
   being there. Verify with `/asdlc-doctor`.
3. **Product manager lane** — the pipeline is: capture business context
   (`pm-client-interview`) → record decisions and rules as they surface
   (`pm-constitution-sync`) → write a decision-complete spec
   (`pm-epic-writing`) → run it through an adversarial check against the
   project's own docs (`pm-grill-with-docs`) → hand off a backlog of
   issues (`pm-to-issues`).
4. **Spec approved?** (second diamond, in the operator lane). *You* approve —
   the spec is the contract. "No" loops back to the PM lane to revise.
5. **Developer·QA·DevOps lane** — `dev-feature-plan` turns the issue into
   `impl-plan.md` + `tasks.md`; **Plan approved?** is your second human gate;
   then per task: `dev-tdd` (RED → GREEN → REFACTOR, evidence pasted) →
   `qa-triage` (verification + regression) → **Open pull request**.
6. **Review PR & merge?** (third diamond). Your call. "Yes" → merged, epic
   updated, done. "No" → changes go back through QA until it's right.

Two-phase story: **Phase 1 (spec)** is the PM lane plus your approval.
**Phase 2 (build)** is the dev lane plus your plan approval and PR merge.

---

## The three gates — why they exist

| Gate | What happens | Who decides | It prevents |
|---|---|---|---|
| Spec approved | PM's spec survives the adversarial grill | Operator | work built from an ambiguous brief |
| Plan approved | tasks.md matches a real plan, not vibes | Operator | undeclared mega-PRs and scope creep |
| QA before merge | qa-triage verifies + regression-checks | Agent-verified, operator merges | broken code landing in main |

Every gateway decision leaves the human in control. Nothing auto-approves
itself — that was the v1 lesson (see slide 16: "the fully automated
agent-team" ran overnight with auto-approves and 10 scheduled routines; v2
trades that autonomy for trust; slide 17: v1 → v2 comparison).

---

## Audience-POV questions & reference answers

**Q1. "What does the framework actually do that a model alone doesn't?"**
A: A model alone restarts cold every session and produces one giant diff. The
framework adds: a spec contract, a plan gate, test-first evidence, a QA lane
before merge, and a traceability trail (spec → plan → tasks → QA). The model
still does the thinking; the team makes the work auditable and repeatable.
Evidence: slide 13 (raw bench output) and slide 14 (bare vs passive vs
activated matrix). On the hard case, activated finished 6.5 min / 24 tests
while bare spent 27.4 min and halted at max_turns.

**Q2. "Isn't this just a prompt template company?"**
A: The public plugin is deliberately tiny — four commands or less — but the
per-project install carries workflow skills and agent definitions that encode
the gates. The prompts are where the value lives, and prompts are exactly what
you'd want to be selling: the discipline, not magic. Encourage a mental model:
*the product is the process.*

**Q3. "What makes this different from a RAG-based AI orchestrator?"**
A: The gates, not the orchestration. Spec-first, test-first, QA-before-merge —
each is an auditable artifact on disk, not a hidden pipeline state. You can
read the spec, the plan, the task list, and the QA report after every run
(see docs/specs/ in a project). Reproducibility beats cleverness here.

**Q4. "How does this prevent context loss between sessions?"**
A: The artifacts ARE the context. The spec, plan, tasks, and QA report live in
the repo; each new session re-reads them instead of re-guessing. That's why
handoff fidelity is the framework's structural answer to cold-start sessions —
no memory database needed.

**Q5. "What's the real constraint — model quality or process?"**
A: Process. The benchmark pins the model (DeepSeek-chat via the proxy, same
for both arms) and still finds 4.2× difference on the hard case — that gap is
pure discipline, not model IQ. The model is a commodity; the gates are not.

**Q6. "Can I use this on a codebase I already have?"**
A: Yes — `/asdlc-adopt` installs the team into an existing repo without
touching your code or committing anything. It only seeds the framework files
(agents, skills, rules, and the delegation block) and respects what you
wrote. Verify with `/asdlc-doctor`; keep tinkering on your fork (slide 2: the
official repo is read-only; the recommended fork is our repo).

**Q7. "We have compliance constraints. Is anything recorded silently?"**
A: No. There are no hooks, no background telemetry, no silent logging in the
public plugin. Every action is an explicit step in the lane. Operator gates = 
log. (The privacy/telemetry plugin that company-internal machines use lives
separately, outside this deck's scope.)

**Q8. "What happens if the agent fails mid-flow — say, a broken build?"**
A: The plan gate and QA lane catch it. If the agent produces a spec that's
internally inconsistent, `pm-grill-with-docs` challenges it (and if a build
breaks, the failing test is RED first, never silent). Nothing merges unless
the gates pass — the operator sees exactly where the failure was.

**Q9. "Why 4 agents and not 8, and why no marketing agent?"**
A: The 4-agent team (PM, developer, QA, devops) matches the work that needs
gates. The old automated marketing lanes (writer, designer, email) were
premature and carried maintenance load without measurement — removed in v2
(slide 16). Smaller roster = tighter context budget and fewer moving parts.

**Q10. "How do I try this for real in a week?"**
A: Two POC clients did exactly that: WorkHealthyAustralia (AU healthcare,
janet.care + occuspan.com) and DOXA (US staffing, under NDA). Each went from
zero to a working POC in one week with one engineer of support. For you:
install (`claude plugin marketplace add trac41799/claude-code-agentic-sdlc` +
`claude plugin install agentic-sdlc@agentic-sdlc`), run `/asdlc-doctor`, then
`/asdlc-project`. Full script in docs/demo/live-demo-guide.md.

**Q11. "Why fork first? Your own notes say the demo/what you present comes
from one repo."**
A: Straightforward ownership: benchmark runs and experiments belong on the
fork (`trac41799/claude-code-agentic-sdlc`). The official repo
(`talentedgeai/infinite-leverage`, ex-company) stays a read-only reference —
do not commit anything there. That's honesty about provenance, slide 2.

**Q12. "What are the real limits / what should I not claim?"**
A: Gaps, labeled honestly on slide 18 and the evidence doc:
- Guardrail adherence is **advisory**, not structural (R4 inversion: the
  fragile-refactor arm violated a guardrail when the operator approved).
- SWE-bench-style floor check not run — documented why (capability-floor
  question, marginal information vs cost).
- Case studies are n=2 with confounds (model mix initially drifted; no cost
  tracking at the time).
- Token economy is unmanaged (baseline pending).
Say "we show the gaps too" — it's the most believable part of the pitch.

**Q13. "Would this scale to a larger team / non-code work?"**
A: The framework organizes work by stages that map to standard SDLC —
Requirements, Design, Implement, Test, Deploy, Maintain (slide 9 cycle
diagram). Whether it scales to your org depends on whether your work has those
stages with checkpointable outputs. If it's ad-hoc, the framework's value is
lower — the honest recommendation is to use it where the discipline pays.

**Q14. "What does V2 trade away vs V1?"**
A: V1 ran on autopilot — 10 overnight routines, auto-approve, silent hooks.
V2 trades overnight autonomy for deliberate control: every gate is a human
decision, nothing installs globally, no hooks/telemetry in the plugin.
Measured result: value concentrated on hard engineering, and full
traceability — at the price of no overnight automation or marketing lanes
(slide 17).

---

## One-liners to land

- "The model does the thinking. The team makes it *auditable*."
- "Spec first, tests first, human first — in that order."
- "We don't sell prompts. We sell the gap between a good answer and a good
  answer you can prove."
- "Our benchmark's best line: the framework arm finished 4.2× faster on the
  hard case — and left a traceability trail the bare arm never had."
- "If we're wrong somewhere, the deck shows it: we grade our own claims."

---

## Repo map (handy if someone asks "where is X")

| Thing | Where |
|---|---|
| Framework + plugin | `github.com/trac41799/claude-code-agentic-sdlc` |
| Evidence summary | `docs/benchmarks/BENCHMARK-SUMMARY.md` |
| Bench kit | `bench/` in the repo (one-command repro) |
| Live demo script | `docs/demo/live-demo-guide.md` |
| Client setup (non-technical, 5 prompts) | `docs/guide/CLIENT-SETUP.md` |
| Official origin (read-only) | `github.com/talentedgeai/infinite-leverage` |
| Benchmark product (froam) | FE `froam-journey-platform-fe` · BE `travelbuddy-agentic-be` |