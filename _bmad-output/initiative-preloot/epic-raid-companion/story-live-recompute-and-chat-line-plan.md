---
title: 'Live recompute and chat line'
type: 'feature'
ticket: '6'
created: '2026-10-26'
status: 'built'
baseline_revision: '905194c'
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

**Problem:** Ratio BiS and Impact stay at their snapshot values all night, so after an award the next roll still shows the winner's old priority. The French chat line telling the winner their new value is also gone since 5.1.

**Approach:**
- Derive each raider's live counts from the snapshot plus the session awards: BIS adds 1 BiS loot, IMPACT adds 1 Impact loot, NORMAL and CLASS_BOUND add nothing.
- Both columns read the live values. The roll table refreshes after every award change: record, edit, delete, treatment change, or a cleared session.
- Decision (owner, 2026-10-26): when the owner confirms an award's treatment in the popup (a button, or closing it), the addon sends its own French chat line:
  - BIS: the winner's new BiS Ratio;
  - IMPACT: the winner's new Impact Score for the awarded item;
  - nothing for NORMAL or CLASS_BOUND, or when the score cannot be computed (tank, unknown winner, or an item with no IMPACT Statut for the winner's spec).

## Boundaries & Constraints

**Always:**
- Live values come from the snapshot operands plus counted session awards, with no other state, and are recomputed on every read.
- Snapshot values themselves are never mutated.
- Chat goes through `GL:sendChatMessage(message, "GROUP")`, and only when Gargul's `AwardingLoot.awardMessagesEnabled` setting is on.
- A popup closed by the addon itself (deleted award, edit reopening it) sends nothing.

**Never:**
- Presence changes during the raid; the workbook credits presence after the raid.
- Chat when the treatment is changed in the `/preloot` list.
- Changes to Gargul or the workbook.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| BIS award | Alya (4/8, 1 BiS loot) gets BIS | live Ratio BiS 0.5/3 = 0.167; chat "Alya : nouveau ratio BiS 0.167" | No error expected |
| IMPACT award | Alya (4/8, parse 1, 2 Impact loots) gets item 888 (gain 0.5) as IMPACT | live Impact base 0.5/4 = 0.125; Impact for 888 0.0625; chat "Alya : nouveau score Impact 0.063 pour [888]" | No error expected |
| Sequence | BIS then IMPACT to Alya, then NORMAL to Beryl | each column matches hand-computed values after each step; Beryl unchanged | No error expected |
| Treatment change | BIS changed to NORMAL | live counts drop back; table refreshed | No error expected |
| Delete / bulk clear / new raid | award removed | live counts drop back; table refreshed | No error expected |
| NORMAL / CLASS_BOUND confirm | popup confirmed | no chat line | No error expected |
| IMPACT not computable | tank or no IMPACT Statut for the spec | no chat line | No error expected |
| Announcements disabled | Gargul setting off | no chat line | No error expected |
| Programmatic close | award deleted or edited while its popup is open | no chat line for that close | No error expected |

</frozen-after-approval>

## Code Map

- `C:/Repos/Gargul_Preloot/Awards.lua`:
  - Session entries keep `winner` (exact raider key) and `treatment`.
  - Add `liveRaider(raiderKey)`: a copy of the snapshot raider with session BIS and IMPACT counts added.
  - Changes from the events, `setTreatment`, `remove`, `reconcile` and `clear` call a refresh hook.
- `C:/Repos/Gargul_Preloot/Columns.lua`:
  - `bisCellText` and `impactCellText` read `GP.Snapshot.raider`; switch them to `GP.Awards.liveRaider`.
  - Add `Columns.refresh()`, which calls `GL.RollOff:refreshRollsTable()` using the GL stored at install.
- `C:/Repos/Gargul_Preloot/Picker.lua`:
  - Popup buttons call `setTreatment` then `popup:Hide()`; `OnClose` runs `showNext`.
  - Programmatic hides happen in `enqueue` (same checksum) and in `refresh` (entry gone).
  - Add a confirm-on-close flag that both programmatic paths clear, and a `Chat.announce(entry)` call.
- `C:/Repos/Gargul_Preloot/Scores.lua`: reuse `bisRatio`, `impactBase` and `impactScore`.
- `C:/Repos/Gargul/Classes/AwardedLoot.lua` L626-L640: Gargul's own announcement uses `GL.Settings:get("AwardingLoot.awardMessagesEnabled")` and `GL:sendChatMessage`.
- `C:/Repos/Gargul_Preloot/tests/addon/run.lua`: the AceGUI stub, the Awards and Picker stubs, and the sample snapshot (Alya 4/8, 1 BiS, 2 Impact, parse 1; item 888 has Mage Givre IMPACT 0.5).

## Tasks & Acceptance

**Execution:**
- [ ] `Awards.lua`:
  - Add `liveRaider(raiderKey)`.
  - Add `Awards.onChange` (a callback set by Core) invoked after every mutation.
- [ ] `Columns.lua`:
  - Live raider in both cells.
  - `Columns.refresh()`, guarded when no roll table exists.
- [ ] `Chat.lua` (new): `Chat.message(entry)`, a pure function returning the French line or nil; `Chat.announce(entry, GL)` checks the setting and sends.
- [ ] `Picker.lua`: confirm-on-close (button or user close) calls `GP.Chat.announce`; programmatic closes do not.
- [ ] `Core.lua` and `Gargul_Preloot.toc`: add Chat.lua and wire `Awards.onChange = Columns.refresh`.
- [ ] `tests/addon/run.lua`:
  - The matrix rows, with hand-computed values.
  - A stub `GL:sendChatMessage` recording messages, and a stub `GL.Settings:get`.

**Acceptance Criteria:**
- Given the repo, when `luajit tests/addon/run.lua` runs, then it prints PASS and exits 0.
- Given two awards in a row in game, when each popup is confirmed, then the columns update before the next roll and the chat shows the new value for BIS and IMPACT only.

## Implementation Notes

- Implemented directly. `Picker.install(GL)` now takes GL, which the chat line needs.
- `Awards.liveRaider` copies the snapshot raider and adds session BIS/IMPACT counts. `Awards.onChange` fires only on real changes: `remove` of an unknown checksum, `reconcile` with nothing removed and an empty `clear` stay silent.
- One 5.5 test block now clears the session first: leftover awards from earlier blocks correctly changed the live values.
- 319 assertions pass.

## Plan Change Log

## Review Triage Log

Pass 1 (quick): high 0, medium 2, low 4, false 0, maybe-false 0, rejected 1.

| Finding | Verdict | Route | Evidence / action |
|---|---|---|---|
| A UI hide (Alt+Z, cinematic) fires the AceGUI Frame's OnHide, so OnClose counted it as a confirmation and sent chat | medium | patch | Confirmed in AceGUIContainer-Frame (`OnHide` → `Frame_OnClose`). Only a treatment button or the Frame's Close button (found by its `CLOSE` text, OnClick wrapped and restored before release, because AceGUI pools frames) now confirms. Test added. |
| `closeSilently` relied on OnHide firing; on an invisible frame the popup slot and the flag stayed stuck | medium | patch | `closeSilently` now finishes the popup itself when OnClose did not run. Test with an invisible frame added. |
| `%.3f` of an exact tie (0.0625) may round to even in WoW's C library, unlike the matrix's 0.063 | low | patch | A shared `Scores.format` rounds halves away from zero before formatting (it also avoids -0.000). Columns and Chat use it; the test asserts the literal "0.063". |
| Tank test never reached the tank check (item 888 has no Druide spec) | low | patch | The test now uses an added item 555 with an IMPACT Statut for Cairn's spec. |
| Bulk clear, the edit path and the Beryl Impact cell were not covered | low | patch | Tests added (reconcile, `Awards.edit` with a winner change and with the same winner, Beryl cell 12). |
| `onChange` fired when nothing changed (edit with the same winner, same treatment set again) | low | patch | Both now return without change. An edit that keeps the winner also returns nil (no popup) and keeps the owner's pick. |
| Other officers running the addon could also announce | low | reject | AD-5: only the owner uses the companion; raiders and officers install nothing. |

333 assertions pass.

## Verification

**Commands:**
- `luajit tests/addon/run.lua` (from C:/Repos/Gargul_Preloot) -- expected: `PASS: <n> assertions`, exit 0.

**Manual checks (if no CLI):**
- In game (batched): two awards in a row; the columns update before the next roll, and the chat line appears on confirm for BIS and IMPACT only.
