---
title: 'One addon folder to copy'
type: 'refactor'
ticket: ''
created: '2026-10-28'
status: 'built'
baseline_revision: '43adfc5'
route: 'oneshot'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Installing the addon means picking the TOC and ten `.lua` files out of the repo root, next to `tools/`, `tests/` and the READMEs.

**Approach:**
- Move the TOC and every addon `.lua` file into a `Gargul_Preloot/` folder at the repo root, with history kept (`git mv`). Installing is then copying that one folder into `Interface/AddOns/`.
- Nothing else lives in it.
- Update the offline tests, the payload generator and the README paths. Addon code is unchanged.

</frozen-after-approval>

## Implementation Notes

- `git mv` of the TOC and the 10 `.lua` files into `Gargul_Preloot/` (100% renames).
- Tests use `addonDir`; the generator loads from `Gargul_Preloot/`.
- README Installation and Files updated. Tests: 383 PASS; the payload regenerated identical.

## Review Triage Log

- Quick review: no findings. The reviewer re-ran both commands and searched the repo for leftover root paths.
## Verification

**Commands:**
- `luajit tests/addon/run.lua` and `luajit tests/addon/make_test_snapshot.lua` (from the repo root) -- expected: PASS, and OK with an unchanged payload.
