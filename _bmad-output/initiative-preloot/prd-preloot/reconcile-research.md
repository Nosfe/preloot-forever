# Reconciliation: feasibility research vs PRD

Source: `../research-preloot-data-sources-feasibility/` (main report + 4 digests). 12 gaps found. Disposition below.

| # | Gap | Disposition |
|---|-----|-------------|
| 1 | wowtbc.gg phase flags, wowsims phases and Anniversary phases are not mapped | Autofixed: §3 Glossary Phase mapping |
| 2 | Bulk sim returns DPS only; the source of HPS is unclear | Autofixed: §8 OQ3 |
| 3 | Name→ID match rate unknown (170/448 items have IDs) | Autofixed: FR-3 match-rate report |
| 4 | WowSimsExporter JSON schema unverified | Ignored: raider gear is out of v1 scope |
| 5 | Warcraft Logs not researched; no fallback | Autofixed: FR-8 unresolved-tie fallback; details remain in §8 OQ2 |
| 6 | Too many paired-slot combinations; cap suggested | Ignored: the user accepted long runs with no cap |
| 7 | P4 launch date uncertain | Ignored: PreLoot is meant to run before a phase launches |
| 8 | Heroic/normal disambiguation not verified | Already covered by the FR-3 assumption |
| 9 | Healer alpha label and test run | Already covered by FR-9 and §8 OQ3 |
| 10 | db.json phase filter not specified | Autofixed: FR-3 phase-bounded matching |
| 11 | MIT attribution not in output | Autofixed: FR-9 source credits |
| 12 | CSV schema undefined | Autofixed: FR-7 columns |
