// Evidence manifest engine tests — SPEC-012 FR-003. Run: node --test test-evidence.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';

import {
  cmdFinalize, cmdMeta, cmdRecord, cmdValidate, manifestPath, readManifest,
} from './evidence.mjs';

function tmpRepo() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'ev-'));
}

test('record creates a manifest and upserts gates', () => {
  const dir = tmpRepo();
  cmdRecord({ dir, taskId: 'TASK-1', gate: 'tests', status: 'passed', command: 'npm test' });
  cmdRecord({ dir, taskId: 'TASK-1', gate: 'tests', status: 'failed', command: 'npm test' });
  const m = readManifest(dir, 'TASK-1');
  assert.equal(m.taskId, 'TASK-1');
  assert.equal(m.schemaVersion, 1);
  assert.equal(m.gates.tests.status, 'failed'); // upsert, not duplicate
  assert.deepEqual(Object.keys(m.gates), ['tests']);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('invalid gate status is rejected', () => {
  const dir = tmpRepo();
  assert.throws(() => cmdRecord({ dir, taskId: 'TASK-1', gate: 'x', status: 'maybe' }), /status/);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('skipped gates require a reason', () => {
  const dir = tmpRepo();
  assert.throws(() => cmdRecord({ dir, taskId: 'TASK-1', gate: 'visual', status: 'skipped' }), /reason/);
  const m = cmdRecord({ dir, taskId: 'TASK-1', gate: 'visual', status: 'skipped', reason: 'non-UI task' });
  assert.equal(m.gates.visual.status, 'skipped');
  fs.rmSync(dir, { recursive: true, force: true });
});

test('cost rules: measured requires actualUsd, unavailable forbids it', () => {
  const dir = tmpRepo();
  cmdMeta({ dir, taskId: 'TASK-1', fields: { cost: 'measured', actual: 1.25, source: 'meter' } });
  const r1 = cmdValidate({ dir, taskId: 'TASK-1' });
  assert.equal(r1.errs.some((e) => e.includes('actualUsd')), false, r1.errs.join('; '));
  cmdMeta({ dir, taskId: 'TASK-2', fields: { cost: 'unavailable', actual: 0, source: 'none' } });
  const r2 = cmdValidate({ dir, taskId: 'TASK-2' });
  assert.ok(r2.errs.some((e) => e.includes('unavailable')), r2.errs.join('; '));
  cmdMeta({ dir, taskId: 'TASK-3', fields: { cost: 'measured', source: 'meter' } });
  const r3 = cmdValidate({ dir, taskId: 'TASK-3' });
  assert.ok(r3.errs.some((e) => e.includes('actualUsd')), r3.errs.join('; '));
  fs.rmSync(dir, { recursive: true, force: true });
});

test('finalize requires headCommit, plan, testFreeze, review; then passes', () => {
  const dir = tmpRepo();
  cmdRecord({ dir, taskId: 'TASK-1', gate: 'compile', status: 'passed', command: 'npm run build' });
  assert.throws(() => cmdFinalize({ dir, taskId: 'TASK-1' }), /manifest invalid/);
  cmdMeta({ dir, taskId: 'TASK-1', fields: {
    headCommit: 'abc123', changedPaths: ['src/a.ts', 'tests/a.test.ts'],
    planPath: 'docs/plans/TASK-1.md', planStatus: 'approved',
    testFreeze: 'passed', lockPath: '.asdlc/test-lock.json',
    review: 'not-run', cost: 'unavailable', costSource: 'host-does-not-expose-cost',
    pluginVersion: '2.11.0-rc.1',
  } });
  const fin = cmdFinalize({ dir, taskId: 'TASK-1', pluginVersion: '2.11.0-rc.1' });
  assert.ok(fin.provenance.generatedAt);
  assert.equal(cmdValidate({ dir, taskId: 'TASK-1' }).ok, true);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('deterministic output: gate insertion order does not change the file', () => {
  const dirA = tmpRepo();
  const dirB = tmpRepo();
  cmdRecord({ dir: dirA, taskId: 'TASK-1', gate: 'bdd', status: 'passed' });
  cmdRecord({ dir: dirA, taskId: 'TASK-1', gate: 'compile', status: 'passed' });
  cmdRecord({ dir: dirB, taskId: 'TASK-1', gate: 'compile', status: 'passed' });
  cmdRecord({ dir: dirB, taskId: 'TASK-1', gate: 'bdd', status: 'passed' });
  cmdMeta({ dir: dirA, taskId: 'TASK-1', fields: { repository: 'repo' } });
  cmdMeta({ dir: dirB, taskId: 'TASK-1', fields: { repository: 'repo' } });
  const a = fs.readFileSync(manifestPath(dirA, 'TASK-1'), 'utf8');
  const b = fs.readFileSync(manifestPath(dirB, 'TASK-1'), 'utf8');
  assert.equal(a, b);
  fs.rmSync(dirA, { recursive: true, force: true });
  fs.rmSync(dirB, { recursive: true, force: true });
});

test('concurrent tasks keep separate manifests', () => {
  const dir = tmpRepo();
  cmdRecord({ dir, taskId: 'TASK-A', gate: 'tests', status: 'passed' });
  cmdRecord({ dir, taskId: 'TASK-B', gate: 'tests', status: 'failed' });
  assert.equal(readManifest(dir, 'TASK-A').gates.tests.status, 'passed');
  assert.equal(readManifest(dir, 'TASK-B').gates.tests.status, 'failed');
  fs.rmSync(dir, { recursive: true, force: true });
});

test('validate: structural checks pass on WIP manifests, strict fails them', () => {
  const dir = tmpRepo();
  cmdRecord({ dir, taskId: 'TASK-1', gate: 'tests', status: 'passed' });
  // Non-strict = structural rules only (statuses, reasons, cost states).
  assert.equal(cmdValidate({ dir, taskId: 'TASK-1' }).ok, true);
  // Strict = full minimum schema (governed completion claim).
  const r = cmdValidate({ dir, taskId: 'TASK-1', strict: true });
  assert.equal(r.ok, false);
  assert.ok(r.errs.some((e) => e.includes('headCommit')));
  assert.ok(r.errs.some((e) => e.includes('review.status')));
  fs.rmSync(dir, { recursive: true, force: true });
});
