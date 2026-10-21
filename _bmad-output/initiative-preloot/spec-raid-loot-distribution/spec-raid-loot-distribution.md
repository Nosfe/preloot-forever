---
id: SPEC-raid-loot-distribution
companions:
  - allocation-rules.md
  - raid-workflow.md
  - brownfield.md
  - ../architecture-raid-loot-distribution/architecture-raid-loot-distribution.md
sources:
  - ../prd-raid-loot-distribution/prd-raid-loot-distribution.md
  - ../prd-raid-loot-distribution/addendum.md
---

# Guild Loot Distribution

## Why

The guild owner needs a consistent, inspectable way to maintain loot priorities and distribute raid loot for one roster across WoW tiers. Raiders need to understand roster state and the basis for awards. The product combines shared Sheets data with an owner-only Gargul enhancement while keeping the award decision manual.

## Capabilities

- **CAP-1 — Maintain roster and phase data**
  - **intent:** The owner maintains one roster and configures phase-specific BiS, Impact, parse, gain, and item-status data.
  - **success:** The roster persists across tiers, one tier is active at a time, and the owner can configure all required inputs for that tier.
- **CAP-2 — Process attendance**
  - **intent:** The owner updates raid attendance from Warcraft Logs and enters bench appearances manually.
  - **success:** Matched attendance and bench records produce separate BiS-window and whole-tier Presence values; unmatched players are ignored and can be corrected manually. Attendance requires presence for more than 25% of a raid's boss fights; Rerolls alts credit their main's attendance.
- **CAP-3 — Prioritize BiS awards**
  - **intent:** The owner uses BiS eligibility and BiS Ratio to guide BiS awards.
  - **success:** Any rolling BiS-eligible Raider outranks non-BiS rollers; eligible Raiders rank by BiS Ratio, with exact ties resolved manually using Gargul's roll value.
- **CAP-4 — Explain Impact priority**
  - **intent:** The owner and raiders inspect Impact Item priority and its score rationale.
  - **success:** Impact Score reflects whole-tier Presence, DPS Warcraft Logs average parse, the Raider's configured simulated percent DPS/HPS gain, and Impact Item Count; missing parse is `1`, tanks use tank priority, and identical complete scores resolve by roll.
- **CAP-5 — Publish raider-facing data**
  - **intent:** The owner shares roster, Impact priority, and per-spec item status through Google Sheets.
  - **success:** Raiders can view all three tabs, including ratios, score details, BiS/alt-BiS/Impact status, and simmed gains, but cannot edit them.
- **CAP-6 — Support manual Gargul awards**
  - **intent:** The owner uses Gargul roll information, BiS Ratios, and Impact Scores to make manual awards.
  - **success:** Each roller's existing BiS Ratio and (non-tanks) Impact Score show during rolls and update before the next roll; each award records the owner's BIS, IMPACT, or NONE choice, where IMPACT changes Impact state only; the addon never classifies items or awards loot.
- **CAP-7 — Synchronize Sheets and Gargul**
  - **intent:** The owner transfers roster state to Gargul before a raid and award results back to Sheets afterward.
  - **success:** A valid pre-raid snapshot loads the correct Raider state; the post-raid Gargul Custom export, tagged with the raid and each award's treatment, updates the correct roster counts; malformed imports leave existing data unchanged.
- **CAP-8 — Manage tier transitions**
  - **intent:** The owner archives completed tiers, triggers the BiS-window reset, and configures Impact Item Count carryover.
  - **success:** Archives are read-only and non-restorable; once three weeks into a new tier the owner triggers the BiS reset between raids, restarting BiS attendance and BiS-loot count while whole-tier Impact attendance remains.

## Constraints

- One persistent roster spans WoW tiers and eras; one tier is active at a time. MVP uses currently available data; no complete future item catalog is required.
- The owner alone edits Sheets and uses the enhanced Gargul interface. Raiders have view-only Sheets access and install no addon.
- Gargul displays roll type/value, BiS Ratio, and Impact Score but does not know item type, choose which signal applies, or assign loot. The owner consults Sheets and decides.
- BiS Ratio uses post-reset attendance; Impact Score uses attendance across the whole active tier. Presence Max initializes to `1` when a window has no possible raids.
- The owner imports each raid once and manually corrects JSON. Malformed JSON is rejected without changing existing data; duplicate-upload detection is not required.
- Raiders are identified by their exact, unique roster character name, without case-folding; awards to Rerolls alts are rejected for owner correction.
- Off-spec, disenchanted, and pattern/design awards never change loot counts.
- Sheet values affecting scores stay fixed while a raid snapshot is open.
- Warcraft Logs credentials stay in the owner's Apps Script User Properties, never in the shared workbook.
- First target: WoW Forever with Gargul v8.0.1, evolving the owner's existing Gargul_Preloot addon and Apps Script (see `brownfield.md`).

## Non-goals

- Multiple guilds or rosters.
- Automatic loot assignment or addon item classification.
- Automated BiS-list or Warcraft Logs parse ingestion.
- Tank Impact Scores.
- A hosted custom service or standalone desktop GUI in the MVP.

## Success signal

In a raid, the owner loads current Sheets data into Gargul, uses the displayed roll, ratio, and score alongside the Sheet's item classification to award loot manually, and sees state changes before the next roll. One post-raid import updates the correct roster and scores; malformed data changes nothing; raiders can inspect the published views.

## Assumptions

- “Guild Loot Distribution” is a working title; the product name is not confirmed.
- Each Raider has an assigned role and class/spec used for eligibility and display.
- Warcraft Logs raid links expose an identity value matchable to most roster members.
- Gargul v8.0.1 fully supports WoW Forever.
- The product works with partially populated tier data; the owner enters first-tier class/spec, item, BiS, and simulation data in Sheets once it is available.

## Open Questions

- None.