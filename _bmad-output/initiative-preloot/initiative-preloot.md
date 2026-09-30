---
type: initiative
title: "Sim-backed loot priority before each raid phase"
parent: none
covers: [CAP-1, CAP-2, CAP-3, CAP-4, CAP-5, CAP-6, CAP-7, CAP-8, CAP-9, CAP-10]
after: []
assignee: ""
risk: medium
---

# Sim-backed loot priority before each raid phase

## Description

Before a TBC Anniversary raid phase launches, the loot officer runs PreLoot once. The officer board gets one report that ranks, by simulation, which Spec gains most from each item several Specs want. The spec owns the capabilities, constraints and non-goals. This initiative delivers them as a proof of concept for one guild, starting with P4.

## Outcome

The officer board decides P4 loot priority from the Priority Table instead of hours of manual investigation. The signal is the spec's success signal.

## Done when

1. Before P4 launches, the officer produces the P4 Priority Table in one run of the portable build on the personal Windows 11 PC, and reviews it in under an hour.
2. The officer board uses the published `report.html` and `priority.csv` from the shared folder as the basis for P4 loot priority.
3. Every capability CAP-1 to CAP-10 works in that build, with no step done by hand beyond copying the two files to the shared folder.
4. The report shows every Issue and match rate from the run, and nothing from the BiS Lists is missing without being listed.

## Boundaries

Split by the spec's capabilities, with one extra split: the contested list is usable before the sims exist. It is not a loot-distribution tool, not per-raider ranking, and not hosted. See the spec's Non-goals. Tracer path: `preloot run --workspace <dir> --phase p4` from the zip loads the P4 and P3 BiS Lists for two DPS Specs, finds one Contested Item, runs the baseline and candidate sims, and produces one ranked row in `report.html`.

- Touch point: GitHub releases of wowsims tbc-new — `wowsimcli.exe` v0.0.145 downloaded at build time; owner: epic-platform-baseline
- Touch point: wowtbc.gg — BiS List page data read; owner: epic-contested-items
- Touch point: wowsims `db.json` at tag v0.0.145 — item data read; owner: epic-contested-items
- Touch point: `wowsimcli.exe` — invoked per sim; owner: epic-sim-priority
- Touch point: Warcraft Logs API — P3 parses read for the Tie-Break; owner: epic-sim-priority
- Touch point: shared folder — the user copies `report.html` and `priority.csv` there by hand, with no code; owners: epic-contested-items (report), epic-sim-priority (CSV)

## References

- spec — _bmad-output/initiative-preloot/spec-preloot/spec-preloot.md, sections Capabilities, Constraints, Non-goals
- architecture — _bmad-output/initiative-preloot/architecture-preloot/architecture-preloot.md, sections Invariants & Rules (AD-1 to AD-14)
- research — _bmad-output/initiative-preloot/research-preloot-data-sources-feasibility/research-preloot-data-sources-feasibility.md, for data-source background

## Notes

- Decision: three epics — platform baseline, then contested items, then sim priority. The contested list gets its own epic so it can be shared before the sims exist (user's decision, 2026-09-30).
- Decision: every rule more than one epic must follow lives in the architecture spine: artifact models (AD-3), the Spec and Phase tables (AD-4, AD-14), the Issue shape (AD-9), settings and run folders (AD-10), and the publish boundary (AD-13). The code for them is built in epic-platform-baseline (2026-09-30).
- Decision: stop at the epic level. No epic is incepted yet (user's decision, 2026-09-30).
- Open question: wowtbc.gg reuse permission. The user asks only if the POC works, and the answer affects no epic now.
