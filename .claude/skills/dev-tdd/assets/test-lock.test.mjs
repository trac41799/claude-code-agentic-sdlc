// Test-integrity lock engine tests — SPEC-012 FR-002. Run: node --test test-lock.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';

import {
  canonContent, canonPath, cmdCreate, cmdRelock, cmdValidate, cmdVerify,
  combinedDigest, enumerate, readLock, sha256,
} from './test-lock.mjs';

function tmpRepo() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'tl-'));
  fs.mkdirSync(path.join(dir, 'tests'), { recursive: true });
  fs.writeFileSync(path.join(dir, 'tests', 'example.test.ts'), 'import assert from "node:assert";\nassert.ok(true);\n');
  fs.writeFileSync(path.join(dir, 'tests', 'other.test.ts'), 'assert.ok(1);\n');
  return dir;
}

test('canonPath normalizes backslashes', () => {
  assert.equal(canonPath('tests\\example.test.ts'), 'tests/example.test.ts');
});

test('canonContent normalizes CRLF to LF', () => {
  assert.equal(canonContent(Buffer.from('a\r\nb\r\n')), 'a\nb\n');
});

test('digest is deterministic for identical ordered inputs', () => {
  const a = new Map([['x', 'h1'], ['y', 'h2']]);
  const b = new Map([['x', 'h1'], ['y', 'h2']]);
  assert.equal(combinedDigest(a), combinedDigest(b));
});

test('digest is independent of insertion order (sorted path order)', () => {
  const a = new Map([['a.txt', 'h1'], ['b.txt', 'h2']]);
  const b = new Map([['b.txt', 'h2'], ['a.txt', 'h1']]);
  assert.equal(combinedDigest(a), combinedDigest(b));
});

test('create writes a valid lock with per-file digests', () => {
  const dir = tmpRepo();
  const lock = cmdCreate({ dir, taskId: 'TASK-1', paths: ['tests/example.test.ts'], createdBy: 'dev' });
  assert.equal(lock.schemaVersion, 1);
  assert.equal(lock.taskId, 'TASK-1');
  assert.equal(lock.digestAlgorithm, 'sha256');
  assert.match(lock.digest, /^[0-9a-f]{64}$/);
  assert.equal(lock.files['tests/example.test.ts'], sha256(canonContent(fs.readFileSync(path.join(dir, 'tests/example.test.ts')))));
  assert.equal(readLock(dir).taskId, 'TASK-1');
  fs.rmSync(dir, { recursive: true, force: true });
});

test('create expands directories and rejects duplicate paths', () => {
  const dir = tmpRepo();
  const lock = cmdCreate({ dir, taskId: 'TASK-2', paths: ['tests'] });
  assert.deepEqual(Object.keys(lock.files).sort(), ['tests/example.test.ts', 'tests/other.test.ts']);
  assert.throws(() => cmdCreate({ dir, taskId: 'TASK-2', paths: ['tests', 'tests'] }), /duplicate test path/);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('verify passes on intact suite', () => {
  const dir = tmpRepo();
  cmdCreate({ dir, taskId: 'TASK-3', paths: ['tests'] });
  const r = cmdVerify({ dir });
  assert.equal(r.ok, true);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('verify fails on changed locked test', () => {
  const dir = tmpRepo();
  cmdCreate({ dir, taskId: 'TASK-4', paths: ['tests/example.test.ts'] });
  fs.writeFileSync(path.join(dir, 'tests/example.test.ts'), 'assert.ok(false); // tampered\n');
  const r = cmdVerify({ dir });
  assert.equal(r.ok, false);
  assert.match(r.detail, /changed: tests\/example\.test\.ts/);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('verify fails on deleted locked test', () => {
  const dir = tmpRepo();
  cmdCreate({ dir, taskId: 'TASK-5', paths: ['tests/example.test.ts'] });
  fs.rmSync(path.join(dir, 'tests/example.test.ts'));
  const r = cmdVerify({ dir });
  assert.equal(r.ok, false);
  assert.match(r.detail, /missing/);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('verify fails on added test inside a locked directory', () => {
  const dir = tmpRepo();
  cmdCreate({ dir, taskId: 'TASK-6', paths: ['tests'] });
  fs.writeFileSync(path.join(dir, 'tests', 'sneaky.test.ts'), 'assert.ok(1);\n');
  const r = cmdVerify({ dir });
  assert.equal(r.ok, false);
  assert.match(r.detail, /added: tests\/sneaky\.test\.ts/);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('verify fails on symlinked test path', (t) => {
  const dir = tmpRepo();
  fs.writeFileSync(path.join(dir, 'real.test.ts'), 'assert.ok(1);\n');
  try {
    fs.symlinkSync(path.join(dir, 'real.test.ts'), path.join(dir, 'tests', 'link.test.ts'));
  } catch (e) {
    fs.rmSync(dir, { recursive: true, force: true });
    t.skip(`symlink creation not permitted on this host (${e.code})`);
    return;
  }
  assert.throws(() => cmdCreate({ dir, taskId: 'TASK-7', paths: ['tests/link.test.ts'] }), /symlink/);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('verify without a lock fails', () => {
  const dir = tmpRepo();
  assert.throws(() => cmdVerify({ dir }), /no lock/);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('relock requires human approver and reason, records prior digest', () => {
  const dir = tmpRepo();
  const lock = cmdCreate({ dir, taskId: 'TASK-8', paths: ['tests/example.test.ts'] });
  assert.throws(() => cmdRelock({ dir, taskId: 'TASK-8', reason: 'no approver' }), /approver/);
  fs.writeFileSync(path.join(dir, 'tests/example.test.ts'), 'assert.ok(true);\n// evolved by plan\n');
  const relocked = cmdRelock({ dir, taskId: 'TASK-8', approver: 'operator@human', reason: 'revised plan adds coverage', plan: 'docs/plans/TASK-8.md' });
  assert.equal(relocked.relocks.length, 1);
  assert.equal(relocked.relocks[0].priorDigest, lock.digest);
  assert.equal(relocked.relocks[0].approvedBy, 'operator@human');
  assert.equal(relocked.relocks[0].plan, 'docs/plans/TASK-8.md');
  assert.equal(cmdVerify({ dir }).ok, true);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('concurrent tasks cannot overwrite another task lock', () => {
  const dir = tmpRepo();
  cmdCreate({ dir, taskId: 'TASK-9', paths: ['tests/example.test.ts'] });
  assert.throws(() => cmdCreate({ dir, taskId: 'TASK-10', paths: ['tests/example.test.ts'] }), /another task/);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('validate rejects malformed locks', () => {
  const dir = tmpRepo();
  cmdCreate({ dir, taskId: 'TASK-11', paths: ['tests/example.test.ts'] });
  const p = path.join(dir, '.asdlc/test-lock.json');
  const bad = JSON.parse(fs.readFileSync(p, 'utf8'));
  bad.digest = 'not-a-hash';
  fs.writeFileSync(p, JSON.stringify(bad));
  const r = cmdValidate({ dir });
  assert.equal(r.ok, false);
  assert.match(r.errs.join('; '), /digest/);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('lock stores hashes only — no test source or secrets', () => {
  const dir = tmpRepo();
  fs.writeFileSync(path.join(dir, 'tests/example.test.ts'), 'const SECRET = "hunter2";\nassert.ok(SECRET);\n');
  const lock = cmdCreate({ dir, taskId: 'TASK-12', paths: ['tests/example.test.ts'] });
  const raw = JSON.stringify(lock);
  assert.equal(raw.includes('hunter2'), false);
  assert.equal(raw.includes('assert.ok'), false);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('enumerate marks missing files', () => {
  const dir = tmpRepo();
  const files = enumerate(dir, ['tests/nope.test.ts']);
  assert.equal(files.get('tests/nope.test.ts'), 'MISSING');
  fs.rmSync(dir, { recursive: true, force: true });
});
