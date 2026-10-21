---
title: 'Workbook rework: Présence grid, Awards blocks, TierItems spec grid, dependent Spé dropdown'
type: 'feature'
ticket: ''
created: '2026-10-21'
status: 'built'
baseline_revision: '33849c758aa731b12d06e4298084c6adef3b2a43' # C:/Repos/Gargul_Preloot (code repo)
route: 'full'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-preloot/plan-4-2-readable-workbook-layout.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The previous change misread the owner:
- Présence and Butin were examples of the layouts wanted for the Attendance and Awards tabs themselves, not new view tabs.
- Attendance and Bench must be one tab.
- TierItems must be a grid of items × specs grouped by role, not a flat list with role title rows.
- Spé must be a real dropdown that offers only the selected class's specs.

**Approach:** "Set up / refresh workbook" builds and refreshes three grid data tabs, adds a dependent Spé dropdown on Roster, and removes the obsolete tabs.

**Decisions:**
- **Présence** (replaces Attendance and Bench) logs attendance only:
  - Columns: Raid (ID), Instance, Date, then one column per raider.
  - Row 2 is a bold Total per raider counting `1` and `B`. Raid rows start at row 3.
  - Cells: `1` = present (the WCL import writes it), `B` = bench (the owner types it), `0` or empty = absent.
  - The header is white on dark blue `073763`. Rows 1-2 and columns A-C are frozen.
- **Awards** is laid out like `loot_details`:
  - One 5-column block per raider. Row 1 holds the raider name, merged over the block, in large white text on `073763`.
  - Row 2 holds Date, Objet, Objet (ID), Traitement and Raid (ID). Entries start at row 3.
  - Traitement is a dropdown: `BIS`, `IMPACT` or `NONE`. A right border separates the blocks. Rows 1-2 are frozen.
- In both Présence and Awards, refresh appends columns or blocks for Roster raiders not yet present. It never deletes or reorders them. New raiders are appended in name order.
- **TierItems** is a spec grid:
  - Columns A and B hold Objet (ID) and Objet. Then each spec has two columns: Gain (%) and Statut.
  - Row 1 holds the role groups, merged and styled bold white on dark slate `253746`.
  - Row 2 holds the spec labels, merged over their pair, with the class colour as background.
  - Row 3 holds `Gain (%)` / `Statut`. Items start at row 4. Rows 1-3 and columns A-B are frozen.
  - Gain cells show as percents: red below 0, plain below 2%, green and bold at 2% or more.
  - Statut is a dropdown: `BIS`, `ALT_BIS`, `IMPACT`, `TIER`, `CLASS_BOUND` or `NORMAL`.
- Spec → role mapping:
  - **Tank**: Guerrier Protection, Paladin Protection, Druide Combat farouche (tank).
  - **Heal**: Paladin Sacré, Prêtre Discipline, Prêtre Sacré, Chaman Restauration, Druide Restauration.
  - **Melee DPS**: Guerrier Armes, Guerrier Fureur, Paladin Vindicte, Voleur Assassinat, Voleur Combat, Voleur Finesse, Chaman Amélioration, Druide Combat farouche (félin).
  - **Ranged DPS**: Chasseur Maîtrise des bêtes, Chasseur Précision, Chasseur Survie.
  - **Caster DPS**: Mage Arcanes, Mage Feu, Mage Givre, Démoniste Affliction, Démoniste Démonologie, Démoniste Destruction, Prêtre Ombre, Chaman Élémentaire, Druide Équilibre.
- **Roster Spé** is a dropdown listing the three specs of the row's class (helper tab `_Listes`, hidden). It replaces the custom spec check.
- Removed: the view tabs Présence (old view) and Butin, and `src/views.js`.
- Awards no longer stores checksum, roll type, off-spec or tier and BiS window; the ledger import (4.7) validates those in memory, and tier and window come from Raids by Raid (ID).

## Boundaries & Constraints

**Always:**
- One `applyBatch_` per run.
- Formulas: no decimal point, separators go through `argSeparator`, sheet names quoted when they start with `_`.
- Grids are sized with `gridProperties.columnCount` before any write past column Z.
- Code finds raider columns and blocks by reading row 1. It finds spec columns from the `SPEC_COLUMNS` table, never from literal letters.
- Keep French accents, existing comments and the roster lookup tests. Each new function gets a one-line comment.

**Never:**
- Never delete a tab or column that holds owner data:
  - Attendance, Bench or old flat Awards with data rows, and old flat TierItems with any item row (an Objet (ID) filled), abort setup with an alert naming the tab.
  - The old Présence view (sheetId 1101) and Butin are always deleted.
- No score formulas (4.3), no WCL or ledger code (4.4, 4.7).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Migrate live workbook | Old tabs present: Attendance, Bench, Awards, TierItems with seeded titles only; views Présence (1101), Butin | Old tabs deleted; Présence, Awards and TierItems grids created | No error expected |
| Old data present | Bench has a data row | Nothing written; the alert names Bench | Whole setup aborted |
| Présence | Roster Ana, Bob | D1 `Ana`, E1 `Bob`; D2 total formula; frozen 2×3 | No error expected |
| Présence refresh | Grid has Ana with values; Roster gains Cid | `Cid` column appended; Ana's values unchanged | No error expected |
| Awards | Roster Ana, Bob | Blocks A-E (Ana), F-J (Bob); row 2 sub-headers; Traitement dropdown | No error expected |
| Awards refresh | Ana's block has an entry; Roster gains Cid | Block K-O for Cid appended; Ana's entry unchanged | No error expected |
| TierItems | Fresh | 58 columns; role groups and spec pairs as mapped; gain and statut rules on every pair | No error expected |
| Spé dropdown | Roster row with Classe `Mage` | Spé offers only Arcanes, Feu, Givre | No error expected |
| Re-run | Everything set up | No duplicated rules, merges or borders; data unchanged | No error expected |

</frozen-after-approval>

## Code Map

- `src/schema.js`:
  - `TABS` (flat contract; `columnOf_` by key) keeps Config, Roster, Rerolls, Raids, RaidReports and PatternItems. Remove Attendance, Bench, Awards and TierItems from it.
  - `CLASS_SPECS` (accents) stays.
  - Add `SPEC_COLUMNS`: ordered `{role, className, spec, label}`. The Druide Combat farouche spec appears twice, with the labels `(tank)` and `(félin)`.
  - Add `GRID_TABS` (Présence 1011, Awards 1008, TierItems 1009) and the `_Listes` id 1020.
- `src/setup.js`:
  - `buildSetupPlan_` builds the flat tabs, with headers, notes, styles, validation, banding, rules, and delete-then-add.
  - `readExistingHeadersByName_` reads rows.
  - `sheetMetadataById_` returns the rules and banding to delete.
  - Helpers to reuse: `rgbHex_`, `columnLetter_`, `applyArgSeparator_`, `formulaArgSeparator_`, `buildConditionalFormatRequest_`, `buildDataValidationRequest_`.
  - Remove the TierItems flat branches: section seed, title rule, slot migration, class, spec and gain rules on TierItems. Remove the call to `buildViewRequests_`.
  - Keep the Roster rules: class colours, duplicate names, the Rerolls rules.
- `src/views.js` -- delete. `dataRange_` and `VIEW_HEADER_HEX` move to the new grid file if still needed.
- New `src/grids.js`:
  - Builders for Présence, Awards, TierItems, `_Listes` and the migration deletes.
  - Read the existing grids and Roster names inside the lock, using `getDataRange().getValues()` and `getMaxColumns()`.
- `tests/harness.js`:
  - Already has the 26-column grid limit, merges, borders, the `range` clear, and delete and append of dimensions.
  - Add `deleteSheet`, `getMaxColumns`, and `hidden` in `updateSheetProperties`.
- `tests/story-4-2.html` -- remove the view tests, add grid tests covering every matrix row, and keep the roster lookup tests. `tests/story-4-1.html` loads `grids.js` instead of `views.js`.

## Tasks & Acceptance

**Execution:**
- [ ] `src/schema.js` -- contract changes as in the Code Map.
- [ ] `src/grids.js` -- grid builders, `_Listes` with the class→specs table and one helper row per Roster row (rows 2-201), and migration deletes.
- [ ] `src/setup.js` -- remove the obsolete branches. Add the Roster Spé `ONE_OF_RANGE` dropdown per row (`='_Listes'!$F{r}:$H{r}`). Call the grid builders.
- [ ] Delete `src/views.js`.
- [ ] `tests/*` -- as in the Code Map.
- [ ] hitl -- owner: push, run setup, check the three grids and the Spé dropdown, and check that the Présence total shows no `#ERROR!`.

**Acceptance Criteria:**
- Given the live workbook, when setup runs, then the matrix rows hold.
- Given both test pages in headless Edge, then both show `PASS`.

## Implementation Notes

- The implementer returned no report and left story-4-2 failing (`seedSheet` refused to re-seed a tab). The parent took over.
- Fixes before review:
  - The grid requests now run first in the batch, so `_Listes` exists before the Roster Spé dropdown references it.
  - The recreated Awards and TierItems get new sheetIds 1012 and 1013, instead of 1008 and 1009, so ids are not reused in the batch that deletes the old tabs.
  - Old rules are deleted only on an existing TierItems grid.
  - `_Listes` no longer writes G:H, which would block the spill.
  - The `_Listes` class column comes from `columnOf_`.
  - The whole Roster Spé column is cleared before the per-row dropdowns.
  - Harness `seedSheet` now replaces the rows of an existing tab.
  - The deleted 4.2 tests were restored.

## Plan Change Log

## Review Triage Log

- Pass 1 (quick): high 2, medium 4, low 7, false 0, maybe-false 0. Patched by the parent. Pages PASS: story-4-1 with 37 assertions, story-4-2 with 151.
  - high, patch -- `grids.js`: refresh set `columnCount` from the computed width, and a lower count deletes columns, including owner data. Refresh now never goes below the current `getMaxColumns()`. Test added.
  - high, patch -- `grids.js`: a blank raider header (Présence) or block title (Awards) compacted the names, so later names landed on another raider's data. Blank slots now keep their position. Test added.
  - medium, patch -- tests: the old-data aborts only checked the alert. They now check that data is kept and no tab is created; the Awards and TierItems aborts were added.
  - medium, patch -- tests: assertions were added for the Traitement dropdown column and values, the Awards block merges, the TierItems role order, the 28 spec labels and 56 gain rules, the `_Listes` Mage specs, and data unchanged after a re-run.
  - medium, patch -- tests: the fr_FR Présence assertion could never fail, so it was removed. fr_FR is still covered by the `_Listes` and rule formulas.
  - medium, patch -- tests: the roster error-message checks were restored.
  - low, patch -- `schema.js` `classSpecRegex_` was dead code; it and its tests were removed.
  - low, patch -- harness: one-line comments added; the unused facade `deleteSheet` was removed.
  - low, rejected -- the fake `unmergeCells` clears every merge, so the re-run merge count is weak. The block merges are now asserted by range instead.
  - low, rejected -- sheetIds differ from the Code Map. This is deliberate and recorded in the Implementation Notes.
  - low, rejected -- `seedSheet` overwrite guard removed. Re-seeding replaces rows on the same id, so a sheet never has two records.
  - low, rejected -- UTF-8 BOM on `story-4-2.html`: harmless in browsers, and the edit tools cannot remove it.

## Design Notes

`_Listes` (hidden):
- A2:A10 holds the class names and B2:D10 their specs, as static values.
- F{r} holds `=IFERROR(XLOOKUP(Roster!B{r},$A$2:$A$10,$B$2:$D$10),"")`, which spills three specs across F:H for Roster row r.
- The Roster Spé validation on row r is `ONE_OF_RANGE` `='_Listes'!$F${r}:$H${r}`, with `showCustomUi` and strict.

Présence Total, for a raider in column X: `=COUNTIF(X3:X,1)+COUNTIF(X3:X,"B")`.

TierItems gain rule for a gain column X: `=X4<0` (red) and `=X4>=1/50` (green and bold), one rule per gain column, range rows 4 and below.

Rule priority: each rule is inserted at index 0, so rules added later win.

## Verification

**Commands:**
- Headless Edge on `tests/story-4-1.html` and `tests/story-4-2.html` -- expected: `PASS`.

**Manual checks (if no CLI):**
- In `preloot-forever`:
  - Présence, Awards and TierItems look as in Decisions.
  - Spé lists only the class's specs.
  - Attendance, Bench and Butin are gone.
