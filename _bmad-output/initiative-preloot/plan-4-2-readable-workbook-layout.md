---
title: 'Readable workbook layout: labels, class colours, gain format'
type: 'feature'
ticket: ''
created: '2026-10-21'
status: 'built'
baseline_revision: '8cd102df98b58f53208a8cc1b9d2f9c5511389d7' # C:/Repos/Gargul_Preloot (code repo)
route: 'full'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-preloot/epic-sheets-workbook/story-workbook-data-model-roster-lookup-and-roster-copy-plan.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The data tabs show technical headers (`raiderKey`, `gainFraction`), so raiders and the owner cannot tell at a glance what each column is for. The tabs are also unstyled: no class colours, gain values are not highlighted, and there is no visual structure.

**Approach:** Every contract column gets a readable label and a header note that explains it. "Set up workbook" applies one consistent layout to every data tab each time it runs, and replaces the earlier rules without duplicating them:
- styled headers and column widths;
- tab colours: owner inputs versus script-written logs;
- percent display for gains;
- WoW class colours;
- gain highlighting: red below 0, nothing below 2%, green and bold at 2% or more.

The raider-facing views (story 4.5) reuse this style.

**Decisions:**
- Labels, notes and class names are in French.
- Gain colouring applies only to the TierItems per-item, per-class sim gain, which may be negative (validation -1 to 1). The Roster raider gain keeps 0 to 1, shows as a percent and is not coloured.
- Exactly 2% is green and bold.
- Classes are the 9 classic classes.
- Value codes stay unchanged (item status, treatment).
- Strict validation protects Classe, Spé and Rôle in Roster, and Classe and Spé in TierItems:
  - Classe: a dropdown of the 9 French class names.
  - Spé: must be one of the three specs of the row's class. Sheets cannot show a dropdown that depends on another cell, so this is a custom check with help text.
  - Rôle: a dropdown of `Tank`, `Heal`, `Melee DPS`, `Ranged DPS` and `Caster DPS`. Story 4.6 maps them to Interchange v1 as `TANK`, `HEALER`, and `DPS` for the three DPS values.
  - Values already entered are not changed; invalid ones show Sheets' invalid marker until the owner re-selects them.

## Boundaries & Constraints

**Always:**
- Code addresses columns by a stable key, never by label.
- An existing header cell that holds either the label or the key from the first 4.2 version is accepted and rewritten to the label; any other value aborts setup.
- Every write goes through one `applyBatch_` call.
- Rule formulas contain no decimal point, and every argument separator goes through `argSeparator`, so they work in every locale.

**Never:**
- No formulas or score logic (story 4.3).
- No raider views (story 4.5).
- No change to `roster.js` matching.
- Setup does not touch cell values outside row 1.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Fresh workbook | No data tabs | Tabs are created with labels, notes and the full layout | No error expected |
| Existing 4.2 workbook | Technical headers and roster data present | Headers become labels; data is unchanged; layout is applied | No error expected |
| Re-run | Layout already applied | The same layout is applied again; rule and banding counts are unchanged | No error expected |
| Conflict | A header cell matches neither the label nor the key | Nothing is written; the alert names the tab | Whole setup aborted |
| Class colour | Class `Mage` | Raider and class cells show the Mage colour | No error expected |
| Gain | TierItems gain -0.01 / 0.015 / 0.02 / 0.05 | Red / plain / green and bold / green and bold | No error expected |
| Spec check | Classe `Mage`, Spé `Givre` / `Ombre` | Accepted / rejected | Sheets rejects the entry |
| Role | `Heal` / `HEALER` | Accepted / rejected | Sheets rejects the entry |

</frozen-after-approval>

## Code Map

- `src/schema.js` -- `TABS[].headers` (string keys). Becomes `columns: [{key, label, note}]`; `columnOf_(tab, key)` keeps returning the 0-based index by key, so `roster.js` is unchanged.
- `src/setup.js`:
  - `readExistingHeadersByName_` (trims trailing blanks), `validateHeaderCompatibility_`, `buildSetupPlan_(existing, argSeparator)`, `formulaArgSeparator_()`: keep the locale helper.
  - The duplicate and reroll rules use `,` and are passed through `argSeparator`; keep them.
  - Rules are currently added only at creation. This change replaces that with delete-then-add, using `Sheets.Spreadsheets.get(id, {fields: 'sheets(properties.sheetId,conditionalFormats,bandedRanges.bandedRangeId)'})` read inside the lock.
- `src/roster.js` -- uses `columnOf_(tab, 'raiderKey')` and similar keys. Do not change it.
- `tests/harness.js` -- the fake `batchUpdate` is atomic and records meta per sheet. It needs:
  - the requests `repeatCell`, `updateDimensionProperties`, `deleteConditionalFormatRule`, `addBanding` and `deleteBanding`;
  - `tabColorStyle` in `updateSheetProperties`;
  - `note` in `updateCells`;
  - `Sheets.Spreadsheets.get` returning `conditionalFormats` and `bandedRanges` from meta.
- `tests/story-4-2.html` -- asserts technical header strings; update it to labels.
- Live workbook `preloot-forever` (fr_FR) already has the ten tabs with technical headers and rules from 4.2.

## Tasks & Acceptance

**Execution:**
- [ ] `src/schema.js` -- columns become `{key, label, note}`; add a `group` per tab (`input` or `log`) -- readable contract.
- [ ] `src/setup.js`:
  - Layout builders: header `repeatCell` (bold white on dark slate, centred, wrapped), notes, widths, tab colour by group, percent format `0.0%` on gain columns, light banding from row 2, class-colour and gain rules, and a class dropdown.
  - Each run deletes the existing rules and banding on the contract tabs, then adds them again.
  - The alert says "Workbook layout applied".
  - Purpose: one idempotent layout.
- [ ] `src/menu.js` -- rename the item to "Set up / refresh workbook" (same handler).
- [ ] `tests/harness.js`, `tests/story-4-1.html`, `tests/story-4-2.html` -- harness support listed in the Code Map; cover every matrix row, including label migration with data rows kept, and stable counts on re-run.
- [ ] hitl -- owner: `clasp push`, run the menu item, then check the Roster and TierItems look.

**Acceptance Criteria:**
- Given the live workbook, when the owner runs setup, then the I/O matrix rows hold and the copied roster data is unchanged.
- Given both test pages in headless Edge, then both show `PASS`.

## Implementation Notes

- Parent fixes after the implementer, before review: it had stripped every French accent (labels, class and spec names, so the dropdown would reject `Prêtre`/`Démoniste`), deleted the story 4.2 roster lookup tests, and removed the code comments the owner had asked for. All restored. Accent and spec-regex tests added. Bench moved to group `input`: the owner enters bench by hand (CAP-2).

## Plan Change Log

## Review Triage Log

- Pass 1 (quick): high 0, medium 3, low 5, false 3, maybe-false 0. The reviewer read a stale diff that PowerShell had re-encoded; findings were checked against the regenerated `git diff --output`. Patched by the parent. Pages PASS: story-4-1 with 37 assertions, story-4-2 with 89.
  - false -- accents dropped: already fixed before review; the current diff has `Prêtre`, `Démoniste` and accented labels.
  - false -- roster lookup tests deleted: already restored.
  - false -- comments removed: already restored.
  - medium, patch -- `setup.js`: class-colour rules inserted after the duplicate-name rule took priority over it, hiding the red duplicate highlight. Colours are now added first; a test asserts the duplicate rule has top priority.
  - medium, patch -- `tests/story-4-2.html`: matrix rows were checked only by formula string. Added the Mage colour and range, red, green and bold gain formats, no commas in any fr_FR formula, the conflict header lists, and validation-count stability.
  - medium, patch -- `tests/harness.js` `setDataValidation` appended instead of replacing, hiding duplicates on re-run. It now replaces by range.
  - low, patch -- `setup.js`: the Roster colour range was hard-coded `0..2`; it is now derived from the `raiderKey` and `class` keys.
  - low, patch -- `setup.js`: percent format `type: 'NUMBER'` is now `'PERCENT'`.
  - low, patch -- `setup.js`: the spec help text now lists every class with its specs.
  - low, rejected -- harness `repeatCell` keeps only the last call, so header style and percent format are not separately assertable. Test-only; the live check covers them.

## Design Notes

Rule formulas without commas: class `=$B2="Mage"` (Roster A:B; TierItems class column), gain on the TierItems gain column `=H2<0` (red text) and `=H2>=1/50` (green and bold). `1/50` avoids a locale-dependent decimal.

Class colours are the WoW defaults, used as the background with dark text (white text for Chaman):

| Classe | Hex |
| --- | --- |
| Guerrier | C69B6D |
| Paladin | F48CBA |
| Chasseur | AAD372 |
| Voleur | FFF468 |
| Prêtre | FFFFFF |
| Chaman | 0070DD |
| Mage | 3FC7EB |
| Démoniste | 8788EE |
| Druide | FF7C0A |

Labels (key → label). The implementer writes one short French note per column saying what to enter and who fills it (owner or script):
- Config: tierId → Palier actif (ID); bisWindowId → Fenêtre BiS active (ID)
- Roster: raiderKey → Raider (nom exact en jeu); class → Classe; spec → Spé; role → Rôle; tankPriority → Priorité tank; dpsParse → Parse WCL moyen (1-100); gainFraction → Gain simulé du raider (%)
- Rerolls: rerollName → Reroll (nom exact); mainKey → Personnage principal
- Raids: raidId → Raid (ID); tierId → Palier; bisWindowId → Fenêtre BiS; instance → Instance; raidDate → Date du raid; status → Statut
- RaidReports: reportCode → Rapport WCL; raidId → Raid (ID); importedAt → Importé le
- Attendance: raidId → Raid (ID); raiderKey → Raider présent
- Bench: raidId → Raid (ID); raiderKey → Raider sur le banc
- Awards: checksum → Checksum Gargul; raidId → Raid (ID); tierId → Palier; bisWindowId → Fenêtre BiS; raiderKey → Gagnant; itemID → Objet (ID); rollType → Type de roll; os → Off-spec; date → Date; time → Heure; treatment → Traitement
- TierItems: tierId → Palier; itemID → Objet (ID); itemName → Objet; slot → Emplacement; class → Classe; spec → Spé; status → Statut; simGainFraction → Gain simulé (%)
- PatternItems: itemID → Objet (ID); itemName → Objet

Setup owns the formatting of the contract tabs: rules the owner adds by hand on those tabs are removed on the next run.

Spec check: a `CUSTOM_FORMULA` validation on the Spé column, with Classe in the column before it (Roster B/C as shown; TierItems E/F). It has one argument separator, which goes through `argSeparator`:
`=REGEXMATCH($B2&":"&C2,"^(Guerrier:(Armes|Fureur|Protection)|Paladin:(Sacré|Protection|Vindicte)|Chasseur:(Maîtrise des bêtes|Précision|Survie)|Voleur:(Assassinat|Combat|Finesse)|Prêtre:(Discipline|Sacré|Ombre)|Chaman:(Élémentaire|Amélioration|Restauration)|Mage:(Arcanes|Feu|Givre)|Démoniste:(Affliction|Démonologie|Destruction)|Druide:(Équilibre|Combat farouche|Restauration))$")`
Generate it from one `CLASS_SPECS` table in `schema.js`; the class dropdown, colour rules and help text read from the same table.

## Verification

**Commands:**
- Headless Edge on `tests/story-4-1.html` and `tests/story-4-2.html` (see the 4.2 plan) -- expected: `PASS`.

**Manual checks (if no CLI):**
- In `preloot-forever`: readable headers with notes on hover, class colours, gain colours, banding, the roster data intact.
