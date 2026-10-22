---
title: 'Score formulas and shared fixtures'
type: 'feature'
ticket: '3'
created: '2026-10-22'
status: 'built'
baseline_revision: '5508d937b83aad4ae3d81cb85d5d5076893c7287' # C:/Repos/Gargul_Preloot (code repo)
route: 'full'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-preloot/spec-raid-loot-distribution/allocation-rules.md'
  - '{project-root}/_bmad-output/initiative-preloot/plan-4-2-workbook-polish.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The Roster shows no scores. The owner and raiders cannot see BiS Ratio or Impact standing, and the addon (epic 5) has no shared reference values to check its own calculations against.

**Approach:**
- "Set up / refresh workbook" adds calculated Roster columns, as native formulas per allocation-rules.md:
  - Présence palier and Max palier;
  - Présence vie and Max vie;
  - Loots BiS and Loots Impact;
  - Ratio BiS;
  - Impact (sans gain objet).
- A pure JS reference (`src/scores.js`) and `fixtures/scores.json` define the expected unrounded values. Epic 5's Lua will run the same fixtures.

**Decisions:**
- Formulas are written per Roster row (rows 2-201) and refer only to their own row, so sorting Roster keeps them correct.
- Raiders are matched to their Présence column and Awards block by exact name in row 1 (`EXACT`).
- **Tier presence:**
  - Présence palier counts the raider's `1` and `B` cells in Présence rows dated on or after Config's Début fenêtre BiS.
  - Max palier counts those raid rows, minimum 1.
  - An empty start date means every raid.
- **Lifetime presence:** Présence vie and Max vie are the same counts over every Présence row. Archived tiers join this count in story 4.8.
- **Loots:**
  - Loots BiS counts `BIS` in the raider's Awards block with a Date on or after the start date.
  - Loots Impact counts every `IMPACT` in the block.
- **Ratio BiS** = (Présence palier / Max palier) / (Loots BiS + 1).
- **Impact (sans gain objet)** = (Présence vie / Max vie) × parse / (Loots Impact + 1). An empty parse counts as 1. The cell is empty for a `🛡️ Tank` role.
- **Display:** ratios and Impact show 3 decimals; stored values are unrounded.
- Formula cells are owned by setup and rewritten on every run. The header note says "Calculé, ne pas saisir".
- **Full Impact Score** (used by the addon and the fixtures) = Impact (sans gain objet) × item gain. It is computed only when the item's Statut for the raider's spec is `IMPACT`, and is null for tanks or any other Statut.

## Boundaries & Constraints

**Always:**
- One `applyBatch_` per run.
- Formulas: no decimal point; separators go through `argSeparator`; column letters and grid positions come from `columnOf_` and shared constants, never literals; sheet names with accents are quoted (`'Présence'!`).
- Keep French accents, existing comments and tests. Each new function gets a one-line comment.

**Never:**
- No snapshot export (4.6), WCL import (4.4), ledger import (4.7) or archives (4.8).
- No change to the Présence, Awards or Objets layouts.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Columns | Setup on the live Roster | Roster keeps A-E data and gains the 8 calculated columns with formulas in rows 2-201 | No error expected |
| Tier window | Start 2026-11-01; Ana `1` on 10-28 and 11-02, `B` on 11-04 | Présence palier 2, Max palier 2, Présence vie 3, Max vie 3 | No error expected |
| No start | Config start empty | Tier equals lifetime | No error expected |
| Loots | Ana block: BIS on 10-29, BIS on 11-03, IMPACT, NONE | Loots BiS 1, Loots Impact 1 | No error expected |
| Ratio and Impact | Values above, parse 80, role ✚ Heal | Ratio BiS = (2/2)/(1+1) = 0.5; Impact = (3/3)×80/(1+1) = 40 | No error expected |
| Tank | Role 🛡️ Tank | Impact cell empty; Ratio BiS still computed | No error expected |
| No raids | Empty Présence | Max = 1, presences 0, Ratio 0 | No error expected |
| Fixtures | Each case in scores.json | JS reference equals expected bisRatio, impactBase and impactScore exactly; near-tie cases stay distinct; exact-tie cases are equal | No error expected |
| Re-run | Setup twice | Same formulas; nothing duplicated | No error expected |

</frozen-after-approval>

## Code Map

- `src/schema.js`:
  - `TABS` Roster columns `raiderKey, class, spec, role, dpsParse`. Append 8 columns flagged `formula: true`, with French labels and notes: `tierPresence`, `tierPresenceMax`, `lifetimePresence`, `lifetimePresenceMax`, `bisLootCount`, `impactLootCount`, `bisRatio`, `impactBase`.
  - Add grid constants: `PRESENCE_FIRST_RAIDER_COLUMN = 3`, `PRESENCE_DATE_COLUMN = 2`, `PRESENCE_FIRST_RAID_ROW = 3`, `AWARDS_BLOCK_WIDTH = 5`, `AWARDS_DATE_OFFSET = 0`, `AWARDS_TREATMENT_OFFSET = 3`, `AWARDS_FIRST_ROW = 3`.
  - `ROLE_DISPLAY.Tank.value` is `🛡️ Tank`.
  - Config `bisWindowStart` is read via `columnOf_`, row 2.
- `src/grids.js` -- Présence and Awards builders currently hard-code 3, `* 5`, `+ 3`. Switch them to the constants; the layout is unchanged.
- `src/setup.js`:
  - `buildSetupPlan_` loops over `TABS` and runs header, style, validation and rules per tab. Add `buildRosterFormulaRequests_(sheetId, tab, argSeparator)`: one `updateCells` writing `formulaValue` for rows 2-201 in the formula columns, plus `repeatCell` number format `0.000` on Ratio BiS and Impact.
  - The header check accepts prefix headers, so the new columns append.
  - Validation and class/role rules do not touch the formula columns.
- New `src/scores.js` -- pure functions `bisRatio_(tierPresence, tierMax, bisLoots)`, `impactBase_(lifetimePresence, lifetimeMax, parse, impactLoots, isTank)` and `impactScore_(impactBase, statut, gainFraction)`. They are reused by story 4.6's export check.
- New `fixtures/scores.json` -- `cases[]` with `name`, `inputs` (all operands, role, statut, gainFraction) and `expected` (`bisRatio`, `impactBase`, `impactScore`, `null` where not applicable). Include:
  - the matrix example;
  - an empty parse;
  - a tank;
  - a NORMAL Statut;
  - a negative gain;
  - zero raids;
  - a near-tie pair (impactBase differs by less than 1e-9 relative);
  - an exact-tie pair.
- New `tests/story-4-3.html`:
  - Load the fixture by synchronous XHR (the page runs with `--allow-file-access-from-files`). Compare `scores.js` with each case using `===`; near-tie and exact-tie are compared between the pair.
  - Run setup in the harness and assert the formula text for each matrix row: the exact header match, the start-date filter, `1` and `B` counted, the BIS/IMPACT counts, the tank blank, empty parse as 1, min Max 1, `'Présence'!` quoted, and no commas in fr_FR.
  - Assert that a re-run is stable.
- `tests/story-4-1.html`, `tests/story-4-2.html` -- load `scores.js` and keep passing.

## Tasks & Acceptance

**Execution:**
- [ ] `src/schema.js`, `src/grids.js` -- columns and constants as in the Code Map.
- [ ] `src/setup.js` -- Roster formula and format requests.
- [ ] `src/scores.js`, `fixtures/scores.json` -- the reference and the fixtures.
- [ ] `tests/story-4-3.html` (plus `scores.js` loaded in the 4-1 and 4-2 pages) -- cover every matrix row.
- [ ] hitl -- owner: push and run setup. On a copy of the workbook, enter the "Tier window" and "Loots" rows (Config start, Présence cells, Awards block lines) and compare the Roster with the matrix. Check a raider account sees Roster read-only.

**Acceptance Criteria:**
- Given the live workbook copy with the matrix inputs, when setup has run, then the Roster shows the matrix values (3-decimal display).
- Given the three test pages in headless Edge, then all show `PASS`.

## Implementation Notes

- The implementer delivered with all pages passing and no tests deleted.
- Parent hardening before review:
  - The exact name lookup is wrapped in `ARRAYFORMULA` (`exactHeaderMatch_`), so `EXACT` compares the whole header row in Sheets.
  - Boolean-only `SUMPRODUCT`s are coerced with `--`.
  - New `PRESENCE_RAID_ID_COLUMN` constant replaces `PRESENCE_FIRST_RAIDER_COLUMN - 2`.

## Plan Change Log

## Review Triage Log

- Pass 1 (quick): high 0, medium 4, low 4, false 0, maybe-false 0. Patched by the parent. Pages PASS: story-4-1 with 27 assertions, story-4-2 with 176, story-4-3 with 73.
  - medium, patch -- Max palier and Max vie showed `1` on empty Roster rows, which stretched `getDataRange` and `hasAnyDataRows_`. They are now blank when the name is empty, like the other columns.
  - medium, patch -- tests did not assert the exact match, the Loots BiS date filter and offsets, the absence of a date filter on the lifetime counts, the last formula row, or the pre-4.3 Roster append keeping A-E data. All are now asserted.
  - medium, patch -- a Config start date entered as text silently meant "no window". Config's Début fenêtre BiS now has strict `DATE_IS_VALID` validation and a date format.
  - medium, patch -- `impactBase_` read the text parse "80" as 80, while the sheet's `N()` gives 1. The JS now matches the sheet, with a test.
  - low, patch -- the fixture's missing parse is now `null` instead of `""`, for the Lua consumer.
  - low, patch -- the Awards sheet name and the Config reference come from constants. The Présence total row start and the Awards Traitement offset and validation row use the grid constants.
  - low, rejected -- the literal label offsets in `buildAwardsRowTwo_` are cosmetic, and the header labels are fixed.
  - low, rejected -- the `$1:$1` header row and `$1000` row bound have no constant. They are formula idioms, fixed by design (Design Notes).
- Note: run each headless Edge page with its own `--user-data-dir`; a shared profile hung once.

## Design Notes

Roster row r, letters from `columnOf_` (here A name, D role, E parse, F-M calculated); `s = N(Config!$C$2)`.
```
F: =IF($Ar="","",IFERROR(LET(c,MATCH(TRUE,EXACT('Présence'!$1:$1,$Ar),0),v,INDEX('Présence'!$3:$1000,0,c),d,INDEX('Présence'!$3:$1000,0,3),i,INDEX('Présence'!$3:$1000,0,1),SUMPRODUCT((i<>"")*(d>=N(Config!$C$2))*((v=1)+(v="B")))),0))
G: =MAX(1,SUMPRODUCT((INDEX('Présence'!$3:$1000,0,1)<>"")*(INDEX('Présence'!$3:$1000,0,3)>=N(Config!$C$2))))
H, I: as F, G without the date factor
J: =IF($Ar="","",IFERROR(LET(c,MATCH(TRUE,EXACT(Awards!$1:$1,$Ar),0),SUMPRODUCT((INDEX(Awards!$3:$1000,0,c+3)="BIS")*(INDEX(Awards!$3:$1000,0,c)>=N(Config!$C$2)))),0))
K: as J with "IMPACT" and no date factor
L: =IF($Ar="","",(Fr/Gr)/(Jr+1))
M: =IF(OR($Ar="",$Dr="🛡️ Tank"),"",(Hr/Ir)*IF(N($Er)=0,1,$Er)/(Kr+1))
```
Row ranges `$3:$1000` avoid grid-width limits. Present `INDEX(…,0,c)` columns as 1-based: `c` (MATCH) is already 1-based; the date and ID columns are the constants + 1. Présence and Awards dates must be real date values; the 4.6 and 4.7 writers store them so.

## Verification

**Commands:**
- Headless Edge on `tests/story-4-1.html`, `tests/story-4-2.html` and `tests/story-4-3.html` -- expected: `PASS`.
