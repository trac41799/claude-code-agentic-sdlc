# QA plan — Research Request Pipeline

## Test pyramid
- **Unit-level**: status transition functions against a temp SQLite DB
  (`tests/test_crash_safety.py`, `tests/test_flow.py`).
- **Integration**: HTTP flow via `TestClient` — submit, list, lookup, SSE
  (`tests/test_flow.py`, `tests/test_sse.py`, `tests/test_validation.py`).
- **E2E smoke** (manual): `uvicorn app.main:app` boots, `GET /` serves the page,
  `curl -N` SSE shows `queued → processing → done`.

## Acceptance criteria → test mapping

| Criteria | Test | Status |
|---|---|---|
| `pytest tests/ -q` passes | whole suite | PASS (17/17) |
| `uvicorn app.main:app` boots + page loads | boot smoke, `GET /` → 200 | PASS |
| Submit → queued | `tests/test_flow.py::test_submit_creates_queued_request` | PASS |
| Status flow to done with result | `tests/test_flow.py::test_status_flow_reaches_done` | PASS |
| List endpoint | `tests/test_flow.py::test_list_includes_submitted` | PASS |
| SSE exact sequence `queued→processing→done` | `tests/test_sse.py::test_sse_emits_full_transition_sequence` | PASS |
| SSE history replay for finished request | `tests/test_sse.py::test_sse_replays_history_for_finished_request` | PASS |
| Crash-safety: processing job re-claimed, done once | `tests/test_crash_safety.py::test_processing_job_reclaimed_and_completes_once` | PASS |
| No double-complete under restart | `tests/test_crash_safety.py::test_done_job_not_reprocessed_on_restart` | PASS |
| Invalid/blank topic → 4xx | `tests/test_validation.py` | PASS |

## Regression watch-list
- **Atomic claim**: `claim_next_job` must never hand the same queued job to two
  workers — guarded by the process-wide lock and the `WHERE status='queued'`
  predicate (`app/db.py`).
- **Exactly-once complete**: `complete_job` only transitions rows that are
  currently `processing`, so a completed job cannot be double-completed
  (`app/db.py:complete_job`).
- **Recovery scope**: `recover_crashed_jobs` only touches `processing` rows,
  never `done`/`failed` (`app/db.py:recover_crashed_jobs`).

## Known limits
- SSE history is in-memory and resets on process restart; a client connecting
  after a restart sees current DB status, not pre-restart history. Not a
  data-integrity issue — SQLite remains the source of truth.
