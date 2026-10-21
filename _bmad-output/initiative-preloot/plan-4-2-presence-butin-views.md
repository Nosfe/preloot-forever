---
title: 'Présence and Butin views, TierItems role sections'
type: 'feature'
ticket: ''
created: '2026-10-21'
status: 'built'
baseline_revision: '71cce1130519f3f2aa2e52c3b91f7ef43e6ed14c' # C:/Repos/Gargul_Preloot (code repo)
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

**Problem:** The owner and raiders are used to the old workbook's `presence_details` grid (raids × raiders, 1/0) and `loot_details` blocks (one 4-column block per raider listing their loot). The new workbook only has flat lists (Attendance, Bench, Awards). TierItems is one flat table with a useless Emplacement column.

**Approach:**
- "Set up / refresh workbook" also builds two read-only view tabs that update themselves from the data tabs through formulas:
  - **Présence**, laid out like `presence_details`;
  - **Butin**, laid out like `loot_details`.
- TierItems drops Emplacement and gets one titled section per role.

**Decisions:**
- Attendance, Bench and Awards stay the flat lists the script and formulas use; the views read them.
- Présence:
  - Row 1 holds Raid (ID), Instance, Date, then one column per raider, sorted by name. One row per raid from Raids, sorted by date.
  - A cell shows `1` when the raider is in Attendance for that raid, `B` when on Bench, and `0` otherwise. Exact name match.
  - Row 2 is a single bold "Total" row: per raider, the number of raids counted as `1` or `B`. Raid rows start at row 3.
  - Header, Total row and first three columns are frozen; the header is white on dark blue, with a right border per raider column.
- Butin:
  - Row 1 holds each raider's name, merged over a 4-column block, sorted by name. Row 2 holds Date, Objet, Objet (ID) and Traitement.
  - From row 3, each block lists that raider's Awards rows, newest first. The item name comes from TierItems by ID, and is empty when unknown.
  - A right border separates the blocks. Rows 1-2 are frozen.
  - Raiders are read from Roster when setup runs, so adding a raider needs a refresh. The values update live.
- TierItems:
  - The columns become Palier, Objet (ID), Objet, Classe, Spé, Statut and Gain simulé (%).
  - A section title row has one of `Tank`, `Heal`, `Melee DPS`, `Ranged DPS` or `Caster DPS` in column A and an empty Objet (ID). It is styled as a dark band with bold white text.
  - Item rows belong to the nearest title above them.
  - Setup seeds the five titles only when TierItems has no data rows.

## Boundaries & Constraints

**Always:**
- Every write goes through one `applyBatch_` call per run.
- Formulas, in cells or in rules, contain no decimal point and no array literal (use `HSTACK`), and every argument separator goes through `argSeparator`.
- Views are fully owned by setup: cleared and rewritten on each run. Data tabs keep the rule that only row 1 is touched, except that an empty Emplacement column is removed.
- Exact, case-sensitive name matching in the views (`EXACT`), as in AD-3.

**Never:**
- No score formulas (4.3) and no Roster/Impact/per-spec raider views (4.5).
- No change to `roster.js`.
- Never delete an Emplacement column that holds data: abort with an alert instead.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Présence | Raids R1, R2; Attendance (R1, Ana); Bench (R2, Ana); Roster Ana, Bob | Ana: R1 `1`, R2 `B`, Total 2; Bob: `0`, `0`, Total 0 | No error expected |
| Présence exact | Attendance (R1, ana); Roster Ana | Ana R1 `0` | No error expected |
| Butin | Awards Ana: item 1 (BIS) and item 2 (NONE); TierItems names item 1 | Ana's block lists both rows, newest first, the name for item 1, empty name for item 2 | No error expected |
| Refresh | Roster gains Cid; setup runs again | Présence and Butin have Cid's column or block; no duplicated rules | No error expected |
| Emplacement empty | Live TierItems has `Emplacement` in D with no data | The column is deleted; headers match the new contract | No error expected |
| Emplacement with data | A cell below `Emplacement` is filled | Nothing is written; the alert names the column | Whole setup aborted |
| Sections | Fresh TierItems | Five title rows; title rows are styled; class, spec and gain rules still apply to item rows | No error expected |
| Sections kept | TierItems already has data rows | Titles are not re-seeded; existing rows are unchanged | No error expected |

</frozen-after-approval>

## Code Map

- House rules learned on the previous change:
  - Keep every French accent in user-visible text (files are UTF-8).
  - Keep all existing comments and existing tests.
  - Give each new function a one-line comment saying what it is for. The owner asked for commented code.
- `src/schema.js`:
  - `TABS`: remove `slot` from TierItems.
  - Add `ROLE_OPTIONS` (already `Tank, Heal, Melee DPS, Ranged DPS, Caster DPS`) as the section titles.
  - Add view definitions (`Présence`, `Butin`, group `view`, fixed sheetIds 1101 and 1102).
- `src/setup.js`:
  - `buildSetupPlan_` loops over the contract tabs.
  - `readExistingHeadersByName_` returns the headers. It also needs to report whether a legacy `slot`/`Emplacement` column holds data.
  - `validateHeaderCompatibility_` accepts the label or the key.
  - `buildTabColorRequests_` handles the `input` and `log` groups; add a colour for `view`.
  - The TierItems class, spec and gain rules use `columnOf_`, so they move automatically.
- New `src/views.js` -- view builders. Each run: create the tab if missing, otherwise clear it (`updateCells` with `fields: '*'` over the sheet, and `unmergeCells`), then write headers, merges, formulas and formats. Read the Roster names inside the lock. Use the `argSeparator` helpers from setup.
- `tests/harness.js` -- the fake batch needs:
  - the requests `deleteDimension`, `mergeCells`, `unmergeCells` and `updateBorders`;
  - `formulaValue` in `updateCells`, stored as a string.

  Formulas are not evaluated in the browser, so tests assert the structure and the formula text. A JS reference for the 1/B/0 and newest-first logic is asserted against the matrix rows.
- `tests/story-4-2.html` -- extend the tests. `tests/story-4-1.html` loads `views.js`.

## Tasks & Acceptance

**Execution:**
- [ ] `src/schema.js` -- contract change and view definitions, as in the Code Map.
- [ ] `src/views.js` -- Présence and Butin builders, following Design Notes.
- [ ] `src/setup.js`:
  - Remove an empty Emplacement column first (`deleteDimension`); abort if it holds data.
  - Seed the TierItems section titles when there are no data rows.
  - Add the title-row style rule as the highest-priority rule.
  - Add the view tab colour.
  - Append the view requests to the same batch.
- [ ] `tests/harness.js`, `tests/story-4-1.html`, `tests/story-4-2.html` -- cover every matrix row.
- [ ] hitl -- owner: push, run "Set up / refresh workbook", then check Présence, Butin and the TierItems sections. Check that the cell formulas are accepted in the fr_FR locale (no `#ERROR!`).

**Acceptance Criteria:**
- Given the live workbook, when setup runs, then the matrix rows hold and data tabs keep their rows.
- Given both test pages in headless Edge, then both show `PASS`.

## Implementation Notes

- The implementer returned no report and left story-4-2 failing: the harness `updateCells` ignored `range`, so the view clear threw. The parent fixed the harness.
- The parent also replaced literal column letters in the view formulas with `dataRange_` (built from `columnOf_`), restored the old dark blue `073763` for view headers, and set Butin raider names in large type (16).

## Plan Change Log

## Review Triage Log

- Pass 1 (quick): high 1, medium 3, low 4, false 0, maybe-false 0. Patched by the parent. Pages PASS: story-4-1 with 37 assertions, story-4-2 with 137.
  - high, patch -- `views.js`: new tabs have 26 columns. Butin needs 4 per raider, so 7 or more raiders would make the whole atomic setup fail live. The view grid is now sized to the roster (`gridProperties.columnCount`). The harness now enforces the 26-column default; a 30-raider test was added.
  - medium, patch -- `views.js` Butin sorted on date only, so awards from the same raid came out oldest first. The Date column is now date and time, and is sorted on.
  - medium, patch -- `tests/story-4-2.html`: several matrix rows were only partly covered (exact name, refresh duplicates, abort writes nothing, title-rule priority). Assertions were added, and the harness clear now resets borders.
  - medium, patch -- `setup.js` title-row rule hard-coded the five role names. It is now built from `ROLE_OPTIONS`, and the misnamed `roleColumnLetter` was renamed.
  - low, patch -- `setup.js`: an unreachable `typeof buildViewRequests_` guard was removed.
  - low, rejected -- `buildSetupPlan_` is no longer pure (the views read Roster). Tests drive `setUpWorkbook` through the harness; passing the names in would add parameters for no caller.
  - low, patch -- the Butin reference sort in the test now uses date and time.
  - low, patch -- the Présence JS reference is now also checked against `ana`-only attendance.

## Design Notes

Formulas are written with `,` and passed through `applyArgSeparator_`. Like rule formulas, cell formulas sent via `userEnteredValue.formulaValue` are parsed in the workbook locale; the live run confirms it.

Présence (row 2 is the Total row; raid rows and one formula per raider column start in row 3):
```
A2: Total
D2: =COUNTIF(D3:D,1)+COUNTIF(D3:D,"B")
A3: =SORT(FILTER(HSTACK(Raids!A2:A,Raids!D2:D,Raids!E2:E),Raids!A2:A<>""),3,TRUE)
D3: =MAP($A3:$A,LAMBDA(r,IF(r="",,IF(SUMPRODUCT((Attendance!$A$2:$A=r)*EXACT(Attendance!$B$2:$B,D$1)),1,IF(SUMPRODUCT((Bench!$A$2:$A=r)*EXACT(Bench!$B$2:$B,D$1)),"B",0)))))
```
Butin block for a raider in column X (one formula in row 3, spilling 4 columns):
```
=IFERROR(SORT(FILTER(HSTACK(Awards!I2:I,IFERROR(XLOOKUP(Awards!F2:F,TierItems!B2:B,TierItems!C2:C),""),Awards!F2:F,Awards!K2:K),EXACT(Awards!E2:E,X$1)),1,FALSE),"")
```
Column letters come from `columnOf_` and `columnLetter_`, never literals. View cell writes use `fields: 'userEnteredValue'` for formulas and leave the spill area empty.

TierItems title-row rule (highest priority, columns A to the last column):
`=AND(OR($A2="Tank",$A2="Heal",$A2="Melee DPS",$A2="Ranged DPS",$A2="Caster DPS"),$B2="")`, dark slate background, bold white text.

## Verification

**Commands:**
- Headless Edge on `tests/story-4-1.html` and `tests/story-4-2.html` (command in the 4.2 plan) -- expected: `PASS`.

**Manual checks (if no CLI):**
- In `preloot-forever`:
  - Présence and Butin show values with no `#ERROR!`.
  - TierItems shows five role bands and no Emplacement column.
  - A second run duplicates nothing.
