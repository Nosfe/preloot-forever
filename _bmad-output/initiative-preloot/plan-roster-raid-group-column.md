---
title: 'Roster raid-group column'
type: 'feature'
ticket: ''
created: '2026-10-23'
status: 'built'
baseline_revision: 'acc387c64c8bd3e7b6ace0c5f04f9be04b4fb29e' # in C:/Repos/Gargul_Preloot (code repo)
route: 'full'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The owner runs two raid groups and cannot tell from the Roster tab which group a raider belongs to, so the Roster can't be filtered by group.

**Approach:** Add an owner-filled column "Groupe de raid" to Roster, directly after the raider name (column B), with a strict dropdown of exactly "Raid 1" and "Raid 2". It is for filtering only: no formula, score, snapshot or End raid behaviour reads it. Setup / refresh inserts the column into an existing Roster so every existing value shifts right intact. The group cells look exactly like the raider-name cells (same formatting rules).

## Boundaries & Constraints

**Always:**
- Roster columns are read by key (`columnOf_`), never by fixed index.
- One refresh migrates a live Roster: insert column B before any request that writes formulas referencing Roster columns.
- The raider name stays in column A (Rerolls rules use `INDIRECT("Roster!A2:A")`).
- All writes go through `applyBatch_`.

**Never:**
- Any score, snapshot, End raid, loot import or parse logic that reads the group.
- Changes to Rerolls (it is removed in a later story).
- Fixing other layout migrations.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Fresh workbook | No Roster tab | Roster created with "Groupe de raid" in B and the dropdown on B2:B | No error expected |
| Live Roster migration | Roster headers without the group, data rows | Column inserted at B; name, class, spec, parse and formulas intact one column right; `_Listes` lookup reads the class column | No error expected |
| Already migrated | Roster with the group in B | Second refresh inserts nothing | No error expected |
| Legacy Roster | Old tank-priority/gain columns plus no group | Legacy columns deleted, then the group inserted; values land under the right headers | No error expected |
| Outdated layout action | Roster not yet refreshed, owner runs Update WCL parses or Start | Refused with "Set up / refresh workbook" (existing `requireCurrentLayout_`) | Nothing written |
| Invalid group | Owner types "Raid 3" | Rejected by the strict dropdown | Sheets validation |

</frozen-after-approval>

## Code Map

- `tools/google_apps_script/src/schema.js` -- Roster `columns`: add `{ key: 'raidGroup', label: 'Groupe de raid', note }` after `raiderKey`. Add the group values as a constant near `ITEM_SLOTS`.
- `tools/google_apps_script/src/setup.js`:
  - `buildSetupPlan_` (L42): today it runs `buildGridRequests_` before `buildLegacyTabMigrationRequests_`. The `_Listes` XLOOKUP on `Roster!<class>` (grids.js L334-350) would be written, then shifted by the insert, so the migration must come first.
  - `buildLegacyTabMigrationRequests_` (L360) and `effectiveHeadersByName_` (L298): add the Roster group insert (`insertDimension` at index 1, `inheritFromBefore: true`). Apply it after the legacy deletes, and splice `''` into the effective rows so the role/spec rewrite (L996) sees the shifted columns.
  - `buildValidationRequestsForTab_` (L723): strict ONE_OF_LIST for the group on Roster only.
  - `buildColumnWidthRequests_` (L668): check whether widths come from the contract.
- `tools/google_apps_script/src/grids.js` `readClassByName_` (L1558) -- reads the live sheet before the batch runs. Find the class column from the live header row (`class`/`Classe`), so the first migration run still colours headers right.
- Unchanged:
  - `roster.js` (name column only);
  - `snapshot.js` and `parses.js` (`columnOf_` plus `requireCurrentLayout_`);
  - `attendance.js` and `ledger.js`.
- `tools/google_apps_script/tests/*.html`:
  - Seeds that use `keysOf_(tabByName_('Roster'))` with positional rows such as `['Ana', 'Mage', ...]` need `''` added after the name.
  - Seeds with explicit old headers now exercise the migration.
  - Assertions that read Roster by index (e.g. story-4-3 `[0][7]`) shift by one.

## Tasks & Acceptance

**Execution:**
- [ ] `src/schema.js` -- add the column and the group values -- contract.
- [ ] `src/setup.js` -- run the migration before the grids; insert the group column for existing Rosters; update the effective headers and rows; add the group dropdown -- one-pass migration.
- [ ] `src/grids.js` -- `readClassByName_` finds the class column from the live header -- correct header colours on the migration run.
- [ ] `tests/story-4-*.html` -- adjust Roster seeds and indexes. Add tests for: migration (values shift, `_Listes` lookup on the class column, no second insert), fresh dropdown values, and the legacy-plus-group case -- I/O matrix.

**Acceptance Criteria:**
- Given a live Roster with data, when Setup / refresh runs, then B is "Groupe de raid", and every other column's header and values are unchanged except for being one column right.
- Given the refreshed Roster, when the owner picks Raid 1 or Raid 2 in B, then Rôle, scores and the snapshot are unchanged.

## Implementation Notes

- Implemented directly, not through a subagent: past coder runs dropped tests and stripped accents.
- Files changed:
  - `schema.js`: the new column and `RAID_GROUPS`.
  - `setup.js`: migrations run before the grids; `needsRosterGroupColumn_` inserts B; the effective headers and rows reflect the insert; the strict group dropdown; a CF rule copying the name rule; width 130.
  - `grids.js`: `readClassByName_` finds Classe in the live header.
  - Tests 4-2, 4-3, 4-4, 4-6 and 4-7.
- Coverage: the parse-update refusal is tested in 4-4, because 4-6 does not load `parses.js`.
- Not changed: the 4-3 archive tests still seed `[name, 'Mage']` under the new header, so 'Mage' sits in the group column. They only check Présence/Awards ordering by name, so the class is irrelevant there.

## Plan Change Log

## Review Triage Log

**Pass 1 (quick): 3 patched, 6 rejected.**

- [low, patch] **Fresh workbook not tested.** Added asserts on the fr_FR fresh setup in 4-2: B is "Groupe de raid" with the Raid 1/Raid 2 dropdown.
- [false] **No test for a second refresh after migration.** The 4-2 test "re-run after migration moves no data and repeats no migration" seeds the legacy Roster (no group), refreshes twice and compares Roster rows.
- [low, rejected] **Header colours only unit-tested through `readClassByName_`.** The harness doesn't record cell formats. The direct test of the lookup's input (live Classe read before the insert) is the observable part.
- [low, patch] **AC 2 not tested.** Added a 4-3 assert that no Roster formula cell references the group column. Snapshot and parses read by key (`columnOf_`), and 4-4/4-7 now run their full flows with Raid 1/Raid 2 filled in.
- [low, rejected] **Moving the migrations before the grids also changes the legacy Rerolls insert ordering.** The plan's Code Map requires migrations first. The only effect is on the pre-polish 2-column Rerolls, which no longer exists live, and it fixes the same `_Listes` reference shift there. Rerolls is removed in a later story.
- [false] **The live header lookup also applies to Rerolls.** Rerolls' live Classe index equals its contract index, so the result is unchanged.
- [low, patch] **Live header not trimmed in `readClassByName_`.** Each cell is now trimmed before matching, as `requireCurrentLayout_` does.
- [false] **`inheritFromBefore` copies A's formatting into B.** That's intended: the owner asked for the group to look like the raider name.
- [false] **Width 130 differs from the name column's 210.** The intent asks for the same cell formatting rules; width is column layout, and "Raid 1" fits 130.

**After patches:** 4-1 PASS 28, 4-2 PASS 255, 4-3 PASS 104, 4-4 PASS 77, 4-6 PASS 85, 4-7 PASS 47.

## Verification

**Commands:**
- Headless Edge, a fresh `--user-data-dir` per page, for `story-4-1`, `story-4-2`, `story-4-3`, `story-4-4`, `story-4-6`, `story-4-7` -- expected: `PASS` on each.

**Manual checks:**
- Live workbook, Setup > Refresh workbook:
  - B is "Groupe de raid" with the dropdown.
  - The class/spec dropdowns, Rôle, scores and colours are still correct.
  - Data > Create a filter filters by group.
