# Requirements checklist — wave-dev-loop

## Completeness
- [x] 1. Every requirement has an actor and trigger (R1–R10, EARS; operator/developer/bench).
- [x] 2. Every requirement has exactly one testable acceptance criterion (AC listed per R).
- [x] 3. Non-goals and out-of-scope explicit and dated (2026-08-31).
- [x] 4. No `[NEEDS CLARIFICATION]` markers — clarify answers recorded in Assumptions.
- [x] 5. External dependencies named: fcc proxy (deepseek-chat pin), frozen briefs, bench kit.
- [x] 6. Failure behavior specified: E3 (failed arm recorded), E2 (partial install), R6 (sub-agent failure path).

## Consistency
- [x] 7. No requirement contradicts another (R1–R2 install/remove are inverses; R9–R10 harness).
- [x] 8. No requirement contradicts the constitution (no global install, no permissions, tests-first, exp-branch-only).
- [x] 9. Terms consistent: wave, scope, coordinator, bundle across spec/plan/tasks.
- [x] 10. Milestones cover every requirement: M1→R1–R8, M2→R9, M3→R10, M4→ship.
- [x] 11. Every task's AC pointer resolves: T3→R1, T4→R2, T5→R3–R8, T6→R9, T7→R9, T9→R10.

## Testability
- [x] 12. Criteria observable from outside: skill counts, file hashes, JSON metrics, gate output.
- [x] 13. Deterministic: 17→20→17 counts, hashes, fixed paths — no "fast/robust" claims.
- [x] 14. Each criterion expressible as one automated test: pytest cases named per task.
- [x] 15. Edge cases have criteria: E1/E2 → R2 tests; E3 → R10 recording; E4 → report field.

## Plan quality
- [x] 16. Chosen approach AND rejected alternative stated (experiments dir vs plugin vs canonical).
- [x] 17. No implementation detail in plan.md beyond architecture delta (scripts live in tasks).
- [x] 18. Risks have mitigations (probe before bench, failure recording, verbatim-diff test, residue test).
- [x] 19. Milestones independently shippable (M1 leaves suite green; M2 adds harness only).

## Tasks quality
- [x] 20. Dependency-ordered (T1 baseline → T2 setup → T3/T4/T5 parallel [P] → T6/T7 [P] → T8 → T9 → T10 → T11).
- [x] 21. Independent tasks marked [P]: T1, T3, T4, T5, T6, T7, T9.
- [x] 22. First task of each behavior is its failing test (T3–T7 all "failing test first").
- [x] 23. Every task names concrete files and its test.
- [x] 24. Baseline snapshot recorded (T1 fills the line in tasks.md).
- [x] 25. No task exceeds ~30 min of agent work (T9 is the exception: measured runs, by nature).