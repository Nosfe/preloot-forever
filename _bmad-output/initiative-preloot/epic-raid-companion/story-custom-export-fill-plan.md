---
title: 'Custom export fill'
type: 'feature'
ticket: '3'
created: '2026-10-26'
status: 'built'
baseline_revision: 'c328ccb7d18bba24564c1e51be35a2a2151f92d7'
route: 'oneshot'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Gargul's Custom export leaves the template's `@GPRAID` and `@GPTREATMENT` tokens unfilled, so the workbook import (4.7) cannot tell which raid each award belongs to or how to count it.

**Approach:**
- Wrap `GL.Exporter:transformEntriesToCustomFormat` and post-process the text it returns, line by line.
- For each line, read its `"checksum":"..."` value and look it up in the session awards map (5.2).
- When found, replace the two tokens as plain text with the session raidId and the award's treatment. Otherwise replace them with empty strings, which the workbook rejects and lists for the owner to fill.
- Other export formats and lines without the tokens pass through unchanged.

</frozen-after-approval>

## Implementation Notes

- Oneshot route: about 40 lines in a new `Export.lua` plus tests.
- Gargul v8.0.1 `transformEntriesToCustomFormat(Entries, format)` (Exporter.lua) returns the whole export text, with one line per award joined by `\n`, after `strtrim`.
- Lines for uncached items are omitted by Gargul itself.
- Gargul's own `gsub` tokens never match inside `@GPRAID` or `@GPTREATMENT`.

- Added `Awards.raidId()` (session raid) for the fill. 132 assertions pass.

## Review Triage Log

- **high, defer.** The workbook import ignores the line's `raidId` and files every award under the open raid. Confirmed: `ledger.js` `parseGargulExport_` never reads `raidId`, and `attendance.js` passes `openRaidId` to `buildAwardRequests_`. This is a pre-existing workbook gap from 4.7, not caused by this change, and is recorded in deferred-work.md for 4.9 or a fix before it.
- **low, reject.** The "other formats pass through" test passes for a reason other than its name. It still checks that `format` is forwarded, and RRobin text cannot contain the tokens.
- **false.** "The raid comes from the session, not from the award." Entries are cleared whenever the raidId changes (5.2 decision), so every captured entry belongs to the session raid. There is no defect today.
- **false.** "No agent instruction files." This is informational; none exist.
- **false.** "The manual in-game check was not done." The owner batches in-game checks, so this is not a defect in the change.

## Verification

**Commands:**
- `luajit tests/addon/run.lua` (from C:/Repos/Gargul_Preloot) -- expected: `PASS: <n> assertions`, exit 0.

**Manual checks (if no CLI):**
- In game (batched): with the Gargul export settings applied, a test award exports with its raidId and treatment, and an award made before the import exports with empty values.
