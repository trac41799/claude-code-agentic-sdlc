# QA Report — Research Request Pipeline

**Date:** 2026-08-31
**Reporter:** QA agent (verification pass on Developer handoff)
**Feature:** `research-request-pipeline`
**Classification:** verification / triage of handoff
**Verdict:** ✅ APPROVED — all acceptance criteria pass; no P0/P1 issues

---

## Verification run

Command: `pytest tests/ -q`

```
13 passed in 1.02s
```

| AC | Criterion | Result |
|----|-----------|--------|
| AC-1 | POST creates `queued` request | ✅ `test_submit_creates_queued_request` |
| AC-2 | Empty/whitespace topic → 400 | ✅ `test_invalid_topic_rejected` |
| AC-3 | Invalid email → 400 | ✅ `test_invalid_email_rejected` |
| AC-4 | GET by id / 404 for unknown | ✅ `test_get_missing_request_returns_404` |
| AC-5 | SSE emits `queued → processing → done` | ✅ `test_sse_emits_transition_sequence` |
| AC-6 | Worker completes with topic-echoing result | ✅ `test_submit_to_done_flow` |
| AC-7 | Crash → restart → exactly-once `done` | ✅ `test_crash_restart_recovers_job_exactly_once`, `test_queued_job_survives_restart` |
| AC-8 | `/` serves frontend | ✅ `test_frontend_served` |
| NFR | `uvicorn app.main:app` boots; page loads | ✅ live check (HTTP 200, HTML) |

Test pyramid applied: unit/integration via httpx ASGI client over a temp
SQLite DB per test; crash-safety simulated by persisting `processing` state
then starting a fresh worker; SSE verified as a live event stream.

## Triage of observed considerations

No defects were found in the tested contract. One design consideration was
reviewed during the pass:

- **SSE stream ends at a terminal state** (the generator returns after the
  `done`/`failed` frame).
  - **Classification:** `ux-degradation` (works correctly; the stream closes
    by design once the request is terminal).
  - **Priority:** P3 (Score: 2 × 1 × 1 = 2)
    - Severity: 2 — cosmetic; polling fallback + `closeWatch` in the frontend
      already reconcile terminal cards.
    - Frequency: 1 — every request ends terminal, but this is the intended
      lifecycle.
    - Blast: 1 — single-user local tool.
  - **Route decision:** PM review → accepted by design. No change required;
    the frontend closes the EventSource on terminal status, and the 5s polling
    fallback is the reconciliation path. Not a bug.

## Route decision

No bugs to assign. Feature passes QA; ready for operator review in the
working tree (nothing committed, per task instruction).

## Notes for follow-up features

- Real research execution / email delivery.
- Multi-worker horizontal scaling would require a lease/heartbeat on the
  `processing` claim (currently safe because a single worker exists per app).
