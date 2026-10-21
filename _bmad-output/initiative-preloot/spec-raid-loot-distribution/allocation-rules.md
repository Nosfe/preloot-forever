# Allocation Rules

**Source flowchart:** [original allocation diagram](../prd-raid-loot-distribution/3178ce18-21f4-43dc-b5aa-b41c73de0b3f.png)

## Presence Windows

- **Tier Presence:** attended raids plus bench appearances across the active tier.
- **Normalized Tier Presence:** `Tier Presence / Tier Presence Max`.
- **BiS Presence:** attended raids plus bench appearances since the latest BiS reset.
- **Normalized BiS Presence:** `BiS Presence / BiS Presence Max`.
- Each Presence Max counts possible raids in its window and initializes to `1` when none are possible.

## BiS

`BiS Ratio = Normalized BiS Presence / (BiS loots received since reset + 1)`.

Any BiS-eligible Raider who rolls outranks every non-BiS roller regardless of ratio. BiS candidates rank by BiS Ratio; exact ties are decided manually using Gargul's roll value. If no candidate has the item marked BiS, interested Raiders roll without BiS Ratio impact. BiS items cannot be passed. Once three weeks into a new tier, the owner triggers the BiS reset between raids; BiS Presence and the BiS-loot count restart. An Impact-marked BiS award leaves BiS Ratio unchanged.

## Impact

`Impact Score = Normalized Tier Presence * DPS Warcraft Logs average parse * simmed percent DPS/HPS gain / (Impact Items already received + 1)`.

Impact Score belongs to the Raider, not the dropped item. The owner configures one Raider-level simulated percent DPS/HPS gain for the active tier in Sheets (potentially from WoWSims Forever), alongside eligible classes, Impact Items, and parses. The per-spec item-gain view is separate; Gargul displays each rolling Raider's existing Impact Score and BiS Ratio without looking up the dropped item's gain or classification. A missing DPS parse is `1`. Tanks use tank priority across their loot table and have no Impact Score. Identical complete scores resolve by roll. At a new-tier transition, the owner chooses whether Impact Item Count carries over or resets; the BiS attendance reset does not change Tier Presence.

## Other Item Categories

- Tier Set Items and Class-Bound Items are rolled among eligible classes after tank priority; MT1 precedes MT2.
- Normal items are neither Tier Set, BiS, nor Impact.
- Rare class-priority exceptions are handled manually and are not encoded in the product.
- Off-spec, disenchanted, and pattern/design awards never change BiS or Impact loot counts.

## Deferred User Notes

- The source chart considers free tank loot for MT2 to improve a DPS set and free DPS loot for healers; neither rule is part of the MVP.