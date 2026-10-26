---
title: 'Snapshot validation and recompute'
type: 'feature'
ticket: '4'
created: '2026-10-26'
status: 'built'
baseline_revision: '9ecd7ec'
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

**Problem:** The addon accepts a snapshot after only minimal checks (5.1). A hand-edited or corrupted snapshot can therefore replace session state with wrong or inconsistent values. AD-6 requires validating the whole Interchange v2 payload and recomputing both scores before any replace.

**Approach:**
- Extend `Snapshot.parse` to validate every Interchange v2 field.
- Recompute BiS Ratio and Impact base from their operands with the workbook formulas, and reject any supplied value outside `1e-9 * max(1, |recomputed|)`.
- Any failure returns a French error naming the raider or item, and the previous session state stays unchanged.
- Displayed values stay the recomputed ones, rounded only at display.

## Boundaries & Constraints

**Always:**
- Same rules and messages in spirit as the workbook exporter (`snapshot.js` `buildSnapshotRaiders_`, `buildSnapshotItems_`, `withinSnapshotTolerance_`).
- Tolerance used only for this import check, never for display or ranking.
- One error message lists the first problem and how many others there are.

**Never:**
- The Impact column or Impact Score (5.5).
- Tier or raid checks against the workbook: the addon has no workbook reference, and raid changes are 5.2's session reset.
- Changes to the workbook.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Valid sample | snapshot-sample.json | accepted; recomputed BiS Ratio and Impact base equal supplied within tolerance | No error expected |
| scores.json cases | each case mapped to a raider | `Scores.bisRatio`/`Scores.impactBase` match `expected` within tolerance; tank Impact base nil | No error expected |
| Envelope | schemaVersion ≠ 2; tierId/raidId empty or not strings; raiders or items missing or not arrays | refused | French error |
| Raider fields | role not DPS/HEALER/TANK; classSpec empty; counts not integers or negative; max < 1; presence > max; dpsParse outside 1–100 or not a number; NaN/inf anywhere | refused, naming the raider | French error |
| Duplicates | two raiders with the same raiderKey; two items with the same itemID; one item with the same classSpec twice | refused | French error |
| Score mismatch | bisRatio or non-tank impactBase off by more than tolerance, or missing | refused | French error |
| Tolerance edge | supplied value off by 0.5e-9 × max(1, recomputed) | accepted | No error expected |
| Tank Impact | TANK with numeric impactBase | refused (must be null) | French error |
| Items | statut not BIS/IMPACT/CLASS_BOUND/NORMAL; gainFraction not a finite number or null; itemID not a positive integer | refused | French error |
| Previous state | any refusal after a good import | session snapshot and awards unchanged | French chat line |

</frozen-after-approval>

## Code Map

- `C:/Repos/Gargul_Preloot/Snapshot.lua` -- `parse(text, GL)` does decode plus minimal envelope and raider-key checks (5.1). Extend it with full validation and keep the decode part. `set` builds the raider and item indexes (5.2).
- `C:/Repos/Gargul_Preloot/Scores.lua` -- `bisRatio(raider)`. Add `impactBase(raider)`. Same formulas as `tools/google_apps_script/src/scores.js`; after validation max ≥ 1 and parse is 1–100, so no fallbacks are needed.
- `C:/Repos/Gargul_Preloot/Import.lua` -- `apply` already refuses with `say(... err ...)` and keeps state. No change expected.
- `C:/Repos/Gargul_Preloot/tools/google_apps_script/src/snapshot.js` (L79-L300, L459) -- the exporter's rules to mirror, read only.
- `C:/Repos/Gargul_Preloot/tools/google_apps_script/fixtures/scores.json` -- 10 cases. Inputs are `tierPresence, tierMax, parse (null → 1), bisLoots, impactLoots, role (emoji label; 🛡️ Tank → TANK)`, and expected values follow.
- `C:/Repos/Gargul_Preloot/tests/addon/run.lua` -- existing runner. Earlier tests build small raider payloads; the large-payload raider is already consistent (3/4, parse 50 → 0.75 and 37.5). Bad-payload cases expect refusal.
- Gargul JSON decodes `null` to nil, so a tank's `impactBase` is nil, the same as absent.

## Tasks & Acceptance

**Execution:**
- [ ] `Scores.lua` -- add `impactBase(raider)`: nil for TANK, else (p/max) × parse / (impactLoots + 1).
- [ ] `Snapshot.lua` -- `validate(data)` returns nil or a French error (the first problem plus "(+N autres)"):
  - envelope, raiders, then items, per the matrix;
  - finite check: `x == x and x ~= math.huge and x ~= -math.huge`;
  - tolerance helper as in snapshot.js;
  - `parse` calls it after decoding.
- [ ] `tests/addon/run.lua`:
  - `scores.json` cases;
  - one broken copy of the sample per matrix row (mutating the decoded table, then re-encoding with `GL.JSON:encode`), each refused with the previous snapshot kept;
  - the tolerance edge accepted.

**Acceptance Criteria:**
- Given the repo, when `luajit tests/addon/run.lua` runs, then it prints PASS and exits 0.
- Given a valid live snapshot, when the owner imports it in game, then it is accepted and Ratio BiS still matches the workbook.

## Implementation Notes

- Implemented directly. `Snapshot.validate(data)` collects every problem and returns the first, plus "(+N autres)".
- `parse` keeps the decode steps and calls `validate`. The 5.1 envelope and raider-key checks moved into it.
- Broken copies are made by plain-text `gsub` on the fixture, which avoids re-encoding precision issues.
- JSON has no NaN; an infinite value is tested with `1e999`.
- 224 assertions pass.

## Plan Change Log

## Review Triage Log

Pass 1 (quick): high 0, medium 0, low 6, false 0, maybe-false 0.

| Finding | Verdict | Route | Evidence / action |
|---|---|---|---|
| Envelope problems (version, tierId/raidId) returned early, without "(+N autres)" | low | patch | Confirmed. They are now collected with the raider and item errors; only non-array raiders/items stop early. Test added ("tierId ou raidId manquant (+2 autres)"). |
| `isArray` passes a trailing JSON null (Gargul sets `VALUE[i] = nil`) and `{}` for arrays | low | reject | Confirmed for a hand-edited payload only: the workbook exporter never writes null entries or `{}` for lists. The dropped trailing entry has no score effect for other raiders. A fix needs a custom decoder hook. |
| "Previous state" row only checks the snapshot, not the awards | low | patch | Each refusal now also checks that a recorded award and its treatment survive. |
| Matrix rows without a broken copy (tierId, parse < 1, infinite bisRatio/gain, missing bisRatio, non-integer itemID) | low | patch | Six cases added; 271 assertions pass. |
| Broken copies use text `gsub` instead of decode/encode | low | reject | A deliberate deviation, recorded in Implementation Notes: re-encoding loses the precision the tolerance tests need. `once()` asserts that each pattern is found. |
| "(+1 autres)" is not correct French | low | patch | Now "(+1 autre)" / "(+N autres)". |

## Verification

**Commands:**
- `luajit tests/addon/run.lua` (from C:/Repos/Gargul_Preloot) -- expected: `PASS: <n> assertions`, exit 0.
