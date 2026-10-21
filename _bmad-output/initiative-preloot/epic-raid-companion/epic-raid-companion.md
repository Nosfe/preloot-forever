---
type: epic
title: "Owner sees live priority in Gargul on WoW Forever"
parent: initiative-preloot
covers: [CAP-6, CAP-7]
after: []
assignee: ""
risk: high
---

# Owner sees live priority in Gargul on WoW Forever

## Description

Gargul_Preloot's `Core.lua` becomes the owner-only companion addon for WoW Forever, per brownfield.md. It imports the workbook snapshot, shows each roller's BiS Ratio and Impact Score in Gargul's roll table, records the owner's BIS, IMPACT, or NONE choice per award, and fills the raid and treatment into Gargul's Custom export. This epic delivers the addon side of CAP-7: the snapshot import and the ledger export.

## Outcome

The owner awards loot in Gargul with live per-roller priorities and exports the raid's ledger for the workbook; the raid-night part of the spec's success signal.

## Done when

1. The new addon build, with `## Interface-Camelot: 16001`, loads with Gargul v8.0.1 in the owner's WoW Forever client and replaces 1.1.0; the release is tagged in the repo.
2. It imports a snapshot exported from epic-sheets-workbook's workbook, rejects an invalid one, and its recomputed scores match epic-sheets-workbook's shared fixtures.
3. Its columns sit after Gargul's ten native roll-table columns, and awarding still records the roll type.
4. The owner picks BIS, IMPACT, or NONE per award, and every roller's values update before the next roll.
5. With the Gargul export settings applied, the Custom export fills `raidId` and `treatment` by checksum; one real raid runs the tracer end to end, and that raid's export is saved as epic-sheets-workbook's parser fixture.
6. The brownfield cleanup on the addon side is done: `GargulPrelootDB` persistence, the random ratio, case-insensitive and `-Thunderstrike` matching, and the test-data and hash helpers removed; `_importButtonAdded` and the `Base64.decode` call fixed; the samples (`json_export_example.json`, `sample_import`, `sample_json`), root README, and `Gargul.code-workspace` updated or removed. The French chat line is kept.

## Boundaries

The addon only; no workbook or Apps Script code. Uses the calculation contract, Interchange v1, and the fixtures as epic-sheets-workbook defines them, without redefining them. Owns the Gargul export settings and the repo's release tag. See the spec's Non-goals.

## References

- parent — _bmad-output/initiative-preloot/initiative-preloot.md, sections Done when, Boundaries
- spec — _bmad-output/initiative-preloot/spec-raid-loot-distribution/spec-raid-loot-distribution.md, CAP-6, CAP-7
- constraint — _bmad-output/initiative-preloot/spec-raid-loot-distribution/allocation-rules.md
- architecture — _bmad-output/initiative-preloot/architecture-raid-loot-distribution/architecture-raid-loot-distribution.md, AD-2, AD-3, AD-4, AD-5, AD-6, AD-8, Interchange v1, Gargul export template
- brownfield — _bmad-output/initiative-preloot/spec-raid-loot-distribution/brownfield.md, addon rows
- code — C:/Repos/Gargul_Preloot/Core.lua, C:/Repos/Gargul_Preloot/Gargul_Preloot.toc

## Notes

- Decision: the opening stories are the platform baseline: the Forever TOC and loading the addon with Gargul v8.0.1 (2026-10-21).
- Waits on epic-sheets-workbook because: it needs the shared score fixtures (4.3), the snapshot export and sample (4.6), and the Custom-export parser and sample (4.7), all in tools/google_apps_script/fixtures/; its recorded real export feeds 4.9.
- Decision: the French chat line on an award shows the recipient's new BiS Ratio when the award is BIS and the new Impact Score when it is IMPACT (2026-10-21).
- Assumption: a NONE award adds no ratio or score to the chat line.
