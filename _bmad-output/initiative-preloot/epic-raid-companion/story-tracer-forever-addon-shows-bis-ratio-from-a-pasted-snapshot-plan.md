---
title: 'Tracer: Forever addon shows BiS Ratio from a pasted snapshot'
type: 'feature'
ticket: '1'
created: '2026-10-23'
status: 'built'
baseline_revision: 'f2d92b2ebce680e7e15fbed83f73826dff5ba7fc'
route: 'full'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The addon (Core.lua, 1.1.0) targets TBC (Interface 20506), persists an old attendance/loot ratio in SavedVariables, shows random values for unknown players, and inserts its column among Gargul's native columns; it cannot read the workbook's Interchange v2 snapshot.

**Approach:** Rebuild the addon as a small set of files for WoW Forever: paste the 4.6 snapshot (Base64 or raw JSON) into a session-only store and show one "Ratio BiS" column appended after Gargul's ten native roll-table columns. Remove all legacy behaviour; offline LuaJIT tests load Gargul's own Base64 and JSON modules.

## Boundaries & Constraints

**Always:** Exact raider keys (no case-folding, no realm stripping beyond Gargul's own display name, minus its " [n]" re-roll suffix). Session-only state (nothing in SavedVariables). Unrounded values in state, `%.3f` only at display. Columns only appended (index 11+). User-facing chat lines in French. LuaJIT/Lua 5.1 syntax only.

**Never:** Full Interchange validation and tolerance checks (5.4), the Impact column (5.5), treatment capture, award hooks, export fill, chat ratio line (5.2, 5.3, 5.6). Editing Gargul or the workbook script. README and Gargul.code-workspace changes (5.7).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Base64 import | Base64 of snapshot-sample.json | 3 raiders stored; chat: tier, raid, count | No error expected |
| Raw JSON import | snapshot JSON text starting with `{` | Same as Base64 | No error expected |
| Accented spec | "Prêtre Sacré" | Stored byte-identical | No error expected |
| Bad payload | non-Base64, bad JSON, schemaVersion ≠ 2, raiders missing | Previous session state unchanged | French chat error |
| Roller in snapshot | row "Alya" or "Alya [2]" | Ratio BiS cell `0.250` | No error expected |
| Roller not in snapshot / no snapshot | any row | Empty cell | No error expected |
| Large payload | > 8192 characters | Accepted (no editbox limit) | No error expected |

</frozen-after-approval>

## Code Map

- `C:/Repos/Gargul_Preloot/Core.lua` -- legacy single file: loader frame + `GP:init`, hooks (`tableColumns`, `refreshRollsTable`, `Importer:open`, `AwardedLoot:addWinner`), `GargulPrelootDB`, random/hash/test data, broken `GL.Base64:Decode`. Reuse the importer-button + AceGUI dialog layout and button reordering; delete the rest.
- `C:/Repos/Gargul_Preloot/Gargul_Preloot.toc` -- `## Interface: 20506`, `SavedVariables: GargulPrelootDB`, lists Core.lua only.
- `C:/Repos/Gargul/Classes/MasterLooterUI.lua:1002` -- `tableColumns()` returns 10 columns; `drawPlayersTable` (L863) sets table width 430; OnClick reads `cols[10]`; Award flow reads cols 1, 2, 4.
- `C:/Repos/Gargul/Classes/RollOff.lua:2014` -- `refreshRollsTable()` builds rows `{cols={...10 cells}}`, then `SetData` + `SortData`. Row name = `GL:disambiguateName(Roll.player)` with " [n]" suffix (L1208).
- `C:/Repos/Gargul/Classes/Base64.lua:91` -- `GL.Base64.decode(b64)` (dot, lowercase; brownfield's `Decode` is wrong). `Classes/JSON.lua:477` -- `GL.JSON:decode(text)`; JSON null decodes to nil. Both start `local _, GL = ...`, so tests can load them with a fake GL.
- `C:/Repos/Gargul/Interface/Importer.lua` -- `Importer:open()`, `windowName`, `GL.Interface:dynamicPanelButton(Window, label)`.
- `C:/Repos/Gargul_Preloot/tools/google_apps_script/fixtures/snapshot-sample.json` -- shared fixture (3 raiders, 2 items, UTF-8).

## Tasks & Acceptance

**Execution:**
- [ ] `Gargul_Preloot.toc` -- `## Interface: 16001` and `## Interface-Camelot: 16001`, version 2.0.0, no SavedVariables, files: Core.lua, Snapshot.lua, Scores.lua, Columns.lua, Import.lua -- Forever load, session-only.
- [ ] `Core.lua` -- rewrite as bootstrap: shared namespace via `local _, GP = ...`, ADDON_LOADED init that checks Gargul and installs Columns and Import hooks.
- [ ] `Snapshot.lua` -- pure `GP.Snapshot.parse(text, GL)` (Base64 or raw JSON → table or nil, err) with minimal checks (schemaVersion 2, tierId/raidId strings, raiders array of tables with string raiderKey); `GP.Snapshot.set/get/raider(key)` session store, replaced only on success.
- [ ] `Scores.lua` -- pure `GP.Scores.bisRatio(raider)` = (tierPresence / tierPresenceMax) / (bisLootCount + 1).
- [ ] `Columns.lua` -- wrap `MasterLooterUI:tableColumns` to append "Ratio BiS" once; wrap `RollOff:refreshRollsTable` to append one cell per row (pure helper `rollerKey(displayName)` strips " [n]"); widen the table/window to fit; re-apply on the sortByPlusOne setting event.
- [ ] `Import.lua` -- importer button "Preloot (snapshot)" added once per window (`_importButtonAdded` set), AceGUI paste dialog with no letter limit, French success/error lines.
- [ ] remove `json_export_example.json`, `sample_import`, `sample_json`.
- [ ] `tests/addon/run.lua` -- LuaJIT runner: loads Gargul's Base64.lua/JSON.lua from `../Gargul` (override with `GARGUL_DIR`), then addon pure files; covers every I/O matrix row except UI.

**Acceptance Criteria:**
- Given the repo, when `luajit tests/addon/run.lua` runs, then it prints PASS with the assertion count and exits 0.
- Given WoW Forever with Gargul v8.0.1, when the owner pastes a live 4.6 snapshot and starts a roll, then Ratio BiS appears after Gargul's columns and matches the workbook to 3 decimals.

## Implementation Notes

- Implemented directly (no subagent). Owner setup done: Gargul v8.0.1 shallow clone at C:/Repos/Gargul; LuaJIT 2.1 (Lua 5.1) via winget `DEVCOM.LuaJIT` (no plain Lua 5.1 package).
- Tests stub WoW string aliases (`strchar`, ...) that Gargul's JSON.lua needs, and add a hook-wiring smoke test with stubbed MasterLooterUI, RollOff, Interface and Importer.
- Gargul's own sortByPlusOne listener calls `self:tableColumns()`, which resolves to the wrapper, so no extra listener is needed. lib-st sizes the table from its columns; only the master looter window (520) is widened by the column width.
- Importer height is re-applied on every open (226) in case Gargul restores a saved size.

## Plan Change Log

## Review Triage Log

Pass 1 (quick): high 0, medium 1, low 3, false 0, maybe-false 0.

| Finding | Verdict | Route | Evidence / action |
|---|---|---|---|
| Import.lua grows the Importer to 226 px, but Gargul clamps it to maxHeight 200 in OnSizeChanged, so the button lands on the watermark | medium | patch | Confirmed at Gargul Interface.lua OnSizeChanged. Fixed: the intro line is hidden, the Preloot button takes its place at -30, Soft-Reserves (and the chain below it) moves down one step, and no height change. Test stub updated. |
| Snapshot.parse accepts `raiders` as a JSON object or with null entries (ipairs stops early) | low | patch | Confirmed. A direct check was added: the pairs count must equal #raiders. Two refusal cases added to the tests. |
| tests/addon/run.lua root detection fails when run from tests/addon | low | patch | Confirmed. Root is now the script directory plus /../..; both run locations pass. |
| Scores.bisRatio returns nil where the workbook defaults operands (missing → 0, max ≤ 0 → 1) | low | reject | Unreachable: the exporter guarantees integer counts and max ≥ 1. Recompute parity belongs to 5.4. |

## Design Notes

Addon files share the private table WoW passes as `...`; tests pass the same pair: `assert(loadfile(path))("Gargul_Preloot", GP)`. Pure modules take `GL` as an argument instead of reading `_G.Gargul`, so tests need no WoW stubs.

## Verification

**Commands:**
- `luajit tests/addon/run.lua` (from C:/Repos/Gargul_Preloot) -- expected: `PASS: <n> assertions`, exit 0.

**Manual checks (if no CLI):**
- Owner, in game: addon listed and loaded with Gargul v8.0.1 (no out-of-date flag); Gargul Importer shows the Preloot button once after reopening; pasted live snapshot reports the raider count; a test roll shows Ratio BiS matching the workbook.
