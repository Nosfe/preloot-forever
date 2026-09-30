---
title: 'technical research: Preloot data sources feasibility'
type: 'technical'
topic: 'Preloot data sources feasibility'
decision: 'Can a loot-priority app for TBC Classic/Anniversary (WoW Forever later) be built on wowtbc.gg BiS lists, the wowsims engine, and Wowhead loot tables — and how should each be integrated?'
source: 'run'
status: complete
preset: 'standard'
validation: 'normal'
claims_verified: 3
claims_unverified: 11
created: '2026-09-29'
updated: '2026-09-29'
---

# technical research: Preloot data sources feasibility

**Decision this research serves:** Can a loot-priority app for TBC Classic/Anniversary (WoW Forever later) be built on wowtbc.gg BiS lists, the wowsims engine, and Wowhead loot tables — and how should each be integrated?

## Executive summary

**Verdict: feasible for TBC Anniversary. Swap one of the three sources: use the wowsims item database for loot tables instead of Wowhead.**

1. **Don't use Wowhead as a data source.** Its terms forbid automated access, data mining, derivative works and any commercial or third-party use [21]. The wowsims item database (MIT) carries its own loot data: 8,256 items, 2,352 of them with a drop source (`npcId`, `zoneId`), plus phase numbers and NPC/zone tables [15][14]. On the one item spot-checked it matches Wowhead's drop data [17]. Equivalence across the whole dataset is not yet verified.
2. **wowtbc.gg BiS data is machine-readable.** Each spec page is backed by a Gatsby `page-data.json` holding per-phase BiS flags (`pre-bis/t4/t5/t6/za/swp`), a numeric `value` score, the boss and the drop chance [2]. It carries no reliable item IDs: only 170 of 448 gear entries link to an item ID. The site publishes no reuse licence, so ask permission before redistributing its data [3].
3. **The engine to use is `wowsims/tbc-new`, not `wowsims/tbc`.** The old repo is deprecated [7]. tbc-new is actively maintained (144 releases, a commit on the day of access), MIT-licensed with an attribution request, and ships a local HTTP API with raid sim, stat weights and bulk (gear-candidate) sim endpoints [8][10][11]. Every class has a registered sim, and all four tanks and four healers are registered. Some specs are merged, for example one `hunter` and one `dps_warrior`. The whole sim is labelled **Alpha**, and healer support was only recently ported [12][13].

**Biggest caveat:** simmed "upgrade value" is solid for DPS specs and weak for healers and tanks. The priority model has to blend three inputs: sim value, BiS list position, and class/role weights. For WoW Forever, no wowsims support was found [8]. No Blizzard API was found either: the only evidence is a low-confidence community reply [30]. Addons there are reportedly restricted [24], and its BiS lists are unranked [4]. Support for it has to be designed as a BiS-only mode.

## 1. BiS data: wowtbc.gg

- **Location:** TBC Classic BiS lists live at `/bis-list/{spec}-{class}/`. No separate "Anniversary" section was found. The phase is not in the URL, and phase switching appears to happen in the browser (medium confidence) [1].
- **Data file:** the real data is `/page-data/bis-list/{spec}-{class}/page-data.json`, referenced from the page HTML [1]. The Fury Warrior file is about 659 KB [2]:
  - `bisList`: 373 entries for Fury Warrior. Each has `name`, `slot`, `phase`, per-phase `{bis: bool}` flags for `pre-bis, t4, t5, t6, za, swp`, `value`/`final_value` (a numeric score; sorting by it gives a plausible within-slot ranking, but its meaning isn't published), `source` (instance), `source_type` (boss), `drop_chance`, `alternative` and `classic`.
  - `gearData`: 448 entries with full stats. Only 170 have a `url` of the form `https://tbcdb.com/?item=<id>`, so **names must be mapped to item IDs**. An exact name match against the wowsims database is the obvious route.
- **Rendered HTML:** item names are plain `div`s, with no Wowhead links or `data-*` IDs [1].
- **Reuse terms:** robots.txt and sitemap.xml returned Not Found (medium confidence) [32]. The only legal page found is a privacy policy from 2021, which mentions "Terms and Conditions" that could not be found anywhere on the site [3]. The site invites lists that "sim better" and updates them "after testing", without describing its method [1].
- **WoW Forever:** lists exist at `/warcraftforever/bis-list/`, but they are **unranked**: "Items are not in order". There are no phases, dungeon loot tables are provisional, and there are no raid loot tables [4][5][6].

## 2. Sim engine: wowsims

- **Which repo:** `wowsims/tbc` is "not maintained nor monitored" [7]. Anniversary is supported in `wowsims/tbc-new`, a fork of the MoP sim with 144 releases and a commit on the day of access [8].
- **Headless options** [9][10][11]:
  - `wowsimcli sim --infile <RaidSimRequest protojson>` runs a raid sim only.
  - The native binary (`sim/web`, default `localhost:3333`) accepts protobuf POSTs to `/raidSim`, `/computeStats`, `/statWeights`, `/bulkSimAsync`, `/asyncProgress` and more.
  - A WASM build exists, and the Go packages can be imported as a library.
- **Upgrade analysis:** `BulkSimRequest` takes a baseline plus `BulkGearCandidate`s and returns each candidate's DPS distribution and paired error against the baseline [11]. So "upgrade value per item per raider" can come from bulk sims. It can also come from paired `RaidSimRequest`s with a fixed seed. Bulk results expose only `dps_metrics`.
- **Stat weights:** `StatWeightsResult` covers `dps`, `hps`, `tps`, `dtps`, `tmi` and `p_death`, which gives a cheaper EP-based fallback for tanks and healers [11].
- **Spec coverage:** every class is registered, some as merged specs (`hunter`, `mage`, `rogue`, `warlock`, `dps_warrior`, `dps_priest`). Feral bear, protection paladin, protection warrior and all four healers are registered. The most recent change ported healers as "gear planners", and every class shows "Alpha" on wowsims.com/tbc [12][13].
- **Gear input:** the WowSimsExporter addon (MIT) supports TBC via `/wse export` and has item fields `id`, `enchant`, `random_suffix` and `gems` [16]. Whether its output matches the sim's `EquipmentSpec` is **unverified**: neither the exporter's JSON output nor `EquipmentSpec`'s fields were read.
- **WoW Forever:** an org-wide code search found no support [8].

## 3. Loot tables

- **Wowhead:** the `&xml` endpoint does return drop data, e.g. `sourcemore: {n:"Gruul the Dragonkiller", ti:19044, z:3923}` [17]. The tooltip JSON has no source data [18], and zone pages list drops [19]. robots.txt blocks AI and scraper bots entirely and blocks `/search` and `/list` for everyone else [20]. **The ZAM terms forbid spiders and data-mining tools, derivative works, and any commercial or third-party use** [21]. Treat Wowhead as a reference for humans only (tooltips and links), not a data feed.
- **wowsims `db.json`** [15]:
  - 8,256 items, 2,352 with `sources[].drop {npcId, zoneId, difficulty}` (schema in `proto/ui.proto` [14]), plus `phase`, `npcs` (509), `zones` (74) and `encounters`.
  - Spot check on one item: Dragonspine Trophy maps to npc 19044, zone 3923 in both wowsims and Wowhead [17]. AtlasLoot lists it under Gruul [22].
  - The database was last updated about a week before access, with Anniversary phase curation ("Battlemaster trinkets in Phase 3") [8]. The refresh cadence and upstream source are unknown.
- **AtlasLootClassic** (GPL-2.0) [22]:
  - Lua tables per raid and boss, with `npcID`, item IDs, tier tokens, trash lists and `ContentPhaseBC` tags.
  - Last release 3 years ago, so it's useful as a cross-check or boss-ordering source, not as the primary feed.
  - Its GPL licence would affect distribution if its data were bundled.
- **Current tier:** Anniversary Phase 3 (Hyjal and Black Temple) went live on 2026-08-27. Phase 4 (Zul'Aman) and Phase 5 (Sunwell) are expected in "autumn" 2026 [23][24]. This comes from Wowhead's roadmap, not an official Blizzard source.

## 4. Player gear input and existing tools

- **Gear input:** WowSimsExporter is the best fit for per-raider gear, and it can also export an inspected target [16]. The Blizzard Classic Profile API exists, but equipment data for Anniversary realms isn't confirmed, and API data may carry a 30-day retention rule. That second point comes from a user paraphrase and wasn't verified [29][31].
- **That's My BIS (TMB):** already runs wishlists, prio lists, attendance and loot history, and claims support for TBC and Forever [33][25]. It requires Discord, and no public source code was found [25].
- **Gargul:** an actively maintained in-game loot distribution addon. It imports TMB exports (base64 + zlib JSON keyed by item ID), a **simple CSV prio format** (`itemId,player1[1],player2[2]`), softres.it and DFT [26]. It is source-visible but "all rights reserved".
- **RCLootCouncil Classic** (GPL-3.0) and **softres.it** cover council and soft-reserve workflows. Their import formats weren't verified [27][28].

## Cross-dimension insights

- **wowsims covers two of your three sources.** Its item database replaces Wowhead for loot tables, and its engine provides upgrade values. Both share one ID space and one licence (MIT). wowtbc.gg becomes the only external source, and the name-to-ID mapping into wowsims items is the single integration seam.
- **Each input has a different reliability, so they should feed a weighted blend, not a single score.** wowtbc.gg `value` scores give a free per-spec ranking that works for every spec, healers and tanks included. wowsims bulk sims give per-raider precision but are Alpha, and they measure DPS only.
- **Output should be a Gargul-compatible CSV or TMB-shaped prio list rather than a new in-game tool.** That puts the app upstream of Gargul/TMB, where the distribution tooling already exists [25][26].
- **WoW Forever needs a different design.** No sim was found [8], no API was found (low confidence) [30], addons are reportedly restricted [24], and BiS lists are unranked [4]. A Forever mode can only use a BiS whitelist plus manual weights, so keep the data-source layer pluggable.

## Recommendations

| # | Recommendation | Feeds | Confidence basis |
|---|---|---|---|
| R1 | Use the wowsims `tbc-new` `db.json` as the loot-table and item-ID source. Pin it to a release tag and refresh it each phase. | PRD data sources; architecture constraint | High on content (direct download [15]); medium on completeness (one item cross-checked against Wowhead [17]). Do a raid-wide diff before relying on it |
| R2 | Don't scrape or bundle Wowhead data. Only link or tooltip to Wowhead in the UI. | PRD non-functional (legal) | High: primary terms text [21] |
| R3 | Pull wowtbc.gg `page-data.json` per spec and map names to wowsims IDs. Email wowtbc.gg@gmail.com for permission to reuse the data, and fall back to manual or curated BiS lists if refused. | PRD data sources; open risk | High on format [2]; the legal position is **unverified** [3] |
| R4 | Run `tbc-new` locally (HTTP API or Go library) and use bulk sim for DPS upgrade values. Use stat-weight EP (hps/tps) for healers and tanks. Show a visible link back to wowsims. | Architecture spine | Medium: API evidenced in source code [10][11]; the sim is Alpha and healer maturity is unverified [12][13] |
| R5 | Priority = weighted blend of (a) BiS phase flag and value rank, (b) per-raider sim or EP delta, (c) class/role rules, all tunable by officers. | PRD core requirement | Medium: follows from the coverage gaps above |
| R6 | Take raider gear from WowSimsExporter pastes. Export results as Gargul CSV (and optionally TMB-compatible). | PRD input/output; UX | Medium for the Gargul CSV (format in code [26]); low for exporter parsing (only field layout seen, JSON output unread [16]); TMB import unverified |
| R7 | Scope v1 to TBC Anniversary with the current tier (P3, rolling to P4/P5). Keep data sources behind an interface so WoW Forever can be a BiS-only mode later. | PRD scope; architecture | Medium: schedule from Wowhead, not Blizzard [23] |

## Open questions

- **wowtbc.gg reuse permission.** Needs an email to the operator [3].
- **Exact `EquipmentSpec`/`ItemSpec` fields and the WowSimsExporter JSON shape.** Answer by reading `proto/common.proto` and `exporter/ExportStructures/` [11][16].
- **Whether bulk sim works for healer and tank specs, and whether healer HPS sims are meaningful.** Needs a test run of `tbc-new` with a healer profile [12].
- **What wowtbc.gg's `value`/`final_value` scores mean** (EP? sim DPS?). Not published. Needs a question to the operator or a correlation check against wowsims EP [1][2].
- **Whether the Blizzard Classic Profile API returns equipment for Anniversary realms, and its retention terms.** Needs the rendered docs and a test token [29][31].
- **Whether TMB can import prio lists, or only export them.** Needs the TMB wiki [25].

## Source appendix

| # | Supports | Publisher | Pub date | Accessed | Confidence |
|---|---|---|---|---|---|
| [1] | BiS URL structure, phase dropdown, community-submitted lists, raw HTML (no IDs, page-data reference) | [WOWTBC.GG – Fury Warrior BiS](https://wowtbc.gg/bis-list/fury-warrior/) | unknown | 2026-09-29 | high |
| [2] | page-data.json fields, per-phase flags, value scores, 170/448 IDs, file size | [WOWTBC.GG – page-data.json](https://wowtbc.gg/page-data/bis-list/fury-warrior/page-data.json) | unknown | 2026-09-29 | high |
| [3] | No reuse licence; privacy policy only | [WOWTBC.GG – Privacy](https://wowtbc.gg/privacy/) | 2021-03-01 | 2026-09-29 | high |
| [4] | WoW Forever BiS lists unranked | [WOWTBC.GG – Forever Fire Mage](https://wowtbc.gg/warcraftforever/bis-list/fire-mage/) | unknown | 2026-09-29 | high |
| [5] | WoW Forever dungeon loot provisional, no raid tables | [WOWTBC.GG – Forever Deadmines loot](https://wowtbc.gg/warcraftforever/loot-tables/dungeons/the-deadmines/) | unknown | 2026-09-29 | high |
| [6] | Site now leads with WoW Forever | [WOWTBC.GG – Home](https://wowtbc.gg/) | 2026-09-15 | 2026-09-29 | high |
| [7] | wowsims/tbc deprecated, points to tbc-new | [wowsims/tbc](https://github.com/wowsims/tbc) | ~2026-07 | 2026-09-29 | high |
| [8] | tbc-new maintained, MIT + attribution, last db update, no Forever (org search) | [wowsims/tbc-new](https://github.com/wowsims/tbc-new) | 2026-09-29 | 2026-09-29 | high |
| [9] | wowsimcli raid-sim only | [tbc-new basic_sim.go](https://github.com/wowsims/tbc-new/blob/master/cmd/wowsimcli/cmd/basic_sim.go) | 2026-03 | 2026-09-29 | high |
| [10] | HTTP protobuf API endpoints | [tbc-new sim/web/main.go](https://github.com/wowsims/tbc-new/blob/master/sim/web/main.go) | 2026-09 | 2026-09-29 | high |
| [11] | RaidSim, BulkSim, StatWeights messages | [tbc-new proto/api.proto](https://github.com/wowsims/tbc-new/blob/master/proto/api.proto) | unknown | 2026-09-29 | high |
| [12] | All specs registered; healers ported as gear planners | [tbc-new register_all.go](https://github.com/wowsims/tbc-new/blob/master/sim/register_all.go) | 2026-09 | 2026-09-29 | high / low (healer maturity) |
| [13] | All classes labelled Alpha | [wowsims.com/tbc](https://wowsims.com/tbc/) | unknown | 2026-09-29 | high |
| [14] | UIItem/DropSource schema | [tbc-new proto/ui.proto](https://github.com/wowsims/tbc-new/blob/master/proto/ui.proto) | unknown | 2026-09-29 | high |
| [15] | db.json counts, populated drop sources | [tbc-new db.json](https://raw.githubusercontent.com/wowsims/tbc-new/master/assets/database/db.json) | 2026-09 | 2026-09-29 | high |
| [16] | WowSimsExporter TBC support and ItemSpec fields | [wowsims/exporter](https://github.com/wowsims/exporter) | 2026-08 | 2026-09-29 | medium |
| [17] | Wowhead XML with sourcemore drop data | [Wowhead item 28830 XML](https://www.wowhead.com/tbc/item=28830&xml) | unknown | 2026-09-29 | high |
| [18] | Tooltip JSON lacks sources | [Wowhead tooltip API](https://nether.wowhead.com/tbc/tooltip/item/28830) | unknown | 2026-09-29 | high |
| [19] | Zone drops listview | [Wowhead – Karazhan](https://www.wowhead.com/tbc/zone=3457/karazhan) | unknown | 2026-09-29 | medium |
| [20] | robots.txt AI/scraper block | [Wowhead robots.txt](https://www.wowhead.com/robots.txt) | unknown | 2026-09-29 | medium |
| [21] | No scraping, no derivative/commercial use | [ZAM/Fanbyte Terms](https://corp.fanbyte.com/legal/terms) | 2025-05-14 | 2026-09-29 | high |
| [22] | AtlasLoot TBC Lua tables, GPL-2.0, stale | [AtlasLootClassic](https://github.com/Hoizame/AtlasLootClassic) | ~2023 | 2026-09-29 | high |
| [23] | Anniversary phase schedule | [Wowhead – Anniversary roadmap](https://www.wowhead.com/tbc/guide/the-burning-crusade-classic-anniversary-phase-release-roadmap) | 2026-08-27 | 2026-09-29 | medium |
| [24] | P3 current; Forever addon restrictions; population drop | [Wowhead – TBC hub](https://www.wowhead.com/tbc) | 2026-09 | 2026-09-29 | medium |
| [25] | TMB features, Discord-gated, no public repo found | [That's My BIS – FAQ](https://thatsmybis.com/wiki/faq) | unknown | 2026-09-29 | high |
| [26] | Gargul TMB/CSV/softres imports, rights reserved | [Gargul](https://github.com/papa-smurf/Gargul) | 2026-09 | 2026-09-29 | high |
| [27] | RCLootCouncil Classic, GPL-3.0 | [RCLootCouncil_Classic](https://github.com/evil-morfar/RCLootCouncil_Classic) | 2026-09 | 2026-09-29 | high |
| [28] | softres.it editions | [softres.it](https://softres.it) | unknown | 2026-09-29 | low |
| [29] | Blizzard Classic Profile API exists | [Blizzard forums – Getting started](https://us.forums.blizzard.com/en/blizzard/t/getting-started-with-the-wow-api/12097) | 2025-09-28 | 2026-09-29 | medium |
| [30] | No Blizzard API for Forever beta | [Blizzard forums – Forever API](https://us.forums.blizzard.com/en/blizzard/t/when-will-we-gain-api-access-to-forever-apis/59595) | 2026-09-18 | 2026-09-29 | low |
| [31] | API ToS 30-day retention (paraphrase) | [Blizzard forums – API discussion](https://us.forums.blizzard.com/en/blizzard/c/api-discussion/18) | 2026-09 | 2026-09-29 | low |
| [32] | robots.txt and sitemap.xml return Not Found | [WOWTBC.GG – robots.txt](https://wowtbc.gg/robots.txt) | n/a | 2026-09-29 | medium |
| [33] | TMB claims support for Forever, Classic, SoD, TBC, WotLK, Cata, MoP | [That's My BIS – Home](https://thatsmybis.com) | unknown | 2026-09-29 | high |

## Staleness map

Computed with `recon_kit.py staleness` using these windows: version, format and schedule 1 month; data-access 3 months; maintenance 6 months; legal and landscape 12 months.

| Claim | Re-check by | Stale now? |
|---|---|---|
| Anniversary phase schedule, P3 current [23][24] | 2026-09-27 | **yes**: P4 (ZA) is due soon |
| WowSimsExporter TBC ItemSpec [16] | 2026-09-29 | **yes** |
| wowsimcli raid-sim only [9] | 2026-04-29 | **yes**: file dates from 2026-03 |
| Wowhead/ZAM terms [21] | 2026-05-14 | **yes**: dated 2025-05, still in force at access |
| wowtbc.gg has no reuse terms [3] | 2022-03-01 | **yes**: policy dated 2021 |
| tbc-new HTTP API endpoints [10] | 2026-10-01 | no |
| Gargul import formats [26] | 2026-10-15 | no |
| Spec coverage / Alpha status [12][13] | 2026-10-22 | no |
| db.json drop sources [15] | 2026-10-22 | no |
| wowtbc.gg page-data.json structure [2] | 2026-12-29 | no |
| wowsims maintenance [7][8] | 2027-03-29 | no |
| Forever addon/API limits [24][30] | 2027-09-18 | no |
| wowsims MIT licence [8] | 2027-09-29 | no |

The two legal documents are flagged stale only because of their publication dates; both were checked and found in force on 2026-09-29. **The earliest real re-check is the phase schedule**, when Phase 4 (Zul'Aman) launches.
