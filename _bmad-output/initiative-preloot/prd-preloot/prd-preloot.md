---
title: PreLoot PRD
status: final
created: 2026-09-30
updated: 2026-09-30
---

# PRD: PreLoot
*Working title — confirm.*

## 0. Document Purpose

This PRD is for the guild officer who builds and uses PreLoot, and for downstream architecture and ticket work. Section 3 sets the vocabulary. Features are grouped, with FRs numbered globally. Every inference is tagged `[ASSUMPTION]` inline and indexed in §9. It builds on the feasibility research in `../research-preloot-data-sources-feasibility/` and does not repeat it. **Stakes:** a proof of concept for one guild. If it works, the next steps are securing data-reuse permissions and adding per-roster ranking.

## 1. Vision

Before each new TBC raid phase, the guild spends hours reading BiS lists to answer two questions: which new items will several specs fight over, and who should get each one first? The answers today are opinion. "Vision of Sargeras is more BiS for Enhancement than for Rogue" is a feeling, not a number.

PreLoot replaces that investigation with one table. It takes the new Phase's BiS Lists and keeps only the items that two or more Specs want. For each of those Specs, it sims how much the item improves on that Spec's Previous Phase BiS. It then ranks the Specs by percentage gain. Items that only one Spec wants never appear. The officer gets an objective, sim-backed priority order for every Contested Item before the Phase launches.

## 2. Target User

### 2.1 Jobs To Be Done
- **Functional:** before a phase launches, know which new items are contested and which spec gains the most from each, measured rather than guessed.
- **Time:** cut the investigation of a new phase from hours of manual cross-referencing down to one run.
- **Social:** defend loot priority decisions to the raid with numbers, not opinion.

### 2.2 Non-Users (v1)
- Other guilds, and the public. PreLoot is for one guild's internal use.
- Tanks. Tank loot priority is set by guild rule, not by sims.
- Individual raiders shopping for their own upgrades.

### 2.3 Key User Journeys

- **UJ-1. The officer settles contested loot before the next phase opens.** A few days before Phase N launches, the loot officer runs PreLoot for Phase N. In a single run it reads each Spec's Phase N and Phase N-1 BiS Lists, finds the Contested Items, sims each Spec's upgrade, and produces the Priority Table. The officer scans it: Vision of Sargeras goes Enhancement Shaman +X% first, then Rogue +Y%. They post the table to the guild's loot channel. **Edge case:** if an item's name can't be matched to an item ID, it appears in an "unresolved" list instead of being silently dropped.

## 3. Glossary

- **Phase** — a TBC content release. The **Target Phase** is the one being analyzed; the **Previous Phase** is the one immediately before it. The same Phase has different names in different sources:
  - wowtbc.gg flags: `pre-bis`, `t4`, `t5`, `t6`, `za`, `swp`
  - wowsims phases: —, 1, 2, 3, 4, 5
  - Anniversary phases: pre-raid, P1, P2, P3, P4, P5
- **Spec** — a class specialization (e.g. Enhancement Shaman, Combat Rogue). Each Spec has one **Role**: DPS, Healer or Tank.
- **BiS List** — the ranked best-in-slot items for one Spec in one Phase, taken from wowtbc.gg.
- **Baseline Set** — the full gear set built from a Spec's Previous Phase BiS List. It is the reference point for every sim of that Spec.
- **Contested Item** — an item on the Target Phase BiS List of two or more Specs of the same Role, excluding Tanks.
- **Upgrade Value** — the percentage increase in DPS (DPS Role) or HPS (Healer Role) when a Contested Item replaces an item in a Spec's Baseline Set. The primary ranking key.
- **Raw Gain** — the same increase as an absolute DPS or HPS number. The first tie-breaker.
- **Tie-Break** — the ordered rules for ranking Specs whose Upgrade Values fall within the sim error margin of each other: Raw Gain first, then the Spec's Warcraft Logs top-percentile parse.
- **Priority Table** — the output: each Contested Item with its competing Specs ranked by Upgrade Value, then Tie-Break.

## 4. Features

### 4.1 Phase BiS Ingestion
**Description:** The officer picks a Target Phase. PreLoot loads the Target Phase and Previous Phase BiS Lists for every non-Tank Spec and matches each item to a game item ID using the wowsims item database. Realizes UJ-1.

#### FR-1: Select target phase
The officer can choose a Target Phase, and PreLoot works out the Previous Phase from it.

**Consequences (testable):**
- Selecting T5 uses T4 as the Previous Phase.
- Selecting the first phase that has a BiS List (pre-BiS → T4) uses the pre-BiS lists as the Baseline Sets.
- v1 targets TBC Anniversary. The first Target Phase is P4 (ZA), so the Previous Phase is P3 (T6).

#### FR-2: Load BiS lists for non-Tank specs
The system loads the Target Phase and Previous Phase BiS Lists for every DPS and Healer Spec.

**Consequences (testable):**
- No Tank Spec BiS List is loaded.
- A Spec with no BiS List for either phase is reported and skipped. The run continues.

#### FR-3: Resolve items to item IDs
The system matches every BiS List item to a wowsims item ID, along with its slot and drop source.

**Consequences (testable):**
- Items that can't be resolved are listed in the run's output with their Spec and slot, and are never silently dropped.
- The run reports the name-to-ID match rate for each Spec. The research found only 170 of 448 wowtbc.gg items carry an ID, so name matching carries most of the load.
- Matches are accepted only for items available in the Target Phase or earlier, based on the wowsims item phase.
- Heroic and normal versions of the same item name resolve to different IDs. [ASSUMPTION: the BiS List context tells us which one is meant; if not, the item is flagged as unresolved.]

### 4.2 Contested Item Detection
**Description:** From the Target Phase BiS Lists only (not the full loot table), PreLoot finds the items wanted by two or more Specs. Realizes UJ-1.

#### FR-4: Detect contested items
The system marks an item as a Contested Item when it appears on the Target Phase BiS List of two or more Specs of the same Role.

**Consequences (testable):**
- An item on only one Spec's BiS List is excluded from the Priority Table.
- Two Specs of the same class (e.g. Fury and Arms Warrior) count as contesting.
- Items from the full loot table that aren't on any Target Phase BiS List are never considered.

**Notes:** [ASSUMPTION: if an item is on both a DPS Spec's BiS List and a Healer Spec's BiS List, which the guild expects to be rare, it is ranked separately within each Role and flagged, because % DPS and % HPS can't be compared.]

### 4.3 Upgrade Simulation
**Description:** For every Spec contesting an item, PreLoot sims the Baseline Set, then sims the Baseline Set with the Contested Item swapped in. The Upgrade Value is the percentage difference. Realizes UJ-1.

#### FR-5: Compute Upgrade Value per spec
The system computes the Upgrade Value for each (Contested Item, Spec) pair using wowsims. It uses % DPS for DPS Specs and % HPS for Healer Specs.

**Consequences (testable):**
- The Upgrade Value = (sim with item − Baseline Set sim) / Baseline Set sim × 100.
- The baseline and the swapped sim use the same random seed and the same number of iterations.
- The encounter is a single-target Patchwerk-style fight lasting 2–3 minutes. The wowsims default encounter is also acceptable.
- The sim settings used (iterations, seed, encounter) are recorded with the output.
- Raw Gain is recorded next to every Upgrade Value.
- There is no cap on the number of sims. A long run is acceptable for completeness.

#### FR-6: Swap slot by slot, covering every combination
The Contested Item replaces the Baseline Set item in its slot. Paired slots (rings, trinkets, one-hand weapons) are handled one slot at a time, not as a pair.

**Consequences (testable):**
- For a paired slot, the system sims the Contested Item in each slot it fits. The other slot takes every option available to it: the Baseline Set item and each Target Phase BiS List option for that slot. Every combination is simmed.
- The Upgrade Value used for ranking is the best of those combinations. Every combination's result is kept in the run output.
- Gems and enchants always use the wowsims defaults, for both the Baseline Set and the Contested Item.

**Notes:** Healer sims in wowsims are still alpha. HPS-based Upgrade Values are accepted for v1 but labeled "Healer, alpha sim" in the Priority Table.

### 4.4 Priority Table
**Description:** The single deliverable of a run. Realizes UJ-1.

#### FR-7: Produce the priority table
The system outputs one row per Contested Item. Each row lists the item, its slot, where it drops (boss and zone), and the competing Specs ranked by Upgrade Value, with the Upgrade Value and Raw Gain shown for each.

**Consequences (testable):**
- The rows are grouped by Role (DPS, Healer).
- The table can be exported to CSV with one row per (Contested Item, Spec). Columns: item ID, item name, slot, drop source, Role, Spec, rank, Upgrade Value, Raw Gain, and tie-break rule applied.

#### FR-8: Apply the tie-break
When two Specs' Upgrade Values for the same Contested Item fall within the sim error margin of each other, the system treats them as tied and orders them by Tie-Break.

**Consequences (testable):**
- Tied Specs are ordered by the higher Raw Gain.
- If the Raw Gain is also within the error margin, the Spec with the higher Warcraft Logs top-percentile parse ranks first.
- If Warcraft Logs data isn't available, PreLoot shows the tie as unresolved instead of blocking the run.
- The Priority Table shows which rule settled each tie.

**Notes:** Parses for a Target Phase can't exist before it launches, so the tie-break uses TBC Anniversary Previous Phase parses (P3 for the P4 Target Phase).

#### FR-9: Functional HTML report
The system produces an HTML report of the Priority Table that is easy to scan and act on.

**Consequences (testable):**
- Each Spec is shown in its class color, and each Upgrade Value is color-coded by size. [ASSUMPTION: color scheme]
- Each item name links to its item page. [ASSUMPTION: Wowhead TBC item pages. A hyperlink only; no Wowhead data is fetched.]
- Each row shows the drop source (boss and zone) from the wowsims item database.
- Unresolved items and skipped Specs appear in a separate section of the report.
- Healer rows carry the "alpha sim" label.
- The report credits its data sources: the wowsims item database (MIT license, attribution requested), wowtbc.gg BiS Lists and Warcraft Logs.

## 5. Non-Goals (Explicit)
- Not a loot-distribution tool. No in-game addon, no soft-reserve and no attendance or loot history. That's My BIS, Gargul and RCLootCouncil already cover those.
- No ranking by individual raider in v1.
- Tanks are not ranked.
- No Wowhead data. Its terms forbid scraping and it has no public API. Item hyperlinks to Wowhead pages are the only use.
- Not hosted publicly and not built for other guilds.

## 6. MVP Scope

### 6.1 In Scope
- Ingestion (FR-1–FR-3): Target Phase selection, BiS Lists for DPS and Healer Specs, and item ID resolution through the wowsims `db.json`.
- Detection (FR-4): Contested Items within each Role.
- Simulation (FR-5–FR-6): Upgrade Value and Raw Gain against the Baseline Set, covering every paired-slot combination.
- Output (FR-7–FR-9): Tie-Break, the Priority Table as a functional HTML report, and CSV export.

### 6.2 Out of Scope for MVP
- Ranking by roster, using each raider's actual gear. Deferred to v2.
- Contested Items that aren't on a BiS List, i.e. items that are strong upgrades but nobody's BiS. Deferred.
- Other game versions (e.g. WoW Forever). Deferred.

## 7. Success Metrics
- **SM-1:** the officer produces the Priority Table for a new Phase in a single run, in under an hour including review. Today this takes hours of manual investigation. [ASSUMPTION: target to be confirmed.] Validates FR-1–FR-9.
- **SM-2:** the officer uses the Priority Table as the basis for the guild's loot priority in the next phase. Validates FR-7, FR-9.
- **SM-C1 (counter-metric):** do not chase sim precision beyond the point where the ranking stops changing. Extra iterations cost run time without changing any decision. Counterbalances SM-1.

## 8. Open Questions
1. **wowtbc.gg reuse permission.** wowtbc.gg publishes no reuse license. Deferred during the POC: if the POC works, the user will ask wowtbc.gg for permission. If they refuse, we need a hand-curated BiS List fallback.
2. **Warcraft Logs details.** Which percentile counts as "top" (95th, 99th, or rank 1)? What do the API terms and credentials require? Not researched yet.
3. **Healer sim validity and source.** The wowsims bulk sim reports DPS only, so HPS must come from another sim call. Healer sims are also alpha. A test run on one Healer Spec (e.g. Holy Paladin) is needed before HPS numbers can be trusted. If it fails, Healer ranking is dropped from the POC.

## 9. Assumptions Index
- §4.1 FR-3: heroic vs normal is decided from BiS List context, otherwise the item is flagged as unresolved.
- §4.2 FR-4: an item on both a DPS Spec's and a Healer Spec's BiS List is ranked separately in each Role and flagged.
- §4.4 FR-9: class colors for Specs, and size-based colors for Upgrade Values.
- §4.4 FR-9: item links point to Wowhead TBC item pages (hyperlink only).
- §7 SM-1: the under-one-hour investigation target.
- Working mode: Fast path was chosen for the user, who didn't state a preference.
