---
title: 'Spec table'
type: 'feature'
ticket: '5'
created: '2026-09-30'
status: 'built'
baseline_revision: '0dede60b96d1ee955e6bd9b7bb749b7d9e375307'
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

**Problem:** Every stage must identify Specs the same way. A Spec is a talent spec as wowtbc.gg publishes it, with its own PreLoot ID, class and Role, even when wowsims sims several Specs as one (AD-4). No such table exists.

**Approach:** Add `src/preloot/models/specs.py` with a `Role` enum (DPS, Healer, Tank), a frozen `Spec` record (`id`, `class_name`, `role`) and the `SPECS` table. The table lists the 28 TBC Specs that have a wowtbc.gg BiS page, with IDs in snake_case of the page name (e.g. `fury_warrior`, `feral_dps_druid`, `destruction_fire_warlock`), plus lookups `get_spec(id)` and `specs_by_role(role)`. An unknown ID raises an error naming the valid IDs. Page names and wowsims spec/talent columns are not added here: epic-contested-items and epic-sim-priority add them. `models/__init__.py` is not touched.

</frozen-after-approval>

## Implementation Notes

- Oneshot: one data module and one test file, about 90 lines.
- Spec list verified 2026-09-30 by scanning wowtbc.gg's JS bundles for `/bis-list/<slug>` links, then HEAD-checking `/page-data/bis-list/<slug>/page-data.json`. There are 28 Specs with 200 responses: 21 DPS, 4 Healer (holy_paladin, holy_priest, restoration_druid, restoration_shaman), 3 Tank (feral_tank_druid, protection_paladin, protection_warrior). Six slugs returned 404 and are left out: combat-daggers-rogue, discipline-priest, feral-druid, fire-ffb-mage, fury-protection-warrior, guardian-druid.
- `Role` is a `StrEnum`, so it serializes as `dps`/`healer`/`tank` when artifacts carry it. `Spec` is a frozen dataclass, a static table like `Phase`. Files: `src/preloot/models/specs.py`, `tests/test_specs.py`. Full suite: 47 passed.

## Review Triage Log

- Quick lens: 0 findings. The first launch returned no output and was re-run.

## Verification

**Commands:**
- `uv run pytest -q` -- expected: all tests pass, exit 0
