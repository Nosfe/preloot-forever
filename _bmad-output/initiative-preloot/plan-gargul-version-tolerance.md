---
title: 'Gargul version tolerance'
type: 'refactor'
ticket: ''
created: '2026-10-26'
status: 'built'
baseline_revision: '2aac848'
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

**Problem:** The addon is written against Gargul v8.0.1 internals. `Core.init` refuses to load unless every Gargul module is present, and each hook assumes exact function names and signatures. On another Gargul version (older on Anniversary, newer later), one missing or renamed piece either disables everything or throws a Lua error mid-raid.

**Approach:**
- One `Compat.lua` module feature-detects every Gargul API the addon uses, with fallbacks where a safe one exists.
- Each feature installs only when its own APIs are present: roll-table columns, Importer button, award tracking, export fill, chat line.
- On load, one French chat line lists any feature turned off and why. A missing piece never stops the others.
- Decision (owner, 2026-10-26): "Gargul version idempotent" means working across Gargul versions.

## Boundaries & Constraints

**Always:**
- Same behaviour as today on Gargul v8.0.1; the existing 333 assertions stay green.
- Fallbacks:
  - Base64: Gargul's `GL.Base64.decode`, else `Decode`, else a bundled pure-Lua decoder.
  - Winner key: `GL:formatPlayerName(name, {includeRealm = "never"})`, else realm stripped at the first `-`.
  - Rolled item: `RollOff.CurrentRollOff.itemID`, else parsed from `CurrentRollOff.itemLink`.
  - Chat: `GL:sendChatMessage(msg, "GROUP")`, else WoW `SendChatMessage` to RAID or PARTY.
  - Announcement setting: missing means on.
- Every hook wraps the original only when it is a function. Every wrapper calls the original first and is guarded with `pcall`, so an addon error never breaks Gargul's own behaviour.

**Never:**
- Raising or lowering the TOC's Gargul dependency, or adding a version-number check.
- Re-implementing a missing Gargul feature (for example, no own roll table or own exporter).
- Changes to the workbook.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Full v8.0.1 | all APIs present | all features on, no warning line | No error expected |
| No Exporter hook | `transformEntriesToCustomFormat` missing | export fill off; other features on | one chat line names it |
| No award events | `GL.Events` missing | award tracking and chat line off | one chat line |
| No Importer | `Interface.Importer.open` missing | import button off; `/preloot import` opens the paste dialog instead | one chat line |
| No roll table | `MasterLooterUI.tableColumns` or `RollOff.refreshRollsTable` missing | columns off | one chat line |
| Base64 variants | `decode`, `Decode` or neither | snapshot decodes in all three | No error expected |
| No `formatPlayerName` | award to "Alya-Realm" | winner key "Alya" | No error expected |
| itemID missing on CurrentRollOff | only `itemLink` set | Impact uses the ID parsed from the link | No error expected |
| No `GL:sendChatMessage` | confirm a BIS award | `SendChatMessage` to RAID or PARTY | No error expected |
| Error in an addon wrapper | e.g. snapshot index throws during refresh | Gargul's roll table still refreshes; addon cells skipped | error printed once |
| Gargul missing | no `_G.Gargul` | addon disabled | one chat line |

</frozen-after-approval>

## Code Map

- `Core.lua` -- `init` requires every module (L9) and installs everything. Becomes: per-feature install with `Compat` checks, plus a summary line.
- `Snapshot.lua` `decodeText` -- calls `GL.Base64.decode` through `pcall`. Swap to `Compat.base64Decode`; the JSON decode stays `GL.JSON:decode` (needed by the import feature).
- `Awards.lua` `winnerKey` -- `GL:formatPlayerName`. Swap to `Compat.winnerKey`. `install` registers 3 events: guard them and register only the events that exist.
- `Columns.lua` -- `install` wraps `tableColumns`/`refreshRollsTable`; `refresh` and `widenWindow` call `Interface:get`. Use `Compat.rolledItemID`, and `pcall` the cell append.
- `Import.lua` `install` -- wraps `Importer.open`. Add a fallback slash command `/preloot import`.
- `Export.lua` `install` -- wraps `transformEntriesToCustomFormat`. Guard it and `pcall` the fill (on error, return Gargul's text unchanged).
- `Chat.lua` `announce` -- `GL.Settings:get` / `GL:sendChatMessage`. Use `Compat.announcementsEnabled` / `Compat.sendChat`.
- `Picker.lua` `install` -- the slash command; extend it with an `import` argument.
- The deleted 5.1 legacy decoder (commit f2d92b2 `GP:base64decode`) is the model for the bundled decoder.
- `tests/addon/run.lua` -- stubbed-GL harness to extend: one stub per matrix row.

## Tasks & Acceptance

**Execution:**
- [ ] `Compat.lua` (new): `base64Decode`, `winnerKey`, `rolledItemID`, `announcementsEnabled`, `sendChat`, `has(path)` and `safeCall(label, fn, ...)` (prints the first error per label). Load it first in the TOC.
- [ ] `Core.lua`: per-feature checks and installs, plus one French summary line when something is off.
- [ ] `Snapshot.lua`, `Awards.lua`, `Columns.lua`, `Import.lua`, `Export.lua`, `Chat.lua`, `Picker.lua`: use Compat and guard each hook and wrapper.
- [ ] `tests/addon/run.lua`: every matrix row.

**Acceptance Criteria:**
- Given the repo, when `luajit tests/addon/run.lua` runs, then it prints PASS and exits 0.
- Given Gargul v8.0.1 in game, when the addon loads, then no warning line appears and behaviour is unchanged.

## Implementation Notes

- Implemented directly.
- `Compat.lua` holds the detection and fallbacks. `GP.installFeatures(GL)` (Core) installs each feature whose APIs exist and returns the list of features left off. `init` prints that list once.
- Wrappers pass `...` through and return Gargul's results.
- The payload generator now loads Compat too.
- 361 assertions pass.

## Plan Change Log

## Review Triage Log

Pass 1 (quick): high 0, medium 2, low 5, false 0, maybe-false 0.

| Finding | Verdict | Route | Evidence / action |
|---|---|---|---|
| Import still reached `GL.JSON.decode` (evaluated outside `pcall`) when JSON is missing | medium | patch | `Snapshot.parse` now refuses with a French reason when `JSON.decode` is absent. Test added. |
| Importer button could stack on Gargul's reused window after a partial failure | medium | patch | `_importButtonAdded` is set before the guarded block. |
| Award events are registered without checking they exist | low | reject | It cannot be detected at runtime: Gargul's `Events:register` accepts any `GL.*` name, and events are strings, not functions. Documented as a known limit in the summary to the owner; the v8.0.1 source scan covers the functions. |
| Bundled Base64 decoder accepted padding mid-text and `x=y` | low | patch | Strict padding checks added; two tests. |
| Matrix rows only partly covered | low | patch | Added: missing `tableColumns`; Impact through the wrapper using the link-parsed ID; chat via `SendChatMessage` through `Chat.announce`; award winner without `formatPlayerName`; other features kept without events; `init` prints exactly one summary line; a scan of the real Gargul v8.0.1 source for every API a feature needs. |
| `/preloot` test weakened | low | patch | Asserts that a plain `/preloot` opens the list. |
| Test leaked global stubs and could leave `print` swallowed | low | patch | The block runs in `pcall`; `print` and globals are restored after it. |

383 assertions pass.

## Verification

**Commands:**
- `luajit tests/addon/run.lua` (from C:/Repos/Gargul_Preloot) -- expected: `PASS: <n> assertions`, exit 0.
