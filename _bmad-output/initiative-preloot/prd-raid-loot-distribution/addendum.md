# Discovery Addendum: Loot Allocation Rules

This addendum preserves the user's supplied flowchart and supporting detail for downstream PRD decisions. The chart image is retained in this run folder as `3178ce18-21f4-43dc-b5aa-b41c73de0b3f.png`; confirmed rules are reflected in the PRD, and unresolved choices remain listed there.

## Allocation Flowchart (Working Transcription)

When loot drops, classify it as a tier set item, BiS item, impact item, or normal item. Normal items are those that are not tier set, BiS, or impact.

- **Tier set item:** roll after tank priority. The user clarified tank priority as MT1 first, then MT2.
- **BiS item:** BiS assignments are configured by the owner for each phase, potentially using an external source such as wowtbc.gg. Any BiS-eligible Raider who rolls has priority over every non-BiS Raider who rolls, regardless of their ratio. Among BiS-eligible Raiders, the ratio `(BiS Presence / BiS Presence Max) / (BiS loots received since reset + 1)` determines priority; equal ratios are resolved manually using Gargul's roll value. BiS Presence counts attended raids plus bench appearances since the latest reset; BiS Presence Max is the number of possible raids since that reset. The chart shows `+2` for a non-BiS candidate; this means BiS candidates have priority, not that the ratio receives a two-point bonus. If no candidate has the item as BiS, interested Raiders roll without ratio impact. BiS items cannot be passed; when awarded as BiS, their ratio is impacted. If the owner marks a BiS award as Impact in Gargul, the BiS Ratio is unchanged and only Impact scoring/count state is updated. No exceptional class-priority rule is modeled; rare exceptions are handled manually during the raid.
- **Impact item:** eligible classes are configured by the owner in the tool. The impact score is `(Tier Presence / Tier Presence Max) * Average parse * Gain / (Impact items already received + 1)`. Tier Presence counts attended raids plus bench appearances across the active tier; Tier Presence Max is the number of possible raids in that tier. Average parse is the player's Warcraft Logs DPS average, with a missing parse treated as `1`; Gain is percent DPS/HPS increase. Tanks have no impact metric because they have priority across their loot table. If complete impact scores are identical, resolve by roll; Gain is a factor in the score, not a separate tie-break. The BiS attendance reset does not change Tier Presence. At a new-tier transition, the owner chooses whether Impact Item counts carry over or reset.
- **Tier set item:** roll among eligible classes after tank priority. Tier sets are distinct from class-bound items but treated similarly. Tank priority is MT1 first, then MT2.
- **Class-bound token / item:** roll among eligible classes after tank priority.

Three weeks after a new raid tier begins, BiS attendance and BiS-loot count restart; Tier Presence continues across the full active tier. Completed-tier data can be archived read-only for reference and cannot be restored into an active tier. The owner chooses whether Impact Item counts carry into the next active tier or reset.

## Raider-Facing Export

The user wants a Google Sheets export that can be shared with the raid team and show each raider's ratios, impact-priority rank, which items are BiS, impact, or alt-BiS, and the simmed gain of an impact item for the relevant class/spec. The purpose is to make allocation decisions understandable before loot is awarded during the raid.

## Product Surface and Persistence Preference

For v1, the user is open to completing the workflow entirely through Google Sheets. The preferred eventual experience is a desktop app with a graphical interface for setup, local JSON-file persistence, and no hosting costs. Google CLASP was suggested as a possible implementation aid; this is a technical consideration for downstream architecture, not a product requirement.

## Raid-Night Integration (Confirmed MVP Direction)

- The owner alone uses an enhanced Lua/Gargul interface; raiders continue using the default Gargul interface and are not asked to install an additional tool.
- The owner keeps Google Sheets open on a second screen to identify an item's category and allocation context. The addon does not know, look up, or classify item types.
- Gargul remains the loot-distribution interface. The enhanced interface displays Gargul's roll value, BiS Ratios, and Impact Scores live; the owner consults Sheets and decides which signal to consider for the item.
- The owner manually makes each loot award through Gargul. During rolls, Gargul shows the roll type (BiS/non-BiS) and roll value; the enhancement shows the BiS Ratio and Impact Score. The owner consults Sheets to choose which signal applies.
- Any category-related treatment, such as marking a BiS award as Impact, must be explicitly selected by the owner. The addon records that input rather than inferring it from the item.
- Before each raid, the owner exports current Sheets data as JSON and loads it into Gargul. During the raid, the enhanced interface updates its working ratio and score state live, and later rolls use the updated values. After the raid, the owner exports all loot attributions as JSON and imports them into Sheets to update roster ratios and scores.
- The shared Sheets view is the raider-facing source for roster ratios, rankings, item status, and simmed gains. It is not updated live during the raid; the JSON handoff occurs before and after the raid.
- The owner ensures each raid export is imported only once and manually edits the JSON before import to correct an award. The MVP does not check for duplicate uploads or reconcile corrections.
- MVP success means no bugs in live ratio/score updates or JSON import/export, and clear, understandable data in Sheets.

## Future-Direction Notes in the Chart

- Tank loot may become free for the MT2 so they can optimize a DPS set.
- DPS loot may also become free for healers.

These are marked as future directions in the chart, not confirmed v1 requirements.

