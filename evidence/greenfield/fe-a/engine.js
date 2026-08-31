/* Infinite activity feed engine — dependency-free.
 *
 * Ships two pieces of logic used by the virtualized feed demo:
 *   1. computeVisibleRange — exact windowing math for a fixed-row-height list.
 *   2. OptimisticLikeSet — per-id pending-op counter so a failed like can be
 *      rolled back without disturbing other pending likes.
 *
 * Loads both as a CommonJS module (`node --test`) and as browser globals
 * (`demo.html`) via the UMD-style wrapper below. Zero external dependencies.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    var api = factory();
    root.InfiniteFeed = api;
    root.computeVisibleRange = api.computeVisibleRange;
    root.OptimisticLikeSet = api.OptimisticLikeSet;
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /**
   * Compute the half-open index range [start, end) that a fixed-row-height
   * virtual list should render for a given scroll position.
   *
   * @param {number} scrollTop      Current scroll offset in px. Negative or
   *                                beyond-the-end values are clamped to the
   *                                valid scroll range.
   * @param {number} viewportHeight Visible height of the scroll container (px).
   * @param {Array}  items          Full item list; only its length is used.
   * @param {number} rowHeight      Fixed row height in px.
   * @param {number} overscan       Extra rows to render above/below the visible
   *                                window; clipped at both boundaries.
   * @returns {{start: number, end: number}} Rows to render, end exclusive.
   */
  function computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan) {
    if (!Array.isArray(items)) {
      throw new TypeError('items must be an array');
    }
    var count = items.length;
    var maxScroll = Math.max(0, count * rowHeight - viewportHeight);
    var top = Math.max(0, Math.min(scrollTop, maxScroll));

    var firstVisible = Math.floor(top / rowHeight);
    var visibleCount = Math.ceil(viewportHeight / rowHeight);
    var os = Number.isFinite(overscan) && overscan > 0 ? Math.floor(overscan) : 0;

    return {
      start: Math.max(0, firstVisible - os),
      end: Math.min(count, firstVisible + visibleCount + os)
    };
  }

  /**
   * Tracks optimistic "likes" so a failed like request can be rolled back
   * without disturbing other pending likes.
   *
   * Each id holds a pending-operation count: add() increments, rollback()
   * decrements, and an id counts as liked (contains() === true) while its
   * count is above zero. Interleaved operations stay correct:
   *   add(A); add(B); rollback(A)   -> B still present, A gone
   *   add(A); add(A); rollback(A)   -> A still present (one op pending)
   *   rollback(neverAdded)          -> no-op, size unchanged
   */
  function OptimisticLikeSet() {
    this._counts = new Map();
  }

  OptimisticLikeSet.prototype.add = function (id) {
    this._counts.set(id, (this._counts.get(id) || 0) + 1);
  };

  OptimisticLikeSet.prototype.contains = function (id) {
    return (this._counts.get(id) || 0) > 0;
  };

  OptimisticLikeSet.prototype.rollback = function (id) {
    if (!this._counts.has(id)) {
      return false;
    }
    var next = this._counts.get(id) - 1;
    if (next <= 0) {
      this._counts.delete(id);
    } else {
      this._counts.set(id, next);
    }
    return true;
  };

  OptimisticLikeSet.prototype.size = function () {
    return this._counts.size;
  };

  return {
    computeVisibleRange: computeVisibleRange,
    OptimisticLikeSet: OptimisticLikeSet
  };
});
