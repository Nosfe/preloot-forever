# Allocation Rules

**Source flowchart:** [original allocation diagram](../prd-raid-loot-distribution/3178ce18-21f4-43dc-b5aa-b41c73de0b3f.png)

## Presence Windows

- **Tier Presence:** attended raids plus bench appearances since the latest BiS reset.
- **Normalized Tier Presence:** `Tier Presence / Tier Presence Max`.
- **Lifetime Presence:** attended raids plus bench appearances across all tiers, archived tiers included.
- **Normalized Lifetime Presence:** `Lifetime Presence / Lifetime Presence Max`.
- Each Presence Max counts possible raids in its window and initializes to `1` when none are possible.

## BiS

`BiS Ratio = Normalized Tier Presence / (BiS loots received since reset + 1)`.

Any BiS-eligible Raider who rolls outranks every non-BiS roller regardless of ratio. BiS candidates rank by BiS Ratio; exact ties are decided manually using Gargul's roll value. If no candidate has the item marked BiS, interested Raiders roll without BiS Ratio impact. BiS items cannot be passed. The BiS reset happens only when the owner activates a new tier, between raids; Tier Presence and the BiS-loot count restart, while Lifetime Presence continues. There is no reset inside a tier (owner decision 2026-10-22). An Impact-marked BiS award leaves BiS Ratio unchanged.

## Impact

`Impact Score = Normalized Lifetime Presence * DPS Warcraft Logs average parse * item gain / (Impact Items already received + 1)`.

- **Item gain** is the dropped item's Gain (%) for the roller's spec on that role's Objets tab, entered by the owner (possibly from WoWSims Forever). It is stored as a fraction.
- The score applies only when the dropped item's Statut for the roller's spec is **IMPACT**. Otherwise the roller has no Impact Score for that item.
- Roster shows the raider part without the item gain: **Impact (sans gain objet)** = `Normalized Lifetime Presence * parse / (Impact Items + 1)`.
- Gargul shows the full score for each roller when an item drops.
- A missing DPS parse is `1`. Tanks have no Impact Score. Identical complete scores resolve by roll.
- At a new-tier transition, the owner chooses whether Impact Item Count carries over or resets.

## Other Item Categories

- Each item has one Statut per spec: `BIS`, `IMPACT`, `CLASS_BOUND`, or `NORMAL`.
- Class-Bound items, tier set pieces included, are rolled among eligible classes. There is no tank priority.
- Rare class-priority exceptions are handled manually and are not encoded in the product.
- Off-spec and disenchanted awards never change BiS or Impact loot counts. The owner marks pattern/design awards `NONE`.

## Owner Decision

The owner decides who receives each item, even against the displayed ratio, score, or roll. Displayed values only inform that decision; nothing awards loot automatically.

## Deferred User Notes

- The source chart considers free tank loot for MT2 to improve a DPS set and free DPS loot for healers; neither rule is part of the MVP.