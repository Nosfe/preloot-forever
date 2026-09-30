---
title: 'Phase table and Previous Phase'
type: 'feature'
ticket: '3'
created: '2026-09-30'
status: 'built'
baseline_revision: 'cb09a2d7942a63ad71653949307fffb8b2ab9ea1'
route: 'oneshot'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-preloot/spec-preloot/glossary.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Every stage must name Phases the same way. wowtbc.gg uses flags (`t4`, `za`), wowsims uses numbers, and the officer types Anniversary IDs (AD-14). Nothing yet maps them or derives the Previous Phase.

**Approach:** Add `src/preloot/models/phases.py` holding the one Phase table from the glossary: canonical `pre`, `p1`–`p5`, each with its Anniversary label, wowtbc.gg flag and wowsims phase number (none for `pre`). Add lookups by canonical ID, wowtbc.gg flag and wowsims number, and `previous_phase()`. `p1` derives `pre`, and `pre` has no Previous Phase. An unknown ID raises an error naming the valid IDs, which entry 6 surfaces in the CLI. `cli.py` and `models/__init__.py` are not touched.

</frozen-after-approval>

## Implementation Notes

- Oneshot: one new module and one test file, about 80 lines.
- `Phase` is a frozen dataclass, not a pydantic model: it's a static lookup table, not an artifact. `PHASES` is in release order, and `previous_phase` indexes into it. `from_wowsims_phase` has no entry for `pre`, because it has no wowsims number.
- Files: `src/preloot/models/phases.py`, `tests/test_phases.py`. The full suite gives 33 passed.

## Review Triage Log

- Quick lens: 0 findings.

## Verification

**Commands:**
- `uv run pytest -q` -- expected: all tests pass, exit 0
