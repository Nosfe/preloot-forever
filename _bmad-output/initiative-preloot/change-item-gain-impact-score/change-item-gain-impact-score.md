# Sprint Change Proposal — Item-gain Impact Score and workbook reshape

Date: 2026-10-21 · Initiative: initiative-preloot · Mode: incremental (6/6 proposals approved) · Scope: **Moderate**

## 1. Issue Summary

While story 4.2 (workbook data model) was being built and reviewed live, the owner reshaped the workbook and revised two core loot rules.

- **Impact Score gain.** The Impact Score's gain is the dropped item's simulated gain for the roller's spec, taken from the Objets tabs. It is not one gain per raider. The score applies only when the item's Statut for that spec is IMPACT.
  - Roster shows the score without the item gain.
  - Gargul shows the full score when the item drops.
- **Tank priority** (MT1/MT2) is removed. Tanks still have no Impact Score.
- **Presence windows are renamed:**
  - **Tier Presence** counts raids since the BiS reset and feeds the BiS Ratio. The BiS reset restarts it, together with the BiS loot count.
  - **Lifetime Presence** counts raids across all tiers, archives included, and feeds the Impact Score.
- **Workbook reshape (built):**
  - Présence grid (1 / B / 0) replaces Attendance and Bench.
  - Awards are blocks per raider.
  - The Objets tabs, one per role, hold Statut and Gain per spec.
  - Raids absorbs RaidReports.
  - Config holds the BiS reset date and the open raid.
  - PatternItems and Diagnostics are removed.
  - Statut values are BIS / IMPACT / CLASS_BOUND / NORMAL.
- **The owner decides every award**, even against the displayed ratio, score or roll.

Evidence: the owner's decisions in this session. The workbook changes are implemented and pushed (Gargul_Preloot `4ea6af4` … `5508d93`). Deferred-work entry from `plan-4-2-workbook-polish.md`.

## 2. Impact Analysis

- **Epics:**
  - epic-sheets-workbook stays viable, with stories 4.3, 4.4, 4.6, 4.7 and 4.8 rescoped and 4.5 dropped.
  - epic-raid-companion stays viable. The addon now reads the item table and computes the full Impact Score on IMPACT items.
- **Artifacts:**
  - spec kernel: CAP-1, CAP-2, CAP-4, CAP-6, CAP-8, Constraints, Non-goals;
  - allocation-rules.md and raid-workflow.md;
  - PRD: Glossary, 4.2, FR-1 to FR-12, Non-goals, SM-3;
  - architecture: AD-1, AD-2, AD-4, AD-6, AD-7, Interchange v1 → v2, plus a new Workbook layout table.
- **Technical:**
  - The pre-raid export becomes Interchange v2: items table, `classSpec`, `tierPresence`, `lifetimePresence`, `impactBase`. It drops `tankPriority`, `gainFraction` and `impactScore`.
  - The post-raid Gargul template is unchanged.
  - No UX documents exist.

## 3. Recommended Approach

**Direct adjustment.** Update the planning documents, then rescope the remaining stories in place. No rollback is needed, because the workbook already matches the new model. MVP scope is unchanged in intent; FR-8/FR-9's per-slot view is replaced by the Objets tabs. Effort: low to medium. Risk: medium, because Interchange v2 and the addon's item lookup are new.

## 4. Detailed Change Proposals (approved)

1. **allocation-rules.md:**
   - Tier and Lifetime Presence definitions; BiS Ratio uses Tier Presence.
   - Impact Score = Normalized Lifetime Presence × parse × item gain / (Impact Items + 1), only for IMPACT items for the roller's spec. Roster shows "Impact (sans gain objet)"; Gargul shows the full score.
   - Statut values are BIS / IMPACT / CLASS_BOUND / NORMAL. No tank priority. Owner picks NONE for patterns.
   - The owner decides every award.
2. **Spec kernel and raid-workflow.md:**
   - CAP-2: Tier and Lifetime Presence.
   - CAP-4: the new Impact rule.
   - CAP-6: shows BiS Ratio and, on IMPACT items, the full Impact Score; never chooses or awards; the owner decides even against the values.
   - CAP-8: the BiS reset restarts Tier Presence and BiS loots; Lifetime continues.
   - Constraints and Non-goals reworded; raid-workflow lists the real tabs.
3. **PRD:**
   - Glossary.
   - Tank priority removed from 4.2.
   - FR-1 to FR-12 as in the proposal: raider fields, Objets tabs, presences, Impact formula, Roster columns, snapshot item data, owner decides, pattern forcing removed.
   - Non-goals and SM-3.
4. **Architecture:**
   - AD-1: open raid in Config; archives count toward Lifetime Presence.
   - AD-2: calculation contract.
   - AD-4: the owner decides; the companion reads the Statut but never classifies.
   - AD-6: the snapshot carries the Objets table; pattern forcing removed.
   - AD-7: Raids report codes and Présence `1`.
   - Interchange v2.
   - Workbook layout table.
5. **epic-sheets-workbook:**
   - Done-when 2, 3 and 6 reworded.
   - 4.2 described as built.
   - 4.3: Roster formulas (Tier and Lifetime Presence, loot counts from Awards blocks, BiS Ratio, Impact (sans gain objet)) and fixtures with item-gain cases.
   - 4.4: Présence `1` and Raids report codes.
   - 4.5: dropped.
   - 4.6: raid lifecycle via Config and Interchange v2.
   - 4.7: append into Awards blocks and clear Raid ouvert; no pattern list.
   - 4.8: BiS reset date, archives count for Lifetime, carryover.
6. **epic-raid-companion:**
   - Description and Done-when 2 and 4: v2 import; full Impact Score only for IMPACT items for the roller's spec; never awards.
   - Note: the snapshot carries `classSpec`.

## 5. Implementation Handoff

- **Scope:** Moderate. The planning documents are edited directly. Backlog changes are applied with `bmad-ticket`: rescope 4.3, 4.4, 4.6, 4.7 and 4.8; drop 4.5; update 4.2's description; reword the epic envelopes.
- **Who:**
  - The developer agent applies the document edits and tickets.toml rewording in this session.
  - The owner confirms.
  - Story 4.3 is then built with `bmad-build`.
- **Success criteria:**
  - No planning document mentions tank priority, a raider-level gain, BiS/tier presence with the old meaning, or the pattern list as live rules.
  - The 4.3 plan cites the new allocation-rules.
  - The deferred-work entry for the spine and spec update is resolved.

## Outcome (2026-10-21)

Approved by the owner and applied.

- **Documents edited:**
  - allocation-rules.md, spec kernel, raid-workflow.md, PRD, architecture (AD-1/2/4/6/7, Interchange schema version 2, Workbook Layout);
  - epic-sheets-workbook (envelope and tickets.toml: 4.2, 4.3, 4.4, 4.6, 4.7, 4.8, 4.10 rescoped; 4.5 marked dropped);
  - epic-raid-companion.
- **Deferred entry:** the entry from `plan-4-2-workbook-polish.md` (spine/spec update before 4.3) is resolved by this change.
- **Leftovers:** a search for the old rules finds them only in historical memlogs.
- **Next:** build story 4.3.
