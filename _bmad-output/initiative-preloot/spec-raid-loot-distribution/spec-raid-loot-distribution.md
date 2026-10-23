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
  - **intent:** The owner maintains one roster and configures phase data: each Raider's class, spec, role and parse, and, per item, one Statut and Gain (%) for each spec, grouped by role.
  - **success:** The roster persists across tiers, one tier is active at a time, and the owner can configure all required inputs for that tier.
- **CAP-2 — Process attendance**
  - **intent:** The owner updates raid attendance from Warcraft Logs and enters bench appearances manually.
  - **success:** Matched attendance and bench (B) produce Tier Presence (since the tier start); unmatched players are ignored and can be corrected manually. Attendance requires presence for more than 25% of a raid's boss fights by that exact Roster character.
- **CAP-3 — Prioritize BiS awards**
  - **intent:** The owner uses BiS eligibility and BiS Ratio to guide BiS awards.
  - **success:** Any rolling BiS-eligible Raider outranks non-BiS rollers; eligible Raiders rank by BiS Ratio, with exact ties resolved manually using Gargul's roll value.
- **CAP-4 — Explain Impact priority**
  - **intent:** The owner and raiders inspect Impact Item priority and its score rationale.
  - **success:** Impact Score = Tier Presence × parse × the dropped item's gain for the roller's spec / (Impact Items since the tier start + 1), only for an item whose Statut for that spec is IMPACT. Roster shows the score without the item gain. Missing parse is `1`, tanks have no Impact Score, and identical complete scores resolve by roll.
- **CAP-5 — Publish raider-facing data**
  - **intent:** The owner shares roster, Impact priority, and per-spec item status through Google Sheets.
  - **success:** Raiders can view all three tabs, including ratios, score details, BiS/alt-BiS/Impact status, and simmed gains, but cannot edit them.
- **CAP-6 — Support manual Gargul awards**
  - **intent:** The owner uses Gargul roll information, BiS Ratios, and Impact Scores to make manual awards.
  - **success:** Each roller's BiS Ratio shows during rolls and, when the dropped item's Statut for the roller's spec is IMPACT, their full Impact Score (non-tanks); values update before the next roll. Each award records the owner's BIS, IMPACT, or NONE choice, where IMPACT changes Impact state only. The addon reads the owner's Statut and gain but never classifies items, chooses, or awards loot: the owner decides every award, even against the displayed values.
- **CAP-7 — Synchronize Sheets and Gargul**
  - **intent:** The owner transfers roster state to Gargul before a raid and award results back to Sheets afterward.
  - **success:** A valid pre-raid snapshot loads the correct Raider state; the post-raid Gargul Custom export, tagged with the raid and each award's treatment, updates the correct roster counts; malformed imports leave existing data unchanged.
- **CAP-8 — Manage tier transitions**
  - **intent:** The owner archives completed tiers, activates the next one (which resets BiS), and configures Impact Item Count carryover.
  - **success:** Archives are read-only and non-restorable. Activating a new tier, between raids, is the BiS reset: Tier Presence, the BiS-loot count and the Impact-loot count restart. There is no BiS reset inside a tier (owner decision 2026-10-22).

## Constraints

- One persistent roster spans WoW tiers and eras; one tier is active at a time. MVP uses currently available data; no complete future item catalog is required.
- The owner alone edits Sheets and uses the enhanced Gargul interface. Raiders have view-only Sheets access and install no addon.
- Gargul displays roll type/value, BiS Ratio, and Impact Score. It reads the owner's Statut and gain from the snapshot but never classifies items, chooses which signal applies, or assigns loot. The owner decides every award.
- BiS Ratio and Impact Score both use Tier Presence (since the tier start); lifetime presence was removed on 2026-10-23. Presence Max initializes to `1` when a window has no possible raids.
- The owner imports each raid once and manually corrects JSON. Malformed JSON is rejected without changing existing data; duplicate-upload detection is not required.
- Raiders are identified by their exact, unique roster character name, without case-folding; an award to a name not in Roster is rejected for owner correction.
- Off-spec and disenchanted awards never change loot counts; the owner marks pattern/design awards NONE.
- Sheet values affecting scores stay fixed while a raid snapshot is open.
- Warcraft Logs credentials stay in the owner's Apps Script User Properties, never in the shared workbook.
- First target: WoW Forever with Gargul v8.0.1, evolving the owner's existing Gargul_Preloot addon and Apps Script (see `brownfield.md`).

## Non-goals

- Multiple guilds or rosters.
- Automatic loot assignment; the addon shows the owner's Statut and gain but never classifies an item itself.
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