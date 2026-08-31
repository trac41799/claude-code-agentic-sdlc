function computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan) {
  if (items.length === 0 || rowHeight <= 0 || viewportHeight <= 0) {
    return { start: 0, end: 0 };
  }

  const overscanSafe = Math.max(0, overscan);
  const maxScrollTop = Math.max(0, items.length * rowHeight - viewportHeight);
  const clampedScroll = Math.min(Math.max(0, scrollTop), maxScrollTop);

  const start = Math.max(0, Math.floor(clampedScroll / rowHeight) - overscanSafe);
  const end = Math.min(
    items.length,
    Math.ceil((clampedScroll + viewportHeight) / rowHeight) + overscanSafe
  );

  return { start, end };
}

class OptimisticLikeSet {
  constructor() {
    this._set = new Set();
  }

  add(id) {
    this._set.add(id);
    return this._set.size;
  }

  contains(id) {
    return this._set.has(id);
  }

  rollback(id) {
    this._set.delete(id);
  }

  size() {
    return this._set.size;
  }
}

if (typeof module === 'object' && module.exports) {
  module.exports = { computeVisibleRange, OptimisticLikeSet };
}
if (typeof window !== 'undefined') {
  window.FeedEngine = { computeVisibleRange, OptimisticLikeSet };
}
