'use strict';

// Entry point so `node --test tests/` resolves on platforms where the test
// runner treats the bare directory path as a module (Node 24 / Windows).
// This file is deliberately NOT named *.test.js, so pattern-based discovery
// on other platforms ignores it and the suites are not run twice.
require('./engine.test.js');
require('./optimistic.test.js');
