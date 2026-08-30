GREENFIELD-1 (E2E) TASK BRIEF (frozen, identical for both arms)

Idea: "Research Request Pipeline" — a user submits a research request; the system queues it, processes it in the background, and the user can watch live status and read the final result.

Build it as a local app:
- Backend: FastAPI + SQLite (file DB in ./data). Endpoints: POST /requests {topic, email} → creates request (status queued); GET /requests/{id} → status + result; GET /requests/{id}/events → SSE stream of status transitions (queued → processing → done | failed).
- Worker: background processing loop (asyncio task started at app startup) that claims queued jobs, simulates work (sleep ~0.2s per request), and marks done with a generated result (echo topic + timestamp).
- Frontend: static HTML/JS single page (no build step): form to submit, list of requests, live status via SSE, auto-refresh.
- Crash-safety: if the process restarts mid-job, the job must NOT be lost or double-completed (claim with status transitions persisted to SQLite; a job crashed while "processing" must be re-claimable).
- Tests (pytest, using a temp DB): submit → status flow, SSE emits the transition sequence, crash-safety (simulate crash by marking processing then restarting worker → job completes exactly once, status done), invalid topic rejected.

Acceptance: `pytest tests/ -q` passes; `uvicorn app.main:app` boots and the frontend page loads.

Do not commit. Leave changes in the working tree.