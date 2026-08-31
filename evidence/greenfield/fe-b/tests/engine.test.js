'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { computeVisibleRange, OptimisticLikeSet } = require('../engine.js');

const ROW_HEIGHT = 40;
const VIEWPORT = 600;
const OVERSCAN = 2;
const ITEMS = 10000; // indices 0..9999
const items = Array.from({ length: ITEMS }, (_, i) => i);

// Total content height = 400000px; max scroll = 400000 - 600 = 399400.
const MAX_SCROLL = ITEMS * ROW_HEIGHT - VIEWPORT;

function visibleAt(scrollTop) {
  return computeVisibleRange(scrollTop, VIEWPORT, items, ROW_HEIGHT, OVERSCAN);
}

test('window math is exact at scrollTop=0', () => {
  // First visible row 0, ceil(600/40)=15 rows visible, overscan 2 each side.
  assert.deepEqual(visibleAt(0), { start: 0, end: 17 });
});

test('window math is exact mid-list', () => {
  // scrollTop 4000 -> firstVisible row 100, start 98, end 117.
  assert.deepEqual(visibleAt(4000), { start: 98, end: 117 });
  // Another mid position.
  assert.deepEqual(visibleAt(200000), { start: 4998, end: 5017 });
});

test('window math clamps at the very end (bottom-clamp)', () => {
  // At max scroll, firstVisible 9985, start 9983, end clipped to 10000.
  assert.deepEqual(visibleAt(MAX_SCROLL), { start: 9983, end: 10000 });
  // scrollTop far beyond the end is clamped to the same window.
  assert.deepEqual(visibleAt(MAX_SCROLL + 99999), { start: 9983, end: 10000 });
  assert.deepEqual(visibleAt(Number.MAX_SAFE_INTEGER), { start: 9983, end: 10000 });
});

test('negative scrollTop clamps to 0', () => {
  assert.deepEqual(visibleAt(-100), { start: 0, end: 17 });
  assert.deepEqual(visibleAt(-1), { start: 0, end: 17 });
});

test('rendered slice covers the viewport with no gaps', () => {
  for (const scrollTop of [0, 1000, MAX_SCROLL / 2, MAX_SCROLL]) {
    const { start, end } = visibleAt(scrollTop);
    const slice = items.slice(start, end);
    const firstPx = start * ROW_HEIGHT;
    const lastPx = (end - 1) * ROW_HEIGHT + ROW_HEIGHT;
    assert.ok(slice.length > 0, `scrollTop ${scrollTop} renders rows`);
    // The visible rows must span the entire viewport (with overscan beyond).
    assert.ok(firstPx <= scrollTop, `start row begins above scrollTop ${scrollTop}`);
    assert.ok(lastPx >= scrollTop + VIEWPORT, `end row reaches below viewport at ${scrollTop}`);
  }
});

test('overscan is clipped at the start boundary', () => {
  // scrollTop 80 -> firstVisible 2; overscan 2 reaches exactly row 0.
  assert.deepEqual(visibleAt(80), { start: 0, end: 19 });
  // scrollTop 120 -> firstVisible 3; overscan no longer clipped.
  assert.deepEqual(visibleAt(120), { start: 1, end: 20 });
});

test('overscan is clipped at the end boundary', () => {
  // Bottom-most position where overscan does not hit the last row yet.
  assert.deepEqual(visibleAt(MAX_SCROLL - 80), { start: 9981, end: 10000 });
  assert.deepEqual(visibleAt(MAX_SCROLL - 40), { start: 9982, end: 10000 });
});

test('overscan=0 renders exactly the visible window', () => {
  const range = computeVisibleRange(4000, VIEWPORT, items, ROW_HEIGHT, 0);
  assert.deepEqual(range, { start: 100, end: 115 });
});

test('empty items list renders nothing', () => {
  const range = computeVisibleRange(0, VIEWPORT, [], ROW_HEIGHT, OVERSCAN);
  assert.deepEqual(range, { start: 0, end: 0 });
  assert.equal(items.slice(range.start, range.end).length, 0);
});

test('list shorter than the viewport renders every row', () => {
  const small = [0, 1, 2, 3, 4];
  const range = computeVisibleRange(0, VIEWPORT, small, ROW_HEIGHT, OVERSCAN);
  assert.deepEqual(range, { start: 0, end: 5 });
});

test('non-integer scroll offsets are handled', () => {
  // Fractional scrollTop (common with subpixel scrolling) still yields a window.
  // 3999.7 / 40 = 99.99... -> first visible row 99 -> {start: 97, end: 116}.
  const range = computeVisibleRange(3999.7, VIEWPORT, items, ROW_HEIGHT, OVERSCAN);
  assert.deepEqual(range, { start: 97, end: 116 });
});

test('items must be an array', () => {
  assert.throws(() => computeVisibleRange(0, VIEWPORT, 'nope', ROW_HEIGHT, OVERSCAN), TypeError);
});

test('OptimisticLikeSet interleaving: add A, add B, rollback A -> B remains', () => {
  const s = new OptimisticLikeSet();
  s.add('A');
  s.add('B');
  assert.equal(s.size(), 2);
  s.rollback('A');
  assert.equal(s.contains('A'), false);
  assert.equal(s.contains('B'), true);
  assert.equal(s.size(), 1);
});

test('OptimisticLikeSet rollback of a never-added id is a no-op', () => {
  const s = new OptimisticLikeSet();
  s.add('A');
  const sizeBefore = s.size();
  assert.equal(s.rollback('never-added'), false);
  assert.equal(s.size(), sizeBefore);
  assert.equal(s.contains('A'), true);
});

test('OptimisticLikeSet multiple rollbacks do not go below zero', () => {
  const s = new OptimisticLikeSet();
  s.add('A');
  assert.equal(s.rollback('A'), true);
  assert.equal(s.rollback('A'), false);
  assert.equal(s.size(), 0);
  assert.equal(s.contains('A'), false);
});
