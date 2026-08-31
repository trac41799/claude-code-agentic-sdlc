# RED Evidence — Research Request Pipeline

**Step:** dev-tdd, Task 1.2 (tests written before any implementation code)
**Date:** 2026-08-31
**Command:** `python -m pytest tests/ -q`
**Expected failure:** `ModuleNotFoundError: No module named 'app'`

## Capture

Tests were written first, covering AC-1…AC-8 (submit flow, SSE sequence,
crash-safety, invalid topic/email, frontend served). No `app/` package existed
yet. The suite fails at collection with the expected import error:

```
ImportError while loading conftest 'D:\TRANSFER DATA\Coding\OpenCode\froam-bench\greenfield-wave\e2e-wave\tests\conftest.py'.
tests\conftest.py:11: in <module>
    from app.main import create_app
E   ModuleNotFoundError: No module named 'app'
```

## Why this is a valid RED

- Fails for the **right reason** — the implementation package is absent, not a
  broken test or a wrong assertion.
- Test files present: `tests/conftest.py`, `tests/helpers.py`,
  `tests/test_api.py`, `tests/test_sse.py`, `tests/test_crash_safety.py`.
- Implementation files (per Task 1.3): **none** existed at this point.

## Gate to GREEN

Implement `app/` (db, worker, events, main, config) and `app/static/index.html`,
then re-run the suite. Task 1.3 / Task 1.4.
