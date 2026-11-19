# Technology chains — object capacity affinity

## Contents

- [Status and selection order](#status-and-selection-order)
- [Relation evidence](#relation-evidence)
- [Conditions and witnesses](#conditions-and-witnesses)
- [Candidate selection](#candidate-selection)
- [Mega-Engineering example](#mega-engineering-example)
- [Scope and related documents](#scope-and-related-documents)

## Status and selection order

Approved by the user on 2026-11-18. The criterion runs **immediately before the empire filter**, after production bonus affinity. The adjacent stages are indirect functional affinity → production bonuses → object capacities → empire filter → seniority by game tier.

This decision is intended for the future specification. This iteration changes documentation; product code, databases and the preceding research calculation remain unchanged.

## Relation evidence

If technology `T` has its own modifier increasing an object capacity, and remaining candidate `P` unlocks an object using that capacity, this confirms functional affinity.

The evidence path is **modifier → increased capacity → object using it → candidate technology unlocking the object**. This does not require `T` itself to unlock an object.

Mappings between modifiers, object types and game fields belong in configuration. The first confirmed example maps `country_starbase_capacity_add` to `starbase_levels.starbase_capacity_used > 0`; the `ship_size` field links the starbase level to a hull in `ship_sizes`, whose `prerequisites` link it to the candidate technology.

Technology names, similar labels and predetermined ID pairs do not establish the selection. This is an analytical criterion for the reference tool, not a claim that the game defines a unique parent.

## Conditions and witnesses

- Confirm an increase to a specific capacity and the object's use of that same capacity. An arbitrary modifier containing the word `capacity` does not automatically gain this relation.
- Use the selected technology representation's own effects, accounting for `technology_swap` and `inherit_effects`; selection weight modifiers are not research bonuses.
- Preserve context, bonus sign, capacity usage conditions and object access conditions. Conditional relations are not presented as unconditional; the live empire's object count is not evaluated.
- Evidence contains the modifier, configured mapping, capacity usage fields, intermediate object references, candidate and sources for each link.
- An unknown mapping supplies no evidence and is not replaced by an ID-based guess.

## Candidate selection

Apply the rule only to the current candidate set `C` when it contains more than one technology.

1. Collect set `M` of candidates with confirmed object capacity affinity.
2. If `M` contains one candidate, select it and stop.
3. If it contains multiple candidates, replace `C` with `M` and proceed to the empire filter.
4. If `M` is empty, retain `C` and proceed to the empire filter.

Previously eliminated candidates do not return. The number of objects or witnesses gives no additional votes. All original game prerequisites and their logic are preserved.

## Mega-Engineering example

Checked against current Stellaris 4.5.4 data:

| Link | Evidence |
| --- | --- |
| Mega-Engineering (`tech_mega_engineering`), tier 5 | Own bonus `country_starbase_capacity_add = 3`. |
| Citadel | `starbase_level_citadel` specifies `starbase_capacity_used = 1` and `ship_size = starbase_citadel`. The hull requires `tech_starbase_5`, tier 4. |
| Third-class arkship | For example, `starbase_level_civilian_arkship_3` contains `starbase_capacity_used = 1` and `ship_size = civilian_arkship_tier_3`; the hull requires `tech_arkship_tier_3`. |
| Battleships (`tech_battleships`), tier 4 | Its unlocked hulls do not confirm starbase capacity usage. |

Before empire filtering, the reviewed case retains `tech_arkship_tier_3`, `tech_battleships` and `tech_starbase_5`. The new criterion retains `tech_arkship_tier_3` and `tech_starbase_5`. The agreed standard nonnomadic empire profile then excludes the nomadic option. Expected outcome: `tech_mega_engineering.parent_tech = tech_starbase_5`, giving the chain **Citadel → Mega-Engineering**.

Sources: [technology bonus](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_megastructures.txt:25), [Citadel level](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_levels/00_starbase_levels.txt:68), [its hull requirement](E:/SteamLibrary/steamapps/common/Stellaris/common/ship_sizes/00_starbases.txt:502), [arkship level](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_levels/06_arkship_levels.txt:34), [its hull requirement](E:/SteamLibrary/steamapps/common/Stellaris/common/ship_sizes/29_nomads_dlc_ships.txt:448).

## Scope and related documents

The subsequent [complete analytical pass dated 2026-11-19](CHAIN_RULES_FULL_REVIEW_EN.md) confirmed narrowing Mega-Engineering's candidates to Citadel and arkship, followed by the empire filter selecting Citadel. Counts and verification scope are documented in the separate report.

The mapping configuration format and full supported capacity list remain to be specified in the implementation specification. Confirming this example is not a full database rerun and does not change the previous study's totals.

- [General chain rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [Preceding criterion — production bonuses](CHAIN_PRODUCTION_AFFINITY_EN.md).
- [Effects and functions dictionary](../semantics/FUNCTIONAL_EFFECTS_EN.md).
- [Русская версия](CHAIN_CAPACITY_AFFINITY_RU.md).
