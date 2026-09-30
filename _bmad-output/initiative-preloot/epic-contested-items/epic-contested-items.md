---
type: epic
title: "Officers see the contested BiS items for a phase"
parent: initiative-preloot
covers: [CAP-2, CAP-3, CAP-4, CAP-8]
after: []
assignee: ""
risk: medium
---

# Officers see the contested BiS items for a phase

## Description

PreLoot loads the Target Phase and Previous Phase BiS Lists for every DPS and Healer Spec from wowtbc.gg. It resolves each item to its wowsims item ID, slot and drop source, detects the Contested Items, and renders them in a self-contained `report.html`. This epic owns the `render` stage and the report template: the BiS Lists and Contested Items tabs, the Issues and match-rate section, provenance, source credits, and escaping. Until epic-sim-priority exists, `render` leaves out the Priority tab. It covers the report-base part of CAP-8; the Priority tab is epic-sim-priority's.

## Outcome

The officer board can share and discuss the contested items for a phase before any sim runs. This is the first half of the spec's success signal.

## Requirements

Completed at this epic's inception.

## Done when

1. For P4, `report.html` shows the P4 and P3 BiS Lists of every DPS and Healer Spec, and no Tank.
2. The Contested Items tab lists each item on the P4 lists of two or more Specs of the same Role, with slot, drop source and a Wowhead link. Cross-Role items are flagged, and single-Spec items are absent.
3. The Issues section shows the match rate per Spec and every unresolved item, including heroic/normal items that couldn't be told apart. Nothing is missing without being listed.
4. The report shows that `db.json` came from the same wowsims tag as the bundled `wowsimcli.exe`, along with the fetch times, and it credits its sources.
5. `report.html` produced by the portable zip opens offline from the shared folder on another PC.

## Boundaries

The stages `ingest_bis`, `resolve_items`, `detect_contested` and `render`. It adds the wowtbc.gg page names to the Spec table. No sims and no ranking.

## References

- spec — _bmad-output/initiative-preloot/spec-preloot/spec-preloot.md, CAP-2, CAP-3, CAP-4, CAP-8
- spec — _bmad-output/initiative-preloot/spec-preloot/acceptance-criteria.md, sections CAP-2, CAP-3, CAP-4, CAP-8
- architecture — _bmad-output/initiative-preloot/architecture-preloot/architecture-preloot.md, AD-2, AD-4, AD-9, AD-11, AD-13, AD-14
- research — _bmad-output/initiative-preloot/research-preloot-data-sources-feasibility/digests/bis-wowtbcgg-r1-1.md, for the wowtbc.gg page-data shape

## Notes

- Waits on epic-platform-baseline because: it needs `preloot.models`, `preloot.io`, the command line writing `settings.json`, and the stage runner.
- Decision: this epic owns the HTTP helper in `preloot.io` (standard-library `urllib` with truststore), as its first user; epic-platform-baseline does not build it (2026-09-30).
- Unknown: how wowtbc.gg's P4 (`za`) page data marks heroic and normal items. When it can't be told, the item becomes an Issue and the run continues.
- Unknown: whether `db.json` has drop sources for every P1–P5 raid item. Only one item was checked in research.
