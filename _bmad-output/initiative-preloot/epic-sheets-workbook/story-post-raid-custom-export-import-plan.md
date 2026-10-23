---
title: 'Post-raid Custom-export import'
type: 'feature'
ticket: '7'
created: '2026-10-22'
status: done
baseline_revision: 'c45b608750a3f668db885b9c683c886ef60d303a' # C:/Repos/Gargul_Preloot (code repo)
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

**Problem:** Ending a raid records attendance, but the loot awarded during the raid still has to be typed into Awards by hand. The End raid window's Gargul box refuses any text.

**Approach:** The End raid window imports Gargul's Custom export.
1. The owner pastes the export and clicks **Prévisualiser le loot**.
2. The window lists the valid awards (winner, item name and ID, OS) with a Traitement dropdown on each line, and lists the rejected lines with their reasons.
3. **End raid** then appends one row per award to the winner's Awards block — Date, Objet, Objet (ID), Traitement, Raid (ID) — in the same single batch as the attendance import and the raid end.

**Decisions (owner, 2026-10-22):**
- **Traitement:**
  - The dropdown is prefilled when the line already holds `BIS`, `IMPACT` or `NONE`; otherwise it is empty.
  - An `os: 1` line is forced to `NONE` and its dropdown is disabled.
  - If any valid line still has no Traitement at End raid, nothing is written and the alert asks for one.
- **Raid ID:** the line's `raidId` field is ignored for now, because the companion addon that fills `@GPRAID` is not built yet. Every award goes to the raid being ended.
- **Rejections:** a line is rejected and listed (line number, checksum, date, time, winner, reason) when:
  - it is not valid JSON;
  - the checksum is empty or appears twice;
  - the itemID is not an integer;
  - the winner is not an exact Roster key;
  - the winner is a Rerolls alt (rejected, never mapped to its main);
  - the winner has no Awards block (run setup).

  Valid lines are imported; rejected lines are only listed, in the preview and in the End raid result.
- **Date:** each award's Date is the raid date from the WCL report, as a date value — the same date as the Présence row.
- **Objet:** the item name comes from column B of the Objets tabs for that itemID; it is blank when the item is not listed.
- **Empty box:** an empty Gargul box ends the raid with no awards.
- **Cleanup:** delete `legacy/ratio.js`, the last legacy file (RCLC import, loot coefficients, Pattern/Design prefix detection).

## Boundaries & Constraints

**Always:**
- One `applyBatch_` per End raid: attendance, awards and the raid end all succeed together or nothing is written.
- The server re-parses and re-validates the text at submit; the preview is only a view.
- Exact names, with no case folding.
- French accents are kept; comments are one short line.

**Never:**
- No change to the score formulas, the WCL attendance rules, or the Interchange snapshot.
- No companion addon code.
- No writes outside Awards beyond what End raid already writes.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy path | Sample: Ana BIS item 777, Ana IMPACT item 888, Bob NONE item 999 (not in Objets); valid WCL link | Ana's block gets 2 new rows, Bob's 1, each with raid date, name (blank for 999), ID, treatment, raid ID; Loots BiS/Impact formulas count them; raid ended | — |
| Existing awards | Ana's block already has 1 entry | New rows appended below it, nothing overwritten | — |
| Preview | Same sample, treatments `@GPTREATMENT` | Preview returns 3 awards, treatment empty, plus the item names | — |
| OS line | `"os":1`, treatment BIS chosen | Written as `NONE` | — |
| Missing treatment | One valid line with no chosen treatment | Nothing written; raid stays started | Alert: choose a Traitement for every award |
| Rejected lines | Bad JSON line; duplicate checksum; unknown winner; reroll Zed | Valid lines imported; result lists each rejected line with reason, checksum, date, time, winner | — |
| Empty box | Gargul text empty | Raid ended, no Awards change | — |
| WCL failure | WCL error with valid loot | Nothing written (no awards either) | Alert with WCL status |

</frozen-after-approval>

## Code Map

- `src/ledger.js` -- currently empty. Add the pure helpers, each with a one-line comment:
  - `parseGargulExport_(text)` → `{ lines: [{lineNumber, checksum, winner, itemID, rollType, os, date, time, treatment}], rejected: [{lineNumber, checksum, date, time, winner, reason}] }`:
    - each non-blank line is trimmed and a trailing `,` removed, then `JSON.parse`d;
    - `treatment` is kept only when it is `BIS`, `IMPACT` or `NONE`; otherwise `''`;
    - empty and duplicate checksums are rejected.
  - `validateAwards_(lines, rosterIndex, blockNames)` moves to `rejected` any unknown winner, Rerolls alt (`rosterIndex.rerollToMain`) or winner without an Awards block.
  - `itemNamesById_(itemStates)` reads ITEM_TABS rows from index 3, column A as the ID and column B as the name.
  - `buildAwardRequests_(awardsSheetId, awardsRows, awards, raidId, dateSerial)` appends below the last non-empty row of each winner's 5-column block (rows from `AWARDS_FIRST_ROW - 1`), using `AWARDS_*_OFFSET`.
- `src/attendance.js`:
  - `showEndRaidDialog_`: add the preview button, the awards table with dropdowns (OS lines disabled at NONE), and the rejected list. Submit sends `treatments` as `{checksum: treatment}`.
  - `previewEndRaidLoot(gargulText)` is a new server function returning `{ awards: [...with itemName], rejected: [...] }`.
  - `submitEndRaid(linkText, gargulText, treatments)`:
    - drop the "story 4.7" refusal;
    - parse, validate and apply treatments (OS forced NONE); a missing treatment throws;
    - add `buildAwardRequests_` to the same requests;
    - the message adds the imported count and the rejected lines.
  - Reuse `dateSerialFromReportStart_`, `buildDateCellRequest_`, `buildStringCellRequest_`, `requireRosterIndex_`, `findRaiderKey_`.
- `src/grids.js` -- reuse `readAwardsBlockNames_(rows)`.
- `src/schema.js` -- `AWARDS_BLOCK_WIDTH`, `AWARDS_DATE_OFFSET`, `AWARDS_TREATMENT_OFFSET`, `AWARDS_RAID_ID_OFFSET`, `AWARDS_FIRST_ROW`, `ITEM_TABS`.
- `tests/story-4-4.html` -- its "Gargul text refused" case changes: text is now parsed.
- Not changed: scores, snapshot, the WCL helpers.

## Tasks & Acceptance

**Execution:**
- [ ] `src/ledger.js` -- the pure helpers above.
- [ ] `src/attendance.js` -- preview, dialog and submit changes.
- [ ] `fixtures/custom-export-sample.txt` -- the matrix sample (3 valid lines, one bad JSON, a duplicate checksum, an unknown winner, a reroll winner, one `os:1` line), each line ending with `,` in the Gargul template format.
- [ ] `tests/story-4-7.html` -- every matrix row, plus parser unit cases. Load `ledger.js` in the 4-1, 4-4 and 4-6 pages if they need it.
- [ ] `tests/story-4-4.html` -- update the Gargul-text case to the new behaviour.
- [ ] Delete `legacy/ratio.js`.

**Acceptance Criteria:**
- Given the sample and chosen treatments, when the owner ends the raid, then exactly the awarded raiders' Loots BiS/Impact counts change, and the rejected lines are listed.
- Given the live workbook (manual check), when the owner ends a raid with a real Gargul export, then the Awards rows match Gargul's awards.

## Implementation Notes

- **Implementer:** delivered `ledger.js` (parser, validator, item names, award append), the End raid preview, table and submit in `attendance.js`, the fixture, `story-4-7.html`, the updated Gargul case in `story-4-4.html`, and deleted `legacy/ratio.js`.
- **Parent fix:** a reroll winner was reported as "not an exact Roster key" because the roster check ran first. The reroll check now runs first, and a test asserts both reasons.
- **Test pages:** 4-1 PASS 24, 4-2 PASS 205, 4-3 PASS 103, 4-4 PASS 74, 4-6 PASS 83, 4-7 PASS 31.
- **Not testable here:** the harness can't evaluate formulas, so the Loots BiS/Impact counts updating is left to the live check. The formulas read the Awards rows this story writes.

## Plan Change Log

## Review Triage Log

**Pass 1 (quick lens):**
- [patched] A `null` JSON line crashed the import. Any non-object line is now rejected as Invalid JSON.
- [patched] A duplicate checksum kept the first copy. Every copy is now rejected, using a two-pass count.
- [patched] The winner was trimmed, which broke exact match (AD-3). It is no longer trimmed in the parser, the validator or the award writer.
- [patched] A quoted itemID was accepted. itemID must now be a JSON number of at least 1.
- [patched] A cleared or unknown dropdown value fell back to the line's own treatment. After a preview the dropdown choice now wins, and a missing value refuses with "Choose a Traitement".
- [patched] The award date could differ from the Présence row date. It now uses the existing Présence date when there is one, otherwise the WCL date.
- [patched] The preview had no OS column. One is added.
- [patched] Some helpers had no comment. One-line comments are added, including `summarizeRejectedLootLines_`.
- [patched] Test gaps. New tests cover:
  - rejected-line details in the message;
  - the Raid (ID) and Traitement cells;
  - a missing treatment writing nothing and not calling WCL;
  - a cleared dropdown;
  - a null line;
  - a quoted itemID;
  - both duplicate copies being rejected;
  - a winner with a trailing space.
- [rejected] Tab indentation in `ledger.js` is cosmetic.
- [rejected] The field mask in `buildAwardRowWriteRequest_` is cosmetic; it writes the same cells.

**After patches:** 4-1 PASS 24, 4-2 PASS 205, 4-3 PASS 103, 4-4 PASS 74, 4-6 PASS 83, 4-7 PASS 46.
## Verification

**Commands:**
- Headless Edge, a fresh `--user-data-dir` per page, for `story-4-1`, `story-4-2`, `story-4-3`, `story-4-4`, `story-4-6` and `story-4-7` -- expected: `PASS` on each.

**Manual checks:**
- Live workbook: start a raid, then End raid with a real WCL link and a real Gargul export. Preview, choose the treatments and end. Check the Awards rows, the Loots counts and the Présence row.
