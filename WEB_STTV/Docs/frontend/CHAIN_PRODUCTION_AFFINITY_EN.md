# Technology chains — production bonus affinity

## Contents

- [Status and selection order](#status-and-selection-order)
- [Relation evidence](#relation-evidence)
- [Conditions and witnesses](#conditions-and-witnesses)
- [Candidate selection](#candidate-selection)
- [Metallurgical production example](#metallurgical-production-example)
- [Scope and related documents](#scope-and-related-documents)

## Status and selection order

Approved by the user on 2026-11-18. The criterion follows the previously agreed functional affinity criteria. With the subsequent addition of [object capacity affinity](CHAIN_CAPACITY_AFFINITY_EN.md), the adjacent stages are indirect functional affinity → production bonus affinity → object capacities → empire filter → seniority by game tier.

This decision is intended for the future specification. This iteration changes documentation; product code and the preceding research calculation remain unchanged.

## Relation evidence

If technology `T` has its own modifier improving an economic category's production, and remaining candidate `P` unlocks an object providing jobs in that category, this confirms functional affinity.

The evidence path is:

1. `T` has a production bonus in its own `modifier`.
2. The bonus is associated with a specific economic category by its ID and modifier generation rules.
3. A job's production belongs to that category through `resources.category`.
4. A building or another supported object provides that job, as confirmed by its game fields.
5. `P` unlocks that object according to game requirements.

This criterion does not require `T` itself to unlock an object: its own bonus supplies the initial evidence. Technology names and predetermined ID pairs do not select the result.

## Conditions and witnesses

- Compare the specific economic category and an improvement to its production. Costs and resource consumption alone do not confirm this relation.
- Associate the modifier with a category using the data and its generation rules. Arbitrary string similarity does not replace this check.
- Preserve the bonus context and sign, job provision conditions and object access conditions. Conditional evidence is not presented as unconditional; evaluating a live game empire is not required.
- Use the active effects of the selected technology representation, accounting for `technology_swap` and `inherit_effects`.
- Evidence records the modifier, category, job, providing object, candidate technology and source references for each link.

## Candidate selection

Apply this rule only to the current candidate set `C` when it contains more than one technology.

1. Collect set `M` of candidates with confirmed production affinity.
2. If `M` contains one candidate, select it and stop.
3. If it contains multiple candidates, replace `C` with `M` and proceed to the object capacity criterion.
4. If `M` is empty, retain `C` and proceed to the object capacity criterion.

Previously eliminated candidates do not return. The number of jobs, buildings or witnesses gives no additional votes. All original game prerequisites are preserved.

## Metallurgical production example

Checked against current Stellaris 4.5.4 data:

| Link | Evidence |
| --- | --- |
| Ceramo-Metal Alloys (`tech_advanced_metallurgy_1`) | Own bonus `planet_metallurgists_produces_mult = 0.05`. |
| Economic category `planet_metallurgists` | Its definition contains `generate_mult_modifiers = { produces upkeep }`, confirming production modifier generation. |
| Job `foundry` | Its `resources.category` is `planet_metallurgists`. |
| Building `building_foundry_2` | After expansion it provides the job through `job_foundry_add` inside `triggered_planet_modifier`; retain that block's conditions. |
| Holographic Casts (`tech_alloys_1`) | Listed in the building's requirements. |

The other candidate, Ceramo-Metal Materials (`tech_ship_armor_2`), does not confirm this production relation. The expected outcome for the reviewed case is **Ceramo-Metal Alloys → Holographic Casts**.

Sources: [technology bonus](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2862), [category](E:/SteamLibrary/steamapps/common/Stellaris/common/economic_categories/01_job_categories.txt:274), [job](E:/SteamLibrary/steamapps/common/Stellaris/common/pop_jobs/02_specialist_jobs.txt:2514), [building](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/04_manufacturing_buildings.txt:94).

## Scope and related documents

The subsequent [complete analytical pass dated 2026-11-19](CHAIN_RULES_FULL_REVIEW_EN.md) confirmed Holographic Casts as the parent of Ceramo-Metal Alloys. Counts and verification scope are documented in the separate report.

This rule extends analysis to technologies' own production bonuses. Configuration formats and supported job provision forms remain to be specified in the implementation specification. This document does not claim an updated full run or new totals.

- [General chain rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [Indirect functional affinity](CHAIN_INDIRECT_AFFINITY_EN.md).
- [Effects and functions dictionary](../semantics/FUNCTIONAL_EFFECTS_EN.md).
- [Русская версия](CHAIN_PRODUCTION_AFFINITY_RU.md).
