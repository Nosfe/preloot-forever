## Findings
- `wowsims/tbc` (the original 2021 TBC sim) is deprecated. Its README says: "This is the old TBC Sim, released in 2021. This version is not maintained nor monitored. TBC Anniversary is being supported at https://github.com/wowsims/tbc-new". It still shows some upkeep: latest release v1.9.3 about 6 months ago, latest commit about a month ago ("Hide sidebar outdated-warning…"), 28 open issues. | https://github.com/wowsims/tbc (README.md) | wowsims | README commit about 2 months before access | accessed 2026-09-29 | high | maintenance
- **`wowsims/tbc-new` replaces it and is actively maintained.** It is "forked from wowsims/mop", described as "World of Warcraft TBC Classic simulations", and linked to the live site wowsims.com/tbc. At access it had 144 releases (latest v0.0.144, 5 days earlier), a latest commit 19 minutes earlier (merge of PR #550), 15 open issues and 4 open PRs. | https://github.com/wowsims/tbc-new | wowsims | commit 13352ce, 2026-09-29 | accessed 2026-09-29 | high | maintenance
- The wowsims org has 18 repos, including tbc-new, tbc, mop, cata, wotlk, classic, sod, exporter, gamedata ("World of Warcraft gamedata files in a readable format", updated 4 days before access), pages-deploy and wowsims.github.io. | https://github.com/wowsims | wowsims | n/a | accessed 2026-09-29 | high | maintenance
- **Headless CLI exists:** `cmd/wowsimcli` is a Cobra command `sim` ("simulate items & settings"). It takes `--infile` ("location of input file (RaidSimRequest in protojson format)"), `--outfile` (default stdout) and `--verbose`. It requires `simOptions` in the input, runs `core.RunRaidSimConcurrentAsync`, and writes a `RaidSimResult` as protojson. The CLI only exposes raid sims; stat weights and bulk sims are not available as CLI commands. | https://github.com/wowsims/tbc-new/blob/master/cmd/wowsimcli/cmd/basic_sim.go (also cli_main.go, root.go, decode_link.go, version.go) | wowsims | about 6 months before access (commit 23f5cad) | accessed 2026-09-29 | high | api
- **The native binary also has an HTTP API.** `sim/web/main.go` serves protobuf (`application/x-protobuf`) on `-host` (default `localhost:3333`) and has an `-nvc` flag. Endpoints:
  - Synchronous: `/raidSim`, `/statWeights`, `/statWeightRequests`, `/statWeightCompute`, `/computeStats`, `/bulkCombinationCount`, `/bulkCandidates`, `/abortById`.
  - Async: `/raidSimAsync`, `/statWeightsAsync`, `/bulkSimAsync`, `/reforgeOptimizeAsync`, polled through `/asyncProgress`.

  The server sets `Access-Control-Allow-Origin: *` on these endpoints and by default auto-launches a browser (`-launch`). Release binaries are published for Windows, macOS and Linux (e.g. wowsimtbc-amd64-linux.zip). | https://github.com/wowsims/tbc-new/blob/master/sim/web/main.go ; README | wowsims | about 28 days before access | accessed 2026-09-29 | high | api
- A WASM build also exists (`sim/wasm/`, "Port MoP simplify improvements", about a month before access). Go packages are importable as a library under the module path `github.com/wowsims/tbc/...`, for example `sim.RegisterAll()`, `core.RunRaidSim`, `core.StatWeights`, `core.ComputeStats` and `sim/core/bulk`. | https://github.com/wowsims/tbc-new/tree/master/sim ; sim/web/main.go imports | wowsims | n/a | accessed 2026-09-29 | high | api
- **The protobuf API is defined in `proto/api.proto`:**
  - `message RaidSimRequest { string request_id=5; Raid raid=1; Encounter encounter=2; SimOptions sim_options=3; SimType type=4; }`
  - `ComputeStatsRequest { Raid raid; Encounter encounter; bool skip_rotation; }`
  - `StatWeightsRequest { Player player; RaidBuffs…; Encounter; SimOptions; repeated Stat stats_to_weigh; Stat ep_reference_stat; }`
  - `StatWeightsResult` holds weights/EP for `dps`, `hps`, `tps`, `dtps`, `tmi` and `p_death`.
  - `UnitMetrics` holds `dps`, `threat`, `dtps`, `tmi` and `hps` distributions. | https://github.com/wowsims/tbc-new/blob/master/proto/api.proto | wowsims | n/a | accessed 2026-09-29 | high | api
- **Batch and upgrade analysis is available through bulk sim.** `BulkSimRequest { RaidSimRequest base_request; repeated BulkGearCandidate candidates; …; BulkSettings bulk_settings; }` and `BulkSettings { repeated ItemSpec items; int32 iterations_per_combo; bool use_legacy_bulk_sim; freeze_* … }`.
  - Results report per-candidate DPS against the equipped gear: `BulkGearResult { EquipmentSpec gear; DistributionMetrics dps_metrics; double paired_error_to_baseline; }`.
  - Bulk sim runs in stages (Low, Medium, High, Finalist).
  - Upgrade values could come either from bulk sims or from two `RaidSimRequest`s (baseline vs. item swapped) using a shared `random_seed`. | proto/api.proto (tbc-new) | wowsims | n/a | accessed 2026-09-29 | high | api
- `Player` supports an item-swap feature: `bool enable_item_swap = 6; ItemSwap item_swap = 7;`. It carries its own item database with `SimDatabase database = 50;`, and `talents_string` uses Wowhead format. | proto/api.proto (tbc-new) | wowsims | n/a | accessed 2026-09-29 | high | format
- **Gear input is `EquipmentSpec` inside `Player.equipment`,** encoded as protobuf or protojson. The exact fields of `EquipmentSpec` and `ItemSpec` (id, enchant, gems) were **not verified** this run because they live in common.proto. | proto/api.proto (tbc-new) | wowsims | n/a | accessed 2026-09-29 | medium | format
- **Spec coverage (Player `oneof spec` plus `sim/register_all.go`):**
  - Druid: balance_druid, feral_cat_druid, feral_bear_druid, restoration_druid
  - Hunter: hunter
  - Mage: mage
  - Paladin: holy_paladin, protection_paladin, retribution_paladin
  - Priest: dps_priest, healer_priest
  - Rogue: rogue
  - Shaman: elemental_shaman, enhancement_shaman, restoration_shaman
  - Warlock: warlock
  - Warrior: dps_warrior, protection_warrior

  All four tanks (feral bear, protection paladin, protection warrior) and all four healers (restoration druid, holy paladin, healer priest, restoration shaman) are registered. | https://github.com/wowsims/tbc-new/blob/master/sim/register_all.go ; proto/api.proto | wowsims | register_all.go last changed about 1 week before access | accessed 2026-09-29 | high | coverage
- **Healer support may be only partial.** The latest commit on `register_all.go` and `proto/` is titled "Healer gear planners ported from wowsims#1562". This suggests healers were added as "gear planners" rather than full HPS sims, but that was not confirmed. | https://github.com/wowsims/tbc-new (folder listing, proto/ and sim/register_all.go commit message) | wowsims | about 1 week before access | accessed 2026-09-29 | low | coverage
- **Every class is labelled "Alpha" on the live site:** "PriestAlpha DruidAlpha Rogue Alpha Hunter Alpha ShamanAlpha Mage Alpha Warlock Alpha PaladinAlpha WarriorAlpha". Separately, the README commit (27 days before access) says "Remove the unsupported Raid Sim UI", so the raid-sim UI is gone. | https://wowsims.com/tbc/ ; tbc-new README history | wowsims | n/a | accessed 2026-09-29 | high | maintenance/coverage
- **Stat weights are covered for tanks and healers too:** `StatWeightsResult` returns `dps`, `hps`, `tps`, `dtps`, `tmi` and `p_death`, and `UnitMetrics.chance_of_death` is "Used for tank sims". | proto/api.proto (tbc-new) | wowsims | n/a | accessed 2026-09-29 | high | api
- **The item database is in the repo:** `assets/database/db.json` and `db.bin` (plus `leftover_db.*` and `loader.go`), with inputs in `assets/db_inputs/`, updated about a week before access ("[DB] Put the Battlemaster trinkets in Phase 3"). The org also has a separate `gamedata` repo. | https://github.com/wowsims/tbc-new/tree/master/assets/database | wowsims | about 1 week before access | accessed 2026-09-29 | high | format
- **Item records carry drop sources in their schema** (`proto/ui.proto`):
  - `UIItem` includes `int32 id; string name; … int32 ilvl; int32 phase; ItemQuality quality; … repeated Class class_allowlist; … Expansion expansion; repeated UIItemSource sources = 23;`.
  - `UIItemSource` is a `oneof` of `CraftedSource crafted | DropSource drop | QuestSource quest | SoldBySource sold_by | RepSource rep`.
  - `DropSource` is `{ DungeonDifficulty difficulty; int32 npc_id; int32 zone_id; string other_name /* e.g. "Trash" */; string category; }`.
  - `UIDatabase` also lists `repeated UIZone zones` (id, name, expansion) and `repeated UINPC npcs` (id, name, zone_id).
  - `RaidFilterOption` covers Kara, Gruul, Mag, TK, SSC, MH, BT, ZA and SWP.

  Whether `db.json` actually fills in `sources` for TBC raid items was **not verified**: the file was too large to fetch. | https://github.com/wowsims/tbc-new/blob/master/proto/ui.proto | wowsims | n/a | accessed 2026-09-29 | high (schema) / unverified (population) | format
- The sim-side `SimItem` in `proto/db.proto` has no source or drop fields (id, name, type, sockets, set, scaling_options, item_effects only). Sources exist only in the UI database. | https://github.com/wowsims/tbc-new/blob/master/proto/db.proto | wowsims | n/a | accessed 2026-09-29 | high | format
- **License is MIT, with an attribution request.** The tbc-new README says: "This project is licensed with MIT license. We request that anyone using this software in their own project to make sure there is a user visible link back to the original project." wowsims/tbc and wowsims/exporter are also MIT. | https://github.com/wowsims/tbc-new (README, LICENSE) ; https://github.com/wowsims/tbc ; https://github.com/wowsims/exporter | wowsims | n/a | accessed 2026-09-29 | high | license
- **An in-game exporter addon (WowSimsExporter) supports TBC.** `Conditional_TBC.lua` ("tbc support", about 7 months before access) sets `Env.prelink = "https://www.wowsims.com/tbc/"` and registers these specs: shaman elemental/enhancement; hunter BM/MM/SV; druid balance/feral(cat); warlock ×3; rogue ×3; mage ×3; warrior arms/fury/protection; paladin protection/retribution; priest shadow.
  - In the fetched snippet, no healer specs and no feral bear appear, though the snippet may be truncated.
  - Usage is `/wse export`, and the output is copied with Ctrl+C. Latest release is v3.2.4, about a month before access.
  - The exact JSON output format was not retrieved; `ExportStructures/` was not read. | https://github.com/wowsims/exporter (README, Conditional_TBC.lua) | wowsims | about 1 month before access | accessed 2026-09-29 | medium | format/coverage
- `cmd/wowsimcli/cmd/decode_link.go` exists, which suggests the CLI can decode wowsims share links. Its behavior was not read. | https://github.com/wowsims/tbc-new/tree/master/cmd/wowsimcli/cmd | wowsims | about 10 months before access | accessed 2026-09-29 | low | api

## Leads
- Read `proto/common.proto` in tbc-new for `EquipmentSpec` and `ItemSpec` (item id, enchant, gems, random suffix), to pin down the exact gear JSON shape.
- Download `assets/database/db.json` directly with a raw download and a JSON parser. Check that `sources[].drop.{npcId,zoneId,difficulty}` is filled in for Karazhan through Sunwell items, and that `zones` and `npcs` are present.
- Read `assets/db_inputs/` and `tools/` (the DB generator) to learn the upstream data source (Wowhead, the gamedata repo, or DB2 files) and how often it refreshes.
- Read `wowsims/exporter/ExportStructures/` and `Shared.lua` for the exporter output schema, and check healer spec entries in the full `Conditional_TBC.lua`.
- Read `sim/core/api.go` and `sim/core/bulk/` to see whether bulk sim works for healer and tank specs, since the bulk result exposes only `dps_metrics`.
- Check tbc-new issues or the commit for PR "wowsims#1562" (healer gear planners) to judge whether healer HPS sims are meaningful.
- Read `docs/commands.md` and `docs/installation.md` in tbc-new for official headless and CLI build guidance.
- The root folder has a commit titled "Add skills file" (`sim/web`), which may document the API for agents.

## Looked for but not found
- **WoW Forever support:** an org-wide code search for "WoW Forever", "wowforever" and "forever" returned no results. Nothing in the org listing, the tbc-new README or the proto files mentions it.
- **CLI subcommands for stat weights or bulk sim:** only the `sim` (RaidSimRequest) and `version` commands were seen. Stat weights and bulk sim are available only through the HTTP server, WASM or the Go library.
- **A sample populated item record from db.json:** the fetch failed because the file is too large, so only the schema is evidenced.
- **An explicit statement that healer sims are production-ready:** not found. All classes are marked Alpha on wowsims.com/tbc.
- **The exporter's exact output JSON format:** not retrieved.
- **A gRPC server mode:** not found. The API is plain HTTP POST with protobuf bodies.