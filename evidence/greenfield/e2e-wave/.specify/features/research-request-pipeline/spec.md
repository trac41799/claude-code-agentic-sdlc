# Feature Spec — Research Request Pipeline

**Slug:** `research-request-pipeline`
**Status:** APPROVED (frozen brief)
**Source:** `docs/product/product.md` (Product Spec capture)
**Date:** 2026-08-31

---

## Summary

Local web app: a user submits a research request (topic + email); the system
queues it, processes it in a background worker, and the user watches live
status over SSE and reads the final result.

## Acceptance Criteria (AC)

Each AC is testable and maps to a functional requirement in the product spec.

| ID | Criterion | Product FR |
|----|-----------|------------|
| AC-1 | `POST /requests` with `{topic, email}` creates a request with status `queued` and returns it | FR-1 |
| AC-2 | `POST /requests` with an empty/whitespace topic returns `400` | FR-1a |
| AC-3 | `POST /requests` with an invalid email (no `@`) returns `400` | FR-1b |
| AC-4 | `GET /requests/{id}` returns status + result; unknown id → `404` | FR-2 |
| AC-5 | `GET /requests/{id}/events` streams the transition sequence `queued → processing → done` as SSE | FR-3 |
| AC-6 | A background worker claims queued jobs, simulates work (~0.2s), and marks the job `done` with a result echoing the topic | FR-5 |
| AC-7 | A job left in `processing` by a crash is re-claimed on restart and completes **exactly once** to `done` | FR-6 |
| AC-8 | `GET /` serves the static frontend page (submit form + request list + live status) | FR-7 |
| AC-9 | `pytest tests/ -q` passes | NFR |

## Interface contract

- **`POST /requests`** — body `{"topic": str, "email": str}` → `201` with request JSON; `400` for empty topic or invalid email; `422` for missing fields.
- **`GET /requests`** — `200` list of request JSON, oldest first.
- **`GET /requests/{id}`** — `200` request JSON; `404` if missing.
- **`GET /requests/{id}/events`** — `text/event-stream`; first event = current status, then one event per transition.
- **Request JSON:** `{id, topic, email, status, result, attempts, created_at, updated_at}`.

## Data model

`requests` table (SQLite):

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER PK AUTOINCREMENT | |
| `topic` | TEXT NOT NULL | |
| `email` | TEXT NOT NULL | |
| `status` | TEXT NOT NULL DEFAULT 'queued' | `queued\|processing\|done\|failed` |
| `result` | TEXT | set when done |
| `error` | TEXT | set when failed |
| `claim_token` | TEXT | worker claim marker |
| `attempts` | INTEGER NOT NULL DEFAULT 0 | incremented per claim |
| `created_at` | TEXT NOT NULL | ISO-8601 |
| `updated_at` | TEXT NOT NULL | ISO-8601 |

## Constraints

- Static frontend, **no build step**.
- SQLite file DB under `./data`.
- Do **not** commit; leave changes in the working tree.
