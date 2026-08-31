'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { OptimisticLikeSet } = require('../engine.js');

test('starts empty', () => {
  const s = new OptimisticLikeSet();
  assert.equal(s.size(), 0);
  assert.equal(s.contains('anything'), false);
});

test('add marks an id as liked and updates size', () => {
  const s = new OptimisticLikeSet();
  s.add('id-1');
  assert.equal(s.contains('id-1'), true);
  assert.equal(s.contains('id-2'), false);
  assert.equal(s.size(), 1);
});

test('distinct ids are counted independently', () => {
  const s = new OptimisticLikeSet();
  s.add('a');
  s.add('b');
  s.add('c');
  assert.equal(s.size(), 3);
  assert.equal(s.contains('a'), true);
  assert.equal(s.contains('b'), true);
  assert.equal(s.contains('c'), true);
});

test('interleaving: add A, add B, rollback A -> B remains', () => {
  const s = new OptimisticLikeSet();
  s.add('A');
  s.add('B');
  assert.equal(s.size(), 2);
  s.rollback('A');
  assert.equal(s.contains('A'), false);
  assert.equal(s.contains('B'), true);
  assert.equal(s.size(), 1);
});

test('rollback of a never-added id is a no-op and leaves size unchanged', () => {
  const s = new OptimisticLikeSet();
  s.add('A');
  const sizeBefore = s.size();
  assert.equal(s.rollback('ghost'), false);
  assert.equal(s.size(), sizeBefore);
  assert.equal(s.contains('A'), true);
});

test('multiple rollbacks do not drive a count below zero', () => {
  const s = new OptimisticLikeSet();
  s.add('A');
  assert.equal(s.rollback('A'), true);
  assert.equal(s.rollback('A'), false);
  assert.equal(s.size(), 0);
  assert.equal(s.contains('A'), false);
});

test('interleaved add/rollback keeps the net count per id correct', () => {
  const s = new OptimisticLikeSet();
  s.add('A'); // pending like A
  s.add('B'); // pending like B
  s.add('A'); // A liked again before the first resolves
  s.rollback('B'); // B's request fails first
  s.rollback('A'); // one of A's pending ops rolls back
  assert.equal(s.contains('B'), false);
  assert.equal(s.contains('A'), true, 'one pending A still present');
  assert.equal(s.size(), 1);
});

test('rollback never removes an id added after it', () => {
  const s = new OptimisticLikeSet();
  s.add('A');
  s.add('B');
  s.add('C');
  s.rollback('A');
  s.rollback('B');
  assert.equal(s.contains('A'), false);
  assert.equal(s.contains('B'), false);
  assert.equal(s.contains('C'), true, 'C, added after A and B, is untouched');
  assert.equal(s.size(), 1);
});

test('a failed like rolls back without disturbing other pending likes', () => {
  const s = new OptimisticLikeSet();
  s.add('post-1');
  s.add('post-2');
  s.add('post-3');
  s.rollback('post-2'); // post-2's like request failed
  assert.equal(s.contains('post-2'), false);
  assert.equal(s.contains('post-1'), true);
  assert.equal(s.contains('post-3'), true);
  assert.equal(s.size(), 2);
});

test('re-adding after a full rollback works', () => {
  const s = new OptimisticLikeSet();
  s.add('A');
  s.rollback('A');
  assert.equal(s.contains('A'), false);
  s.add('A');
  assert.equal(s.contains('A'), true);
  assert.equal(s.size(), 1);
});
