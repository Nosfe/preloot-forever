---
title: 'Impact par objet: top 5 tab and precomputed Impact scores'
type: 'feature'
created: '2026-11-02'
status: 'built'
baseline_revision: 'dda81b1'
route: 'full'
route_source: 'auto'
---

## Intent

**Problem:** Roster shows "Impact (sans gain objet)", a number that means little on its own: the real Impact depends on the item's gain for each spec. The owner wants to see, before the raid, who gets each IMPACT item, and wants Gargul to receive those real scores.

**Approach:**
- Remove the Roster column `Impact (sans gain objet)`.
- Add a tab **Impact par objet**: one row per item that has an IMPACT Statut for at least one spec, with the top 5 Roster raiders by full Impact score.
- The snapshot carries the full Impact score per item and raider (computed by the script, same formula). The addon shows that value instead of computing it.

Formula unchanged: Impact = (Présence palier / Nombre de raids du palier) × parse (empty or text = 1) / (Loots Impact + 1) × gain of the item for the raider's spec, only when that spec's Statut is IMPACT; tanks have none.

Owner decisions (2026-11-02):
- Scores are sent precomputed. Consequence accepted: during a raid the Impact shown in Gargul stays as exported (an IMPACT loot no longer lowers the winner's Impact until the next snapshot). Ratio BiS still updates live.
- One row per item; top 5 over the whole Roster (both raid groups).

## Design

**Workbook**
- Roster loses its last column (`impactBase`). Ratio BiS and every other column unchanged.
- `_Listes` gets a hidden helper table: one row per (item, Classe|Spé) with an IMPACT Statut and its gain, built by one formula that stacks a FILTER per spec column of the five Objets tabs (the script generates it from `SPEC_COLUMNS`).
- **Impact par objet** (after Awards, read-only, warning protection like the other calculated parts):
  - A: Objet (ID), sorted unique list of the helper table's items (spill).
  - B: Objet, name looked up in the Objets tabs.
  - C to G: 1er to 5e, "Nom (score)", score with 3 decimals like Gargul. Fewer than 5 eligible raiders leaves the rest empty.
  - One spill formula per column (MAP over the item list): for every Roster raider, Impact base × helper gain for that item and raider's Classe|Spé; SORTN 5 descending; ties by Roster order.
- Snapshot (`Raid > Démarrer`) becomes **schemaVersion 3**:
  - raiders: as v2 without `impactBase`.
  - items[]: `itemID`, `specs[]` (classSpec, statut, gainFraction, kept for the treatment prefill), new `impactScores[]` = `{ raiderKey, score }` for every non-tank raider whose spec has IMPACT on the item (not only the top 5: any roller needs a score). Computed in Apps Script with `scores.js`, so the tab and Gargul show the same numbers.
- The Roster check in the export no longer reads an Impact cell; it still checks Ratio BiS.

**Addon**
- Accepts schemaVersion 3 only (v2 refused with a message asking for a new Raid > Démarrer).
- Validation: each `impactScores` entry names a snapshot raider, is a number, and matches the formula within the existing tolerance.
- Impact column and chat line read the precomputed score for (item, roller). No more Impact live recompute; Ratio BiS live recompute unchanged.

**Fixtures and tests:** `scores.json` keeps the formula cases; `snapshot-sample.json` and the addon payload generator move to v3; workbook pages and `luajit tests/addon/run.lua` updated; Anniversary kit regenerated.

## Owner answers (2026-11-02)

1. The owner deletes Roster column Q `Impact (sans gain objet)` by hand before refreshing; no migration code.
2. Tab name: **Classement par objet** (used below wherever the design says Impact par objet).

## Tasks

- [x] Workbook: schema (Roster column, new tab, _Listes helper), formulas, snapshot v3, export check; story-4-x pages.
- [x] Addon: Snapshot v3 parse/validate, Scores/Columns/Chat on precomputed scores, Awards live recompute limited to BiS; Lua tests.
- [x] Fixtures, payload generator, READMEs and LISEZMOI (the Anniversary kit TSVs are unchanged).
- [x] Review, commit, clasp push; push on request.

## Implementation Notes

- No warning protection on the new tab (formula-only; a typed value just blocks a spill until removed).
- Gain table in `_Listes` T:W (key, gain, Objet (ID), Objet), tank Objets tab skipped; `_Listes` sized to 5000 rows.
- Rank formulas: `MAP` over A2:A501, each body `ARRAYFORMULA(LET(...))`; 3 decimals with `FIXED`.
- IMPACT chat line now reads `Alya : score Impact 0.083 pour [item]` (score at award time, no longer a "new" score).
- Addon refuses snapshots that miss a score for an eligible raider, or carry one for a tank / non-IMPACT spec / unknown raider.
- Tests: workbook pages PASS (story-4-3 117, 4-6 105, others unchanged); addon 395 assertions.

## Review Triage Log

Quick review (1 adversarial reviewer), 2026-11-02:
- **Dismissed (high):** old Roster column Q blocks Rafraîchir. Owner decision: delete it by hand first.
- **Fixed:** array mode inside LAMBDA (inner `ARRAYFORMULA`), `IFERROR` on the Impact base, `_Listes` row count (5000) and read range, tank specs skipped in the gain table, addon check for a missing score, README wording.
- **Deferred (medium):** each rank column re-sorts the raiders (5× per item); revisit if the sheet feels slow.
- **Dismissed (low):** tie order and the parse-range note (display only; export already refuses out-of-range parses).

## Verification

- All workbook pages PASS; `luajit tests/addon/run.lua` PASS.
- Tests check the generated tab formulas and helper ranges (the test harness does not evaluate formulas) and the snapshot v3 scores against `scores.json`.
- Owner: Rafraîchir, check the tab, Raid > Démarrer, import in Gargul; the Impact column shows the tab's values.
