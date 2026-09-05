#!/usr/bin/env node
// Evidence manifest engine — SPEC-012 FR-003. Dependency-free (node: builtins only).
//
// Every governed task produces one machine-readable manifest at
// .asdlc/evidence/<task-id>.json. The manifest is the authoritative index for
// the task handoff; prose summaries link to it rather than duplicating it.
//
// Verbs:
//   record   --task <id> --gate <name> --status <passed|failed|skipped|not-run>
//            [--command <cmd>] [--reason <text>]          record/upsert one gate result
//   meta     --task <id> [--repository <r>] [--base-commit <sha>] [--head-commit <sha>]
//            [--changed-paths <csv>] [--plan-path <p>] [--plan-status <s>]
//            [--test-freeze <status>] [--lock-path <p>] [--review <status>]
//            [--reviewer <x>] [--handoff <p>] [--risks <csv>] [--followups <csv>]
//            [--cost <measured|estimated|unavailable>] [--budget <usd>] [--actual <usd>]
//            [--cost-source <x>] [--plugin-version <v>]   set any provided fields
//   finalize --task <id> [--plugin-version <v>]           stamp provenance + validate; exit 1 if invalid
//   validate --task <id>                                  validate only
//
// Rules enforced: gate statuses are passed|failed|skipped|not-run; skipped
// requires a reason; cost status measured requires actualUsd, unavailable
// forbids it (unknown cost is never zero); one manifest per task; task IDs
// immutable; no prompts, credentials, or raw model output.

import * as fs from 'node:fs';
import * as path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

export const EVIDENCE_DIR = '.asdlc/evidence';
export const SCHEMA_VERSION = 1;

export const GATE_STATUSES = ['passed', 'failed', 'skipped', 'not-run'];
export const REVIEW_STATUSES = ['approved', 'revise', 'blocked', 'not-run'];
export const COST_STATUSES = ['measured', 'estimated', 'unavailable'];

export function gitHead(dir) {
  const r = spawnSync('git', ['rev-parse', 'HEAD'], { cwd: dir, encoding: 'utf8' });
  return r.status === 0 ? r.stdout.trim() : 'unknown';
}

export function manifestPath(dir, taskId) {
  return path.join(dir, EVIDENCE_DIR, `${taskId}.json`);
}

export function readManifest(dir, taskId) {
  const p = manifestPath(dir, taskId);
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function writeManifest(dir, m) {
  const p = manifestPath(dir, m.taskId);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  // Deterministic output: gate keys sorted, fixed key order.
  const sorted = {
    schemaVersion: m.schemaVersion,
    taskId: m.taskId,
    repository: m.repository,
    baseCommit: m.baseCommit,
    headCommit: m.headCommit ?? null,
    plan: m.plan ?? {},
    changedPaths: m.changedPaths ?? [],
    gates: Object.fromEntries(Object.entries(m.gates ?? {}).sort((a, b) => (a[0] < b[0] ? -1 : 1))),
    testFreeze: m.testFreeze ?? {},
    review: m.review ?? {},
    handoff: m.handoff ?? {},
    cost: m.cost ?? {},
    provenance: m.provenance ?? {},
  };
  fs.writeFileSync(p, JSON.stringify(sorted, null, 2) + '\n', 'utf8');
  return sorted;
}

export function ensureManifest(dir, taskId, repository) {
  const existing = readManifest(dir, taskId);
  if (existing) return existing;
  return writeManifest(dir, {
    schemaVersion: SCHEMA_VERSION,
    taskId,
    repository: repository ?? path.basename(path.resolve(dir)),
    baseCommit: gitHead(dir),
    headCommit: null,
    plan: {},
    changedPaths: [],
    gates: {},
    testFreeze: {},
    review: {},
    handoff: {},
    cost: {},
    provenance: {},
  });
}

export function validateManifest(m) {
  const errs = [];
  if (m.schemaVersion !== SCHEMA_VERSION) errs.push(`schemaVersion must be ${SCHEMA_VERSION}`);
  if (!m.taskId || typeof m.taskId !== 'string') errs.push('taskId required');
  if (!m.repository || typeof m.repository !== 'string') errs.push('repository required');
  if (!m.baseCommit || typeof m.baseCommit !== 'string') errs.push('baseCommit required');
  if (m.headCommit === undefined || m.headCommit === null) errs.push('headCommit required (set via meta --head-commit)');
  if (!Array.isArray(m.changedPaths)) errs.push('changedPaths must be an array');
  if (!m.plan || !m.plan.path) errs.push('plan.path required');
  for (const [name, g] of Object.entries(m.gates ?? {})) {
    if (!GATE_STATUSES.includes(g.status)) errs.push(`gates.${name}.status must be one of ${GATE_STATUSES.join('|')}`);
    if (g.status === 'skipped' && !g.reason) errs.push(`gates.${name} skipped requires a reason`);
  }
  if (m.testFreeze?.status && !GATE_STATUSES.includes(m.testFreeze.status)) {
    errs.push(`testFreeze.status must be one of ${GATE_STATUSES.join('|')}`);
  }
  if (m.review?.status && !REVIEW_STATUSES.includes(m.review.status)) {
    errs.push(`review.status must be one of ${REVIEW_STATUSES.join('|')}`);
  }
  const cost = m.cost ?? {};
  if (cost.status && !COST_STATUSES.includes(cost.status)) {
    errs.push(`cost.status must be one of ${COST_STATUSES.join('|')}`);
  }
  if (cost.status === 'measured' && (cost.actualUsd === null || cost.actualUsd === undefined)) {
    errs.push('cost measured requires actualUsd');
  }
  if (cost.status === 'unavailable' && cost.actualUsd !== null && cost.actualUsd !== undefined) {
    errs.push('cost unavailable must have actualUsd null — unknown cost is never estimated as zero');
  }
  if (m.handoff?.knownRisks && !Array.isArray(m.handoff.knownRisks)) errs.push('handoff.knownRisks must be an array');
  if (m.handoff?.followUps && !Array.isArray(m.handoff.followUps)) errs.push('handoff.followUps must be an array');
  if (m.provenance?.generatedAt && Number.isNaN(Date.parse(m.provenance.generatedAt))) {
    errs.push('provenance.generatedAt must be ISO-8601');
  }
  return errs;
}

export function cmdRecord({ dir, taskId, gate, status, command, reason }) {
  if (!taskId) throw new Error('--task <id> is required');
  if (!gate) throw new Error('--gate <name> is required');
  if (!GATE_STATUSES.includes(status)) throw new Error(`--status must be one of ${GATE_STATUSES.join('|')}`);
  if (status === 'skipped' && !reason) throw new Error('skipped gates require --reason');
  const m = ensureManifest(dir, taskId);
  m.gates[gate] = { status, command: command ?? null, reason: reason ?? null };
  return writeManifest(dir, m);
}

export function cmdMeta({ dir, taskId, fields }) {
  if (!taskId) throw new Error('--task <id> is required');
  const m = ensureManifest(dir, taskId);
  if (fields.repository !== undefined) m.repository = fields.repository;
  if (fields.baseCommit !== undefined) m.baseCommit = fields.baseCommit;
  if (fields.headCommit !== undefined) m.headCommit = fields.headCommit;
  if (fields.changedPaths !== undefined) m.changedPaths = fields.changedPaths;
  if (fields.planPath !== undefined || fields.planStatus !== undefined) {
    m.plan = { path: fields.planPath ?? m.plan?.path ?? null, status: fields.planStatus ?? m.plan?.status ?? null };
  }
  if (fields.testFreeze !== undefined || fields.lockPath !== undefined) {
    m.testFreeze = { status: fields.testFreeze ?? m.testFreeze?.status ?? null, lockPath: fields.lockPath ?? m.testFreeze?.lockPath ?? null };
  }
  if (fields.review !== undefined || fields.reviewer !== undefined) {
    m.review = { status: fields.review ?? m.review?.status ?? null, reviewer: fields.reviewer ?? m.review?.reviewer ?? null };
  }
  if (fields.handoff !== undefined || fields.risks !== undefined || fields.followUps !== undefined) {
    m.handoff = {
      summaryPath: fields.handoff ?? m.handoff?.summaryPath ?? null,
      knownRisks: fields.risks ?? m.handoff?.knownRisks ?? [],
      followUps: fields.followUps ?? m.handoff?.followUps ?? [],
    };
  }
  if (fields.cost !== undefined || fields.budget !== undefined || fields.actual !== undefined || fields.costSource !== undefined) {
    m.cost = {
      status: fields.cost ?? m.cost?.status ?? null,
      budgetUsd: fields.budget !== undefined ? fields.budget : (m.cost?.budgetUsd ?? null),
      actualUsd: fields.actual !== undefined ? fields.actual : (m.cost?.actualUsd ?? null),
      source: fields.costSource ?? m.cost?.source ?? null,
    };
  }
  if (fields.pluginVersion !== undefined) m.provenance.pluginVersion = fields.pluginVersion;
  return writeManifest(dir, m);
}

export function cmdFinalize({ dir, taskId, pluginVersion }) {
  if (!taskId) throw new Error('--task <id> is required');
  const m = ensureManifest(dir, taskId);
  if (pluginVersion !== undefined) m.provenance.pluginVersion = pluginVersion;
  m.provenance.generatedAt = new Date().toISOString();
  writeManifest(dir, m);
  const errs = validateManifest(m);
  if (errs.length) {
    throw new Error(`manifest invalid — ${errs.join('; ')}`);
  }
  return m;
}

export function cmdValidate({ dir, taskId }) {
  if (!taskId) throw new Error('--task <id> is required');
  const m = readManifest(dir, taskId);
  if (!m) throw new Error(`no manifest for task ${taskId} at ${manifestPath(dir, taskId)}`);
  return { ok: validateManifest(m).length === 0, errs: validateManifest(m) };
}

function parseCsv(s) {
  return String(s).split(',').map((x) => x.trim()).filter(Boolean);
}

function usage() {
  console.log(`evidence.mjs — SPEC-012 FR-003 evidence manifest

  record   --task <id> --gate <name> --status <passed|failed|skipped|not-run> [--command <cmd>] [--reason <text>]
  meta     --task <id> [--repository <r>] [--base-commit <sha>] [--head-commit <sha>] [--changed-paths <csv>]
           [--plan-path <p>] [--plan-status <s>] [--test-freeze <status>] [--lock-path <p>]
           [--review <status>] [--reviewer <x>] [--handoff <p>] [--risks <csv>] [--followups <csv>]
           [--cost <measured|estimated|unavailable>] [--budget <usd>] [--actual <usd>] [--cost-source <x>]
           [--plugin-version <v>]
  finalize --task <id> [--plugin-version <v>]
  validate --task <id>`);
}

export function main(argv) {
  const verb = argv[2];
  const args = argv.slice(3);
  const opts = {};
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a.startsWith('--')) opts[a.slice(2)] = args[++i];
  }
  const num = (v) => (v === undefined ? undefined : Number(v));
  try {
    if (verb === 'record') {
      const m = cmdRecord({ dir: process.cwd(), taskId: opts.task, gate: opts.gate, status: opts.status, command: opts.command, reason: opts.reason });
      console.log(`evidence: recorded gate ${opts.gate}=${opts.status} for ${m.taskId}`);
    } else if (verb === 'meta') {
      const m = cmdMeta({ dir: process.cwd(), taskId: opts.task, fields: {
        repository: opts.repository, baseCommit: opts.baseCommit, headCommit: opts.headCommit,
        changedPaths: opts.changedPaths ? parseCsv(opts.changedPaths) : undefined,
        planPath: opts.planPath, planStatus: opts.planStatus,
        testFreeze: opts.testFreeze, lockPath: opts.lockPath,
        review: opts.review, reviewer: opts.reviewer,
        handoff: opts.handoff, risks: opts.risks ? parseCsv(opts.risks) : undefined, followUps: opts.followUps ? parseCsv(opts.followUps) : undefined,
        cost: opts.cost, budget: num(opts.budget), actual: num(opts.actual), costSource: opts.costSource,
        pluginVersion: opts.pluginVersion,
      } });
      console.log(`evidence: updated ${m.taskId}`);
    } else if (verb === 'finalize') {
      const m = cmdFinalize({ dir: process.cwd(), taskId: opts.task, pluginVersion: opts.pluginVersion });
      console.log(`evidence: finalized ${m.taskId} — manifest valid`);
    } else if (verb === 'validate') {
      const r = cmdValidate({ dir: process.cwd(), taskId: opts.task });
      console.log(r.ok ? `evidence: ${opts.task} manifest valid` : `evidence: INVALID — ${r.errs.join('; ')}`);
      process.exit(r.ok ? 0 : 1);
    } else {
      usage();
      process.exit(2);
    }
  } catch (e) {
    console.error(`evidence: ${e.message}`);
    process.exit(1);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main(process.argv);
}
