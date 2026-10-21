# Technology Lens Review

Date: 2026-10-21  
Lens: Configured technology validation (provider-fact check + hook-proof separation)  
Target: _bmad-output/initiative-preloot/architecture-raid-loot-distribution/architecture-raid-loot-distribution.md  
Reviewer: ReviewerCodex

## Verdict
FAST-FIX

## Confidence
0.95

## Provider Facts Confirmed

1. WoW Forever target is pinned to client `1.60.1` and interface `16001` in the architecture stack.
2. Gargul baseline is pinned to `v8.0.1-forever` in the architecture stack.
3. WoWSims Forever is positioned as a candidate input source for Raider-level Gain, not a hard dependency.
4. Warcraft Logs integration is pinned to public GraphQL API `v2` with owner-scoped credentials.
5. Sheet-side runtime/commit semantics are pinned to Apps Script `V8` plus Sheets API `v4` `spreadsheets.batchUpdate`, with atomic batch expectations called out.

## Proven vs Assumed (Addon Surface)

### Proven in current project evidence
- Version pins and runtime/API selections above are explicitly present in the stack and rules.
- The architecture explicitly states that release support is not treated as proof of hook feasibility.
- Deferred items require capture of a native `v8.0.1-forever` export fixture and prototype verification for importer/export hooks.

### Still assumed (not yet proven by local code/fixture in this initiative)
- Availability and stability of all required companion hooks for:
  - raid-only export capture,
  - checksum-safe correlation/edit/delete flows,
  - guaranteed roll type/value presence for every required award path.
- Complete first-tier WoWSims Forever data coverage for all needed class/spec/item contexts.

## Top Concrete Blockers

### Major
1. Required Gargul hook surface is still assumption-backed, not fixture/prototype-proven for the pinned build.
- Path: _bmad-output/initiative-preloot/architecture-raid-loot-distribution/architecture-raid-loot-distribution.md
- Why this blocks: AD-5/AD-6 behaviors depend on hooks/fields that are deferred pending prototype proof.
- Fast fix: add a release-gate artifact in review evidence: pinned native export fixture + hook matrix (available/missing) for `v8.0.1-forever/interface16001`.

2. Native export field completeness for strict AD-6 validation (especially checksum + roll payload invariants) remains unproven for all expected award scenarios.
- Path: _bmad-output/initiative-preloot/architecture-raid-loot-distribution/architecture-raid-loot-distribution.md
- Why this blocks: strict import contract can reject legitimate native records unless exact field availability/shape is demonstrated.
- Fast fix: define fixture-backed acceptance shape and explicit reject/remediation behavior for missing fields before implementation.

### Minor
1. WoWSims Forever is correctly labeled candidate, but first-tier coverage sufficiency is still open.
- Path: _bmad-output/initiative-preloot/architecture-raid-loot-distribution/architecture-raid-loot-distribution.md
- Why this matters: Gain-input availability could delay workbook initialization for the first tier.
- Fast fix: capture a simple per-class/spec coverage checklist for the three first-tier raids.
