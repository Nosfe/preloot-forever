---
title: 'Refactor sweep (workbook)'
type: 'refactor'
ticket: '10'
created: '2026-11-02'
status: 'built'
baseline_revision: 'fdf8fb2'
route: 'full'
route_source: 'auto'
review: 'quick'
review_source: 'auto'
lenses_ran: ['adversarial']
review_loop_iteration: 1
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The workbook script carries about 180 lines of upgrade code for older workbook layouts that no longer exist. About 40 user-facing messages are still English while the menu is French. The 7 browser test pages each repeat the same assertion and seeding helpers.

**Approach:** A cleanup only; behaviour on the current layout stays identical. In three passes, each green before the next:
1. Remove the old-layout migration code and its tests.
2. Translate every user-facing message, dialog title, label, button and rejection reason to French.
3. Move the shared test helpers into one file.

The script README was already rewritten (plan-readmes, 2026-10-28) and only needs the parts touched here.

## Boundaries & Constraints

**Always:**
- Same requests and formulas for a current-layout workbook. The browser tests' expected values change only where a message text changes, or where a removed migration test goes.
- Setup must still stop with "nothing was changed" on a header it does not recognise; that protects current data and is not migration.
- Keep the current-layout features that only look like legacy: old-tier grey rows (`oldTierFormat_`, `TIER_START_REF`, `OLD_TIER_STYLE`), the archive of departed raiders, and the Objets/Awards archive tabs.
- French wording style: as in the menu and in parses.js, tier.js and raids.js (sentence case, "Raid 5 terminé.").

**Never:**
- Behaviour changes, new features, or changes to the addon (`Gargul_Preloot/`).
- Changes to the shared fixtures' data. Their message expectations live in the tests only.

Decisions (owner, 2026-11-02):
- **Translation:** translate every user-facing English message to French.
- **Migrations:** remove the old-layout migrations. The live workbook has been refreshed on the current layout and there are no older copies.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Current workbook refresh | current layout | same requests as before the sweep | No error expected |
| Fresh workbook | empty spreadsheet | same tabs, columns, formulas as before | No error expected |
| Unknown header | a current tab with an unrecognised header | setup refused, nothing changed (French message) | French error |
| Old layout (no longer supported) | e.g. a Rerolls tab or lifetime columns | not migrated; current tabs refreshed or refused by the header check | French error when a header conflicts |
| Messages | every alert, dialog, error, End raid summary, rejection reason | French | — |

</frozen-after-approval>

## Code Map

- **Migration (remove):**
  - `src/setup.js`: `legacyRosterColumns_` (L297), `isLegacyRosterHeaders_` (L342), `legacyConfigWindowColumn_` (L292), `needsRosterGroupColumn_` (L347), `buildLegacyTabMigrationRequests_` (L308, called at L47).
  - Helpers `indexOfHeader_`/`buildDeleteColumnRequest_`: remove only if unused afterwards.
  - The migration branch of `effectiveHeadersByName_` (L259-L290, used at L48): keep the header normalisation.
- **Migration, continued:**
  - `src/grids.js`: `assertGridMigrationIsSafe_` (L95, called L15), `isLegacyRaidsSheet_` (L114), `itemTabHasLegacyOrder_` (L122), `isLegacyAwardsSheet_` (L130, also checked in `buildAwardsGridRequests_` L804), `isLegacyTierItemsSheet_` (L139), `legacyTierItemsHasItemRows_` (L149), `buildGridMigrationDeleteRequests_` (L164, called L17), `buildLegacyNoneTreatmentRequest_` (L778, L804/L809), any Objets order or Emplacement-insert migration, and the reads of legacy tab states in `gridSheetStates_` (L40).
  - `src/schema.js`: `REMOVED_TAB_NAMES`, `GRID_TABS.tierItems`, and `formerLabels` on the column definitions (with their use in setup.js `validateHeaderCompatibility_` L561).
- **Migration tests:** `tests/story-4-2.html`:
  - `seedLegacyLiveWorkbook` (L33-50) and the migration happy path (L100-130);
  - the Objets order migration (L155-205) and `expectAbort` legacy cases (L220-280);
  - legacy tab deletion and the Rerolls removal cases (L280-405);
  - the old Parse label (L720-730).
  
  Keep the fresh-layout and current-refresh tests.
- **English messages:** found by grep. Translate the strings and update each test's `contains(...)` expectation.
  - `src/attendance.js`: the WCL dialog L27-66, End raid L14-20, L59-149, L195-242, L251-270, L468, L525-542, and the WCL errors L551-644.
  - `src/batch.js`: L7, L22.
  - `src/grids.js`: the setup aborts that remain after the removal.
  - `src/ledger.js`: L30 and the rejection reasons L77-121, plus `validateRaidIds_`.
  - `src/parses.js`: L35-37, L86-92.
  - `src/raids.js`: L38.
  - `src/roster.js`: L56.
  - `src/schema.js`: L318-324, developer-facing; keep these English.
  - `src/setup.js`: L19-21.
  - `src/snapshot.js`: L53, L294, L421-430, L493, L561.
  - `src/tier.js`: L45.
- **Test helpers:** `equal`/`contains` (7 pages), `truthy` (5) and `withHarness` (6) live in each page. `seedCoreTabs_`/`setStartedRaid_`/`queueWclSuccess_` repeat in 4-4 and 4-7. They move to a new `tests/helpers.js` loaded after `harness.js`.
- `legacy/`: an empty, untracked folder; delete it.

## Tasks & Acceptance

**Execution:**
- [x] Pass 1: remove the migration code listed in the Code Map (schema.js, setup.js, grids.js) and its story-4-2 tests; run every page.
- [x] Pass 2: translate the messages in all `src/*.js` files except schema's developer errors; update the `contains(...)` expectations; run every page.
- [x] Pass 3: `tests/helpers.js`; remove the copies from the pages; run every page.
- [x] Delete the empty `legacy/` folder. Check `tools/google_apps_script/README.md` against the changes. `clasp push --force` after the passes.

**Acceptance Criteria:**
- Given the 7 browser pages, when each runs headless, then each prints PASS.
- Given the live workbook, when the owner runs **Rafraîchir le classeur** after the upload, then it succeeds with nothing changed in the data.

## Implementation Notes

- Pass 1 also removed the `formerLabels` header fallback in `snapshot.js` `requireCurrentLayout_`, the presence 1101 check and the Objets Emplacement insert in grids.js, and `indexOfHeader_` (its last caller, `readClassByName_`, now uses `columnOf_`). story-4-3 lost its lifetime-column and NONE-rewrite migration tests; its "Roster is extended" test now seeds the current six owner columns. story-4-6's old-Config migration test became a current-Config refresh test.
- Pass 2: `batch.js` `applyBatch_ request builder ...` stays English (developer error). `RAID_OPEN_PROTECTION_PREFIX` ('Raid ouvert') stays: it matches protections already in the live workbook.
- Pass 3: the shared `seedCoreTabs_` writes story-4-7's two Objets Caster DPS items for 4-4 too; 4-4 is unaffected.
- Result: 7 pages PASS (25, 170, 99, 81, 100, 59, 39). Diff vs fdf8fb2: about 180 insertions, 1170 deletions.

## Plan Change Log

## Review Triage Log

Quick review (1 adversarial reviewer), 2026-11-02:
- **Fixed:** grids.js `readClassByName_` stale migration comment and live-header lookup -> `columnOf_`; `indexOfHeader_` removed.
- **Fixed:** ledger.js raidId reason said "raid ouvert"; Config labels it "Raid en cours". The cancel summary in snapshot.js now says "Raid en cours vidé" too.
- **Fixed:** story-4-7 indentation of two `contains` blocks.
- **Dismissed (medium):** `requireCurrentLayout_` sends an old-layout tab to Rafraîchir, which refuses it. No old-layout workbook exists (owner decision); the refusal names the conflicting headers.
- **Dismissed (low):** extra test for an old-layout Roster refusal; the unknown-column abort covers the same check.
- **Dismissed (low):** `raider: message` spacing in snapshot.js validation lines; unchanged text, nit.

## Verification

**Commands:**
- Headless Edge on `tests/story-4-1`, `4-2`, `4-3`, `4-4`, `4-6`, `4-7` and `4-8.html` (fresh `--user-data-dir` each, `--allow-file-access-from-files`) -- expected: PASS on each.

**Manual checks (if no CLI):**
- The owner runs Rafraîchir le classeur on the live workbook once after the upload.
