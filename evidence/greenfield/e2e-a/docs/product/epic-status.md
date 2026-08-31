# Epic status — Research Request Pipeline

Updated: 2026-08-29

| Epic | Status | Verified by |
|------|--------|-------------|
| Epic 1 — Request intake & validation | DONE | `tests/test_validation.py` (blank/missing topic → 4xx), `tests/test_flow.py::test_submit_creates_queued_request` |
| Epic 2 — Background worker | DONE | `tests/test_flow.py::test_status_flow_reaches_done`, live smoke test (`POST /requests` then `GET /requests/{id}` shows `done`) |
| Epic 3 — Crash-safety & recovery | DONE | `tests/test_crash_safety.py` (processing job reclaimed → done exactly once; done job not reprocessed) |
| Epic 4 — Live status via SSE | DONE | `tests/test_sse.py` (exact sequence `queued → processing → done`), live `curl -N` capture |
| Epic 5 — Static frontend | DONE | `uvicorn app.main:app` boots; `GET /` returns 200 and serves `app/static/index.html` |

## Known limits
- SSE history is in-memory (`app/bus.py:EventBus`), so a client connecting after
  a full process restart sees the current DB status rather than the pre-restart
  history. The SQLite row is always the source of truth.
