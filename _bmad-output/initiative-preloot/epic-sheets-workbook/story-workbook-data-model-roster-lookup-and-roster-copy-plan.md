---
title: 'Workbook data model, roster lookup and roster copy'
type: 'feature'
ticket: '2'
created: '2026-10-21'
status: done
baseline_revision: 'b80fb21c57d308b34b9dac805674ad7e5ca0d9ab' # C:/Repos/Gargul_Preloot (code repo)
route: 'full'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-preloot/architecture-raid-loot-distribution/architecture-raid-loot-distribution.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The `preloot-forever` workbook has no data tabs, so no later story has a fixed place to read or write. Raider names are still matched case-insensitively and with the `-Thunderstrike` suffix stripped (legacy `ratio.js` `getRosterPlayerKey`, `attendance.js` `getRerollPresenceMaps_`). Raiders cannot yet view the workbook.

**Approach:**
- An owner menu action, "Set up workbook", creates every data tab with its header row in one locked batch and is safe to run again.
- A shared exact-name roster lookup rejects duplicate or invalid keys.
- Native conditional formatting flags bad roster and Rerolls names live.
- The owner copies the roster and Rerolls from the old workbook by hand and shares the workbook with raiders as Viewer.

**Decisions:**
- Owner-only editing is done through Drive sharing: raiders get Viewer access, and no protected ranges are used.
- Keys are compared verbatim; a key with leading or trailing whitespace is invalid.
- Tab names and headers follow Design Notes.

## Boundaries & Constraints

**Always:**
- Every write goes through `applyBatch_`.
- Setup creates missing tabs. An existing tab whose header row is a prefix of the contract gets its missing trailing headers added. Any other existing header row aborts setup with no write.
- Lookups use exact string equality, through `Object.create(null)` maps.
- Rerolls alts resolve only for attendance.

**Never:**
- No formulas, views, WCL, snapshot, ledger or tier logic (stories 4.3-4.8).
- No changes to `legacy/`; stories 4.4 and 4.7 rewrite those files on top of this lookup.
- No change to the old workbook.
- No case-folding or realm stripping.
- No script-driven copy from the old workbook.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| First setup | No data tabs | All tabs are created with headers, row 1 frozen, plus validation and duplicate highlighting; an alert lists the created tabs | No error expected |
| Re-run | All tabs match | No batch is sent; an alert says the workbook is already set up | No error expected |
| Older contract | Roster header row is a prefix | Only the missing trailing headers are written | No error expected |
| Header conflict | A tab's row 1 differs from the contract | Nothing is written; the alert names the tab and both header rows | Whole setup aborted |
| Lookup | Roster `Ana`, `ana`; lookup `ANA` | `Ana` and `ana` are two distinct keys; `ANA` is not found | No error expected |
| Duplicate key | Two Roster rows `Ana` | `requireRosterIndex_` throws, naming `Ana` and both rows; the cells are highlighted | Callers refuse to write |
| Bad reroll | Reroll name equals a roster key, repeats another reroll, or its main is not a roster key | Error lists the row; the cell is highlighted | Callers refuse to write |
| Whitespace key | `Ana ` | Invalid-key error naming the row | Callers refuse to write |

</frozen-after-approval>

## Code Map

- `src/batch.js` -- `applyBatch_(buildRequests)`: the builder runs inside the document lock; `[]` means no write. Reuse it unchanged.
- `src/menu.js` -- `onOpen` builds the "Loot priority" menu. Add the "Set up workbook" item first. Keep the existing items, labels and handlers. Use `DIAGNOSTICS_SHEET_ID` 41041 as the pattern for fixed sheet ids.
- `legacy/ratio.js` L399-444 and `legacy/attendance.js` L1023-1086 -- the old roster lives in `Ratio Présence/Loot (Préloot)`, column A from row 3; Rerolls has the headers "Reroll name" and "Main name". Use them as the source for the hand copy; never call this code.
- `tests/harness.js` -- `TracerHarness`. The fake `batchUpdate` copies the store and commits only when every request succeeds. Extend it; do not rewrite it.
- `tests/story-4-1.html` -- checks that every menu handler exists through `window[functionName]`, so it must also load the new `src` files.

## Tasks & Acceptance

**Execution:**
- [ ] `tools/google_apps_script/src/schema.js` -- `TABS`: ordered `{name, sheetId, headers}`, plus the column-index helper `columnOf_(tab, header)` -- one header contract for every story.
- [ ] `tools/google_apps_script/src/setup.js` -- `setUpWorkbook` handler and the pure builder `buildSetupRequests_(existingHeadersByName)`. New tabs get `addSheet` (fixed id, `frozenRowCount` 1), the header `updateCells`, and the data validation and conditional formats from Design Notes. Prefix tabs get `updateCells` for the missing headers only. Conflicts throw. Alerts summarise the result -- idempotent setup.
- [ ] `tools/google_apps_script/src/roster.js` -- `buildRosterIndex_(rosterRows, rerollRows)` → `{raiders, rerollToMain, errors}`; `readRosterIndex_()` reads both tabs by name; `requireRosterIndex_()` throws with every error; `findRaiderKey_(index, name)`; `resolveAttendanceKey_(index, name)` -- the exact lookup for stories 4.4 and 4.7.
- [ ] `tools/google_apps_script/src/menu.js` -- add the "Set up workbook" → `setUpWorkbook` item.
- [ ] `tools/google_apps_script/tests/harness.js` -- support the requests `updateCells` (at `start` rowIndex/columnIndex), `setDataValidation`, `addConditionalFormatRule` and `updateSheetProperties` (recorded per sheet); sheet facade `getLastColumn`, `getDataRange().getValues()`; and `seedSheet(name, rows)` and `getSheetMeta(name)`.
- [ ] `tools/google_apps_script/tests/story-4-1.html` -- load `schema.js`, `setup.js` and `roster.js` so the handler check still passes.
- [ ] `tools/google_apps_script/tests/story-4-2.html` -- cover each I/O matrix row, including the atomic abort on a conflict, the lock being released, and the rule and validation counts on a new Roster -- per-story test page.
- [ ] hitl -- owner, after `clasp push`:
  1. Run "Set up workbook" twice.
  2. Copy the names from the old roster sheet into `Roster.raiderKey`, and the old Rerolls rows into `Rerolls`, keeping exact in-game spelling. Fill in role, class, spec and tankPriority.
  3. Fix any highlighted cell.
  4. Share the workbook as Viewer with raiders.
  5. Open it from a raider account.

**Acceptance Criteria:**
- Given the pushed script, when the owner runs "Set up workbook" in `preloot-forever`, then the I/O matrix setup rows hold on the live workbook.
- Given a raider account, when it opens the workbook, then every tab is view-only.
- Given the copied Roster and Rerolls, when the owner compares them with the old workbook, then the names and mappings match and no cell is highlighted.
- Given `tests/story-4-1.html` and `tests/story-4-2.html` in headless Edge, then both show `PASS`.

## Implementation Notes

- Live run on `preloot-forever` (fr_FR locale) failed with `Invalid ConditionValue.userEnteredValue ... CUSTOM_FORMULA`: the Sheets API parses rule formulas like typed input, in the workbook locale. Setup now picks `;` when the locale uses a decimal comma (`formulaArgSeparator_`); a fr_FR test was added (story-4-2 PASS, 45 assertions). Commit 8cd102d.

## Plan Change Log

## Review Triage Log

- Pass 1 (quick): high 0, medium 1, low 4, false 0, maybe-false 0. Patched by the parent (the implementer could not be re-engaged). After patching, the pages show PASS: story-4-1 with 37 assertions, story-4-2 with 41.
  - medium, patch -- `src/setup.js` `readExistingHeadersByName_`: `getDataRange` pads row 1 to the widest used column, so an owner note to the right of the headers produced a false header conflict. Trailing empty header cells are now trimmed; a padded-row test was added.
  - low, rejected -- `src/setup.js`: an empty data tab created by hand before setup takes the extend path and gets no frozen row, validation or highlight rules. Unlikely on the setup-created workbook, and the fix adds a branch.
  - low, patch -- `tests/story-4-2.html`: the conflict test did not assert both header rows in the alert. Both are now asserted.
  - low, patch -- `tests/story-4-2.html`: the duplicate-key test did not assert the row numbers. It now asserts `rows 2 and 3`.
  - low, rejected -- `tests/harness.js` `seedSheet`: seeding an existing name corrupts the fake store. No test seeds an existing name; this is a test-only hazard, and the guard adds a branch.

## Design Notes

Tabs, in creation order, with their sheet ids and headers:

| Tab | id | headers |
| --- | --- | --- |
| Config | 1001 | tierId, bisWindowId (values in row 2) |
| Roster | 1002 | raiderKey, class, spec, role, tankPriority, dpsParse, gainFraction |
| Rerolls | 1003 | rerollName, mainKey |
| Raids | 1004 | raidId, tierId, bisWindowId, instance, raidDate, status |
| RaidReports | 1005 | reportCode, raidId, importedAt |
| Attendance | 1006 | raidId, raiderKey |
| Bench | 1007 | raidId, raiderKey |
| Awards | 1008 | checksum, raidId, tierId, bisWindowId, raiderKey, itemID, rollType, os, date, time, treatment |
| TierItems | 1009 | tierId, itemID, itemName, slot, class, spec, status, simGainFraction |
| PatternItems | 1010 | itemID, itemName |

Validation (strict, rows 2 and below):
- Roster.role: `DPS`, `HEALER` or `TANK`.
- Roster.tankPriority: `MT1` or `MT2`.
- Roster.dpsParse: 1-100.
- Roster.gainFraction: 0-1.
- TierItems.status: `BIS`, `ALT_BIS`, `IMPACT`, `TIER`, `CLASS_BOUND` or `NORMAL`.

Conditional formatting uses `EXACT`; `COUNTIF` is case-insensitive.
- Roster A2:A, duplicate key:
  `=AND($A2<>"",SUMPRODUCT(--EXACT($A$2:$A,$A2))>1)`
- Rerolls A2:A, name repeats another reroll or matches a roster key:
  `=AND($A2<>"",SUMPRODUCT(--EXACT($A$2:$A,$A2))+SUMPRODUCT(--EXACT(INDIRECT("Roster!A2:A"),$A2))>1)`
- Rerolls B2:B, main is not a roster key:
  `=AND($B2<>"",SUMPRODUCT(--EXACT(INDIRECT("Roster!A2:A"),$B2))=0)`

Rules are added only when the tab is created, so running setup again never duplicates them. Awards stores tierId and bisWindowId so that the story 4.3 count formulas do not join through Raids. Stories that need more columns append headers to the contract, and setup adds them.

## Verification

**Commands:**
- `msedge --headless=new --allow-file-access-from-files --dump-dom file:///C:/Repos/Gargul_Preloot/tools/google_apps_script/tests/story-4-2.html` -- expected: `PASS`. Run the same check for `story-4-1.html`.
- `clasp show-file-status` from `tools/google_apps_script` -- expected: only `appsscript.json` and `src/*.js` are listed.

**Manual checks (if no CLI):**
- In `preloot-forever`, the ten tabs exist with frozen headers. The second run says the workbook is already set up. A duplicate `raiderKey` is highlighted.
