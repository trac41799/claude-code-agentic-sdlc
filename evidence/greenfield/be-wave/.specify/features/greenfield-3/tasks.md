# Tasks — GREENFIELD-3 Rate-Limited Live Event Proxy

Status: derived from spec.md (dev-feature-plan). `[P]` = parallel-safe.
Wave plan (dev-multi-agent, disjoint file scopes):

- **Wave 0** (coordinator): project scaffold + test suite → RED baseline.
- **Wave 1** — Foundation, scope `{app/rate_limit.py, app/streams.py}`.
- **Wave 2** — API, scope `{app/main.py}`.

---

## Phase 0: Scaffold & Baseline

### Task 0.1: Create project scaffold
**Description**: `pyproject.toml` (pytest config: `asyncio_mode=auto`,
`testpaths`, `pythonpath`), `.gitignore`, `app/__init__.py`, `tests/__init__.py`,
`app/config.py` (Settings dataclass with tunable defaults), and stub modules
(`app/rate_limit.py`, `app/streams.py`, `app/main.py`) so test collection
succeeds before implementation.
**Acceptance Criteria**:
- [ ] `pytest tests/ -q` collects tests and they fail with `NotImplementedError`
      (RED for the right reason, not import errors).
- [ ] `Settings` defaults: capacity 10, refill 5/s, buffer 100, heartbeat 15s.
**Effort**: S
**Dependencies**: None

### Task 0.2: Write the acceptance test suite
**Description**: Write `tests/test_rate_limit.py`, `tests/test_streams.py`,
`tests/test_api.py` covering AC-1…AC-6 (bucket burst+drop, refill ≈5/s over 2s,
overflow→error, heartbeat during silence, non-blocking publisher, clean
shutdown) plus API wiring tests (POST 202, info endpoint dropped counter,
lifespan shutdown, SSE end-to-end over a real in-process uvicorn server).
**Acceptance Criteria**:
- [ ] Every AC-1…AC-6 from spec.md has at least one test (cited in test name/comment).
- [ ] Suite is RED before any implementation.
**Effort**: M
**Dependencies**: Task 0.1

---

## Phase 1: Implementation

### Task 1.1: Implement the token bucket
**Description**: Implement `TokenBucket` in `app/rate_limit.py` — capacity 10,
refill 5 tokens/sec (lazy refill from a monotonic clock), `try_consume(n)`,
injectable clock.
**Acceptance Criteria**:
- [ ] AC-1: 10-token burst then drop.
- [ ] AC-2: refill ≈5/sec over 2s (tolerant real-time + exact fake-clock).
**Effort**: S
**Dependencies**: Task 0.2
**Wave**: 1

### Task 1.2: Implement stream broadcast, subscriber queues, heartbeat, shutdown
**Description**: Implement `Stream`, `Subscriber`, `StreamRegistry`,
`PublishResult` in `app/streams.py`. Bounded per-client queue (max 100),
drop-on-empty-bucket with `dropped` counters, overflow → `error` frame +
close, 15s heartbeat comment, disconnect cleanup, graceful shutdown flushing
pending events. `publish()` must be fully synchronous.
**Acceptance Criteria**:
- [ ] AC-3: overflow closes connection and emits `event: error` (status 429).
- [ ] AC-4: heartbeat `: heartbeat` arrives during silence.
- [ ] AC-5: publisher non-blocking under a slow consumer (bounded + drop-on-full).
- [ ] AC-6: shutdown flushes pending events and exits without exception.
- [ ] `dropped` counter surfaced via `Stream.info()`.
**Effort**: M
**Dependencies**: Task 1.1
**Wave**: 1

### Task 1.3: Implement FastAPI endpoints + lifespan
**Description**: Implement `create_app()` in `app/main.py` — POST publisher
(202 / 400), GET SSE consumer (`text/event-stream` with heartbeat, overflow
error, disconnect cleanup), GET stream info (dropped counter, 404 when
missing), lifespan shutdown → `registry.shutdown_all()`.
**Acceptance Criteria**:
- [ ] POST `/streams/{id}/events` returns 202 and publishes to the stream.
- [ ] GET `/streams/{id}/events` streams events and heartbeats (end-to-end
      over a real uvicorn server).
- [ ] GET `/streams/{id}` surfaces `dropped`.
- [ ] App shutdown is clean (no exceptions; registry drained).
**Effort**: M
**Dependencies**: Task 1.2
**Wave**: 2

---

## Phase 2: Verification

### Task 2.1: Full-suite green + wave reports
**Description**: Run `pytest tests/ -q`; run QA verification; write
`wave-report.md` and the QA triage report. Leave changes in the working tree.
**Acceptance Criteria**:
- [ ] `pytest tests/ -q` passes (acceptance gate).
- [ ] Wave scopes verified against `git status --porcelain`.
- [ ] `docs/qa/{date}-greenfield-3-triage.md` and
      `.specify/features/greenfield-3/wave-report.md` exist.
**Effort**: S
**Dependencies**: Task 1.3
**Wave**: —
