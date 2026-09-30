# Research brief

- **Topic:** Preloot data sources feasibility
- **Type:** technical (breadth-first)
- **Decision:** Can a loot-priority app for TBC Classic/Anniversary (WoW Forever later) be built on wowtbc.gg BiS lists, the wowsims engine, and Wowhead loot tables — and how should each be integrated?
- **Priority inputs the app must support:** BiS list position, simmed upgrade value per player, class/role weighting rules.
- **Knobs:** preset standard (3 assistants, 8 sources/round, depth 2), validation normal. Source: skill defaults.
- **Search surfaces:** web page fetch, GitHub repo/code search. No generic web search.

## Dimensions
1. BiS data — wowtbc.gg structure, item IDs, extractability, ToS/robots, TBC vs WoW Forever.
2. Sim engine — wowsims/tbc maintenance, headless options, batch upgrade/stat weights, gear import, tank/healer coverage, WoW Forever.
3. Loot tables — Wowhead access and ToS; alternatives (wowtbc.gg loot tables, wowsims item DB, AtlasLoot); raid tier per Anniversary phase.
4. Player gear input & prior art — WowSimsExporter/armory; ThatsMyBis, RCLootCouncil, Gargul, softres.
