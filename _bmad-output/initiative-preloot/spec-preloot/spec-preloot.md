---
id: SPEC-preloot
companions: ['glossary.md', 'acceptance-criteria.md', '../architecture-preloot/architecture-preloot.md']
sources: ['../prd-preloot/prd-preloot.md']
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# PreLoot — Sim-Based Loot Priority for Contested BiS Items

## Why

**The pain:** before each TBC Anniversary raid phase, one guild's loot officer spends hours cross-referencing BiS lists to decide which new items several Specs will compete for, and who should get each one first. Today that decision is opinion, not measurement. PreLoot replaces the investigation with one sim-backed Priority Table that the officer board uses for the whole phase. It is a proof of concept for a single guild. If it works, the next steps are securing data-reuse permission and adding ranking based on the guild roster.

## Capabilities

Terms are defined in [glossary.md](glossary.md). Testable detail for each CAP is in [acceptance-criteria.md](acceptance-criteria.md).

- **CAP-1**
  - **intent:** The officer chooses a Target Phase, and PreLoot derives the Previous Phase.
  - **success:** Choosing P4 yields P3 as the Previous Phase. Choosing the first raid phase uses the pre-raid BiS Lists as the Baseline Sets.
- **CAP-2**
  - **intent:** The system loads the Target Phase and Previous Phase BiS Lists for every DPS and Healer Spec.
  - **success:** No Tank BiS List is loaded. A Spec missing a list is reported and skipped, and the run continues.
- **CAP-3**
  - **intent:** The system resolves every BiS List item to a wowsims item ID, slot and drop source.
  - **success:** The run reports the match rate for each Spec. Every unresolved item is listed with its Spec and slot. Only items available at or before the Target Phase are accepted.
- **CAP-4**
  - **intent:** The system identifies Contested Items among the Target Phase BiS Lists.
  - **success:** An item on the Target Phase BiS Lists of two or more Specs of the same Role is contested. An item on only one Spec's list is excluded, and items outside the BiS Lists are never considered.
- **CAP-5**
  - **intent:** The system measures each competing Spec's Upgrade Value and Raw Gain for a Contested Item by simulation against its Baseline Set.
  - **success:** Every paired-slot combination is simmed and kept. The best combination sets the Upgrade Value. The baseline and candidate sims share the seed and iterations, and the settings are recorded.
- **CAP-6**
  - **intent:** The system ranks the competing Specs for each Contested Item.
  - **success:** Specs are ordered by Upgrade Value. Values within the sim error margin are tied and ordered by Tie-Break. The report names the rule that settled each tie, and a tie shows as unresolved when Warcraft Logs data is missing.
- **CAP-7**
  - **intent:** The officer gets a Priority Table grouped by Role, exportable to CSV.
  - **success:** Each row shows the item, slot, drop source, and the ranked Specs with their Upgrade Value and Raw Gain. The CSV has one row per (Contested Item, Spec), in the same order as the report.
- **CAP-8**
  - **intent:** The officer board gets one self-contained HTML report to use for the whole phase.
  - **success:** It opens from the shared folder on any PC without PreLoot running. It has tabs for the Priority Table, Contested Items and BiS Lists. It shows class colors, Upgrade Values color-coded by size, item links, drop sources, Issues, sim settings and data provenance, and it credits its sources. Healer rows carry an "alpha sim" label.
- **CAP-9**
  - **intent:** The officer can resume an interrupted run without redoing completed sims.
  - **success:** Killing a run mid-simulation and restarting it with the same settings finishes with no sim run twice, and the output is identical.
- **CAP-10**
  - **intent:** The officer runs PreLoot on a personal Windows 11 PC without installing Python.
  - **success:** A zipped folder copied to a clean Windows 11 PC runs a full Target Phase analysis.

## Constraints

- **No Wowhead data.** Its terms forbid scraping and it has no public API. Item data comes from wowsims `db.json` (MIT; attribution is requested and shown in the report). Wowhead appears only as item hyperlinks.
- **Tanks are excluded.** Guild rule gives tanks loot priority. Specs contest items only within the same Role.
- **Specs are talent specs.** A Spec is a talent spec as wowtbc.gg publishes it (e.g. Fury and Arms Warrior are separate). Each Spec is simmed as its wowsims spec with its own talent build, so two Specs of the same class compete.
- **Metric.** % DPS for DPS Specs and % HPS for Healer Specs, against the Previous Phase BiS Baseline Set. Gems and enchants use the wowsims defaults. The encounter is a single-target Patchwerk fight lasting 2–3 minutes; the wowsims default encounter is acceptable.
- **Scope of v1.** TBC Anniversary only. The first Target Phase is P4 (ZA), so the Previous Phase is P3. Tie-Break parses come from TBC Anniversary Previous Phase logs.
- **Run model.** A local batch run on the user's personal Windows 11 PC. There is one frozen run per Target Phase, with no mid-phase reruns. A long run is acceptable, and there is no cap on the number of sims.
- **Publishing.** Only `report.html` and `priority.csv` go to the shared folder. Warcraft Logs credentials and raw sim results never leave the PC.
- **Precision.** Don't pursue sim precision beyond the point where the ranking stops changing.

## Non-goals

- Loot distribution: no in-game addon, soft-reserve, attendance or loot history. That's My BIS, Gargul and RCLootCouncil cover those.
- Ranking per raider using actual gear in v1. It is deferred to v2, and the architecture keeps room for it (AD-5).
- Items that are strong upgrades but aren't on any BiS List.
- Other game versions, such as WoW Forever.
- Public hosting, or use by other guilds.
- Individual raiders using PreLoot to shop for their own upgrades.

## Success signal

- Before P4 launches, the officer produces the Priority Table in one run and reviews it in under an hour, where the investigation used to take hours by hand.
- The officer board uses the Priority Table as the basis for loot priority throughout P4.

## Assumptions

- Heroic and normal versions of an item are told apart from BiS List context. If the context doesn't settle it, the item is reported as unresolved.
- Color scheme: class colors per Spec, and size-based colors per Upgrade Value.
- The under-one-hour review target in the Success signal.

## Open Questions

- Where each Spec's talent build (and rotation options, e.g. Hunter BM/MM/SV) comes from when it is passed to wowsimcli: wowsims presets, or a table maintained by hand?
- wowtbc.gg reuse permission: the user asks only if the POC works. If refused, a hand-curated BiS List replaces the wowtbc.gg source.
- Warcraft Logs: which percentile counts as "top", and what the API terms and credentials require. Owned by the developer at build start.
- Healer HPS: is the wowsimcli healer output valid? Test on one Healer Spec first. If it fails, drop healer ranking from the POC.
- The sim error-margin formula that defines a tie. Owned by the rank stage.
