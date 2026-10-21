---
title: 'Workbook polish: merged Raids, Config, Rerolls like Roster, WoW-flavoured Rôle/Spé, Objets Statut first'
type: 'feature'
ticket: ''
created: '2026-10-21'
status: 'built'
baseline_revision: 'f9390ffd4882effce4e44a16cdb1b6954b5422e4' # C:/Repos/Gargul_Preloot (code repo)
route: 'full'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-preloot/plan-4-2-grids-rework.md'
  - '{project-root}/_bmad-output/initiative-preloot/plan-4-2-split-items-reorder-tabs.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The owner wants:
- a simpler tab set and order;
- one Raids tab instead of Raids plus RaidReports;
- Rerolls with the same columns as Roster;
- a WoW feel on Roster's Rôle and Spé;
- Statut before Gain in the Objets tabs, with fewer statut values.

Diagnostics and PatternItems add no value for the owner.

**Approach:** "Set up / refresh workbook" migrates the live workbook in the same single batch and applies the new layout.

**Decisions:**
- **Tab order:** Roster, Rerolls, Présence, Raids, Awards, the five Objets tabs, Config, then the hidden `_Listes`. Other tabs end up after these.
- **Raids** is merged with RaidReports:
  - Columns: Raid (ID), Instance, Date du raid, Rapports WCL, Importé le.
  - Rapports WCL holds that raid's report codes separated by spaces. A code already listed is a no-op on re-import (story 4.4).
  - RaidReports is deleted.
  - Fenêtre BiS, Palier and Statut are removed:
    - the tier is the active one (archiving moves raids out, story 4.8);
    - the BiS window is the raids dated on or after Config's BiS reset date;
    - the open raid is Config's Raid ouvert.
- **Config** columns: Palier actif (ID), Fenêtre BiS active (ID), Début fenêtre BiS (date), Raid ouvert (ID). Its values sit in row 2.
- **Removed:** PatternItems (the owner picks NONE for patterns in Gargul), and Diagnostics: the tab, the Diagnostics submenu and its handlers.
- **Objets tabs:**
  - Each spec pair is Statut, then Gain (%).
  - Statut values are `BIS`, `IMPACT`, `CLASS_BOUND` and `NORMAL`.
  - Gain colours are unchanged.
- **Rôle** (Roster and Rerolls) is a dropdown, each value with its own colour:
  - `🛡️ Tank`, steel blue;
  - `✚ Heal`, green;
  - `⚔️ Melee DPS`, red;
  - `🏹 Ranged DPS`, brown;
  - `🔮 Caster DPS`, purple.
- **Spé** (Roster and Rerolls) values carry an emoji, e.g. `❄️ Givre`, `🔥 Feu`, `🌑 Ombre` (full table in Design Notes). The Spé cell takes the class colour, like the Raider and Classe cells.
- Existing Rôle and Spé cells holding the plain value (`Heal`, `Givre`) are rewritten to the emoji value. No other data cell is changed.
- **Roster** columns: Raider (nom exact en jeu), Classe, Spé, Rôle, Parse WCL moyen.
  - Priorité tank is removed everywhere: tank priority is no longer a product rule.
  - Gain simulé du raider is removed: the Impact Score gain will come from the item's gain for the roller's spec in the Objets tabs, a rule change for story 4.3 and the architecture.
  - Both columns are deleted, with their contents, at the owner's request.
  - The BiS Ratio and Impact Score columns come with story 4.3.
- **Rerolls** columns: Reroll (nom exact), Classe, Spé, Rôle, Parse WCL moyen, Personnage principal.
  - It has the same dropdowns, dependent Spé, validation and colours as Roster.
  - The duplicate and main-not-in-Roster highlights stay.
  - Existing rows are kept by inserting the four new columns before Personnage principal.

## Boundaries & Constraints

**Always:**
- One `applyBatch_` per run.
- Formulas: no decimal point, separators through `argSeparator`, column letters from `columnOf_`/`columnLetter_`.
- Grids are never shrunk.
- Keep French accents, existing comments and tests. Each new function gets a one-line comment.

**Never:**
- Never delete owner data. Setup aborts, with an alert naming the tab, when:
  - old Raids (with Palier or Statut columns) or RaidReports has data rows;
  - PatternItems has data rows;
  - an Objets tab has item rows while its row 3 still shows `Gain (%)` before `Statut`.
- Diagnostics is deleted whatever its content (test rows only).
- No score, WCL, snapshot or ledger code.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Migrate live workbook | Old Raids, RaidReports, PatternItems, Diagnostics empty; Rerolls (Reroll, Personnage principal) with 1 row; Roster role `Heal`, spec `Givre`, tank priority `MT1`, gain `0.03`, parse `80` | Old tabs gone; Raids recreated with the new columns; Rerolls row kept with its main in column F; Roster row reads `Ana`, `Mage`, `❄️ Givre`, `✚ Heal`, `80`; tab order as decided | No error expected |
| Data in old tab | RaidReports has a row | Nothing written; the alert names RaidReports | Whole setup aborted |
| Objets swap | Objets Tank exists, old order, no items | Row 3 reads `Statut`, `Gain (%)` per pair; the Statut dropdown is on the first column of each pair; gain rules and percent format are on the second | No error expected |
| Objets with items, old order | Objets Heal row 4 has data | Nothing written; the alert names Objets Heal | Whole setup aborted |
| Rerolls dropdowns | Rerolls row with Classe `Prêtre` | Spé offers `📿 Discipline`, `✨ Sacré`, `🌑 Ombre` | No error expected |
| Menu | Workbook opens | No Diagnostics submenu | No error expected |
| Re-run | Everything migrated | Nothing duplicated or moved; data unchanged | No error expected |

</frozen-after-approval>

## Code Map

- `src/schema.js`:
  - `TABS` keeps Config, Roster, Rerolls and Raids; remove RaidReports and PatternItems.
  - Config gains `bisWindowStart` and `openRaidId`.
  - Raids becomes `raidId, instance, raidDate, reportCodes, importedAt`.
  - Rerolls becomes `rerollName, class, spec, role, dpsParse, mainKey`.
  - Roster becomes `raiderKey, class, spec, role, dpsParse`. On a live Roster still holding `tankPriority` (E) or `gainFraction` (G), delete G first, then E, with `deleteDimension`, and plan Roster from the post-migration headers.
  - `ROLE_OPTIONS` stays plain: it names the Objets tabs and `SPEC_COLUMNS` roles. Add `ROLE_DISPLAY` (plain → emoji value, plus colour).
  - Add a `specIcons` map to each `CLASS_SPECS` entry.
  - `TAB_ORDER` is updated.
- `src/setup.js`:
  - `buildSetupPlan_` currently runs the grid requests first, then the flat tabs from `existingHeadersByName`. A flat tab deleted or reshaped by the migration must be planned from its post-migration state: treat deleted ids as missing, and give migrated Rerolls the new headers.
  - Update the Rerolls highlight formulas: the mainKey column is now H, taken from `columnOf_`.
  - Extend the class colours to the Spé column. Add the Rôle colour rules on Roster and Rerolls.
  - Add the Rerolls Spé dropdown in `_Listes` J:L.
  - Add the Roster and Rerolls role and spec value rewrite: `updateCells` per changed cell only.
  - `buildTabOrderRequests_` stays.
- `src/grids.js`:
  - The migration deletes and aborts go in `assertGridMigrationIsSafe_` and `buildGridMigrationDeleteRequests_`.
  - `_Listes` grows to columns A-L. Spec values carry the emoji; J holds the Rerolls lookup.
  - The Objets builders use `gainColumn = 2 + index*2`; swap to statut at `+0` and gain at `+1`.
  - Clear validation on row 4+ of each Objets tab before setting it again.
  - Statut columns get a TEXT number format.
- `src/menu.js` -- remove the Diagnostics submenu, `runDiagnostics*` and the `DIAGNOSTICS_*` constants.
- `tests/story-4-1.html` -- replace the Diagnostics tests with direct `applyBatch_` tests: a write, an atomic forced failure, a busy lock, and the lock released.
- `tests/story-4-2.html` -- cover every matrix row.
- `roster.js` -- unchanged. It reads `rerollName` and `mainKey` by key.

## Tasks & Acceptance

**Execution:**
- [ ] `src/schema.js`, `src/setup.js`, `src/grids.js`, `src/menu.js` -- as in the Code Map.
- [ ] `tests/story-4-1.html`, `tests/story-4-2.html`, `tests/harness.js` -- cover the matrix rows. Add `insertDimension` support to the harness if missing.
- [ ] `_bmad-output/initiative-preloot/deferred-work.md` (preloot-agent) -- add an entry to update the architecture spine, spec and PRD before story 4.3. Five decisions need recording there:
  - Raids fields, and the BiS window by reset date;
  - the open raid in Config;
  - PatternItems removed (AD-6's pattern/design list);
  - tank priority removed (AD-2, Interchange `tankPriority`);
  - the Impact Score gain is the item's simulated gain for the roller's spec from the Objets tabs, not a raider-level gain. This reverses AD-2's "no item gain lookup" and changes Interchange v1 and the addon.
- [ ] hitl -- owner: push, run setup, check the tab order, Raids, Rerolls, the Roster flavour and the Objets order.

**Acceptance Criteria:**
- Given the live workbook, when setup runs, then the matrix rows hold.
- Given both test pages in headless Edge, then both show `PASS`.

## Implementation Notes

- The implementer returned no report: story-4-2 was failing, about 90 earlier assertions had been deleted, and a scratch `tmp_vm_runner.js` was left behind (removed). The parent took over.
- Parent fixes before review:
  - `_Listes` A:D now hold the emoji spec values, so they match the rewritten Roster and Rerolls cells.
  - Raids gets new sheetId 1014, so no id is reused in the batch that deletes the old Raids.
  - The legacy-order item check sliced from row 4 and skipped row 4 itself.
  - The Objets Statut validation now clears both columns of each pair before it is set again.
  - The empty `buildValueFormatRequests_` was removed.
  - The roster lookup tests were moved to the new Rerolls layout, and the deleted tests were restored.

## Plan Change Log

## Review Triage Log

- Pass 1 (quick): high 1, medium 5, low 4, false 0, maybe-false 0. Patched by the parent. Pages PASS: story-4-1 with 27 assertions, story-4-2 with 171.
  - high, patch -- `setup.js` `effectiveHeadersByName_`: legacy Roster and Rerolls headers were replaced with the contract labels, skipping the conflict check, so an unknown owner column was silently overwritten. Rerolls rows were also read in the pre-insert layout.
    - Fix: the migration is now applied to the read headers and rows (deleted columns removed, the four blank Rerolls columns inserted). Legacy Rerolls must be exactly 2 columns. The deletes run highest index first.
    - Tests added for an unknown Roster column and for an extra Rerolls column.
  - medium, patch -- tests deleted by the implementer were restored: deletions, aborts, refresh, Objets structure, the 28 specs, frozen panes, merges, and `_Listes` created before the dropdown.
  - medium, patch -- the abort tests now check that data is kept and that no `_Listes` or Objets tab is created. The old Raids abort was added.
  - medium, patch -- the Rerolls Prêtre specs and the `_Listes` J lookup are now asserted.
  - medium, patch -- harness: a validation clear now removes overlapping rules, like the API. A swap test seeds the old Statut rule on column D and asserts it is removed and that the gain rules moved.
  - medium, patch -- a re-run after the legacy migration is asserted to move no data.
  - low, patch -- `_Listes` `columnCount` never shrinks.
  - low, patch -- deleted test comments restored; `seedLegacyLiveWorkbook` commented.
  - low, rejected -- the percent and TEXT formats are not asserted, because the harness keeps only the last `repeatCell`. They are covered by the live check.
  - low, rejected -- tab order after migration is not asserted on the migrated workbook. It is asserted on a fresh one with the same code path.

## Design Notes

Spec emoji (value = emoji, space, spec):

| Classe | Specs |
| --- | --- |
| Guerrier | ⚔️ Armes, 💢 Fureur, 🛡️ Protection |
| Paladin | ✨ Sacré, 🛡️ Protection, ⚖️ Vindicte |
| Chasseur | 🐾 Maîtrise des bêtes, 🎯 Précision, 🌲 Survie |
| Voleur | 🗡️ Assassinat, ⚔️ Combat, 🌫️ Finesse |
| Prêtre | 📿 Discipline, ✨ Sacré, 🌑 Ombre |
| Chaman | ⚡ Élémentaire, 🌪️ Amélioration, 💧 Restauration |
| Mage | 🔮 Arcanes, 🔥 Feu, ❄️ Givre |
| Démoniste | ☠️ Affliction, 😈 Démonologie, 💥 Destruction |
| Druide | 🌙 Équilibre, 🐻 Combat farouche, 🌿 Restauration |

Rerolls dropdown in `_Listes`: J{r} holds `=IFERROR(XLOOKUP(Rerolls!{classLetter}{r},$A$2:$A$10,$B$2:$D$10),"")`, which spills into J:L. Rows 2-201.

Rôle colours: Tank `C9D6E3`, Heal `C8E6C9`, Melee DPS `F4C7C3`, Ranged DPS `E0CDB5`, Caster DPS `D9C8F0`.

Rôle rule: one `CUSTOM_FORMULA` per role on the Rôle column, `=$D2="🛡️ Tank"`, with the letter from `columnOf_`. Spé class colour: extend each class rule's range to cover the Spé column too.

## Verification

**Commands:**
- Headless Edge on `tests/story-4-1.html` and `tests/story-4-2.html` -- expected: `PASS`.
