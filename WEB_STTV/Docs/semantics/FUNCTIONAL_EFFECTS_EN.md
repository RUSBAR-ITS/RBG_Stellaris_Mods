# Dictionary — effects and function

## Contents

- [Effect containers](#effect-containers)
- [Economic fields](#economic-fields)
- [Specific modifiers](#specific-modifiers)
- [Capacity usage fields](#capacity-usage-fields)
- [Using the evidence](#using-the-evidence)
- [Sources](#sources)

## Effect containers

| Keyword | Context and form | Meaning and use | Sources |
| --- | --- | --- | --- |
| `modifier` | Technology; modifier block | Technology bonuses. Its contents help identify what the technology improves. | F1, F4 |
| `modifier` | Component; modifier block | Stats documented as displayed in the ship designer. The block name alone does not make them country modifiers. | F2 |
| `ship_modifier` | Component; modifier block | Effects on the ship, such as armor hardening. | F2, F3 |
| `triggered_station_modifier` | Starbase building; block with `potential`, modifiers and an optional multiplier | Conditional effects on the station. Preserve the condition and magnitude; a key's presence does not imply an unconditional bonus. | F5 |
| `feature_flags` | Technology; list of capability IDs | Unlocked game capabilities, such as `megaengineering`. A flag's function is established from its uses, not guessed from its name. | F1 |

## Economic fields

| Keyword | Context and form | Meaning and use | Sources |
| --- | --- | --- | --- |
| `resources` | Object; structured block | Economic parameter container. Preserve categories, cost, production, upkeep and conditions separately. | F3, F6 |
| `category` | Inside `resources`; economic category ID | Grouping for economic accounting and modifiers. Not a scientific technology category. | F6 |
| `produces` | Inside `resources`; resource/value block, sometimes conditional | Produced resources. Evidence of an object's production function; blocks may repeat with different conditions. | F6 |
| `upkeep` | Inside `resources`; resource/value block | Maintenance expenditure. Consuming crystals does not make an object part of crystal production technology. | F3, F6 |
| `cost` | Inside `resources`; resource/value block | Creation or action cost in the object's context. Not the research cost in `technology.cost`. | F3 |

## Specific modifiers

Values in these examples are numeric and can use static variables in the source. Modifiers describe stats and bonuses, not technology references.

| Keyword | What it changes | Potential evidence of function | Sources |
| --- | --- | --- | --- |
| `ship_armor_hardening_add` | Ship armor hardening | Protecting armor against bypassing attacks; affinity between armor components. | F3 |
| `ship_cloaking_detection_add` | Cloaking detection | Shared function of the detection module and its enhancing building. | F5, F7 |
| `planet_metallurgists_produces_mult` | Production multiplier for the corresponding metallurgist economic category | Improving metallurgical production. | F4 |
| `starbase_upgrade_cost_mult` | Starbase upgrade cost multiplier | Developing starbase infrastructure. | F4 |
| `starbase_upgrade_speed_mult` | Starbase upgrade speed multiplier | The same construction function through speed. | F4 |
| `country_starbase_capacity_add` | Additive country starbase capacity bonus | Relation to objects using this capacity; mappings to their fields belong in configuration. | F1, F8 |

## Capacity usage fields

| Keyword | Context and form | Meaning and use | Sources |
| --- | --- | --- | --- |
| `starbase_capacity_used` | Starbase level in `starbase_levels`; number | Starbase capacity used by the object. A positive value confirms the relation to that capacity. This is an object field, not a country modifier. | F8, F9 |
| `ship_size` | Starbase level; hull ID | Links the capacity usage definition to a hull in `ship_sizes`; its requirements identify the unlocking technology. | F8, F9, F10 |

## Using the evidence

A matching specific modifier provides stronger evidence than a broad “ship-related” label, but can occur in multiple nonadjacent technologies. It is input to the agreed selection criteria, not an already established `parent_tech` link.

Comparison must preserve target context, sign and bonus conditions. A `modifier` inside `weight_modifier` changes selection weight; it is not a researched technology bonus. Effects of the selected `technology_swap` must account for `inherit_effects`.

The approved [functional group rule](../frontend/CHAIN_FUNCTIONAL_GROUPS_EN.md) describes deriving function from combinations of unlocked object features. The first example uses `ship_sizes`, speed and combat roles. This is an anchor selection rule for future implementation, not an extension of parser syntax.

[Indirect affinity](../frontend/CHAIN_INDIRECT_AFFINITY_EN.md) through a candidate's original prerequisites is approved separately, with an initial depth of one transition. The example uses `ship_armor_hardening_add` in hardening and armor components; context and sign match while bonus magnitudes differ.

`feature_flags` and economic categories contain IDs of other game concepts. This dictionary explains the reference role without claiming that all flag consumers or economic formulas have been evaluated.

A technology's own production bonuses participate in a separate [affinity criterion through an economic category, jobs and their providing objects](../frontend/CHAIN_PRODUCTION_AFFINITY_EN.md). The example connects `planet_metallurgists_produces_mult` to the `resources.category` of job `foundry` and building `building_foundry_2`.

The approved [object capacity affinity criterion](../frontend/CHAIN_CAPACITY_AFFINITY_EN.md) follows it, immediately before the empire filter. The example links Mega-Engineering's own `country_starbase_capacity_add` bonus to `starbase_capacity_used > 0`, then through `ship_size` to hull requirements. This is an explicit configured mapping, not automatic interpretation of every key containing `capacity`.

## Sources

- [F1 — Mega-Engineering capabilities and bonuses](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_megastructures.txt:20).
- [F2 — component modifier and ship_modifier documentation](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/000_documentation.txt:12).
- [F3 — armor hardener cost and effect](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:250).
- [F4 — starbase upgrade modifiers](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:1615); [metallurgy modifier](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2862).
- [F5 — conditional detection enhancement](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_buildings/00_starbase_buildings.txt:2382).
- [F6 — job economy, repeated produces blocks and conditions](E:/SteamLibrary/steamapps/common/Stellaris/common/pop_jobs/02_specialist_jobs.txt:84).
- [F7 — detection module](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_modules/00_starbase_modules.txt:282).
- [F8 — Citadel capacity usage and hull](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_levels/00_starbase_levels.txt:68).
- [F9 — arkship capacity usage and hull](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_levels/06_arkship_levels.txt:34).
- [F10 — Citadel hull technology requirement](E:/SteamLibrary/steamapps/common/Stellaris/common/ship_sizes/00_starbases.txt:502).

[Dictionary index](README_EN.md) · [Русская версия](FUNCTIONAL_EFFECTS_RU.md).
