---
type: epic
title: "Officers get a sim-backed priority for each contested item"
parent: initiative-preloot
covers: [CAP-5, CAP-6, CAP-7, CAP-8, CAP-9]
after: []
assignee: ""
risk: high
---

# Officers get a sim-backed priority for each contested item

## Description

PreLoot builds each Spec's Baseline Set from its Previous Phase BiS List, then plans and runs every paired-slot combination through the bundled `wowsimcli.exe`. It fetches Previous Phase Warcraft Logs parses and ranks the competing Specs for each Contested Item by Upgrade Value and Tie-Break. It adds the Priority tab and `priority.csv` to the `render` stage owned by epic-contested-items. It covers the Priority-tab part of CAP-8 and the sim-resume part of CAP-9.

## Outcome

The officer board has an objective, sim-backed priority order for every Contested Item before the phase launches. This completes the spec's success signal.

## Requirements

Completed at this epic's inception.

## Done when

1. For P4, the Priority tab ranks the competing Specs of every Contested Item by Upgrade Value, shows Raw Gain, and groups rows by Role. `priority.csv` has the same rows in the same order.
2. Every paired-slot combination's result is in the run output, and the best combination sets the rank.
3. Ties within the error margin are ordered by Raw Gain, then by the Warcraft Logs P3 parse, and the rule used is shown. A tie is shown as unresolved when Warcraft Logs is unavailable.
4. Killing the run mid-simulation and restarting it finishes with no sim run twice, and `priority.csv` is identical to an uninterrupted run.
5. Healer rows are labelled "alpha sim", or healer ranking is dropped by a recorded `Decision:` after a healer test run.
6. A full P4 run from the portable zip on the personal PC produces the published `report.html` and `priority.csv`.

## Boundaries

The stages `build_baselines`, `plan_sims`, `simulate`, `fetch_parses` and `rank`, plus the Priority tab and CSV in `render`. It adds the wowsims spec and talent build to the Spec table. Not per-raider ranking; see the spec's Non-goals.

## References

- spec — _bmad-output/initiative-preloot/spec-preloot/spec-preloot.md, CAP-5 to CAP-9, Constraints, Open Questions
- spec — _bmad-output/initiative-preloot/spec-preloot/acceptance-criteria.md, sections CAP-5 to CAP-9
- architecture — _bmad-output/initiative-preloot/architecture-preloot/architecture-preloot.md, AD-4 to AD-9, AD-13, Deferred
- research — _bmad-output/initiative-preloot/research-preloot-data-sources-feasibility/digests/sim-wowsims-r1-2.md, for the wowsimcli and proto shapes

## Notes

- Waits on epic-platform-baseline because: it needs `wowsimcli.exe` v0.0.145 bundled in the build.
- Waits on epic-contested-items because: it needs `resolved_bis.json`, `contested.json`, and the `render` stage with its template.
- Decision: this epic owns loading Warcraft Logs credentials from `<workspace>/secrets/` or environment variables (AD-12), as its first user (2026-09-30).
- Open question: where each Spec's talent build and rotation options come from, wowsims presets or a hand-kept table.
- Open question: which Warcraft Logs percentile counts as "top", and what the API terms and credentials require. A person registers the API client (hitl).
- Unknown: whether wowsimcli healer HPS is valid. A test run on one Healer Spec comes first.
- Unknown: the error-margin formula that defines a tie. Owned by `rank`.
