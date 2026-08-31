'use strict';

// Entry point so `node --test tests/` also resolves on platforms where the
// runner treats the bare directory path as a module (Windows). Pattern-based
// scanning ignores this file because it is not named *.test.js.
require('./engine.test.js');
require('./optimistic.test.js');
