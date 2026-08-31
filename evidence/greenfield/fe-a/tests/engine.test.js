'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { computeVisibleRange, OptimisticLikeSet } = require('../engine.js');

const ROW_HEIGHT = 40;
const VIEWPORT = 600;
const OVERSCAN = 2;
const ITEM_COUNT = 10000;
const items = Array.from({ length: ITEM_COUNT }, (_, i) => i);

// Content height = 400000px; max scroll offset = 400000 - 600 = 399400.
const MAX_SCROLL = ITEM_COUNT * ROW_HEIGHT - VIEWPORT;

function visibleAt(scrollTop) {
  return computeVisibleRange(scrollTop, VIEWPORT, items, ROW_HEIGHT, OVERSCAN);
}

test('window math is exact at scrollTop=0', () => {
  assert.deepEqual(visibleAt(0), { start: 0, end: 17 });
});

test('window math is exact mid-list', () => {
  assert.deepEqual(visibleAt(4000), { start: 98, end: 117 });
  assert.deepEqual(visibleAt(200000), { start: 4998, end: 5017 });
});

test('window math clamps at the very end (bottom-clamp)', () => {
  assert.deepEqual(visibleAt(MAX_SCROLL), { start: 9983, end: 10000 });
  assert.deepEqual(visibleAt(MAX_SCROLL + 99999), { start: 9983, end: 10000 });
  assert.deepEqual(visibleAt(Number.MAX_SAFE_INTEGER), { start: 9983, end: 10000 });
});

test('negative scrollTop clamps to 0', () => {
  assert.deepEqual(visibleAt(-100), { start: 0, end: 17 });
  assert.deepEqual(visibleAt(-1), { start: 0, end: 17 });
});

test('rendered slice spans the viewport at every scroll position', () => {
  for (const scrollTop of [0, 1000, MAX_SCROLL / 2, MAX_SCROLL]) {
    const { start, end } = visibleAt(scrollTop);
    assert.ok(start < end, `non-empty window at scrollTop ${scrollTop}`);
    assert.ok(start * ROW_HEIGHT <= scrollTop, 'start row begins at or above scrollTop');
    assert.ok(end * ROW_HEIGHT >= scrollTop + VIEWPORT, 'window reaches below the viewport');
  }
});

test('overscan is clipped at the start boundary', () => {
  assert.deepEqual(visibleAt(80), { start: 0, end: 19 });
  assert.deepEqual(visibleAt(120), { start: 1, end: 20 });
});

test('overscan is clipped at the end boundary', () => {
  assert.deepEqual(visibleAt(MAX_SCROLL - 80), { start: 9981, end: 10000 });
  assert.deepEqual(visibleAt(MAX_SCROLL - 40), { start: 9982, end: 10000 });
});

test('overscan=0 renders exactly the visible window', () => {
  assert.deepEqual(
    computeVisibleRange(4000, VIEWPORT, items, ROW_HEIGHT, 0),
    { start: 100, end: 115 }
  );
});

test('empty items list renders nothing', () => {
  const range = computeVisibleRange(0, VIEWPORT, [], ROW_HEIGHT, OVERSCAN);
  assert.deepEqual(range, { start: 0, end: 0 });
  assert.equal(items.slice(range.start, range.end).length, 0);
});

test('list shorter than the viewport renders every row', () => {
  const small = [0, 1, 2, 3, 4];
  assert.deepEqual(
    computeVisibleRange(0, VIEWPORT, small, ROW_HEIGHT, OVERSCAN),
    { start: 0, end: 5 }
  );
});

test('non-integer scroll offsets are handled', () => {
  assert.deepEqual(visibleAt(3999.7), { start: 97, end: 116 });
});

test('items must be an array', () => {
  assert.throws(
    () => computeVisibleRange(0, VIEWPORT, 'nope', ROW_HEIGHT, OVERSCAN),
    TypeError
  );
});
