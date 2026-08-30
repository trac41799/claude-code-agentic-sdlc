BROWNFIELD-A TASK BRIEF (frozen — project-agnostic, works on ANY repo)

Find an existing pure function or small service module in this repo that currently has NO unit-test coverage, and add unit tests for it.

- Choose the target yourself: a function/module with real logic (not a trivial getter). State the choice in your summary with the file:line.
- Follow the repo's existing test conventions (framework, markers, location). If the repo has no test framework at all, add pytest with the minimal dev dependency noted in the summary.
- Run the new tests and confirm they pass. Do not modify the target's production behavior.
- Do not commit. Leave changes in the working tree.

Acceptance: the new test file passes with the repo's test runner (run the exact command you used and report its output tail).