---
title: 'Impact column'
type: 'feature'
ticket: '5'
created: '2026-10-26'
status: 'built'
baseline_revision: '429ab2d'
route: 'oneshot'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** During a roll the owner sees only Ratio BiS. The full Impact Score is missing for items whose Statut is IMPACT for the roller's spec.

**Approach:**
- Append an "Impact" column right after "Ratio BiS".
- For each roller, the cell shows Impact base × the rolled item's `gainFraction` for the roller's `classSpec` (a null gain counts as 0, as in the workbook's `impactScore_`), formatted `%.3f`.
- The cell is empty when that Statut is not IMPACT, the item or spec has no entry, the roller is unknown, or the roller is a tank.
- The rolled item is `GL.RollOff.CurrentRollOff.itemID`.
- The window widens for both columns.

</frozen-after-approval>

## Implementation Notes

- Oneshot route: about 40 lines in Scores, Snapshot and Columns, plus tests.
- `Snapshot.itemSpec(itemID, classSpec)` returns the spec entry, and `statut` now reads from it. `Scores.impactScore(raider, itemSpec)` mirrors the workbook's `impactScore_`.
- The window widens to 650 for both columns. 299 assertions pass.

## Review Triage Log

- **low, patch.** No test sent `CurrentRollOff.itemID` through the hook. A stubbed RollOff with `CurrentRollOff = { itemID = 888 }` now checks cell 12 after a refresh.
- **low, patch.** A zero score with a negative gain displayed as `-0.000`. The cell now shows `0.000`; test added.

## Verification

**Commands:**
- `luajit tests/addon/run.lua` (from C:/Repos/Gargul_Preloot) -- expected: `PASS: <n> assertions`, exit 0.

**Manual checks (if no CLI):**
- In game (batched): a roll on an item with an IMPACT Statut for some specs shows the Impact score for those rollers only, and nothing for tanks.
