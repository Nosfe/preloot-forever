# Raid Workflow

## Sheets

The owner manually maintains the roster (class, spec, role, parse), Rerolls, and, per item, one Statut and Gain (%) for each spec on the Objets tabs. Warcraft Logs raid links write `1` for matched attendance in the raid's row of the Présence tab; the owner types `B` for bench. Unmatched participants are ignored and can be corrected by the owner. A Raider counts as attending only when present for strictly more than 25% of the raid's completed boss fights (kills and wipes); an alt listed in the Rerolls sheet credits its main's attendance but never its loot.

Raiders receive view-only access to the workbook:

- Roster: raider, raid group, class, spec, role, parse, Tier Presence, BiS Ratio, and Impact (sans gain objet).
- Rerolls: alts and their main.
- Présence: one row per raid, one column per raider (`1` present, `B` bench, `0` absent).
- Raids: raid ID, instance, date, imported Warcraft Logs reports.
- Awards: one block per raider listing their loot and its treatment.
- Objets Tank / Heal / Melee DPS / Ranged DPS / Caster DPS: per item, a Statut and Gain (%) for each spec of that role.

## Gargul and JSON

1. Before a raid, the owner exports current Sheet state, including the Objets item table, as JSON and loads it into the owner-only Gargul enhancement.
2. During rolls, Gargul shows roll type/value; the enhancement displays each roller's BiS Ratio and, when the dropped item's Statut for the roller's spec is IMPACT, the full Impact Score. It reads the owner's Statut and gain but never classifies an item or chooses which signal applies. The owner decides every award, even against the displayed values. Updates affect subsequent rolls.
3. If the owner marks a BiS award as Impact, BiS Ratio remains unchanged and Impact state updates.
4. After the raid, the owner exports the raid's awards from Gargul (Custom JSON-per-line export, with roll type and the owner's BIS/IMPACT/NONE choice) and imports them once into Sheets. Off-spec and disenchanted awards never change loot counts; the owner marks pattern/design awards NONE. The owner manually edits the JSON when correcting an award; the system does not deduplicate uploads.
5. Malformed JSON imports are rejected without changing existing data.

For MVP, Google Sheets plus the owner-only Lua/Gargul enhancement is acceptable. A local desktop GUI with local JSON persistence and no hosting cost is a future preference, not an MVP requirement. The owner's existing `zambelaba/Gargul_Preloot` repo (addon and Apps Script) is the base to evolve for WoW Forever; Google CLASP remains an optional development aid.