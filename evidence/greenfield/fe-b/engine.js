/* Infinite activity feed engine — dependency-free.
 * Works both as a CommonJS module (node --test) and as a browser global
 * (demo.html) via the UMD-style wrapper below. No imports, no requires.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.InfiniteFeed = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /**
   * Compute the slice of items that should be rendered for a virtualized,
   * fixed-row-height list.
   *
   * @param {number} scrollTop      Current scroll offset in px (may be negative
   *                                or beyond the end; it is clamped).
   * @param {number} viewportHeight Visible height of the scroll container in px.
   * @param {Array}  items          Full list of items.
   * @param {number} rowHeight      Fixed row height in px.
   * @param {number} overscan       Extra rows to render above/below the visible
   *                                window. Clipped at both boundaries.
   * @returns {{start: number, end: number}} Half-open index range
   *                                          [start, end) to render.
   */
  function computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan) {
    if (!Array.isArray(items)) {
      throw new TypeError('items must be an array');
    }
    var count = items.length;
    var totalHeight = count * rowHeight;
    var maxScroll = Math.max(0, totalHeight - viewportHeight);

    var top = Math.max(0, Math.min(scrollTop, maxScroll));
    var firstVisible = Math.floor(top / rowHeight);
    var visibleCount = Math.ceil(viewportHeight / rowHeight);

    var os = Number.isFinite(overscan) && overscan > 0 ? Math.floor(overscan) : 0;

    var start = Math.max(0, firstVisible - os);
    var end = Math.min(count, firstVisible + visibleCount + os);
    return { start: start, end: end };
  }

  /**
   * Tracks optimistic "likes" so a failed like request can be rolled back
   * without disturbing other pending likes.
   *
   * Each id keeps a count of pending operations. add() increments, rollback()
   * decrements; an id is "liked" (contains() === true) while its count is > 0.
   * This makes interleaved operations safe:
   *   add(A); add(B); rollback(A)  -> B still present
   *   add(A); add(A); rollback(A)  -> A still present (one like still pending)
   *   rollback(neverAdded)         -> no-op
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
