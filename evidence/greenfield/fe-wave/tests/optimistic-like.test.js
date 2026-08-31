// tests/optimistic-like.test.js
//
// Wave 1 test authoring for OptimisticLikeSet (engine.js).
// Pins the exact semantics specified in .specify/features/optimistic-feed/spec.md
// (AC-6, AC-7) so the Wave 2 implementation has a concrete contract to satisfy.
//
// Node built-in test runner ONLY — no external dependencies.
const { test } = require('node:test');
const assert = require('node:assert');
const { OptimisticLikeSet } = require('../engine.js');

// AC-6: add(A), add(B), rollback(A) -> contains(B) === true, contains(A) === false, size() === 1
test('AC-6 interleaving: rollback of one id leaves other pending likes intact', () => {
  const set = new OptimisticLikeSet();
  set.add('a');
  set.add('b');
  set.rollback('a');
  assert.strictEqual(set.contains('b'), true);
  assert.strictEqual(set.contains('a'), false);
  assert.strictEqual(set.size(), 1);
});

// AC-6: rollback removes ONLY the target id
test('AC-6 rollback removes only the target id', () => {
  const set = new OptimisticLikeSet();
  set.add('x');
  set.add('y');
  set.rollback('y');
  assert.strictEqual(set.contains('x'), true);
  assert.strictEqual(set.size(), 1);
});

// AC-7: rollback of a never-added id is a no-op on an empty set (no throw)
test('AC-7 rollback of never-added id is a no-op on an empty set', () => {
  const set = new OptimisticLikeSet();
  assert.doesNotThrow(() => set.rollback('ghost'));
  assert.strictEqual(set.size(), 0);
  assert.strictEqual(set.contains('ghost'), false);
});

// AC-7: rollback of a never-added id does not disturb existing ids
test('AC-7 rollback of never-added id leaves existing ids unchanged', () => {
  const set = new OptimisticLikeSet();
  set.add('z');
  set.rollback('ghost');
  assert.strictEqual(set.contains('z'), true);
  assert.strictEqual(set.size(), 1);
});

// add(id) returns the NEW size and is idempotent: adding the same id twice keeps size 1
test('add returns new size and is idempotent (duplicate add keeps size 1)', () => {
  const set = new OptimisticLikeSet();
  assert.strictEqual(set.add('a'), 1);
  assert.strictEqual(set.add('a'), 1);
  assert.strictEqual(set.size(), 1);
});

// contains(id) on an empty set -> false
test('contains on an empty set is false', () => {
  const set = new OptimisticLikeSet();
  assert.strictEqual(set.contains('a'), false);
});

// Set semantics: add(A), add(A), rollback(A) -> size 0 (a set, not a counter)
test('set semantics: duplicate adds collapse, rollback fully removes the id', () => {
  const set = new OptimisticLikeSet();
  set.add('a');
  set.add('a');
  set.rollback('a');
  assert.strictEqual(set.size(), 0);
});

// AC-6 + AC-7: 100 distinct ids stay fully independent under add/rollback
test('mixed ids stay independent across add and rollback at scale', () => {
  const set = new OptimisticLikeSet();
  const ids = Array.from({ length: 100 }, (_, i) => `id-${i}`);
  for (const id of ids) {
    set.add(id);
  }
  assert.strictEqual(set.size(), 100);
  assert.strictEqual(set.contains(ids[0]), true);
  assert.strictEqual(set.contains('nope'), false);

  set.rollback(ids[0]);
  assert.strictEqual(set.size(), 99);
  assert.strictEqual(set.contains(ids[0]), false);
  for (let i = 1; i < ids.length; i++) {
    assert.strictEqual(set.contains(ids[i]), true);
  }
});
