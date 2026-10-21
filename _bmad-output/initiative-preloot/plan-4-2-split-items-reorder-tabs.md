---
title: 'Split TierItems by role and reorder tabs'
type: 'feature'
ticket: ''
created: '2026-10-21'
status: 'built'
baseline_revision: '4ea6af4448521935b04201593eacc626bf6a1057' # C:/Repos/Gargul_Preloot (code repo)
route: 'oneshot'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-preloot/plan-4-2-grids-rework.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The single TierItems grid (58 columns) is too wide to work in. Technical tabs are mixed with the tabs the owner and raiders use.

**Approach:**
- Replace TierItems with five tabs, one per role, with the same layout restricted to that role's specs: `Objets Tank`, `Objets Heal`, `Objets Melee DPS`, `Objets Ranged DPS` and `Objets Caster DPS`.
  - The layout: role header in row 1, spec pairs in class colours in row 2, `Gain (%)` / `Statut` in row 3, items from row 4, frozen A-B and rows 1-3, gain colours, Statut dropdown.
  - The current TierItems grid is deleted only when it has no item rows (row 4+). Otherwise setup aborts and names it.
- Each setup run orders the tabs:
  1. Roster, Rerolls, Présence, Awards;
  2. the five Objets tabs;
  3. Raids, PatternItems, Config;
  4. RaidReports, Diagnostics (when present), `_Listes`.
- No spec icons: Google Sheets dropdowns cannot show images.

</frozen-after-approval>

## Implementation Notes

- `schema.js`:
  - `ITEM_TABS` (sheetIds 1021-1025) is derived from `ROLE_OPTIONS`.
  - `TAB_ORDER` holds the tab order.
  - `GRID_TABS.tierItems` is kept only so setup can detect and delete the old tab.
- `grids.js`:
  - Every tier builder takes the role's `specs`.
  - TierItems is always deleted, whether it has the old flat layout or the single-grid layout. If it holds item rows (from row 4), setup aborts.
- `setup.js`:
  - `buildTabOrderRequests_` runs last in the batch.
  - It resolves each title's final id from the batch's `addSheet`/`deleteSheet` requests, falling back to the current sheet.
  - Tabs not listed (e.g. the default empty sheet) end up after the ordered ones.
- Tests: story-4-1 PASS with 37 assertions, story-4-2 PASS with 121.

## Verification

**Commands:**
- Headless Edge on `tests/story-4-1.html` and `tests/story-4-2.html` -- expected: `PASS`.

## Review Triage Log

- Pass 1 (quick): high 0, medium 1, low 7, false 0, maybe-false 0. Patched by the parent. Pages PASS: story-4-1 with 37 assertions, story-4-2 with 121.
  - medium, patch -- the tab-order test used an empty header map, so the fallback for existing tabs was untested. It now uses `readExistingHeadersByName_()` and asserts the existing tab names in order.
  - low, patch -- the comment on `buildTabOrderRequests_` is now one line.
  - low, patch -- stale "TierItems" width comment corrected.
  - low, patch -- misleading assertion label corrected.
  - low, rejected -- the harness ignores `index`, so the final tab order is not simulated. The request sequence is asserted; the live run confirms the result.
  - low, rejected -- Diagnostics created after setup sits after `_Listes` until the next run. The order is applied on each setup run, as the intent says.
  - low, rejected -- an existing tab already named `Objets <role>` is treated as a grid. Setup creates those names itself; a hand-made tab with the same name is unlikely.
  - low, rejected -- tab titles derive from the role labels. A label change would need a migration anyway; no change is planned.
