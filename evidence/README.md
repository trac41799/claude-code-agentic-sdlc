# Evidence — raw artifacts behind the deck's claims

This directory is the audit trail for the results slides. Everything claimed in
the deck (test counts, timeline, folder structure) can be reproduced from here.

- **`manifest.md`** — claim → evidence → validation mapping.
- **`validate.py`** — reruns every acceptance gate in the bundled projects and
  asserts the counts match the claims (12/12 reproduce).
- **`tree/`** — folder structures: the `/asdlc-adopt` per-project install, the
  `/asdlc-project` canonical scaffold, and an A-arm vs B-arm project contrast.
- **`sessions/`** — raw metered provider session JSONs (12).
- **`greenfield/`** — 12 intact runnable project folders (source + tests +
  spec/plan/tasks/QA process artifacts).

Validate the claims yourself:

```bash
python evidence/validate.py     # → evidence/validation-report.md
```

Caveats are documented in `manifest.md` and `docs/slides/GAP-ANALYSIS.md`
(provider `costBasis: "unknown"` — test counts are exact, dollar cells are
approximate).