---
title: 'Treatment per award'
type: 'feature'
ticket: '2'
created: '2026-10-26'
status: 'built'
baseline_revision: '8d8567207cd3485f0c4d41ec91fb9b03d2118724'
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

**Problem:** The workbook import (4.7) needs each award's treatment (BIS, IMPACT, CLASS_BOUND, NORMAL), but the addon records nothing about awards since 5.1 removed the legacy award hook.

**Approach:** Listen to Gargul's award events and keep a session-only map, checksum → {itemID, winner, treatment}. Each new award gets a treatment prefilled from the winner's spec Statut for that item in the snapshot, and the owner can change it in a small picker. Edits re-derive the entry for the new winner, and deletions remove it.

## Boundaries & Constraints

**Always:**
- Key entries by Gargul's award checksum, never by position or item ID.
- Winner key = `GL:formatPlayerName(awardedTo, { includeRealm = "never" })`, the same value Gargul exports as `@WINNER`. Match it exactly against snapshot raider keys.
- Record only while a snapshot is imported (AD-6: the import starts the session). Nothing goes into SavedVariables.
- Prefill = the snapshot Statut for (itemID, the winner's classSpec), and NORMAL when there is no entry, the winner is unknown, or the award is off-spec.
- The prefill is a suggestion. The owner's pick always wins, and the addon never awards or blocks an award.
- Decision (owner, 2026-10-26), picker form:
  - One small popup per award (item, winner, four buttons BIS / IMPACT / CLASS_BOUND / NORMAL, prefill highlighted). Closing it keeps the current treatment.
  - Awards that arrive while it is open queue and show one after another.
  - Edits reopen it for that award.
  - A list window (`/preloot`) shows every session award with its treatment, for later changes.
- Decision (owner, 2026-10-26): a re-import with the same raidId keeps the recorded treatments; a different raidId clears them.

**Never:**
- The `@GPRAID`/`@GPTREATMENT` export fill (5.3).
- Score recompute after awards and the chat line (5.6).
- Impact column (5.5).
- Changes to Gargul or the workbook.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Award, IMPACT spec | snapshot loaded; item 888 to Alya (Mage Givre → IMPACT) | entry {888, Alya, IMPACT}; picker shows it | No error expected |
| Award, no item entry | item absent from snapshot items | treatment NORMAL | No error expected |
| Award, OS | AwardEntry.OS = true | treatment NORMAL | No error expected |
| Award, unknown winner | winner not in snapshot | treatment NORMAL | No error expected |
| Award, disenchant | awardedTo = `\|\|de\|\|` | not recorded | No error expected |
| No snapshot | award before any import | not recorded | No error expected |
| Owner changes treatment | picker sets BIS on entry | entry treatment BIS | No error expected |
| Edit winner | ITEM_AWARD_EDITED, new awardedTo | winner updated, treatment re-prefilled for new winner | No error expected |
| Delete | ITEM_UNAWARDED with entry | entry removed | No error expected |
| Bulk clear | ITEM_UNAWARDED with no payload | entries whose checksum left `GL.DB.AwardHistory` removed | No error expected |
| Edit/delete unknown checksum | checksum not in map | map unchanged | No error expected |

</frozen-after-approval>

## Code Map

- `C:/Repos/Gargul/Classes/AwardedLoot.lua`:
  - `addWinner` (L439) fires `GL.ITEM_AWARDED` with the AwardEntry (L727). Remote awards also fire it (L1300).
  - Entry fields: `checksum`, `itemID`, `itemLink`, `awardedTo` (FQN), `OS`.
  - `editWinner` (L317) changes only `awardedTo` and fires `GL.ITEM_AWARD_EDITED` (L423).
  - `deleteWinner` (L273) fires `GL.ITEM_UNAWARDED` with the entry (L304).
- `C:/Repos/Gargul/Classes/Exporter.lua` and `Interface/Award/Overview.lua`:
  - Exporter (L155, L186) and Overview (L294, L312, L327) fire `GL.ITEM_UNAWARDED` with no payload after clearing `GL.DB.AwardHistory`.
  - `@WINNER` is `GL:formatPlayerName(awardedTo, { includeRealm = "never" })` (L327).
  - The disenchant winner is `GL.Exporter.disenchantedItemIdentifier` (`"||de||"`).
- `C:/Repos/Gargul/Classes/Events.lua`: `GL.Events:register(identifier, event, callback(event, payload))`.
- `C:/Repos/Gargul_Preloot/Snapshot.lua`:
  - `set`/`raider`/`get` exist.
  - Add an items index and `statut(itemID, classSpec)`.
  - `Import.apply` calls `set`, so the raidId check for clearing awards hooks in there.
- `C:/Repos/Gargul_Preloot/Core.lua`: `init` installs the modules; add Awards and Picker.
- `C:/Repos/Gargul_Preloot/tests/addon/run.lua`: the existing runner and stubs to extend.

## Tasks & Acceptance

**Execution:**
- [ ] `Snapshot.lua`:
  - Index `items` by itemID, then by classSpec.
  - Add `Snapshot.statut(itemID, classSpec)`, which returns nil when absent.
- [ ] `Awards.lua` (new, pure):
  - Functions: `defaultTreatment(itemID, raiderKey, isOS)`, `record(AwardEntry, GL)`, `setTreatment(checksum, treatment)`, `edit(AwardEntry, GL)`, `remove(checksum)`, `reconcile(history)`, `get(checksum)`, `list()` (newest first), `clear()`.
  - `onSnapshotImported(raidId)` clears the map when the raid changes.
  - `install(GL)` registers the three events and calls `GP.Picker.enqueue(checksum)` after a record or an edit.
- [ ] `Picker.lua` (new, UI):
  - Per-award popup with a queue, using AceGUI Frame and four Buttons; the current treatment is marked in the title or status.
  - `/preloot` list window: AceGUI ScrollFrame, one row per `Awards.list()` entry with a treatment Dropdown.
  - API: `Picker.enqueue(checksum)` and `Picker.openList()`.
- [ ] `Import.lua`: call `GP.Awards.onSnapshotImported(raidId)` before `Snapshot.set`, using the previous raidId.
- [ ] `Core.lua`: install Awards and Picker.
- [ ] `Gargul_Preloot.toc`: add `Awards.lua` and `Picker.lua` before `Core.lua`.
- [ ] `tests/addon/run.lua`: cover every matrix row, plus event wiring through a stub `GL.Events`.

**Acceptance Criteria:**
- Given the repo, when `luajit tests/addon/run.lua` runs, then it prints PASS and exits 0.
- Given an imported snapshot in game, when the owner awards, edits and deletes an award, then the picker shows the right treatments and the deleted award disappears.

## Implementation Notes

- Implemented directly.
- `GL.ITEM_AWARDED` also fires for awards received from other officers (AwardedLoot L1300). They are recorded too, because the owner's export includes them.
- Tests add a minimal AceGUI stub, whose `Hide` fires OnClose. The popup queue, the closing behaviour, the list dropdown and the refresh after a delete are now covered offline.
- Only the real in-game layout stays unverified.

## Plan Change Log

## Review Triage Log

Pass 1 (quick): high 0, medium 2, low 4, false 0, maybe-false 0.

| Finding | Verdict | Route | Evidence / action |
|---|---|---|---|
| Disenchant awards edited to a raider never get a treatment; awards edited to disenchant stay recorded | medium | patch | Confirmed: Overview Edit calls `editWinner` on any row. Fixed: disenchant checksums are remembered, so an edit to a raider records that award and an edit to disenchant drops it. Edits of other unknown checksums still change nothing (matrix row kept). Tests added. |
| Remote awards show "item <id>": Gargul fills `itemLink` later, on the same table | medium | patch | Confirmed at AwardedLoot `storeReceivedAward` (L1237). Fixed: the entry keeps a reference to Gargul's AwardEntry, and `Awards.itemLink` reads it when displayed. Test added. |
| A repeated `ITEM_AWARDED` for the same checksum overwrites the owner's pick | low | patch | `receiveAwardedItem` does not dedupe. Fixed with a direct guard (an existing checksum is ignored). Test added. |
| Editing an award already queued leaves the open list stale | low | patch | Confirmed: the duplicate branch returned before the refresh. Fixed: refresh is called in that branch and after every edit event. |
| A different-raidId import leaves an open popup or list showing cleared awards | low | patch | Confirmed. Fixed: `Import.apply` calls `Picker.refresh()` after `set`. |
| A list dropdown change leaves the open popup's marker and status stale | low | reject | Cosmetic. Closing the popup keeps the new value, so the stored treatment is right. It would only happen with both windows open on the same award, and the fix needs extra popup re-render logic. |
| Tests miss the cases above | low | patch | Tests were added with the fixes; 113 assertions pass. |

## Design Notes

Awards.lua stays free of UI, so the picker can be stubbed in tests. Prefill example: snapshot item 888 has `{classSpec = "Mage Givre", statut = "IMPACT"}`. Alya's classSpec is Mage Givre, so her award prefills IMPACT. Beryl (Prêtre Sacré) has no entry for 888, so hers prefills NORMAL.

## Verification

**Commands:**
- `luajit tests/addon/run.lua` (from C:/Repos/Gargul_Preloot) -- expected: `PASS: <n> assertions`, exit 0.

**Manual checks (if no CLI):**
- In game (batched with 5.1's checks): import a snapshot, award an item, change its treatment, edit the winner, delete it. The picker reflects each step.
