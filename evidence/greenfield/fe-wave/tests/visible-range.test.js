const { test } = require('node:test');
const assert = require('node:assert');
const { computeVisibleRange } = require('../engine.js');

// Shared constants for the primary scenario (AC-1..AC-4).
const rowHeight = 40;
const viewportHeight = 600;
const overscan = 5;
const items = Array.from({ length: 10000 }, (_, i) => ({ id: i }));

// AC-1: exact window math at a mid-list scroll position.
test('AC-1: exact window math at a mid-list scroll position', () => {
  const result = computeVisibleRange(200000, viewportHeight, items, rowHeight, overscan);
  assert.deepStrictEqual(result, { start: 4995, end: 5020 });
});

// AC-2: at scrollTop = 0, start is 0 and the overscan below the viewport is included.
test('AC-2: window math at the top (scrollTop = 0)', () => {
  const result = computeVisibleRange(0, viewportHeight, items, rowHeight, overscan);
  assert.deepStrictEqual(result, { start: 0, end: 20 });
});

// AC-3: at the maximum scroll position, end === items.length and the window covers the last rows.
test('AC-3: window math at the maximum scroll position (bottom clamp)', () => {
  const result = computeVisibleRange(399400, viewportHeight, items, rowHeight, overscan);
  assert.deepStrictEqual(result, { start: 9980, end: 10000 });
});

// AC-3: an over-large scrollTop clamps to the same bottom window (never out of bounds).
test('AC-3: over-large scrollTop clamps to the bottom window', () => {
  const result = computeVisibleRange(9999999, viewportHeight, items, rowHeight, overscan);
  assert.deepStrictEqual(result, { start: 9980, end: 10000 });
});

// AC-4: an empty list yields an empty window.
test('AC-4: empty items list returns { start: 0, end: 0 }', () => {
  const result = computeVisibleRange(0, viewportHeight, [], rowHeight, overscan);
  assert.deepStrictEqual(result, { start: 0, end: 0 });
});

// AC-5: overscan end-clip on a small list — end never exceeds items.length.
test('AC-5: overscan clips end to items.length on a small list', () => {
  const smallItems = Array.from({ length: 10 }, (_, i) => ({ id: i }));
  const result = computeVisibleRange(0, 600, smallItems, 40, 50);
  assert.deepStrictEqual(result, { start: 0, end: 10 });
});

// AC-5: overscan start-clip on a small list — start never drops below 0.
test('AC-5: overscan clips start to 0 on a small list', () => {
  const smallItems = Array.from({ length: 10 }, (_, i) => ({ id: i }));
  const result = computeVisibleRange(100, 200, smallItems, 40, 5);
  assert.deepStrictEqual(result, { start: 0, end: 10 });
});

// AC-1 (window-math invariants): results stay integer, in-bounds, and non-inverted
// across a spread of scroll positions including the clamp boundary.
test('AC-1: window invariants hold across a spread of scrollTops', () => {
  const scrollTops = [0, 1, 999, 12345, 200000, 399400, 399401, 9999999];
  for (const scrollTop of scrollTops) {
    const { start, end } = computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan);
    assert.ok(Number.isInteger(start), `start must be an integer (got ${start}) at scrollTop=${scrollTop}`);
    assert.ok(Number.isInteger(end), `end must be an integer (got ${end}) at scrollTop=${scrollTop}`);
    assert.ok(start >= 0, `start must be >= 0 (got ${start}) at scrollTop=${scrollTop}`);
    assert.ok(end <= items.length, `end must be <= items.length (got ${end} > ${items.length}) at scrollTop=${scrollTop}`);
    assert.ok(start <= end, `start must be <= end (got ${start} > ${end}) at scrollTop=${scrollTop}`);
  }
});
