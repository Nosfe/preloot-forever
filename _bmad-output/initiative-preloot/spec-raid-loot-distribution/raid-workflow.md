# Raid Workflow

## Sheets

The owner manually maintains the roster, Impact Items, Warcraft Logs parses, and per-phase BiS lists. Warcraft Logs raid links update matched attendance; bench appearances are entered manually. Unmatched participants are ignored and can be corrected by the owner. A Raider counts as attending only when present for strictly more than 25% of the raid's completed boss fights (kills and wipes); an alt listed in the Rerolls sheet credits its main's attendance but never its loot.

Raiders receive view-only access to three tabs:

- Roster: raider name, role, Presence, bench/attendance basis, and BiS Ratio.
- Impact Items: attribution priority and score breakdown.
- Per-spec items: equipment slots, BiS/alt-BiS/Impact status, and class/spec simmed gain.

## Gargul and JSON

1. Before a raid, the owner exports current Sheet state as JSON and loads it into the owner-only Gargul enhancement.
2. During rolls, Gargul shows roll type/value; the enhancement displays BiS Ratios and Impact Scores. It has no item-type knowledge and does not choose which signal applies. The owner consults Sheets and makes each award manually. Updates affect subsequent rolls.
3. If the owner marks a BiS award as Impact, BiS Ratio remains unchanged and Impact state updates.
4. After the raid, the owner exports the raid's awards from Gargul (Custom JSON-per-line export, with roll type and the owner's BIS/IMPACT/NONE choice) and imports them once into Sheets. Off-spec, disenchanted, and pattern/design awards never change loot counts. The owner manually edits the JSON when correcting an award; the system does not deduplicate uploads.
5. Malformed JSON imports are rejected without changing existing data.

For MVP, Google Sheets plus the owner-only Lua/Gargul enhancement is acceptable. A local desktop GUI with local JSON persistence and no hosting cost is a future preference, not an MVP requirement. The owner's existing `zambelaba/Gargul_Preloot` repo (addon and Apps Script) is the base to evolve for WoW Forever; Google CLASP remains an optional development aid.