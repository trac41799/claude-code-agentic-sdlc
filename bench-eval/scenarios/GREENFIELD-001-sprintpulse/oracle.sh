#!/usr/bin/env bash
# SprintPulse acceptance gate — GREENFIELD-001.
# Enforces the deliverable evidence contract (D1-D6) + build + tests.
# Exit 0 only when every deliverable exists AND the app builds AND all tests pass.
set -u
cd "$(dirname "$0")"
fail=0

echo "== GREENFIELD-001 oracle =="

# D1 codebase
if [ -d app ] && find app -name "*.py" | grep -q .; then echo "D1 code:        PASS"; else echo "D1 code:        FAIL"; fail=1; fi
# D2 docs
if [ -s README.md ] && [ -s docs/product/product.md ]; then echo "D2 docs:        PASS"; else echo "D2 docs:        FAIL"; fail=1; fi
# D3 task tracking
if [ -s docs/plans/tasks.md ]; then echo "D3 tracking:    PASS"; else echo "D3 tracking:    FAIL"; fail=1; fi
# D4 test suite
if ls tests/*_test.py tests/test_*.py >/dev/null 2>&1 || find tests -name "*.py" | grep -q .; then echo "D4 tests dir:   PASS"; else echo "D4 tests dir:   FAIL"; fail=1; fi
# D5 test results artifact
if [ -s docs/qa/test-results.txt ] || [ -s docs/qa/test-results.md ]; then echo "D5 results:     PASS"; else echo "D5 results:     FAIL"; fail=1; fi
# D6 CI config
if [ -s .github/workflows/ci.yml ]; then echo "D6 CI:          PASS"; else echo "D6 CI:          FAIL"; fail=1; fi

# Build + tests
if python -c "import sys; sys.path.insert(0,'.'); import app" >/dev/null 2>&1; then
  echo "app imports:   PASS"
else
  echo "app imports:   FAIL (trying app dir on path)"
  if PYTHONPATH=. python -c "import app" >/dev/null 2>&1; then echo "app imports:   PASS"; else echo "app imports:   FAIL"; fail=1; fi
fi

if python -m pytest tests/ -q >/dev/null 2>&1; then
  echo "pytest:        PASS"
else
  echo "pytest:        FAIL"; fail=1
fi

echo "== oracle verdict: $([ $fail -eq 0 ] && echo PASS || echo FAIL) =="
exit $fail
