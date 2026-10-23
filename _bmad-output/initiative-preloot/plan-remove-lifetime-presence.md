---
title: 'Remove lifetime presence; Impact uses tier presence'
type: 'refactor'
ticket: ''
created: '2026-10-23'
status: 'built'
baseline_revision: '9dcda4ec874ba6aa6bde1e6c4d8672c86b4a7f15' # in C:/Repos/Gargul_Preloot (code repo)
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

**Problem:** Impact (sans gain objet) uses lifetime presence across all tiers, while BiS ratio uses tier presence. The owner wants both scores to reset at each new tier, with the same presence factor.

**Approach:**
- Remove the Roster columns "Présence totale" and "Nombre de raids totaux".
- Compute Impact from "Présence palier" / "Nombre de raids du palier", the same factor as BiS ratio.
- Setup / refresh deletes the two columns from a live Roster in one pass.
- The pre-raid snapshot stops exporting the lifetime fields.

**Decisions (owner, 2026-10-23; nobody has used the sheet yet):**
- Full reset: "Loots Impact" counts only IMPACT awards dated on or after *Début du palier*, with exactly the BiS date rule (a blank award Date falls back to its raid's Présence date). At a new tier, both scores restart on every factor.
- The snapshot keeps `schemaVersion` 2 and simply drops `lifetimePresence`/`lifetimePresenceMax`. No addon reads it yet.

## Boundaries & Constraints

**Always:**
- Roster columns are read by key.
- Column deletes run in `buildLegacyTabMigrationRequests_`, which comes before the grid requests.
- Impact stays null for tanks.
- Parse fallback stays: an empty, 0 or text parse counts as 1.
- All writes go through `applyBatch_`.

**Never:**
- Changes to Rerolls (a later story removes it).
- Tier activation or archive behaviour (story 4.8).
- Changes to the BiS ratio formula.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Live Roster migration | Roster with Présence totale and Nombre de raids totaux (current or former labels) | Both columns deleted; later columns shift left with values intact; Impact formula reads Présence palier / Nombre de raids du palier | No error expected |
| Already migrated | Roster without them | Second refresh deletes nothing | No error expected |
| Fresh workbook | No Roster | Roster created without the two columns | No error expected |
| Impact value | Tier presence 2/4, parse 80, 1 Impact loot, non-tank | Impact base = 0.5 × 80 / 2 = 20 | No error expected |
| Impact loot before the tier | IMPACT award dated before Début du palier | Not counted in Loots Impact | No error expected |
| Impact loot, blank Date | IMPACT award with blank Date, its raid dated in the tier | Counted (falls back to the Présence date) | No error expected |
| Snapshot | Valid Roster | Raiders carry no lifetimePresence fields; impactBase checked against tier presence | Mismatch reported as today |
| Outdated layout action | Roster not refreshed, owner runs Start or Update WCL parses | Refused with "Set up / refresh workbook" | Nothing written |

</frozen-after-approval>

## Code Map

- `tools/google_apps_script/src/schema.js` L249-250 -- remove `lifetimePresence` and `lifetimePresenceMax` from Roster `columns`.
- `tools/google_apps_script/src/setup.js`:
  - `buildRosterFormulaRequests_` (L94-180): drop the two formula cells. The Impact formula (L146) uses the tier presence letters.
  - Delete `buildLifetimePresenceFormula_` and `buildLifetimePresenceMaxFormula_` (L254-262).
  - Rename `buildBisLootFormula_` (L270) to a tier loot formula taking the treatment (`BIS` or `IMPACT`). It replaces `buildImpactLootFormula_` (L281), so both counts share the date filter.
  - `legacyRosterColumns_` and `isLegacyRosterHeaders_` (L352, L394): add the removed columns (`lifetimePresence`/`Présence totale`/`Présence vie`, `lifetimePresenceMax`/`Nombre de raids totaux`/`Max vie`). `effectiveHeadersByName_` then removes them, and the Groupe de raid insert still runs after.
- `tools/google_apps_script/src/scores.js` L12-29 -- `impactBase_` parameters renamed to tier presence. The math is unchanged.
- `tools/google_apps_script/src/snapshot.js` L121-193 -- stop reading the lifetime columns. Recompute Impact with the tier values. Drop `lifetimePresence`/`lifetimePresenceMax` from each raider.
- Unchanged: `attendance.js`, `ledger.js`, `parses.js`, `roster.js`, `grids.js`.
- Tests and fixtures:
  - `tests/story-4-3.html`: score fixture loop (L71), formula asserts (L110-145, L173-174), former-labels test (L212-226).
  - `tests/story-4-6.html`: L130-131 and L328.
  - `fixtures/scores.json`: drop the lifetime inputs; recompute `impactBase`/`impactScore` from the tier inputs.
  - `fixtures/snapshot-sample.json`: drop the lifetime fields.
- Docs (preloot-agent):
  - `architecture-raid-loot-distribution.md` L51, L53 (Presence and Impact rules), L111 (Interchange raiders fields), L191 (CAP-5).
  - `epic-sheets-workbook/epic-sheets-workbook.md` L25.

## Tasks & Acceptance

**Execution:**
- [ ] `src/schema.js`, `src/setup.js` -- remove the columns, the formulas and the builders; add the migration deletes -- contract and one-pass migration.
- [ ] `src/scores.js`, `src/snapshot.js` -- Impact uses tier presence; the snapshot drops the lifetime fields -- same factor everywhere.
- [ ] `tests/story-4-3.html`, `tests/story-4-6.html`, `fixtures/*.json` -- update, and add tests for: migration (current and former labels), no second delete, the impact value row, snapshot fields -- I/O matrix.
- [ ] Architecture and epic docs -- rules and Interchange fields updated -- keep the contract truthful.

**Acceptance Criteria:**
- Given a refreshed Roster, when a raider has tier presence 2 of 4, parse 80 and 1 Impact loot, then "Impact (sans gain objet)" shows 20.
- Given the refreshed workbook, when Raid > Start runs, then the snapshot validates and exports no lifetime fields.

## Implementation Notes

- Implemented directly, as for the Roster group column.
- `buildTierLootFormula_(..., treatment)` replaces `buildBisLootFormula_` and `buildImpactLootFormula_`. A test asserts that the Impact formula equals the BiS formula with the treatment swapped.
- The migration reuses `legacyRosterColumns_`, which `isLegacyRosterHeaders_` now derives from.
- Fixtures:
  - `scores.json`: only `empty-parse` changed; tier 3/4 became 4/5, so its Impact stays 0.4 and its BiS ratio becomes 0.8. The other cases had equal tier and lifetime ratios.
  - `snapshot-sample.json`: Alya's Impact is now 0.5×1/3 = 0.16666666666666666, Beryl's 0.75×88/2 = 33.
- Docs: architecture AD-1, AD-2, Interchange and CAP-5, plus epic outcomes 3 and 5. The 4.8 Impact carryover choice is dropped.

## Plan Change Log

## Review Triage Log

**Pass 1 (quick): 3 patched, 1 deferred, 1 rejected.**

- [medium, patch] **The calculation contract and spec still used lifetime presence.** Updated `allocation-rules.md` (L9-10, L17, L21, L25), `spec-raid-loot-distribution.md` (L26, L32, L44, L51) and `raid-workflow.md` L9.
- [medium, defer] **Tickets 4.8 and 4.6 in `tickets.toml` still mention Lifetime Presence and the Impact carryover choice.** Ticket files change only through the ticket workflow (bmad-ticket refine). Recorded in deferred-work.md.
- [low, patch] **The epic's decision line (L51) still described lifetime presence.** Marked as superseded on 2026-10-23.
- [low, rejected] **AC 1 is checked only through the JS helper and formula references.** The harness can't evaluate Sheets formulas. The parity between helper and formula, plus the formula's cell references, is the observable part; the live check in Verification covers the value.
- [low, patch] **The outdated-layout row was only partly covered.** Added a 4-4 test: Update WCL parses refuses a Roster with lifetime columns, with no write and no WCL call. Added a 4-6 assert that Config, Raids and Roster are unchanged on the refused export.

**After patches:** 4-1 PASS 28, 4-2 PASS 255, 4-3 PASS 109, 4-4 PASS 80, 4-6 PASS 91, 4-7 PASS 47.

## Verification

**Commands:**
- Headless Edge, a fresh `--user-data-dir` per page, for `story-4-1`, `story-4-2`, `story-4-3`, `story-4-4`, `story-4-6`, `story-4-7` -- expected: `PASS` on each.

**Manual checks:**
- Live workbook, Setup > Refresh workbook:
  - The two columns are gone.
  - Impact matches tier presence × parse / (Impact loots + 1).
  - Raid > Start exports.
