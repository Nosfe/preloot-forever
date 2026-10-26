---
title: 'Gargul import: accept only the open raid ID'
type: 'bugfix'
ticket: ''
created: '2026-10-26'
status: 'built'
baseline_revision: '7e9bc9f'
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

**Problem:** End raid's Gargul import never reads a line's `raidId`. It files every award under Config's open raid, so awards from an earlier raid in the same export land in the wrong raid. AD-6 says Sheets rejects any raidId other than the single open raid.

**Approach:**
- The parser keeps each line's `raidId`.
- A new check, run in both the preview and the submit, moves to the rejected list every line whose `raidId` is not exactly Config's open raid. That includes an empty value and the literal `@GPRAID`.
- Each rejection gets a reason that tells the owner to type the open raid ID or delete the line. Rejected lines are listed as today and never written.
- Decision (owner, 2026-10-26): strict, as in AD-6.

</frozen-after-approval>

## Implementation Notes

- Oneshot route: the check is about 25 lines in ledger.js, plus two call sites in attendance.js and test updates.
- The shared fixture `custom-export-sample.txt` now carries `"raidId":"5"`, as the companion fills it. The raid tests open raid 5.
- Uploaded with `clasp push --force` on 2026-10-26.

## Review Triage Log

- **low, patch.** The preview had no open-raid guard: with an empty Config value, lines without a raidId would pass. Fixed: the preview now refuses with "Raid > Démarrer first." like the submit. Test added.
- **low, patch.** The preview read Config without `requireCurrentLayout_`. Fixed.
- **low, reject.** The raidId is trimmed, so " 5 " matches 5. This is harmless: raid IDs are workbook integers and the companion writes them exactly. Only names need AD-3's exact match.
- **low, patch.** A literal `@GPRAID` was reported as "empty". The wording is now "raidId is not filled" for an empty value or the token.
- **low, patch.** Tests missed the no-raid preview case. Added; story-4-7 passes (59 assertions) and story-4-4 passes (81).

## Verification

**Commands:**
- Headless Edge test pages story-4-4 and story-4-7 (plus 4-1, 4-2, 4-3, 4-6, 4-8 as regression) -- expected: PASS each.
- `luajit tests/addon/run.lua` -- expected: PASS (it reads the fixture's first line).
