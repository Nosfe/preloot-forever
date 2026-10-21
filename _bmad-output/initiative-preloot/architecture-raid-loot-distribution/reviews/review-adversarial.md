# Adversarial Review: Guild Loot Distribution Architecture Spine

**Verdict:** FAST-FIX
**Confidence:** 0.89
**Target:** [architecture-raid-loot-distribution.md](../architecture-raid-loot-distribution.md)
**Scope:** Current spine after Interchange v1 and numeric-domain edits, compared with prior M-01 through M-06 and m-01. Two independently built units may obey the written contract but disagree at their boundary. The spine was not edited.

## Critical

None.

## Major

### M-07 - Snapshot scores can disagree with their required operands

**Location:** AD-2, AD-6, Interchange v1 (pre-raid row).

**Independent pair:** A Sheets exporter includes valid operands plus an older, nonnegative `bisRatio` or `impactScore` after an owner input change (or the owner hand-edits a score in the JSON). The addon imports the envelope because every field passes the stated type/domain checks, and displays the supplied score on the first roll. Another addon implementation recomputes it from the same required operands on import, as AD-6 requires after award changes. Both follow the current interchange contract, but show different priorities for the same raid snapshot.

**Consequence:** The displayed priority can differ from the canonical Sheet formula before any award event; a valid-looking edited snapshot can silently alter the first award decision.

**Fix:** Make the operands authoritative on snapshot import: recompute BiS Ratio and Impact Score from them before the first roll, and reject an envelope whose supplied derived values do not agree with the recomputation under a specified numeric comparison rule. Apply the same rule after ledger changes; alternatively omit derived score fields from Interchange v1 and always recompute them from operands.

## Minor

None remaining from the prior report.

## Prior Findings Rechecked

| Finding | Current disposition | Evidence in the spine |
| --- | --- | --- |
| M-01 | Closed | AD-1 refuses tier activation with open raids; AD-6 creates/reuses the raid ID and closes it only on atomic ledger commit. |
| M-02 | Closed | Interchange v1 requires `role` and nullable `tankPriority`; tank `impactScore` is null and AD-2 suppresses tank Impact display. |
| M-03 | Closed | Interchange v1 defines `dpsParse` as percentage points, range `1` to `100`, with missing input exported as `1`; Gain is a fraction and AD-2 forbids Lua conversion. |
| M-04 | Closed | AD-7 defines one scheduled `raidId` per possible-raid increment, merges overlapping reports, and caps attendance and bench credit at one per Raider and raid. |
| M-05 | Closed | AD-3 requires exact `raiderKey` equality with realm-stripped `awardedTo`; both fields must be edited to correct a recipient. |
| M-06 | Closed | Interchange v1 binds versioned field names, types, context, required operands, derived scores, and post-raid award fields. Native Gargul shape remains subject to the pinned fixture gate. |
| m-01 | Closed | Interchange v1 rejects invalid types, non-finite and negative numeric inputs, impossible Presence, invalid role/priority combinations, and nonpositive maxima before changing state. |

## Pre-implementation Gates

The Deferred section explicitly gates companion implementation on a pinned Gargul `v8.0.1-forever` native export fixture and prototype proof of new-award capture, per-roller display, roll fields, checksum correlation, edit/delete handling, and raid-only export hooks. It also requires first-tier class/spec, item, BiS, and simulation data confirmation before workbook population. These are gates to satisfy before implementation, not additional architecture findings. Do not interpret this review verdict as evidence that the gates have passed.

## Verification Scope

This is a contract review, not an executed Gargul prototype or workbook test. No critical finding remains; M-07 is the one material cross-unit ambiguity preventing a clean pass.
