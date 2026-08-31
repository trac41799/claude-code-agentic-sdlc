// Aggregator test entry.
// Node v24 treats `node --test` positional args as glob patterns; a bare
// directory glob matches the directory itself rather than scanning it, so the
// runner executes the path as a file. CommonJS directory resolution then loads
// this index, which pulls in both test files so `node --test tests/` runs the
// full suite (visible-range + optimistic-like). Not matched by the runner's
// default `**/*.test.js` auto-discovery pattern, so `node --test` (no args)
// does not run it twice.
require('./visible-range.test.js');
require('./optimistic-like.test.js');
