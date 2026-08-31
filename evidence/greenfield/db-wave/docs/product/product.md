# GREENFIELD-4 (DB+ETL) — Event Analytics with Nightly Rollup at Scale

**Status:** Approved (brief frozen, identical for both arms)
**Owner:** Bench
**Date:** 2026-08-31
**Source of truth:** Task brief GREENFIELD-4 (DB+ETL)

## 1. Problem

We need a local, dependency-free event-analytics store: ingest raw events into
a database and roll them up into daily aggregates every night. The rollup must
be **correct even when the job re-runs** (idempotent — no double counting) and
**fast enough for 1M rows** (ingest < 120 s, rollup < 30 s on a dev machine).

## 2. Goals

- G1 — Ingest raw events idempotently by event `id` (`INSERT OR IGNORE`).
- G2 — Aggregate events into per-(day, kind, tenant) counts nightly.
- G3 — Rollup is re-runnable: re-running for the same day yields identical
  totals (delete-and-recompute of the day's rows in one transaction — a
  "watermark" approach).
- G4 — Scale: ingest 1,000,000 synthetic events < 120 s; rollup < 30 s.
- G5 — Correctness proven by a pytest suite and a scale/perf test.

## 3. Non-goals

- No external services — SQLite only, no network, no Docker, no cloud.
- No time-series engine, no windowing beyond calendar-day rollup.
- No idempotency across *partial* files within a single ingest run beyond
  `id` dedupe.
- No schema migration framework, no API/UI surface.

## 4. Scope

Deliverables (all local):

| Artifact | Purpose |
|---|---|
| `schema.sql` | `raw_events` + `daily_rollup` DDL |
| `etl/init_db.py` | Applies `schema.sql` to a SQLite file (init script) |
| `etl/ingest.py` | JSONL → `raw_events`, `INSERT OR IGNORE`, returns inserted count |
| `etl/rollup.py` | Aggregates `raw_events` → `daily_rollup`, delete-and-recompute, re-runnable |
| `etl/perf_test.py` | 1M-event scale + idempotency test |
| `tests/test_ingest.py`, `tests/test_rollup.py` | Correctness suite (pytest) |

## 5. Data model

`raw_events` (fact table — append-only):

| column | type | notes |
|---|---|---|
| `id` | TEXT PK | natural key, dedupe point |
| `kind` | TEXT NOT NULL | event type, e.g. `page_view` |
| `occurred_at` | TEXT NOT NULL | ISO-8601 timestamp (`YYYY-MM-DDTHH:MM:SSZ`) |
| `tenant` | TEXT NOT NULL | tenant/account dimension |
| `payload` | TEXT | free-form JSON blob (nullable) |

`daily_rollup` (aggregate table — one row per group):

| column | type | notes |
|---|---|---|
| `day` | TEXT | `YYYY-MM-DD` (prefix of `occurred_at`) |
| `kind` | TEXT | part of PK |
| `tenant` | TEXT | part of PK |
| `cnt` | INTEGER NOT NULL | event count for the group |

`PRIMARY KEY (day, kind, tenant)` — exactly one row per group.

## 6. Key decisions

- **Idempotent ingest** via `INSERT OR IGNORE` keyed on `id`; the ingest
  function returns the number of rows actually inserted (duplicates ignored).
- **Re-runnable rollup** via a full-day delete-and-recompute: for each day
  processed, delete that day's `daily_rollup` rows, then re-derive them from
  `raw_events` — all inside **one transaction**. A re-run therefore never
  double-counts; a partial-day first run is corrected by the next run. This is
  the watermark approach.
- **Day extraction** = `substr(occurred_at, 1, 10)` (ISO prefix), deterministic.
- **Deterministic scale test**: seeded RNG so the 1M-event workload is
  reproducible; assertions on row counts and sums for idempotency.

## 7. Acceptance criteria

- AC-1 `pytest tests/ -q` passes.
- AC-2 `python etl/perf_test.py` passes: 1M rows ingested, ingest < 120 s,
  rollup < 30 s, double-run of rollup yields identical row counts and sums.
- AC-3 Ingest dedupes duplicate `id`s (returned count reflects unique inserts).
- AC-4 Rollup aggregates correctly across two days.
- AC-5 Double-run of rollup is idempotent (same row counts and sums).
- AC-6 Rollup of a partial day then a full-day re-run fixes counts.
- AC-7 Process artifacts exist: this doc, `impl-plan.md`, `tasks.md`, TDD RED
  evidence, QA triage, `wave-report.md`.
- AC-8 Work left uncommitted in the working tree (no commit).

## 8. Risks & assumptions

| Risk | Mitigation |
|---|---|
| 1M-row ingest too slow | Single transaction + chunked `executemany`; SQLite WAL not required for a temp DB |
| Rollup double-counts on re-run | Delete-and-recompute inside one transaction (watermark) |
| Perf budget depends on machine | Budgets are generous (120 s / 30 s) vs. expected single-digit seconds |
| `INSERT OR IGNORE` rowcount quirk | Track inserted count via `total_changes` delta, not cursor rowcount |
