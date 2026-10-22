---
title: 'Raid lifecycle and pre-raid snapshot export'
type: 'feature'
ticket: '6'
created: '2026-10-22'
status: 'built'
baseline_revision: '6335ec97673610a2ecd1569f7edd159c26dd1700' # C:/Repos/Gargul_Preloot (code repo)
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

**Problem:** Before a raid, the owner has no way to hand the workbook's scores and item table to the Gargul companion, and nothing records which raid is in progress.

**Approach:** The owner clicks **Export raid snapshot** before the raid.
- **When no raid is open**, the click opens one:
  - The next Raid (ID) is created.
  - A Raids row is appended with only that ID.
  - Config's Raid ouvert is set.
  - Score inputs get warning-only protections.
  - All of this happens in one batch.
- **When a raid is already open**, the click re-exports with the same ID and writes nothing.
- **In both cases**, the action builds the Interchange v2 snapshot from the current workbook values and shows it Base64-encoded in a dialog with a copy button.

**Decisions (owner, 2026-10-22):**
- **Flow:**
  - Before the raid, the owner clicks Export and pastes the Base64 into Gargul.
  - After the raid:
    - the owner pastes Gargul's JSON and processes the loot (4.7, which closes the raid);
    - then pastes the WCL link in the Raids tab and processes it (4.4). This fills the raid's Présence row, Date and Instance.
  - 4.6 does not use WCL and adds no Présence row, so an open raid never changes any score.
- **Raid (ID):**
  - Plain integers 1, 2, 3, auto-incremented, with no owner input.
  - Next = highest numeric ID in Raids column A and Présence column A (rows 3+), plus 1. With no raids yet, the first ID is 1.
- **Freeze:**
  - While a raid is open, warning-only protections cover Roster, Rerolls, Présence, Awards, the five Objets tabs and Config. Each protection's description starts with `Raid ouvert`.
  - 4.7 removes them when it closes the raid.
- **Export:** Base64 only (UTF-8 JSON), in a dialog with a read-only textarea and a copy button.

## Boundaries & Constraints

**Always:**
- **Writes:**
  - One `applyBatch_` per run.
  - Validate everything before writing. An invalid workbook alerts the error list and writes nothing.
- **Snapshot values:**
  - Snapshot values are the sheet's unrounded formula values.
  - `bisRatio` and `impactBase` must match `scores.js` within `1e-9 * max(1, |recomputed|)`; otherwise reject.
- **Envelope:** `tierId` and `bisWindowId` come from Config row 2 and must be non-empty.
- **Code style:** French accents kept; comments are one short line.

**Never:**
- No WCL calls and no credentials (4.4).
- No ledger import or raid closing (4.7).
- No Présence row, Date or Instance written.
- No change to the Roster formulas or the grid layouts.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| First export | Raid ouvert empty; Présence IDs 1-3 | Raid 4 opened (Raids row `4`, Config `4`, protections); dialog shows Base64 whose JSON has `raidId: "4"` | — |
| Re-export | Raid ouvert `4` | Same `raidId`; no write | — |
| Tank | Rôle `🛡️ Tank` | `role: TANK`, `impactBase: null` | — |
| Parse | Empty, text or 0 | `dpsParse: 1` | Above 100: reject |
| Feral druid | Druide Combat farouche | Tank → `Druide Combat farouche (tank)`, otherwise `(félin)` | — |
| Bad raider | Missing class, spec or role; unknown spec; Presence > Max; non-integer count; score mismatch | Nothing written | Alert lists the raiders and reasons |
| Items | Same itemID on two Objets tabs | One item, specs merged | Same itemID+classSpec twice, non-integer itemID, or non-numeric Gain: reject |
| Config | Palier actif or Fenêtre BiS empty | Nothing written | Alert names the field |

</frozen-after-approval>

## Code Map

- `src/snapshot.js` -- stub `exportRaidSnapshot()`; replace it with the action plus pure builders.
- `src/schema.js`:
  - reuse `TABS`, `columnOf_`, `ROLE_DISPLAY`, `CLASS_SPECS` (with `specIcons`), `SPEC_COLUMNS` (role + className + spec + label), `ITEM_TABS`, `GRID_TABS`, and the `PRESENCE_*` constants;
  - add `RAID_OPEN_PROTECTION_PREFIX`.
- `src/setup.js`:
  - `specDisplayValue_(className, spec)` (the emoji spec text stored in Roster);
  - `roleDisplayValue_`;
  - `columnLetter_`.
- `src/scores.js` -- `bisRatio_` and `impactBase_` for the recompute check.
- `src/batch.js` -- `applyBatch_` (lock plus one batch; an empty request list does nothing).
- Objets layout (grids.js, `buildTierHeaderRows_`):
  - item rows start at row 4 (index 3);
  - column A is Objet (ID), B is Objet;
  - spec i of the tab's role has Statut at column 2+2i and Gain at column 3+2i;
  - Gain is a fraction (percent format);
  - spec order = the `SPEC_COLUMNS` filtered by role.
- `tests/harness.js`:
  - add `HtmlService` (`createHtmlOutput`, `setWidth`/`setHeight`, captured `showModalDialog`);
  - add `Utilities.base64Encode` / `base64Decode` with UTF-8;
  - add `addProtectedRange` / `deleteProtectedRange`;
  - add `protectedRanges` in `sheetsGet_`.
- `tests/story-4-1.html` -- already loads `snapshot.js`; keep its menu test passing.
- Not changed: `grids.js` layouts, `ledger.js`, `attendance.js`, `tier.js`.

## Tasks & Acceptance

**Execution:**
- [ ] `src/schema.js` -- add `RAID_OPEN_PROTECTION_PREFIX = 'Raid ouvert'` -- shared with 4.7.
- [ ] `src/snapshot.js` -- add the pieces below:
  - `exportRaidSnapshot()`:
    - inside `applyBatch_`, read Config, Roster, the Objets tabs, Raids and Présence;
    - build and validate the snapshot;
    - when no raid is open, return the open requests; otherwise return `[]`;
    - then show the Base64 dialog.
  - Pure builders, each with a one-line comment:
    - `nextRaidId_`, `buildSnapshotRaiders_`, `buildSnapshotItems_`, `buildSnapshot_`, `buildOpenRaidRequests_`;
    - `classSpecLabel_(className, specCell, role)`;
    - `snapshotRole_(roleCell)`.
- [ ] `tests/harness.js` -- add the fakes listed in the Code Map.
- [ ] `fixtures/snapshot-sample.json` -- the snapshot JSON for the story-4-6 seeded workbook: 3 raiders (DPS, healer, tank), feral tank, empty parse, and 2 items with one shared across two tabs.
- [ ] `tests/story-4-6.html`:
  - seed a workbook, run the export and check the matrix;
  - decode the Base64 and deep-compare it with the fixture;
  - check re-export writes nothing;
  - check protections are added once with the prefix;
  - check a rejected workbook is left unchanged.

**Acceptance Criteria:**
- Given the seeded workbook, when the owner exports twice, then both dialogs decode to the same JSON as `fixtures/snapshot-sample.json`, and only the first run wrote (Raids row, Config Raid ouvert, 10 protections).
- Given an invalid Roster row, when exporting, then the alert names the raider and nothing is written.
- Given the live workbook, when the owner exports, then the dialog's Base64 is accepted by the current addon importer's Base64 decoding (manual check).

## Implementation Notes

- **Implementer:** delivered `snapshot.js`, the harness fakes (HtmlService, Base64, protected ranges), the fixture and `story-4-6.html`. Because 4.6 implemented the snapshot stub, `story-4-1.html` now expects 3 stub alerts instead of 4. The implementer could not run headless Edge.
- **Parent fixes:**
  - `nextRaidId_` skipped the first Raids data row; the test seed hid this. It now scans Raids from row 2 and Présence from `PRESENCE_FIRST_RAID_ROW`.
  - Raid IDs are now written as numbers.
  - Added tests for the edge-case table rows the implementer had not covered: parse, Presence > Max, counts, score mismatch, role, spec, félin, items, empty Config, and next ID.
- **Test pages:** 4-1 PASS 26, 4-2 PASS 181, 4-3 PASS 98, 4-6 PASS 37.
- **Tickets updated with the owner flow:** 4.4 (WCL link in Raids after the raid; adds the Présence row, Date and Instance) and 4.7 (removes the `Raid ouvert` protections).

## Plan Change Log

## Review Triage Log

- **Pass 1 (quick):** high 0, medium 3, low 9, false 0, maybe-false 2. The parent patched the code because the implementer cannot be re-engaged. Pages after patching: 4-1 PASS 26, 4-2 PASS 181, 4-3 PASS 98, 4-6 PASS 60.
  - medium, patch -- duplicate Roster names were exported (contract: unique `raiderKey`). Now rejected as "nom en double", with a test.
  - medium, patch -- a spec was not checked against its role (Mage Givre + Tank exported as TANK). `classSpecLabel_` now keeps only the `SPEC_COLUMNS` entry whose role group matches, otherwise "incompatible". This also settles félin vs tank. Tests both ways.
  - medium, patch -- the copy button failed silently when `navigator.clipboard` refuses in the sandboxed iframe. Rejection now falls back to `execCommand`, then a Ctrl+C hint.
  - low, patch -- a parse between 0 and 1 was exported. Now: 0, empty or text gives 1; otherwise the value must be 1-100. Test added.
  - low, patch -- a parse above 100 also produced a false Impact mismatch. Impact is not rechecked when the parse is invalid. Test asserts a single error.
  - low, patch -- `nextRaidId_` read Raids with the Présence constant. Now uses `columnOf_(Raids, 'raidId')`.
  - low, patch -- the integer parser accepted `true`, blank, exponent text, 0 and negatives. Replaced by `snapshotPositiveInteger_` (numbers or digit-only text, at least 1). Tests for item 0 and raid IDs `true`/`1e3`.
  - low, patch -- item errors named the role, not the tab, and the duplicate error gave no location. Now `Objets <rôle> ligne N`, and the duplicate error names the earlier location.
  - low, patch -- duplicated `normalizeSnapshotString_` and generic global names. Now reuses `normalizeCellString_`; helpers renamed `snapshotSheet_`, `snapshotPositiveInteger_` and `snapshotEscapeHtml_`.
  - low, patch -- helpers had no comment. Added one line each.
  - low, patch -- protection tests were weak. Now asserts one warning-only protection per tab with the exact description, and that a leftover `Raid ouvert` protection is replaced.
  - low, patch -- only one end-to-end rejection test. Added an empty-Config action run (alert names the field, nothing written, no dialog) and a check that `exportRaidSnapshot` exists.
  - maybe-false, defer (high if true) -- AC 3: is the Base64 accepted by the current addon importer? No `base64decode`/`Base64:Decode` call was found in the repo's Lua, so it can't be verified here. To settle: the owner pastes the export into the addon in game, or epic 5's importer test decodes `fixtures/snapshot-sample.json` encoded.
  - maybe-false, reject -- the 4-1 menu entry resolving to a function was treated as weak. Now asserted in 4-6.

## Design Notes

**classSpec:**
- The Roster Spé cell is either `specDisplayValue_(class, spec)` (e.g. `❄️ Givre`) or the bare spec.
- Match it against `CLASS_SPECS[class].specs`, then find the `SPEC_COLUMNS` entry for class + spec.
- When there are two entries (Druide Combat farouche), pick the `Tank` entry for a tank role and the other one otherwise.

**Roles:** `🛡️ Tank`/`Tank` → `TANK`; `✚ Heal`/`Heal` → `HEALER`; the 3 DPS roles → `DPS`.

**Protections:** each request is `addProtectedRange { protectedRange: { range: { sheetId }, warningOnly: true, description: 'Raid ouvert 4 : entrées de score figées' } }`. Before adding, remove any existing protection whose description starts with the prefix.

**Base64:** `Utilities.base64Encode(json, Utilities.Charset.UTF_8)`. JSON uses `JSON.stringify` with no rounding.

## Verification

**Commands:**
- Headless Edge, one fresh `--user-data-dir` per page, for `story-4-1`, `story-4-2`, `story-4-3` and `story-4-6` -- expected: `PASS` on each.

**Manual checks:**
- Live workbook:
  - Export: a dialog with Base64 appears; Raids gets a new row; Config's Raid ouvert is set.
  - Editing Roster shows the protection warning.
  - Exporting again shows the same ID.
