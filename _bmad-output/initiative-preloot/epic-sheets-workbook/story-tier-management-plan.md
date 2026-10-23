---
title: 'Tier management (Nouveau palier)'
type: 'feature'
ticket: '8'
created: '2026-10-23'
status: 'built'
baseline_revision: 'a52b8a4e12222d46e00e52ef17c7d26d5dd3f541' # in C:/Repos/Gargul_Preloot (code repo)
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

**Problem:** The menu action "Archive tier and activate next" is a placeholder. The owner starts a new tier by typing *Palier actif (ID)* and *Début du palier* in Config by hand. Nothing checks for a raid in progress, nothing protects Config, and the old tier's rows look the same as the current tier's.

**Approach:** Replace the placeholder with **Setup > Nouveau palier**, the BiS reset. Both scores then fully reset: the formulas already count presence and BiS/Impact loots only from *Début du palier*.

1. **Dialog:** asks for the new *Palier (ID)* and *Début du palier* (date, default today).
2. **Confirmation:** before anything is written, a confirmation recaps the entered values: new ID and start date, the outgoing tier ID, the archive tab name, and that the live Objets tabs will be emptied.
3. **Refusals:** refused while a raid is in progress (Config *Raid en cours* set).
4. **One atomic batch then:**
   - writes *Palier actif (ID)* and *Début du palier*;
   - stamps the outgoing tier ID in Raids' new **Palier (ID)** column on every raid row where it is blank;
   - archives all Objets tabs into **one** read-only tab "Objets (<outgoing tier ID>)", then empties the live Objets tabs (data rows from row 4 cleared; headers, dropdowns and formats kept) so the new tier starts fresh.

**Decisions (owner, 2026-10-23):**
- **Old tier data stays in place**, greyed out: raid rows in Raids and Présence, and Awards entries dated before *Début du palier*, show grey text. The new Raids **Palier (ID)** column (Raid > Start stamps the active tier on each new raid) makes filtering by tier easy.
- **Objets archive (owner, final answer):** one tab, long layout. Columns: *Rôle* (the Objets tab's role), *Objet (ID)*, *Objet*, *Emplacement*, *Spé* (e.g. "Mage Givre"), *Statut*, *Gain (%)*.
  - One row per item and spec that has a Statut or a Gain.
  - Items with no spec filled get one row with blank Spé/Statut/Gain, so no item is lost.
  - The live Objets tabs are emptied.
- **Config is protected against manual input** with a warning-only protection on Palier actif (ID), Début du palier and Raid en cours, applied by setup. Sheets cannot hard-lock the owner, so this is a warning. *Serveur WCL* stays freely editable. The first tier is also set through Nouveau palier: with no current tier there is nothing to stamp and no copy to make.
- **Menu label:** "Nouveau palier".

## Boundaries & Constraints

**Always:**
- One `applyBatch_`; `requireCurrentLayout_` on Config and Raids.
- The grey rules are conditional formats rebuilt by setup and read Config B2 live, so they follow any start date.
- Raids columns are only appended (schema convention).
- The archive tab is created with `addSheet` plus `updateCells`, and gets a warning-only protection.

**Never:**
- A reset inside a tier.
- Impact carryover.
- Moving or deleting old-tier rows.
- Changing score formulas.
- Touching Roster owner columns.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy path | Tier t1 active since D1, no raid in progress; owner enters t2, D2 > D1 and confirms | Config A2=t2, B2=D2; blank Raids Palier cells → t1; one tab "Objets (t1)" in long layout with warning protection; live Objets data rows empty, headers and dropdowns kept | No error expected |
| First tier | Config A2 empty | Config set; nothing stamped; no archive; live Objets untouched | No error expected |
| Raid in progress | Config Raid en cours set | Refused before the dialog | Nothing written |
| Same ID | New ID = current tier ID | Refused with a message | Nothing written |
| Start not after current | D2 ≤ D1 | Refused | Nothing written |
| Archive name taken | "Objets (t1)" already exists | Refused | Nothing written |
| Archive content | Item with Statut on 2 specs, item with no spec filled | 2 rows for the first; 1 row with blank Spé/Statut/Gain for the second | No error expected |
| Empty ID or invalid date | — | Refused in the dialog | Nothing written |
| Cancel | Owner cancels at the dialog or the confirmation | Nothing written | No error |
| Greying | Raid/Présence row or Awards entry dated before Début du palier (blank Award date uses its raid's date) | Grey text; current-tier rows unchanged | No error expected |
| Raid start | Raid > Start | New Raids row stamped with the active Palier (ID) | No error expected |
| Config protection | Setup refresh | One warning-only protection on Config A:C (not Serveur WCL); refreshes do not duplicate it | No error expected |

</frozen-after-approval>

## Code Map

- `src/schema.js`:
  - Raids columns: append `{ key: 'tierId', label: 'Palier (ID)' }`.
  - Add `CONFIG_PROTECTION_DESCRIPTION`, `TIER_COPY_PROTECTION_DESCRIPTION` and a grey style constant.
  - Config L227-231: `tierId` (A), `bisWindowStart` (B), `openRaidId` (C), `wclRealm` (D).
- `src/tier.js` -- replace the placeholder:
  - `archiveTierAndActivateNext` becomes `openNewTierDialog` (the menu entry).
  - The HTML dialog has its date default and a client-side `confirm()` recap; the dialog pattern is in `raids.js` `deleteRaid`.
  - `submitNewTier(tierId, startIso)` validates and returns the summary.
  - `buildNewTierRequests_` builds the Config writes, the Raids stamps, the archive tab (`addSheet` plus rows read from each `ITEM_TABS` tab at `OBJETS_FIRST_SPEC_COLUMN` pairs, spec label from `SPEC_COLUMNS` like `buildSnapshotItems_`), the archive protection, and the clearing of the live Objets data rows (row 4+, `userEnteredValue` only).
  - Date serial: reuse the logic of `attendance.js` `existingPresenceDateSerial_` or `dateSerialFromReportStart_`.
- `src/menu.js` L19 -- label "Nouveau palier", handler renamed.
- `src/snapshot.js`:
  - `exportRaidSnapshot`'s Raids append stamps `tierId` from Config.
  - Reuse `requireCurrentLayout_`, `snapshotSheet_` and the protection request pattern. The raid-start protections use the `RAID_OPEN_PROTECTION_PREFIX` description; Config's own protection must use a different description, so cancel/end do not remove it.
- `src/setup.js`:
  - Config protection, idempotent by description; existing ranges come from the `Sheets.Spreadsheets.get` metadata already read.
  - Grey CF rules for Raids rows.
- `src/grids.js`:
  - Grey CF on Présence raid rows (`buildPresenceGridRequests_`, beside the 1/B/0 rules).
  - Grey CF on Awards blocks, added after the rarity rules so it wins.
  - Awards date rule: `$date<>""` → date; blank → `VLOOKUP` of Raid (ID) in Présence, like `buildTierLootFormula_`.
- Tests:
  - New `tests/story-4-8.html` (harness pattern from story-4-6) for every matrix row.
  - `tests/harness.js`: add range-limited `updateCells` clearing if missing.
  - Update the 4-1 menu labels, the 4-2 Raids headers and CF counts, and the 4-6 Raids row and protection counts.

## Tasks & Acceptance

**Execution:**
- [ ] `src/schema.js`, `src/setup.js`, `src/grids.js` -- Raids Palier (ID) column, Config protection, grey rules -- greying and protection.
- [ ] `src/tier.js`, `src/menu.js`, `src/snapshot.js` -- Nouveau palier dialog, confirmation, batch; raid start stamps the tier -- the action.
- [ ] `tests/harness.js`, `tests/story-4-8.html`, existing pages -- matrix coverage.

**Acceptance Criteria:**
- Given an active tier with raids, when the owner confirms Nouveau palier, then the Roster scores restart from the new date, the old rows look grey, one read-only "Objets (old tier)" tab holds every item and spec, and the live Objets tabs are empty.
- Given the confirmation recap, when the owner cancels, then nothing changes.

## Implementation Notes

- Implemented directly.
- **Raids column key:** the new Raids column uses key `raidTier`, label "Palier (ID)". The key `tierId` would trip `isLegacyRaidsSheet_`, which treats a Raids header containing `tierId` as the old layout and recreates the tab; the 4-2 tab-order test caught this.
- **Raid start and cancel:**
  - Raid > Start appends `[raidId, …, raidTier]`.
  - Cancel's "ID-only row" check now also ignores the tier column.
  - End raid writes Raids cell by cell, so the stamp is kept.
- **Grey rules:**
  - They use `N(INDIRECT("Config!B2"))`, since rules cannot reference another tab.
  - They are added last at index 0, so they win over the tints.
  - Awards: a blank Date falls back to the raid's Présence date, and an unknown raid counts as current (not grey).
- **Config protection:** setup's metadata read now includes `protectedRanges`, and the protection is replaced by its description. Raid protections keep their own prefix, so Cancel/End never remove it.
- **Archive tab:** its sheet id is derived from its name (deterministic, for same-batch requests). Live Objets are emptied with a range-limited `updateCells` on values only, which keeps dropdowns and formats. The harness gained that clear mode.
- **Tests:**
  - New `story-4-8.html` covers every matrix row.
  - 4-1: menu label; stub check removed.
  - 4-2: grey rules asserted separately.
  - 4-3: Awards rule count 3×5.
  - 4-6: protection counts filtered to raid protections.

## Plan Change Log

## Review Triage Log

**Pass 1 (quick): 5 patched, 1 partly rejected.**

- [medium, patch] **The Awards grey rule disagreed with the loot formulas when an award had no usable date.** Examples: a blank Présence date, or a date typed as text, was greyed but still counted. The rule now greys only `N(date or raid date) > 0` and `< Début du palier`, matching `buildTierLootFormula_`, where no usable date counts as current.
- [low, patch] **Awards entries with no Traitement were never greyed.** The `Traitement<>""` guard is dropped; the date condition alone decides, and empty rows have no date.
- [medium, patch] **Objets rows with a blank ID and name but a Statut or Gain were neither archived nor kept**, because the live rows were cleared. Any non-empty row is now archived. A 4-8 test covers it.
- [low, patch] **The archive sheet id could clash with a renamed tab's id.** The derived id now skips ids in use (`getSheets`). The harness gained `getSheets()`.
- [medium, patch] **With a backdated start, raids dated on or after the new start were stamped with the outgoing tier**, while the scores count them for the new tier. Blank stamps now follow the raid date: from the new start the new tier, otherwise the outgoing one. A 4-8 test covers it.
- [low, partly rejected] **Tests do not cover greying output, the Config read on raid start, Cancel, or the Config protection surviving raid actions.**
  - Patched:
    - 4-6 asserts that Raid > Start stamps the Config tier.
    - 4-6 asserts the Config protection survives Start and Cancel.
  - Rejected:
    - The greying result: the harness cannot evaluate conditional formats; the formulas are asserted, and the live check covers it.
    - Cancel: the dialog's recap and confirm are asserted, and a refused confirm never calls the server.

**After patches:** 4-1 PASS 25, 4-2 PASS 237, 4-3 PASS 109, 4-4 PASS 81, 4-6 PASS 100, 4-7 PASS 47, 4-8 PASS 39.

## Verification

**Commands:**
- Headless Edge, a fresh `--user-data-dir` per page, for `story-4-1`, `story-4-2`, `story-4-3`, `story-4-4`, `story-4-6`, `story-4-7`, `story-4-8` -- expected: `PASS` on each.

**Manual checks:**
- On a workbook copy:
  - Run Nouveau palier and confirm.
  - Scores restart.
  - Old rows are grey.
  - The archive tab exists in long layout with a warning on edit, and the live Objets tabs are empty.
  - Editing Config A2 shows a warning.
  - It is refused during a raid.
