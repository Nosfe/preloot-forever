# Flowchart Reconciliation

**Input:** [3178ce18-21f4-43dc-b5aa-b41c73de0b3f.png](3178ce18-21f4-43dc-b5aa-b41c73de0b3f.png)

## Confirmed and represented

- Class-bound items and tier sets go to eligible classes after tank priority; MT1 precedes MT2.
- For BiS items, any BiS-eligible Raider who rolls outranks non-BiS Raiders, regardless of ratio. BiS candidates rank by BiS Ratio; exact ties are decided manually with Gargul's roll value.
- Non-BiS/no-BiS candidates roll without BiS Ratio impact. BiS items cannot be passed.
- BiS Ratio uses attendance since the latest reset and resets its attendance baseline and BiS-loot count three weeks into a new tier. A BiS award marked Impact leaves BiS Ratio unchanged and updates Impact state instead.
- Impact Scores use whole-tier attendance, DPS Warcraft Logs average parse, simmed percent gain, and prior Impact Item count. Missing parse is `1`; identical complete scores are resolved manually by roll. Impact attendance is not reset with BiS attendance.
- The owner handles rare priority exceptions manually; the product does not encode an exception path.
- The two future tank/healer loot ideas remain outside confirmed MVP scope.

## Clarifications applied

- The user clarified separate attendance values: BiS uses attendance/bench since its reset; Impact uses whole-tier attendance. Each is normalized by its own possible-raid count.
- The chart's `+2` is priority for a BiS-eligible Raider, not a literal two-point bonus.
- Impact Item Count carryover is owner-configurable at a tier transition; completed-tier archives are read-only and non-restorable.
- The Gargul enhancement displays roll value, BiS Ratio, and Impact Score but does not identify item type or choose which signal governs. The owner consults Sheets.

No material flowchart details remain unresolved for the current PRD scope.