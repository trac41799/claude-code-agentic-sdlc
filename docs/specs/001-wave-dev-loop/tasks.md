# Tasks — wave-dev-loop

Baseline: run the CI-equivalent gates locally (T1) and record the result here
before any implementation task starts.

## T1 [P] Baseline gate — files: (none) — acceptance: spec.md checklist
— test: run CI-equivalent checks locally (manifest JSON, version lockstep,
no-global-install grep, 4/17 counts, frontmatter, plan-protocol node tests)
— record `baseline: N passed / M failed` below.
- task: execute the CI steps against the working tree and paste results into
  this file's baseline line.

## T2 Setup — files: exp branch, docs/specs/001-wave-dev-loop/, docs/adr/0001,
docs/sdlc/constitution.md — acceptance: spec.md (files exist) — test: n/a (docs)
- task: create the exp branch artifacts (done in authoring); verify
  `git status` clean on `exp/wave-dev-loop`.

## T3 [P] wave-install.sh — files: experiments/wave-dev-loop/scripts/wave-install.sh
— acceptance: spec.md R1 — test: tests/test_wave.py::test_install_adds_three_and_preserves_canonical
- task: write the FAILING test first (17 → 20 skills in a staged project,
  canonical skill hashes unchanged), then implement the script.

## T4 [P] wave-remove.sh — files: experiments/wave-dev-loop/scripts/wave-remove.sh
— acceptance: spec.md R2, E1, E2 — test: tests/test_wave.py::test_remove_restores_17_and_idempotent
- task: failing test first (20 → 17, wave-report.md artifacts gone, second run
  no-op; partial-install case removes remnants), then implement.

## T5 [P] Wave skill content — files: experiments/wave-dev-loop/SKILL.dev-multi-agent.md,
skills/asdlc-wave-on/SKILL.md, skills/asdlc-wave-off/SKILL.md — acceptance:
spec.md R3–R8 — test: tests/test_wave.py::test_v1_sections_verbatim_and_gaps_present +
frontmatter name==dir checks
- task: failing tests first (v1 sections present & unchanged vs 66dc6a2 source;
  R4–R8 gap sections present with required markers; frontmatter valid; no
  ~/.claude writes per CI grep), then author the skill files.

## T6 [P] benchkit wave integration — files: bench/benchkit.py — acceptance:
spec.md R9 — test: tests/test_wave.py::test_benchkit_install_wave_and_activation
- task: failing test first (install_framework(wave=True) → 20 skills;
  wave activation text contains the dispatch instruction), then implement.

## T7 [P] greenfield --wave — files: bench/greenfield.py — acceptance: spec.md
R9 — test: tests/test_wave.py::test_greenfield_wave_flag
- task: failing test first (argparse accepts --wave, fresh_repo installs
  bundle, activation flag flows), then implement.

## T8 Docs — files: experiments/wave-dev-loop/README.md,
experiments/wave-dev-loop/BENCH-WAVE.md (template) — acceptance: spec.md
(checklist) — test: n/a (docs; frontmatter-free)
- task: write README (what/why/toggle/how to bench), evidence template.

## T9 [P] Bench runs — files: greenfield-wave/{be,fe,db,e2e}-wave-a.json + gate
output — acceptance: spec.md R10 — test: n/a (measured runs; E3 records failure)
- task: verify fcc pin with a 1-turn probe, then run `bench/greenfield.py
  --wave` for all 4 frozen cases on the fork's bench kit; paste JSON metrics
  + gate lines into BENCH-WAVE.md.

## T10 Evidence — files: experiments/wave-dev-loop/BENCH-WAVE.md — acceptance:
spec.md (checklist; honest grading) — test: n/a (evidence doc)
- task: A+wave vs existing A/B comparison table, interpretation, confounds.

## T11 Ship — files: (repo state) — acceptance: spec.md (all) — test: sdd-gates
- task: run sdd-gates (lint/typecheck-equivalents, full tests, checklist,
  spec↔code gap), commit `exp/wave-dev-loop`, push; verify `main` untouched.

---
baseline: 5/5 gates passed — manifests ok, lockstep 2.8.0, 4 agents/17 skills, frontmatter n/a (checked in CI), plan-protocol node suite green (0 fail)