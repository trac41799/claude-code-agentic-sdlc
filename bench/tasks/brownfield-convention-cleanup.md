BROWNFIELD-B TASK BRIEF (frozen — project-agnostic, works on ANY repo)

Do a code-convention cleanup pass on this repo: find and fix THREE clear convention violations (naming style, dead code, leftover debug prints, TODO leftovers, inconsistent docstrings), each with evidence.

- Pick concrete, defensible violations; state each as file:line → fix.
- Verify the repo still passes its existing test suite (run it and report the tail).
- Do not touch dependency files, CI config, or anything unrelated to the three fixes.
- Do not commit. Leave changes in the working tree.

Acceptance: the repo's existing test suite still passes; the three fixes are listed with file:line evidence.