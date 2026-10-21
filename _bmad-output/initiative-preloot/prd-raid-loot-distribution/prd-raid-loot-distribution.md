---
title: Guild Loot Distribution
status: final
created: 2026-10-14
updated: 2026-10-15
---

# PRD: Guild Loot Distribution
*Working title; product name to confirm.*

## 0. Document Purpose

This PRD defines an internal loot-management product for one World of Warcraft roster across its phases. The guild owner configures the roster, phase data, loot rules, and awards; raiders can consult the published Sheets view. The MVP pairs Google Sheets with an enhanced, owner-only Lua/Gargul interface. The accompanying `addendum.md` preserves the user's source flowchart and implementation preferences. Requirements describe user-visible capabilities; implementation specifics remain in the addendum for downstream architecture.

## 1. Vision

Guild Loot Distribution helps one guild owner manage phase-specific loot priorities for a single roster. Google Sheets holds roster and item data for raider reference; an owner-only Gargul enhancement displays roll values, BiS Ratios, and Impact Scores without deciding the award. JSON handoffs keep in-raid state current. A local desktop GUI is a future preference, not an MVP requirement.

## 2. Target User

### 2.1 Jobs To Be Done

- As the guild owner, prepare one roster's phase-specific loot data and allocation rules before a raid.
- As the guild owner, see the applicable priority and its rationale while manually awarding a dropped item.
- As the guild owner, record attendance and loot awards so BiS ratios and impact scores stay current across phases.
- As a raider, consult the published roster state, item classifications, priority order, and score details before loot is awarded.

### 2.2 Non-Users (MVP)

- Other guilds and other rosters are not managed by this MVP.
- Raiders do not need to install or operate the enhanced Lua/Gargul interface.
- Automated ingestion of BiS lists or Warcraft Logs parse data is not part of the MVP.

## 3. Glossary

- **Roster** — the single guild roster managed by the product across all supported phases.
- **Raider** — a person on the Roster, with a role and class/spec information used for eligibility and display.
- **Phase** — a progression period or raid tier for which BiS lists and loot state are managed. The product maintains one Roster across tiers and has one active raid tier at a time.
- **Tier Presence** — the raw count of attended raids plus manually recorded bench appearances across the active tier. **Tier Presence Max** is the number of possible raids in that tier; **Normalized Tier Presence** is `Tier Presence / Tier Presence Max`.
- **BiS Presence** — the raw count of attended raids plus manually recorded bench appearances since the latest BiS reset. **BiS Presence Max** is the number of possible raids since that reset; **Normalized BiS Presence** is `BiS Presence / BiS Presence Max`.
- **BiS Item** — an item marked by the owner as best-in-slot for one or more specs for a Phase.
- **Impact Item** — an item configured for impact scoring and attribution among eligible classes.
- **Tier Set Item** — a tier-set item rolled among eligible classes after tank priority.
- **Class-Bound Item** — an item rolled among eligible classes after tank priority, distinct from a Tier Set Item.
- **BiS Ratio** — `Normalized BiS Presence / (BiS loots received since reset + 1)`. A BiS award affects the recipient's ratio. BiS Presence and the BiS-loot count reset three weeks after a new raid tier begins.
- **Impact Item Count** — the number of Impact Items awarded to a Raider; the owner can choose whether this count carries into a new active tier.
- **Impact Score** — `Normalized Tier Presence * DPS Warcraft Logs average parse * simmed percent DPS/HPS gain / (Impact Items already received + 1)`. If complete Impact Scores are identical, the outcome is resolved by roll.
- **Raid Award** — the manually chosen recipient and item classification recorded during loot distribution.

## 4. Features

### 4.1 Roster and Phase Setup

The owner maintains one Roster across Phases. Initial roster, Impact Item, Warcraft Logs parse, and BiS data are entered manually in Sheets. Attendance is processed from a Warcraft Logs raid link; bench appearances are entered manually. This realizes the owner's preparation and state-maintenance jobs.

#### FR-1: Maintain the roster

The owner can create and update Raiders in the single Roster, including raider name, role, class/spec, attendance, bench appearances, and current BiS Ratio. `[ASSUMPTION: Each Raider has an assigned role and class/spec, since those values drive eligibility and display.]`

**Consequences (testable):**
- The Roster can be maintained in Google Sheets without requiring a separate raider account.
- Raiders can consult the published Roster view.
- One Roster can retain its state across multiple Phases.

#### FR-2: Configure phase data

The owner can configure Phase-specific BiS Items by spec and item slot, Impact Items and their eligible classes, manually supplied parses and simmed gains, and applicable item classifications.

**Consequences (testable):**
- The owner can add and revise BiS data for each Phase without automated source retrieval.
- The owner can configure which classes are eligible for each Impact Item.
- Changes to a Phase's data do not erase the Roster's other Phase data.

#### FR-3: Process attendance

The owner can provide a Warcraft Logs raid link so the system updates raid attendance for the Roster; the owner can enter bench appearances manually. `[ASSUMPTION: Warcraft Logs links expose an identity value that can be matched to the manually maintained Roster.]`

**Consequences (testable):**
- Attendance and bench appearances are distinguishable in the Roster.
- Tier Presence and BiS Presence each count matched attended raids plus manually recorded bench appearances in their respective windows; each Presence Max is the number of possible raids in that window.
- Before the first possible raid in a window, its Presence Max is initialized to `1`, so Presence `0` produces Normalized Presence `0`.
- At the BiS reset, BiS Presence starts a new window; Tier Presence continues to count from the start of the active tier.
- Warcraft Logs participants that cannot be matched to a Raider are ignored; the owner can correct attendance in the JSON or Roster list.
- A Raider counts as attending a raid only when present for strictly more than 25% of its completed boss fights (kills and wipes; all completed fights if the log has no boss).
- An alt listed in the Rerolls sheet credits its main's attendance; awards to an alt are not credited to the main.

### 4.2 Loot Priority and Score Transparency

The product presents the applicable item category, eligible classes or Raiders, and allocation basis. Tier Set Items and Class-Bound Items are rolled among eligible classes after tank priority; tank priority is MT1 followed by MT2. BiS assignments and Impact Item eligibility are configured by the owner.

#### FR-4: Calculate BiS ratios

The system calculates each eligible Raider's BiS Ratio as `(BiS Presence / BiS Presence Max) / (BiS loots received since reset + 1)` and updates the ratio when a BiS Raid Award is recorded.

**Consequences (testable):**
- Any BiS-eligible Raider who rolls has priority over every non-BiS Raider who rolls, regardless of their BiS Ratio.
- Among BiS-eligible Raiders, the higher BiS Ratio has priority; if ratios are equal, the owner uses Gargul's roll value to decide manually.
- If no candidate has the item marked BiS, interested Raiders roll without BiS Ratio impact.
- A BiS Item cannot be passed; when awarded as BiS to a Raider, it impacts that Raider's BiS Ratio.
- If the owner marks a BiS award as Impact in Gargul, the award does not affect BiS Ratio; it updates Impact scoring/count state instead.
- The system does not model exceptional class-priority overrides; the owner handles rare exceptions manually during the raid.
- Three weeks after a new raid tier begins, BiS Presence and the BiS-loot count restart; a Raider with no post-reset attendance has a BiS Ratio of `0/1`.

#### FR-5: Calculate and explain Impact Item priority

The system calculates an Impact Score for eligible classes and presents the resulting priority order and score components to the owner and raiders.

**Consequences (testable):**
- The score is `(Tier Presence / Tier Presence Max) * DPS Warcraft Logs average parse * simmed percent DPS/HPS gain / (Impact Items already received + 1)`.
- The owner maintains one simulated percent DPS/HPS Gain per Raider for the active tier. The Impact Score belongs to that Raider, not to the dropped item; per-spec item gains remain separately visible in Sheets.
- Tier Presence counts attended raids plus bench appearances across the active tier; Tier Presence Max is the number of possible raids in that tier.
- The BiS attendance reset does not change Tier Presence or the attendance input to Impact Score.
- A missing DPS parse is treated as `1`, the lowest value.
- Tanks are handled by tank priority across their loot table and do not receive a configurable Impact Score.
- If complete Impact Scores are identical, the outcome is resolved by roll. Simmed percent gain is part of the score, not a separate tie-break.
- The owner can choose whether Impact Item counts carry into the next active tier or reset.

#### FR-6: Show the reason for priority

The system lets the owner and raiders inspect the data contributing to an Impact Score, including gain, Warcraft Logs parse, Presence, and prior Impact Items received.

**Consequences (testable):**
- Raiders can see the Impact Item attribution order and the score details used to produce it.
- The published score details are consistent with the values used by the owner-only raid interface.

### 4.3 Raider-Facing Sheets

Google Sheets is the MVP's shared view for the owner and Raiders. The user-defined starting layout has three tabs: roster, Impact Items, and per-spec BiS Items. Raiders have view-only access to all three tabs; editing is restricted to the owner.

#### FR-7: Publish roster state

The owner can share a roster view showing raider name, role, Presence and its attendance/bench basis, and BiS Ratio.

#### FR-8: Publish Impact Item priority

The owner can share Impact Items ordered by attribution priority, with score details available for inspection.

#### FR-9: Publish per-spec BiS lists

The owner can share each spec's item list with equipment slots as columns and item status labeled as BiS, alt-BiS, Impact, or other configured status. Raiders can consult all configured specs and see simmed gain by class/spec for Impact Items.

**Consequences (testable):**
- The shared view has a row for each configured spec and columns for equipment slots.
- Item status distinguishes BiS, alt-BiS, and Impact Items; Impact Items show the associated class/spec simmed gain.
- Raiders can view all three tabs but cannot edit them; only the owner can edit the workbook.

### 4.4 Raid-Night Award Workflow

The owner alone uses the enhanced Lua/Gargul interface. Raiders continue using Gargul's default interface and do not install the enhancement. The owner identifies item types using Google Sheets on a second screen and makes awards manually through Gargul. The addon has no item-type knowledge and does not decide which signal governs an award; it displays Gargul's roll value, BiS Ratios, and Impact Scores so the owner can consult the Sheet and decide what to consider.

#### FR-10: Load current state before a raid

The owner can export current Sheets data as JSON and load roster ratio and score state into the enhanced raid interface before a raid.

**Consequences (testable):**
- The imported state is sufficient for the interface to display current BiS Ratios and Impact Scores during the raid.
- The interface is used by the owner only.
- The interface does not look up, identify, or classify the dropped item; the owner refers to Google Sheets for item type and priority context.

#### FR-11: Assist with manual loot awards

The enhanced interface displays Gargul's roll type (BiS/non-BiS) and roll value alongside BiS Ratios and Impact Scores while the owner manually awards loot. The owner uses Google Sheets on a second screen to identify whether a drop is BiS, Impact, Tier Set, Class-Bound, or another type and decides whether to consider the ratio, score, or roll value.

**Consequences (testable):**
- The interface displays Gargul's roll type and roll value, plus BiS Ratios and Impact Scores; it does not infer the dropped item's classification or determine which signal applies.
- The interface displays each rolling Raider's existing BiS Ratio and Impact Score (except tanks, who have no Impact Score); it does not look up an item's simulated gain.
- The owner uses the Sheet's item classification to decide whether to consider the ratio, score, or roll value.
- When the owner awards a BiS Item, Gargul presents an Impact checkbox; selecting it records the award as Impact for scoring and count updates, without changing BiS Ratio. The addon does not infer item type from the item identity.
- The interface updates relevant ratios and scores live as awards are made during the raid, and the changed values are used for subsequent rolls.
- The interface does not automatically choose or award the recipient.

#### FR-12: Export raid results to Sheets

After a raid, the owner can export all Raid Awards from Gargul and import them into Sheets to update roster ratios and Impact Scores.

**Consequences (testable):**
- Pre-raid state identifies each Raider consistently and includes current BiS Ratios and Impact values needed by Gargul; it does not need item classifications.
- Each post-raid award identifies the recipient, item reference supplied by Gargul, roll type, and owner-selected BiS/Impact/None treatment needed to update the correct ratio or Impact Item Count.
- Off-spec, disenchanted, and pattern/design awards never change BiS or Impact loot counts.
- The exchange does not require the addon to identify or classify an item.
- Importing the results updates the Roster and priority views without re-entering each award manually.
- The owner ensures each raid export is imported only once and manually edits the JSON before import to correct an award; duplicate detection and correction reconciliation are not required.

#### FR-13: Archive completed-tier data and configure carryover

The owner can archive completed-tier data for reference and choose whether Impact Item counts carry into the next active tier. Three weeks after a new tier begins, BiS Presence and the BiS-loot count reset; Tier Presence remains tier-wide for Impact Scores.

**Consequences (testable):**
- Archived tier data remains available for reference after a new tier becomes active.
- Archived tier data is read-only and cannot be restored into an active tier.
- The owner can choose whether Impact Item counts carry forward or reset at the tier transition.
- Three weeks after the new tier begins, BiS attendance and BiS-loot count restart; tier-wide attendance remains unchanged for Impact Scores.

#### FR-14: Reject malformed JSON imports

The system rejects malformed or incomplete JSON imports without changing existing data.

**Consequences (testable):**
- A malformed pre-raid state file does not alter the current Gargul state.
- A malformed post-raid results file does not alter the current Sheets data.
- Duplicate-upload detection is not required; the owner imports each raid once.

## 5. Non-Goals (Explicit)

- Supporting multiple guilds or multiple Rosters.
- Automatically assigning loot; the owner makes each award.
- Classifying dropped items in the addon; the owner consults Sheets.
- Modeling rare class-priority exceptions; the owner handles those manually during the raid.
- Calculating Tank Impact Scores; tanks receive priority across their loot table.

## 6. MVP Scope

### 6.1 In Scope

- One persistent Roster across WoW tiers, with one active raid tier at a time.
- Manual setup in Google Sheets for roster, Impact Items, Warcraft Logs parses, and per-phase BiS lists.
- Warcraft Logs raid-link attendance processing and manual bench entry.
- BiS Ratio and Impact Score calculation and visibility.
- Completed-tier archiving, with owner-controlled Impact Item Count carryover and the scheduled BiS Ratio reset.
- Three shared Sheets views: roster, Impact Item priority, and per-spec BiS by slot.
- Owner-only Lua/Gargul enhancement with pre-raid state import, live in-raid score/ratio display, manual award support, and post-raid results export.
- JSON exchange between Sheets and the raid interface.

### 6.2 Out of Scope for MVP

- Automatic retrieval of BiS lists or Warcraft Logs parse averages; manual setup is acceptable initially.
- Separate addon installation for Raiders.
- A hosted custom web service.
- A standalone desktop GUI; preferred future direction if it can avoid hosting costs.
- Future tank-loot and healer-loot exceptions shown in the source flowchart unless later confirmed as MVP rules.

## 7. Success Metrics

- **SM-1:** A single post-raid JSON import updates roster ratios and Impact Item counts to match the recorded Raid Awards, without manual re-entry. Validates FR-4, FR-5, FR-12.
- **SM-2:** After an award is recorded, the affected BiS Ratio or Impact Score is updated in Gargul before the next roll in that raid. Validates FR-10, FR-11.
- **SM-3:** All three Sheets tabs expose the roster ratios, Impact Item priorities and score details, and per-spec BiS/alt-BiS item status to Raiders in view-only mode. Validates FR-7, FR-8, FR-9.
- **SM-4:** In the end-to-end acceptance scenario, valid pre-raid and post-raid JSON preserves all expected ratio/score changes, while malformed JSON leaves existing state unchanged. Validates FR-10, FR-11, FR-12, FR-14.

**End-to-end acceptance scenario:** Start a new tier with Tier Presence `0` / Tier Presence Max `1` and BiS Presence `0` / BiS Presence Max `1`; export the Sheet state and load it into Gargul. During a raid, verify that a BiS roller outranks a non-BiS roller regardless of ratio, equal BiS Ratios are resolved manually using roll value, and a BiS award updates BiS Ratio unless marked Impact. An Impact-marked award updates Impact state without changing BiS Ratio. Each change is visible before the next roll. Three weeks into the tier, verify that BiS attendance and BiS-loot count restart at `0/1` while Tier Presence and Impact Score continue using whole-tier values. Export the raid results and import once into Sheets; verify roster ratios, Impact counts, and score order against the awards. A malformed pre-raid or post-raid JSON file is rejected without changing existing data.

**Counter-metric:** The process must not silently change the owner's manual award into an automatic assignment; the owner retains the decision. Counterbalances SM-1 and SM-2.

## 8. Open Questions

No unresolved product decisions remain at this checkpoint. The product name is still a working title; implementation details remain for downstream architecture.

## 9. Assumptions Index

- `[ASSUMPTION]` FR-1 — each Raider has a role and class/spec identity maintained with the roster, since class/spec drives BiS and Impact Item eligibility.
- `[ASSUMPTION]` FR-3 — Warcraft Logs links expose an identity value that can match most participants to the manually maintained Roster; unmatched participants are ignored and can be corrected manually by the owner.