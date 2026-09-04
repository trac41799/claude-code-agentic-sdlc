#!/usr/bin/env node
// Test-integrity lock engine — SPEC-012 FR-002. Dependency-free (node: builtins only).
//
// The development workflow locks the test suite before implementation. The lock
// records SHA-256 digests of the selected test paths; verification re-enumerates
// them and fails on any content change, added/deleted/renamed file, or symlink.
// It does NOT make files read-only and does NOT authenticate identity — it
// detects tampering and requires an explicit human-approved re-lock to proceed.
//
// Verbs:
//   create  --task <id> [--paths <p>]... [--createdBy <id>]   write .asdlc/test-lock.json
//   verify  [--task <id>]                                      compare current state, exit 1 on mismatch
//   relock  --task <id> --approver <human> --reason <text> [--plan <ref>] [--paths <p>]...
//   validate [--task <id>]                                     schema-check an existing lock
//
// Canonicalization: UTF-8 text, LF line endings (CRLF normalized), `/` path
// separators, deterministic sorted path order, explicit MISSING marker. Lock
// stores hashes only — never test source or secrets.

import * as fs from 'node:fs';
import * as path from 'node:path';
import * as crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

export const LOCK_PATH = '.asdlc/test-lock.json';
export const SCHEMA_VERSION = 1;
const MISSING_MARKER = 'MISSING';
const HEX_RE = /^[0-9a-f]{64}$/;

export function canonPath(p) {
  return String(p).split('\\').join('/');
}

export function canonContent(buf) {
  // UTF-8 text, LF line endings — CRLF -> LF so the digest is stable across OSes.
  return buf.toString('utf8').replace(/\r\n/g, '\n');
}

export function sha256(s) {
  return crypto.createHash('sha256').update(s, 'utf8').digest('hex');
}

export function gitHead(dir) {
  const r = spawnSync('git', ['rev-parse', 'HEAD'], { cwd: dir, encoding: 'utf8' });
  return r.status === 0 ? r.stdout.trim() : 'unknown';
}

function isSymlink(abs) {
  try { return fs.lstatSync(abs).isSymbolicLink(); } catch { return false; }
}

function walkDir(absDir, out) {
  for (const ent of fs.readdirSync(absDir, { withFileTypes: true })) {
    const abs = path.join(absDir, ent.name);
    if (ent.isSymbolicLink()) out.push({ abs, symlink: true });
    else if (ent.isDirectory()) walkDir(abs, out);
    else out.push({ abs, symlink: false });
  }
}

// Enumerate the locked paths into { relPath: sha256 } in canonical form.
// Directories expand recursively; missing files get the MISSING marker (and
// still fail verification later — they can never match a real hash).
export function enumerate(lockDir, paths) {
  const files = new Map();
  for (const raw of paths) {
    const p = canonPath(raw);
    const abs = path.resolve(lockDir, p);
    if (isSymlink(abs)) throw new Error(`symlinked test path is invalid: ${p}`);
    let st = null;
    try { st = fs.statSync(abs); } catch { files.set(p, MISSING_MARKER); continue; }
    if (st.isDirectory()) {
      const out = [];
      walkDir(abs, out);
      for (const { abs: f, symlink } of out) {
        const rel = canonPath(path.relative(lockDir, f));
        if (symlink) throw new Error(`symlinked file inside locked path: ${rel}`);
        files.set(rel, sha256(canonContent(fs.readFileSync(f))));
      }
    } else {
      files.set(p, sha256(canonContent(fs.readFileSync(abs))));
    }
  }
  return files;
}

// Deterministic combined digest over sorted (path, hash) pairs.
export function combinedDigest(files) {
  const parts = [...files.entries()]
    .sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0))
    .map(([p, h]) => `${p}\n${h}`);
  return sha256(parts.join('\n') + '\n');
}

export function readLock(lockDir) {
  const p = path.join(lockDir, LOCK_PATH);
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function writeLock(lockDir, lock) {
  const p = path.join(lockDir, LOCK_PATH);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(lock, null, 2) + '\n', 'utf8');
}

function assertValidPaths(paths) {
  if (!paths.length) throw new Error('at least one --paths entry is required');
  const seen = new Set();
  for (const p of paths) {
    const c = canonPath(p);
    if (seen.has(c)) throw new Error(`duplicate test path is invalid: ${c}`);
    seen.add(c);
  }
}

export function cmdCreate({ dir, taskId, paths, createdBy, baseCommit }) {
  if (!taskId) throw new Error('--task <id> is required');
  assertValidPaths(paths);
  const existing = readLock(dir);
  if (existing) {
    if (existing.taskId === taskId) throw new Error(`lock already exists for task ${taskId} — use relock, not create`);
    throw new Error(`another task's lock exists (${existing.taskId}) — concurrent tasks may not overwrite each other's lock`);
  }
  const files = enumerate(dir, paths);
  const lock = {
    schemaVersion: SCHEMA_VERSION,
    taskId,
    baseCommit: baseCommit ?? gitHead(dir),
    testPaths: paths.map(canonPath),
    digestAlgorithm: 'sha256',
    digest: combinedDigest(files),
    files: Object.fromEntries([...files.entries()].sort((a, b) => (a[0] < b[0] ? -1 : 1))),
    createdAt: new Date().toISOString(),
    createdBy: createdBy ?? 'unknown',
    relocks: [],
  };
  writeLock(dir, lock);
  return lock;
}

export function cmdVerify({ dir, taskId }) {
  const lock = readLock(dir);
  if (!lock) throw new Error(`no lock at ${LOCK_PATH} — create one before implementation`);
  if (taskId && lock.taskId !== taskId) {
    throw new Error(`lock belongs to task ${lock.taskId}, not ${taskId}`);
  }
  const current = enumerate(dir, lock.testPaths);
  const expected = new Map(Object.entries(lock.files ?? {}));
  const changed = [], missing = [], added = [], symlinked = [];
  for (const [p, h] of current) {
    if (h === MISSING_MARKER) { missing.push(p); continue; }
    if (!expected.has(p)) { added.push(p); continue; }
    if (expected.get(p) !== h) changed.push(p);
  }
  for (const p of expected.keys()) {
    if (!current.has(p)) missing.push(p);
  }
  for (const p of lock.testPaths) {
    const abs = path.resolve(dir, p);
    if (isSymlink(abs)) symlinked.push(p);
  }
  const problems = { changed, missing, added, symlinked };
  const ok = !changed.length && !missing.length && !added.length && !symlinked.length;
  if (!ok) {
    const detail = Object.entries(problems)
      .filter(([, v]) => v.length)
      .map(([k, v]) => `${k}: ${v.join(', ')}`)
      .join(' · ');
    return { ok: false, detail, digest: lock.digest, currentDigest: combinedDigest(current) };
  }
  const currentDigest = combinedDigest(current);
  if (currentDigest !== lock.digest) {
    return { ok: false, detail: `combined digest mismatch`, digest: lock.digest, currentDigest };
  }
  return { ok: true, detail: `${current.size} files intact`, digest: lock.digest, currentDigest };
}

export function cmdRelock({ dir, taskId, approver, reason, plan, paths }) {
  if (!taskId) throw new Error('--task <id> is required');
  if (!approver) throw new Error('--approver <human-identity> is required — a re-lock must be human-approved');
  if (!reason) throw new Error('--reason <text> is required');
  const existing = readLock(dir);
  if (!existing) throw new Error(`no lock at ${LOCK_PATH}`);
  if (existing.taskId !== taskId) throw new Error(`lock belongs to task ${existing.taskId}, not ${taskId}`);
  const newPaths = paths?.length ? paths : existing.testPaths;
  assertValidPaths(newPaths);
  const files = enumerate(dir, newPaths);
  const priorDigest = existing.digest;
  existing.testPaths = newPaths.map(canonPath);
  existing.files = Object.fromEntries([...files.entries()].sort((a, b) => (a[0] < b[0] ? -1 : 1)));
  existing.digest = combinedDigest(files);
  existing.relocks.push({
    priorDigest,
    newDigest: existing.digest,
    approvedBy: approver,
    approvedAt: new Date().toISOString(),
    reason,
    plan: plan ?? null,
  });
  writeLock(dir, existing);
  return existing;
}

export function cmdValidate({ dir, taskId }) {
  const lock = readLock(dir);
  if (!lock) throw new Error(`no lock at ${LOCK_PATH}`);
  const errs = [];
  if (lock.schemaVersion !== SCHEMA_VERSION) errs.push(`schemaVersion must be ${SCHEMA_VERSION}`);
  if (!lock.taskId || typeof lock.taskId !== 'string') errs.push('taskId required');
  if (taskId && lock.taskId !== taskId) errs.push(`taskId mismatch: ${lock.taskId} != ${taskId}`);
  if (!Array.isArray(lock.testPaths) || !lock.testPaths.length) errs.push('testPaths must be a non-empty array');
  if (lock.digestAlgorithm !== 'sha256') errs.push('digestAlgorithm must be sha256');
  if (typeof lock.digest !== 'string' || !HEX_RE.test(lock.digest)) errs.push('digest must be a sha256 hex string');
  if (!lock.files || typeof lock.files !== 'object') errs.push('files map required');
  for (const [p, h] of Object.entries(lock.files ?? {})) {
    if (typeof h !== 'string' || !HEX_RE.test(h)) errs.push(`files.${p} must be a sha256 hex string`);
  }
  if (!lock.createdAt) errs.push('createdAt required');
  if (!lock.createdBy) errs.push('createdBy required');
  if (!Array.isArray(lock.relocks)) errs.push('relocks must be an array');
  return { ok: errs.length === 0, errs };
}

function usage() {
  console.log(`test-lock.mjs — SPEC-012 FR-002 test-integrity lock

  create  --task <id> [--paths <p>]... [--createdBy <id>]
  verify  [--task <id>]
  relock  --task <id> --approver <human> --reason <text> [--plan <ref>] [--paths <p>]...
  validate [--task <id>]`);
}

export function main(argv) {
  const verb = argv[2];
  const args = argv.slice(3);
  const opts = {};
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      if (key === 'paths') { (opts.paths ??= []).push(args[++i]); continue; }
      opts[key] = args[++i];
    }
  }
  try {
    let out;
    if (verb === 'create') out = cmdCreate({ dir: process.cwd(), taskId: opts.task, paths: opts.paths ?? [], createdBy: opts.createdBy, baseCommit: opts.baseCommit });
    else if (verb === 'verify') { const r = cmdVerify({ dir: process.cwd(), taskId: opts.task }); console.log(r.ok ? `test-lock: PASS — ${r.detail}` : `test-lock: FAIL — ${r.detail}`); process.exit(r.ok ? 0 : 1); }
    else if (verb === 'relock') out = cmdRelock({ dir: process.cwd(), taskId: opts.task, approver: opts.approver, reason: opts.reason, plan: opts.plan, paths: opts.paths });
    else if (verb === 'validate') { const r = cmdValidate({ dir: process.cwd(), taskId: opts.task }); console.log(r.ok ? 'test-lock: valid' : `test-lock: INVALID — ${r.errs.join('; ')}`); process.exit(r.ok ? 0 : 1); }
    else { usage(); process.exit(2); }
    console.log(`test-lock: wrote ${LOCK_PATH} (task ${out.taskId}, digest ${out.digest.slice(0, 12)}…)`);
  } catch (e) {
    console.error(`test-lock: ${e.message}`);
    process.exit(1);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main(process.argv);
}
