# Glossary

Every downstream artifact uses these terms exactly, with no synonyms.

- **Phase** — a TBC Anniversary content release. The canonical IDs are `pre`, `p1`–`p5`. The **Target Phase** is the one being analyzed; the **Previous Phase** is the one immediately before it.
- **Spec** — a talent specialization as wowtbc.gg publishes it, with a PreLoot ID (e.g. `fury_warrior`, `arms_warrior`, `shadow_priest`). Each Spec maps to one wowsims spec plus its own talent build: `fury_warrior` and `arms_warrior` both sim as wowsims `dps_warrior`. Each Spec has exactly one **Role**: DPS, Healer or Tank.
- **BiS List** — the ranked best-in-slot items for one Spec in one Phase, taken from wowtbc.gg.
- **Baseline Set** — the full gear set built from a Spec's Previous Phase BiS List, and the reference point for every sim of that Spec. It is keyed by an owner: in v1 the owner is the Spec, and later it may be a raider.
- **Contested Item** — an item on the Target Phase BiS List of two or more Specs of the same Role, excluding Tanks. It is identified by `(item_id, role)`. An item on both a DPS BiS List and a Healer BiS List becomes two Contested Items, flagged as cross-Role.
- **Upgrade Value** — the percentage increase in DPS (DPS Role) or HPS (Healer Role) when a Contested Item replaces an item in a Baseline Set: (sim with item − Baseline Set sim) / Baseline Set sim. It is the primary ranking key.
- **Raw Gain** — the same increase, as an absolute DPS or HPS number. It is the first tie-breaker.
- **Tie-Break** — the ordered rules for ranking Specs whose Upgrade Values fall within the sim error margin of each other: Raw Gain first, then the Spec's Warcraft Logs top-percentile parse from the Previous Phase.
- **Priority Table** — the output: each Contested Item with its competing Specs ranked by Upgrade Value, then Tie-Break.
- **Issue** — a data problem found during a run (an unresolved item, a skipped Spec, a missing parse, a failed sim). It is recorded and shown in the report and never stops the run.

## Phase name mapping

| Canonical | Anniversary | wowtbc.gg flag | wowsims phase |
| --- | --- | --- | --- |
| `pre` | pre-raid | `pre-bis` | — |
| `p1` | P1 | `t4` | 1 |
| `p2` | P2 | `t5` | 2 |
| `p3` | P3 | `t6` | 3 |
| `p4` | P4 | `za` | 4 |
| `p5` | P5 | `swp` | 5 |
