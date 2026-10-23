---
title: 'Remove the Rerolls concept'
type: 'refactor'
ticket: ''
created: '2026-10-23'
status: 'built'
baseline_revision: '8ccec69725fe00bfd4fc4656f64e82dc73f2fcf3' # in C:/Repos/Gargul_Preloot (code repo)
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

**Problem:** The workbook still models alts in a Rerolls tab: their attendance credits a main, and their loot is rejected. The owner decided every character is a main listed in Roster, so the concept is dead weight across setup, imports, parses and the snapshot.

**Approach:** Remove Rerolls everywhere:
- the tab and its `_Listes` spec lookup;
- crediting an alt's attendance to its main in End raid (a WCL character not in Roster is simply ignored);
- the "Winner is a Rerolls alt" rejection in the loot import (a winner not in Roster gets the existing "not an exact Roster key" rejection);
- Rerolls names as active Présence/Awards columns (their columns archive like any name not in Roster);
- Rerolls in the parse update, the raid-start protections, tab order, docs and tests.

**Decision (owner, 2026-10-23):** refresh deletes an existing Rerolls tab even when it has rows. Their Présence/Awards columns are archived unless the name is in Roster.

## Boundaries & Constraints

**Always:**
- Roster rules, scores, the Groupe de raid column and the archive/restore behaviour stay as they are.
- Setup refresh is one atomic batch.
- `_Listes` keeps its Rôle table position (columns Q/R), because the Roster Rôle formula reads it.

**Never:**
- Moving Rerolls rows into Roster automatically.
- Changing how archived columns are restored.
- Any other refactor.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Fresh workbook | No tabs | No Rerolls tab created; `_Listes` has no Rerolls lookup | No error expected |
| Empty Rerolls tab | Rerolls with headers only | Refresh deletes the tab | No error expected |
| Rerolls with rows | Rerolls with at least one data row | Refresh deletes the tab and its rows; former alts' columns are archived (name not in Roster) | No error expected |
| WCL attendance | Report character not in Roster (former alt) | Not credited; no main credited for it | No error expected |
| Loot import | Winner not in Roster (former alt) | Rejected as "Winner is not an exact Roster key." | Line listed, others imported |
| Archive | Name with Présence/Awards columns that is no longer in Roster | Columns move to the archive tabs | No error expected |
| Raid start | Start | Protections on 10 tabs (Rerolls gone) | No error expected |

</frozen-after-approval>


## Code Map

- `src/schema.js` -- remove the Rerolls tab entry (L255-265), `LISTS_LAYOUT.rerollsLookupColumn` (L202) and 'Rerolls' from `TAB_ORDER` (L153). Fix the comments at L4, L131 and L197.
- `src/setup.js`:
  - Remove the Rerolls branches in the Rôle formula (L180), bold data (L449), validation (L759/775), conditional formats (L923/969-990) and the role/spec rewrite (L1029).
  - Remove the legacy Rerolls migration (`effectiveHeadersByName_` L311-323, `buildLegacyTabMigrationRequests_` L387-398, `isLegacyRerollsHeaders_` L414) and the `rerollName`/`mainKey` widths.
  - The existing Rerolls sheet is deleted (or refused) through the grids' obsolete-tab mechanism.
- `src/grids.js`:
  - Remove the `_Listes` Rerolls rows (L297-298, `buildRerollsListsRows_` L360-372).
  - Remove the Rerolls entry in `readClassByName_` (L1561) and in `readActiveNames_` (L1582-1600).
  - Add Rerolls to `gridSheetStates_` and `buildGridMigrationDeleteRequests_` (deleted even with rows; no `assertGridMigrationIsSafe_` guard).
- `src/roster.js` -- `buildRosterIndex_(rosterRows)` without Rerolls; `readRosterIndex_` reads Roster only; delete `resolveAttendanceKey_`.
- `src/attendance.js` L315 -- use `findRaiderKey_` directly.
- `src/ledger.js` L163-165 -- drop the alt rejection.
- `src/parses.js` L5-55 -- Roster only.
- `src/snapshot.js` L335 -- remove Rerolls from `freezeTabs`.
- `tests/story-4-*.html`:
  - Remove Rerolls seeds and asserts (4-2 ×42, 4-3 ×9, 4-4 ×7, 4-6 ×2, 4-7 ×6).
  - The protection count drops from 11 to 10.
  - Add tests for the matrix rows.
- Docs (preloot-agent):
  - architecture (Rerolls mentions, AD-3 rule, CAP-5);
  - spec and raid-workflow lines;
  - epic outcome 2 ("Rerolls alts to their main");
  - ticket 4.7 entry wording (NONE→NORMAL, no Rerolls alt rejection).

## Tasks & Acceptance

**Execution:**
- [ ] `src/schema.js`, `src/setup.js`, `src/grids.js` -- remove the tab, its lookups, styling, migrations and active names; delete the existing tab even with rows -- setup no longer knows Rerolls.
- [ ] `src/roster.js`, `src/attendance.js`, `src/ledger.js`, `src/parses.js`, `src/snapshot.js` -- Roster-only lookups, attendance, loot validation, parses and protections -- no alt logic.
- [ ] `tests/story-4-*.html` -- update and add tests for the matrix rows -- coverage.
- [ ] Docs and ticket 4.7 entry -- remove Rerolls -- keep the contract truthful.

**Acceptance Criteria:**
- Given a refreshed workbook, when the owner looks at the tabs, then there is no Rerolls tab, and the class/spec dropdowns and Rôle on Roster still work.
- Given a WCL report with a character absent from Roster, when End raid runs, then only Roster characters are credited.

## Implementation Notes

- Implemented directly.
- Remaining mentions in code, by necessity:
  - `REMOVED_TAB_NAMES = ['Rerolls']` in schema.js, so refresh can find and delete the old tab;
  - two 4-2 tests that seed that tab and check it is deleted.
- `readActiveNames_` now takes only the roster names.
- The 4-3 archive test makes Zed a Roster raider, so 3 Awards blocks remain.
- In 4-4, Zed in the WCL sample is now an unmatched name; Cid gets no credit.
- The 4-4 missing-column test blanks Ana's column, since Cid is no longer credited.
- `custom-export-sample.txt`: checksum `csum-reroll` became `csum-not-in-roster`.
- Docs: alt mentions removed from the architecture (AD-3, attendance rule, layout table, CAP-5), epic, tickets 4.1/4.4/4.7, initiative, PRD, brownfield, raid-workflow and spec.
  - New decision lines record "every character is its own raider" (2026-10-23).
  - History files (past plans, `.memlog`, deferred-work) are left as written.

## Plan Change Log

## Review Triage Log

**Pass 1 (quick): 4 patched, 2 rejected.**

- [low, patch] **`freezeTabs` line in snapshot.js indented 4 spaces instead of 2.** My edit introduced it (the baseline had 2 spaces). Fixed.
- [medium, patch] **The 4-4 missing-column test lost its "other raiders still credited" check.** Zed is now added to Roster in that test, so both Ana and Zed are credited. Zed's column is blanked, and the test asserts that Ana is still credited along with the refresh message.
- [medium, patch] **Matrix rows without tests.** Added in 4-2:
  - a fresh workbook has no alt tab;
  - a headers-only alt tab is deleted;
  - a former alt with Présence/Awards columns has its tab deleted and its columns archived.
- [low, patch] **The `readActiveNames_` comment described a removed guard.** It now points to the guard in `buildArchiveMoveRequests_`.
- [false] **Plan Execution boxes unchecked and Verification results not recorded.** The workflow records results in this log and leaves the task list as planned.
- [false] **"Groupe de raid" added to the architecture's Roster row is out of scope.** The same row was edited to remove the alt tab, and it would otherwise describe the Roster wrongly. It is doc accuracy, not a code refactor.

**After patches:** 4-1 PASS 28, 4-2 PASS 229, 4-3 PASS 109, 4-4 PASS 81, 4-6 PASS 90, 4-7 PASS 47.

## Verification

**Commands:**
- Headless Edge, a fresh `--user-data-dir` per page, for `story-4-1`, `story-4-2`, `story-4-3`, `story-4-4`, `story-4-6`, `story-4-7` -- expected: `PASS` on each.

**Manual checks:**
- Live workbook, Setup > Refresh workbook:
  - Rerolls is gone.
  - The Roster dropdowns and Rôle still work.
  - Raid > Start protects 10 tabs.
