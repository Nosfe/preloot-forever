---
type: epic
title: "Owner runs loot priority from the new workbook"
parent: initiative-preloot
covers: [CAP-1, CAP-2, CAP-3, CAP-4, CAP-5, CAP-7, CAP-8]
after: []
assignee: ""
risk: medium
---

# Owner runs loot priority from the new workbook

## Description

A new Google Sheets workbook, with a bound Apps Script evolved from Gargul_Preloot's `tools/google_apps_script`, holds the roster, tier inputs, attendance, and awards. Native formulas compute Presence, BiS Ratio, and Impact Score. Owner menu actions fetch Warcraft Logs attendance, export the pre-raid snapshot, and import the post-raid award ledger. This epic delivers the Sheets side of CAP-7: the snapshot export and the ledger import.

## Outcome

The owner and raiders read current loot priorities from the new workbook, and one raid's awards update it in one import; the Sheets part of the spec's success signal.

## Done when

1. The workbook is deployed with its bound script, the Advanced Sheets service, and Warcraft Logs credentials in the owner's User Properties; the roster and Rerolls are copied from the old workbook, and raiders have view-only access.
2. The owner can set the active tier's BiS, Impact, parse, gain, and item-status inputs and enter bench appearances; a Warcraft Logs import credits attendance (more than 25% of boss fights, Rerolls alts to their main) and repeating the same report changes nothing.
3. The Roster, Impact Items, and per-spec tabs show BiS Ratio and Impact Score with their breakdowns.
4. The pre-raid snapshot exported from the workbook loads in epic-raid-companion's addon; importing a Gargul Custom export, first a hand-written sample and then epic-raid-companion's real export, updates loot counts in one atomic write, and a malformed export changes nothing.
5. The owner triggers the BiS reset, archives a tier, and chooses Impact Item Count carryover; a new tier cannot be activated while a raid is open, and archives are read-only.
6. The brownfield cleanup on the Apps Script side is done: RCLootCouncil import, loot coefficients, date cutoffs, Drive output, and Pattern/Design name-prefix detection removed; `test_runner.html`, the script README, and the local Warcraft Logs tools (`generate_raid_json.ps1`, `run_local.cmd`, `.env.example`, `raid_ids.csv`, `presence_test_runner.html`) repaired or removed.

## Boundaries

The workbook and its bound Apps Script only; no addon code. Owns any change to the calculation contract and Interchange v1, and the shared fixtures: near-tie and exact-tie score fixtures, a sample snapshot, and a hand-written Custom export. See the spec's Non-goals.

## References

- parent — _bmad-output/initiative-preloot/initiative-preloot.md, sections Done when, Boundaries
- spec — _bmad-output/initiative-preloot/spec-raid-loot-distribution/spec-raid-loot-distribution.md, CAP-1, CAP-2, CAP-3, CAP-4, CAP-5, CAP-7, CAP-8
- constraint — _bmad-output/initiative-preloot/spec-raid-loot-distribution/allocation-rules.md
- constraint — _bmad-output/initiative-preloot/spec-raid-loot-distribution/raid-workflow.md
- architecture — _bmad-output/initiative-preloot/architecture-raid-loot-distribution/architecture-raid-loot-distribution.md, AD-1, AD-2, AD-3, AD-6, AD-7, Interchange v1, Gargul export template
- brownfield — _bmad-output/initiative-preloot/spec-raid-loot-distribution/brownfield.md, Apps Script rows
- code — C:/Repos/Gargul_Preloot/tools/google_apps_script

## Notes

- Decision: the opening stories are the platform baseline: the new workbook, the bound script with the Advanced Sheets service, credentials, and copying the roster and Rerolls (a person does the copy) (2026-10-21).
- Decision: story 1 is the tracer bullet; stories 4 and 8 follow the raid lifecycle (6) and the ledger import (7) because they need raid state; story 5 can run beside 6-8 (2026-10-21).
- Decision: code reaches the bound script with CLASP; tests are browser HTML pages with fake sheets, one page per story; built with bmad-build one story at a time (2026-10-21).
- Decision: loot counts are calculated by formula from the Awards rows, not stored (2026-10-21).
- Decision: shared fixtures live in tools/google_apps_script/fixtures/: scores.json (story 3), snapshot-sample.json (story 6), custom-export-sample.txt (story 7) (2026-10-21).
- Check (high risk): story 2 — the owner compares the copied roster with the old workbook; stories 7 and 8 — the owner runs them on a workbook copy and reviews the counts before the live workbook.
