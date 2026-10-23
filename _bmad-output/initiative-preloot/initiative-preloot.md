---
type: initiative
title: "Loot priority from Sheets and Gargul on WoW Forever"
parent: none
covers: [CAP-1, CAP-2, CAP-3, CAP-4, CAP-5, CAP-6, CAP-7, CAP-8]
after: []
assignee: ""
risk: high
---

# Loot priority from Sheets and Gargul on WoW Forever

## Description

The guild owner keeps one roster's loot priorities in a Google Sheets workbook and awards raid loot in Gargul with each roller's BiS Ratio and Impact Score in view, while the award decision stays manual. Raiders read the published priorities. The spec owns the capabilities, constraints, and non-goals; this initiative delivers them for WoW Forever by evolving the owner's existing Gargul_Preloot addon and Apps Script.

## Outcome

The owner runs a WoW Forever raid from the new workbook and companion addon instead of the current single attendance/loot ratio; the signal is the spec's success signal.

## Done when

1. The owner pastes a WoW Forever Warcraft Logs link into the new workbook, and that raid's attendance is credited: more than 25% of its boss fights, for each exact Roster character.
2. Raiders with view access see the Roster, Impact Items, and per-spec tabs with BiS Ratio and Impact Score breakdowns, and cannot edit them.
3. Before a raid the owner loads the workbook snapshot into the companion on WoW Forever; during rolls each roller's BiS Ratio and Impact Score show and update before the next roll after each award.
4. After the raid, one Gargul Custom export pasted into the workbook updates loot counts for exactly the awarded raiders according to each award's BIS, IMPACT, or NONE choice; a malformed export changes nothing.
5. The owner triggers the BiS reset and archives a tier; archives are read-only.

## Boundaries

Split by side: the workbook and its bound Apps Script first, then the Gargul companion addon. Both live in the owner's repo `zambelaba/Gargul_Preloot`. See the spec's Non-goals. Out of scope: CLASP, a desktop GUI, entering first-tier class/spec/item/BiS/sim data (the owner does it), and running the old version alongside the new one. Tracer path: workbook snapshot, companion display, award with treatment, Gargul Custom export, workbook import updating counts.

- Touch point: Warcraft Logs API v2 — public report attendance read; owner: epic-sheets-workbook
- Touch point: Gargul v8.0.1 — roll table, award, importer and exporter hooks, and the export settings; owner: epic-raid-companion
- Touch point: WoWSims Forever — the owner types each Raider's simulated gain into the workbook by hand, with no code; owner: epic-sheets-workbook
- Touch point: the old workbook — read once to copy the roster; owner: epic-sheets-workbook

## References

- spec — _bmad-output/initiative-preloot/spec-raid-loot-distribution/spec-raid-loot-distribution.md, sections Capabilities, Constraints, Non-goals
- architecture — _bmad-output/initiative-preloot/architecture-raid-loot-distribution/architecture-raid-loot-distribution.md, sections Invariants & Rules (AD-1 to AD-8), Interchange v1, Gargul export template
- brownfield — _bmad-output/initiative-preloot/spec-raid-loot-distribution/brownfield.md
- code — C:/Repos/Gargul_Preloot (github.com/zambelaba/Gargul_Preloot, tag 1.1.0)

## Notes

- Dropped: the PreLoot initiative content and its epics 1-3 (platform baseline, contested items, sim priority) and the item in deferred-work.md; the product was redefined as Sheets plus Gargul loot distribution (user's decision, 2026-10-21).
- Decision: two epics, the workbook first, then the addon (2026-10-21).
- Decision: start a new workbook and copy the roster from the old one (2026-10-21).
- Decision: every character is its own raider in Roster; no alt tab or alt-to-main mapping (2026-10-23).
- Decision: switch over at once; the old addon and workbook are not kept running in parallel (2026-10-21).
- Decision: no separate platform-baseline epic; each epic opens with its own setup stories (the workbook, script and credentials; the Forever TOC and loading on Gargul v8.0.1) (2026-10-21).
- Decision: shared contracts live in the spine: Interchange v1 and the Gargul export template (governed by AD-6), the raid ID lifecycle (AD-6), identity (AD-3), the calculation contract (AD-2). epic-sheets-workbook owns any change to them and the shared fixtures (2026-10-21).
- Decision: stop at the epic level; no epic is incepted yet (2026-10-21).