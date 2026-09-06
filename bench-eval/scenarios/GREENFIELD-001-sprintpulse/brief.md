# Product brief — SprintPulse

Build a complete, working product from this brief. Everything the brief lists as
a deliverable must exist and work. Do not invent scope beyond this brief; do not
add authentication, external services, or deployment.

## Product

SprintPulse is a small internal team tool: a REST API + minimal web UI that
tracks work items ("tickets") and reports per-sprint summary metrics.

## Functional requirements

FR-1 **Tickets.** `POST /api/tickets` creates a ticket `{id, title, status, points, created_at, resolved_at}`.
- `status` ∈ `open | in_progress | resolved`.
- `points` ∈ 1..13 (Fibonacci scale: 1,2,3,5,8,13); reject others with 400.
- `created_at` is set by the server (ISO-8601 with timezone offset).
- `resolved_at` is `null` until the ticket is resolved.

FR-2 **Resolve.** `PATCH /api/tickets/{id}` sets `status=resolved` and stamps `resolved_at` (server time).

FR-3 **List.** `GET /api/tickets` returns all tickets, newest first.

FR-4 **Sprint summary.** `GET /api/sprints/{sprint_id}/summary` aggregates the tickets whose
`created_at` falls inside the sprint window `[start, end]`:
- `total_points`, `resolved_points` (points of tickets resolved within the same window),
- `open_count`, `resolved_count`,
- `cycle_time_hours` = mean of `(resolved_at - created_at)` in hours for resolved tickets in the window.

FR-5 **Timezone correctness (the trap).** Sprint windows are defined in the **project timezone**,
read from the `SPRINTPULSE_TZ` environment variable (IANA name, default `UTC`). Ticket timestamps
may arrive with any offset. Aggregation must be computed in the project timezone — a ticket created
at `2026-09-05T23:30:00+02:00` belongs to the sprint whose window contains `2026-09-05T21:30:00Z`.
A test that checks a non-UTC window will fail if this is handled naively.

FR-6 **UI.** `GET /` serves a single HTML page that lists tickets and shows the current sprint's
summary (no styling framework; vanilla HTML+CSS+JS is fine; the page must load the API data).

## Non-functional requirements

- NFR-1 Language/runtime: **Python 3.10+** with a small web framework of your choice
  (Flask, FastAPI, or stdlib `http.server` are all acceptable — no other dependencies beyond
  what the framework pulls in; SQLite is the datastore, using the stdlib `sqlite3` or the
  framework's ORM).
- NFR-2 Tests: unit tests (validation, summary math) AND integration tests (API round-trips,
  timezone case from FR-5) using `pytest`; `pytest tests/ -q` must pass.
- NFR-3 Migrations: schema created via a `migrations/` file that a fresh checkout applies
  (document the command in the README).
- NFR-4 Config: `SPRINTPULSE_TZ` read from environment at startup.

## Deliverables (all required — the eval gate checks each)

1. `app/` — the application code (importable module).
2. `migrations/` — schema migration(s).
3. `tests/` — unit + integration tests (FR-5 timezone test included).
4. `README.md` — how to run (install, migrate, start, test), and the `SPRINTPULSE_TZ` config.
5. `docs/product/product.md` — product purpose and scope (a few paragraphs).
6. `docs/plans/tasks.md` — the task list you actually executed, with each task's status.
7. `docs/qa/test-results.txt` — dated test run summary (pass counts).
8. `.github/workflows/ci.yml` — a workflow that runs the test command.

## Constraints

- No authentication, no external APIs, no Docker, no cloud deployment.
- No commits required — the sandbox is the deliverable.
- If a requirement is genuinely impossible, document the deviation in `docs/product/product.md`
  instead of silently skipping it.
