# PRD Quality Review — Guild Loot Distribution

## Review status (2026-10-15)

The findings below are from an earlier pass and are retained as review history. They were addressed in the PRD: BiS candidate ordering and ties are explicit; alt-BiS and sim gain are in the raider-facing view; malformed JSON is rejected without mutation; the end-to-end scenario covers imports, live state updates, and the separate BiS/Impact attendance windows; success measures are observable. The final rubric cross-check found no remaining material findings. Its sole mechanical note, the missing inline FR-1 assumption tag, was corrected. The PRD remains `draft` pending user approval.

## Overall verdict
**Adequate.** The PRD is unusually clear about the single-owner workflow, manual award authority, and the pre-/post-raid Sheets-to-Gargul handoff; those confirmed choices form a coherent and appropriately scoped internal tool. The main risk is downstream interpretation: priority edge cases and measurable acceptance criteria are not fully pinned down, and the addendum's requested `alt-BiS` raider-facing data is not explicitly represented in the PRD.

## Decision-readiness — adequate
The important product decisions are stated directly: one roster, one active tier, Google Sheets for shared visibility, owner-only enhancement, no automated item classification or award, and explicit attendance/score formulas. The addendum further confirms that identical complete Impact Scores resolve by roll, that the owner selects Impact treatment, and that future tank/healer exceptions are not MVP rules. The PRD's “No unresolved product decisions remain” is credible for the broad product direction.

The remaining decision-readiness gap is the operational boundary between BiS and non-BiS candidates. FR-4 says a Raider whose spec marks the item BiS has priority, while its ratio rule and “no candidate has the item marked BiS” case do not specify the exact candidate ordering when BiS and non-BiS Raiders both roll, or how ratios are compared among the BiS subset. The addendum clarifies that the flowchart's `+2` means priority for a BiS spec, not two points, but does not translate that clarification into a complete ordering rule. This matters even in a manual-award product because the interface is intended to inform the owner's decision.

### Findings
- **medium** BiS candidate ordering is underspecified (§4.2, FR-4; Addendum, Allocation Flowchart) — The documents establish BiS-over-non-BiS priority and a ratio among BiS awards, but do not explicitly state the ordered comparison when both candidate types are present or the ratio tie behavior. *Fix:* State the candidate tiers and ordering explicitly, including whether ratios apply only within the BiS-eligible set and what happens on equal ratios; retain the documented manual override boundary.

## Substance over theater — strong
This reads as a specific guild loot workflow, not generic product-template furniture. The Vision names the actual decision context and state transitions; the three shared Sheet views, owner-only raid interface, and manual JSON handoff each support the stated job. Non-Goals explicitly rule out multi-roster support, automated assignment, automatic data retrieval, and addon item classification. The internal single-operator context also makes the lack of a persona roster appropriate rather than a deficiency. No material persona, innovation, NFR, or vision theater is apparent.

### Findings
None.

## Strategic coherence — adequate
The thesis is consistent: consolidate the roster's attendance and loot state, make priority inputs inspectable, and preserve a human award decision. The feature sequence supports that arc from setup, through shared transparency and raid-night use, to recording and archiving. The counter-metric directly guards the most important product constraint: an efficiency improvement must not become automatic loot assignment.

The Success Metrics are mostly behavior statements rather than measurable thresholds. “Clearly consult” in SM-3 and “No defects” in SM-4 do not define a pass condition or observation period, and SM-4 largely restates correctness expectations already present in FRs. As written, the metrics support discussion but cannot reliably establish whether the MVP validated its thesis during raid use.

### Findings
- **medium** Success measures lack observable thresholds (§7, SM-3 and SM-4) — “Clearly consult” and “No defects occur” leave the owner without a reproducible acceptance or evaluation method, despite the counter-metric being usefully specific. *Fix:* Define a small, observable MVP evaluation for Sheet comprehension and raid/import/export correctness, including the test scenario and pass condition; avoid implying a statistically meaningful sample for a single-roster tool.

## Done-ness clarity — thin
Several core calculations have testable definitions, and the consequences around manual award, live state changes, and one-time import responsibility make important boundaries explicit. FR-3 also specifies how unmatched Warcraft Logs participants are handled. However, testability is uneven across the requirements: words such as “immediately,” “clearly,” and “sufficient” are not bounded, and there is no explicit acceptance scenario for the combined raid workflow or the state transition at three weeks after a tier begins. In particular, the core BiS selection behavior still needs the ordering clarification noted above before two implementations can be expected to present equivalent priority information.

The requirement text also leaves some input edge conditions unspecified, including how a zero possible-raid count affects normalized Presence and what constitutes a complete/valid JSON import. The PRD need not prescribe implementation, but it should define observable outcomes for these domain cases or explicitly defer them.

### Findings
- **high** Core workflow lacks end-to-end acceptance conditions (§4 FR-3–FR-5, FR-10–FR-13; §7 SM-1–SM-4) — Formula consequences exist, but there is no bounded acceptance scenario covering representative input, live award updates, export/import result, and the three-week reset; “immediately” and “no defects” cannot serve as test criteria. Edge behavior for zero Presence Max and invalid/incomplete import data is also unstated. *Fix:* Add concise, observable acceptance conditions for the normal raid cycle and the material edge cases, or explicitly identify deferred cases and their expected behavior.

## Scope honesty — adequate
The MVP boundary is unusually visible: manual data sourcing, a single roster, no raider installation, no automatic assignment, no addon item detection, no tank Impact Score, and no restoration of archived data are all called out. The addendum's future tank/healer rules are correctly kept out of confirmed MVP scope. Open Questions honestly distinguish an unconfirmed product name from implementation details, which are deferred to architecture.

One raider-facing request in the addendum is not clearly resolved by that scope: it asks for item status including `alt-BiS` and the relevant class/spec's simmed Impact gain. FR-9 promises per-spec BiS lists, and FR-2 mentions applicable classifications, but neither explicitly requires an `alt-BiS` status or clearly specifies the public item-level view. The reader cannot tell whether this is an intentional omission or an incomplete carry-through.

### Findings
- **medium** `alt-BiS` visibility is neither included nor excluded (§4.3 FR-2/FR-9, §6; Addendum, Raider-Facing Export) — The addendum asks the shared view to show BiS, Impact, and `alt-BiS` status plus class/spec-specific simmed gain, while the PRD specifies per-spec BiS lists and Impact priority without resolving `alt-BiS`. *Fix:* Confirm whether `alt-BiS` and item-level gain belong in MVP; add observable coverage to the relevant Sheet requirement or list them explicitly as a non-goal/deferred item.

## Downstream usability — adequate
The PRD has a useful glossary, unique and contiguous FR-1–FR-13 and SM-1–SM-4 identifiers, and resolving FR references in the success metrics. Core domain terms and formulas are mostly repeated where needed, making sections reasonably extractable. The addendum provides useful provenance for decisions, and the PRD explicitly assigns implementation choices to downstream architecture. Named-protagonist UJs are not present, but this is an internal single-owner tool and the capability-spec shape is suitable.

The most consequential downstream gaps are the unresolved BiS ordering and the missing explicit `alt-BiS` scope decision. In addition, the PRD promises JSON interchange but specifies only selected export content and not the minimum import/export contract or rejection/correction behavior; architecture and story authors would otherwise have to infer domain semantics from the implementation preference.

### Findings
- **medium** JSON interchange contract is not sufficiently sourceable (§4.4 FR-10/FR-12; Addendum, Raid-Night Integration) — The PRD requires JSON in both directions and names recipient and selected award treatment, but leaves the required roster/award identifiers, item/tier context, and invalid-import behavior to inference. *Fix:* Specify the minimum domain fields and observable validation/error behavior needed to preserve the documented award and score semantics; leave serialization and storage technology to architecture.

## Shape fit — strong
The PRD appropriately uses capability requirements and operational success measures for an internal tool operated by one guild owner. It does not add a persona cast, a consumer-style journey framework, or a multi-stakeholder approval model merely to satisfy a template. Raiders are represented where their read-only Sheet access creates a real requirement, while the owner retains the decision and operating role. The owner-only Lua/Gargul enhancement and future desktop preference are clearly distinguished from the MVP's shared view and handoff workflow.

### Findings
None.

## Mechanical notes
- **Glossary drift:** The PRD consistently uses “owner,” while the addendum's confirmed workflow repeatedly uses “officer.” The role appears to be the same operator, but the equivalence is not defined. “Phase” and “tier” are also used near-interchangeably; the glossary relates them, though downstream requirements should preserve the distinction between phase-specific data and active-tier transitions.
- **ID continuity and references:** FR-1–FR-13 and SM-1–SM-4 are unique and contiguous. The stated SM-to-FR references resolve.
- **Assumptions Index roundtrip:** FR-1 and FR-3 are tagged inline and indexed. The FR-12 owner-responsibility statement is listed in the Assumptions Index but is not tagged `[ASSUMPTION]` inline; align the tag/index or classify it as an explicit constraint instead.
- **UJ protagonists:** No UJs are included. This is acceptable for the agreed single-operator capability-spec shape; the raider-facing requirements are directly captured in FR-6–FR-9.
- **Required sections:** Vision, users/jobs, glossary, features/FRs, explicit non-goals, MVP scope, success metrics, open questions, and assumptions are present. No additional persona/UJ section is necessary for the stated product type.
