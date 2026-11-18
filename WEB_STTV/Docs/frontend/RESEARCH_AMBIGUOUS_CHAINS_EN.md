# Stellaris Technological Tree View — analysis of 39 ambiguous continuations

## Contents

- [Research scope](#research-scope)
- [Signal evaluation](#signal-evaluation)
- [Preserving independent chains](#preserving-independent-chains)
- [Explicit object upgrade links](#explicit-object-upgrade-links)
- [All cases](#all-cases)
- [Proposals for discussion](#proposals-for-discussion)
- [Artifacts and verification](#artifacts-and-verification)

## Research scope

Research dated 2026-11-17, requested by the user. All 39 technologies with multiple prerequisite candidates after matching both `area` and `category` were examined. The main input is `data/stage10/database.json`.

Localized names, shared ID prefixes and numeric suffixes are not used to identify continuations. IDs are opaque reference keys. Names in the table are included only for readability.

Installed game component and building definitions were also read, with selected called scripts and other objects inspected for individual cases. These additional data are absent from the current technology database. The database, product code and game files were unchanged. The results below are observations and proposals, not newly approved sorting rules.

Subsequent user decision dated 2026-11-17: mandatory prerequisite priority was approved as [L-08](TECHNOLOGY_CHAINS_AND_SORTING_EN.md#mandatory-prerequisite-priority). It resolves five additional cases: together with the 21 cases supported by object upgrades or matching effects, there is a basis for selection for 26 technologies; 13 remain ambiguous. References to a possible rule in the original table reflect research before this decision. Programmatic use of upgrades separately requires component and building databases and frontend support for three databases.

## Signal evaluation

| Signal | Result across 39 cases | Limitation |
| --- | --- | --- |
| Prefer the prerequisite with the highest `tier` | One candidate in 19 cases | Selects thrusters for afterburners and reactors for reactor boosters. Does not identify a family. |
| The predecessor has no other continuation with a unique same-area/category candidate | One candidate in 19 cases | Selects AI for sapient combat computers despite explicit component upgrades from earlier combat computers. |
| The predecessor has only one dependent in the same area/category | One candidate in 24 cases | Selects `tech_alloys_2` for durasteel alloys despite the shared production modifier connecting them to the earlier metallurgy technology. |
| Shared actual modifier keys | One candidate in 6 cases | Useful evidence of shared effects; most technologies act through unlocked objects rather than their own `modifier`. |
| Equal nonempty `potential` structure | One candidate in 14 cases | Shared eligibility restrictions are not a shared family. Includes the unwanted AI candidate for combat computers. |
| `gateway`, `feature_flags`, `weight_groups` | No matching continuation distinguished | None of the 39 has `gateway`; only mega-engineering has its own `feature_flags`; only the two repeatables have `weight_groups`. |
| Only directly mandatory prerequisite among matching candidates | 5 of the 11 cases involving `OR` | Could justify a layout preference. The game does not declare it the main family continuation. |
| Explicit upgrade of an unlocked component or building | Pairs confirmed for 16 technologies: 12 through components, 4 through buildings | Requires additional directories; positive evidence rather than a complete audit of all possible unlocks. |

Modifier matching compares exact keys, not lexical similarity. Administrative `description`, `custom_tooltip` and description parameters are not game effects. The six matches are `tech_advanced_metallurgy_2`, `tech_consumer_good_refinement_2`, `tech_cryostasis_2`, `tech_habitat_3`, `tech_robomodding_points_2` and `tech_xeno_relations`. Modifier and object-upgrade evidence overlap, so their counts cannot simply be added.

Separate evidence for `tech_capital_productivity_3` was found outside its technology definition: in `common/inline_scripts/buildings/on_all_capital_buildings.txt:69`, successive technology conditions switch `pop_bonus_workforce_mult` from 0.05 to 0.10 and 0.15 depending on capital tier. This supports continuation from `tech_capital_productivity_2`. The technology itself only contains a description key for this effect.

## Preserving independent chains

The user's example is supported by the structure:

```text
tech_thrusters_1 -> tech_thrusters_2 -> tech_thrusters_3 -> tech_thrusters_4
        |
        +--------> tech_afterburners_1 -----------------> tech_afterburners_2

Additional requirement: tech_thrusters_3 -> tech_afterburners_2
```

The only prerequisite of `tech_thrusters_4` is `tech_thrusters_3`. The only continuation of `tech_afterburners_1` is `tech_afterburners_2`. Keeping both continuations avoids breaking either the thruster branch or the afterburner branch.

Two versions of this idea were tested:

1. **Locally excluding a reserved predecessor.** For each vertex, identify dependent technologies for which it is the sole candidate after matching area/category. With multiple prerequisites, prefer a predecessor without such other continuations. One candidate remains in 19 cases. This is a heuristic, not proof of branch membership.
2. **Selecting continuations jointly across the graph.** The experimental objective is to keep as many continuations as possible, allowing at most one main incoming and one main outgoing continuation per technology. Other dependencies remain additional links. Across 679 technologies and 483 eligible links, the maximum is 294 continuations, or 385 paths including isolated vertices. Each parent's feasibility and the possibility of starting a separate path were checked at the same maximum, rather than inspecting just one solution. In 18 of the 39 cases, the parent is the same in every optimum.

Both approaches select `tech_afterburners_1` for `tech_afterburners_2`. Both also select `tech_sapient_ai` for `tech_combat_computers_3`: the previous combat computer has another independent continuation, `tech_combat_computers_autonomous`. Yet component definitions explicitly upgrade an advanced combat computer to a sapient one. Maximizing preserved paths does not by itself guarantee preservation of game families.

Another example: the global experiment attaches mega-engineering to an arkship because this improves the retained path count. This geometric result does not prove that mega-engineering is the next arkship level.

These experiments treat `OR` leaves as possible layout links without evaluating country conditions. Their numeric results do not mean that 18 or 19 game chains have been confirmed.

## Explicit object upgrade links

For afterburners, `common/component_templates/00_utilities_afterburners.txt` contains:

```text
utility_component_template = {
    key = "AFTERBURNER_1"
    prerequisites = { "tech_afterburners_1" }
    upgrades_to = "AFTERBURNER_2"
}

utility_component_template = {
    key = "AFTERBURNER_2"
    prerequisites = { "tech_afterburners_2" }
}
```

These are abridged definitions with unrelated fields omitted. The link uses the exact `upgrades_to` reference and object prerequisites, not similarity between IDs. Buildings provide an analogous `upgrades` list.

Direct inspection of 83 component and building files found 1892 objects and 60 upgrade witnesses for 16 of the technologies examined. Multiple witnesses may represent different component sizes or types for one technology. This supplemental pass structurally detected 1626 inline calls without expanding them. Consequently, absent evidence does not prove an absence of all external links; only explicitly read top-level upgrades with one scalar technology prerequisite at each endpoint were counted.

## All cases

The candidate column contains only prerequisites matching both area and category. Original requirements, including other areas and `OR`, remain in the research JSON. A preference below is the result of a specific signal, not a newly approved rule.

| # | Technology | Candidates | Observation |
| ---: | --- | --- | --- |
| 1 | Ceramo-Metal Alloys — `tech_advanced_metallurgy_1` | `tech_alloys_1`; `tech_ship_armor_2` | Both candidates have their own continuations. The new metallurgist-production modifier does not match parent effects; starting a separate branch seems better justified than automatically choosing either parent, but remains a proposal. |
| 2 | Durasteel-Laced Alloys — `tech_advanced_metallurgy_2` | `tech_advanced_metallurgy_1`; `tech_alloys_2`; `tech_ship_armor_4` | `tech_advanced_metallurgy_1`: the sole candidate sharing actual modifier keys. |
| 3 | Advanced Afterburners — `tech_afterburners_2` | `tech_afterburners_1`; `tech_thrusters_3` | `tech_afterburners_1`: explicit component upgrade [AFTERBURNER_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_afterburners.txt:24) → [AFTERBURNER_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_afterburners.txt:63). |
| 4 | Subspace Imaging Array — `tech_arkship_system_scanner` | `tech_sensors_2`; `tech_automated_exploration` | Both structural experiments select `tech_automated_exploration`. It unlocks a separate arkship module (`common/starbase_modules/00_arkship_spinal_modules.txt:197`); no direct upgrade from candidate unlocks was established. |
| 5 | Arkship Engineering — `tech_arkship_tier_2` | `tech_cruisers`; `tech_arkship_construction` | `tech_arkship_construction` is directly mandatory; the other matching candidates occur in `OR`. Preferring the mandatory one is a possible layout rule, not a game family marker. |
| 6 | Arkship Mastery — `tech_arkship_tier_3` | `tech_battleships`; `tech_arkship_tier_2` | `tech_arkship_tier_2` is directly mandatory; the other matching candidates occur in `OR`. Preferring the mandatory one is a possible layout rule, not a game family marker. |
| 7 | Armor Hardening — `tech_armor_hardeners_1` | `tech_advanced_metallurgy_1`; `tech_rare_crystals` | Start of the observed armor-hardener component chain. The single-dependent rule selects `tech_rare_crystals`, but there is no confirmed upgrade from parent unlocks. |
| 8 | Adaptive Armor Hardening — `tech_armor_hardeners_2` | `tech_armor_hardeners_1`; `tech_mine_living_metal` | `tech_armor_hardeners_1`: explicit component upgrade [ARMOR_HARDENER_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:250) → [ARMOR_HARDENER_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:284). |
| 9 | Maximized Productivity — `tech_capital_productivity_3` | `tech_galactic_administration`; `tech_capital_productivity_2` | `tech_capital_productivity_2`: external conditions successively change the same `pop_bonus_workforce_mult`; see the example above. The technology's own `modifier` contains only a description. |
| 10 | Advanced Cloaking Fields — `tech_cloaking_2` | `tech_cloaking_1`; `tech_shields_3` | `tech_cloaking_1`: explicit component upgrade [CORVETTE_CLOAKING_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:10) → [CORVETTE_CLOAKING_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:87). |
| 11 | Elite Cloaking Fields — `tech_cloaking_3` | `tech_cloaking_2`; `tech_shields_4` | `tech_cloaking_2`: explicit component upgrade [CORVETTE_CLOAKING_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:87) → [CORVETTE_CLOAKING_3](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:173). |
| 12 | Dark Matter Cloaking Fields — `tech_cloaking_dark_matter` | `tech_dark_matter_deflector`; `tech_cloaking_3` | `tech_cloaking_3`: explicit component upgrade [SCIENCE_CLOAKING_3](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:1249) → [SCIENCE_CLOAKING_DARK_MATTER](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:1274). |
| 13 | Extended Combat Algorithms — `tech_combat_computers_2` | `tech_combat_computers_1`; `tech_self_aware_logic` | `tech_combat_computers_1`: explicit component upgrade [COMBAT_COMPUTER_SWARM_BASIC](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_roles.txt:297) → [COMBAT_COMPUTER_SWARM_ADVANCED](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_roles.txt:339). |
| 14 | Sapient Combat Simulations — `tech_combat_computers_3` | `tech_combat_computers_2`; `tech_sapient_ai` | `tech_combat_computers_2`: explicit component upgrade [COMBAT_COMPUTER_SWARM_ADVANCED](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_roles.txt:339) → [COMBAT_COMPUTER_SWARM_SAPIENT](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_roles.txt:381). |
| 15 | Predictive Consumerism — `tech_consumer_good_refinement_2` | `tech_consumer_good_refinement_1`; `tech_self_aware_logic` | `tech_consumer_good_refinement_1`: the sole candidate sharing actual modifier keys. |
| 16 | Self-Aware Colony Ships — `tech_cryostasis_2` | `tech_self_aware_logic`; `tech_cryostasis_1` | `tech_cryostasis_1`: the sole candidate sharing actual modifier keys. |
| 17 | Tachyon Lances — `tech_energy_lance_2` | `tech_lasers_5`; `tech_energy_lance_1` | `tech_energy_lance_1`: explicit component upgrade [ENERGY_LANCE_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_extra_large.txt:6) → [ENERGY_LANCE_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_extra_large.txt:73). |
| 18 | Robot Manufacturing Nexus — `tech_fe_assembly_1` | `tech_robomodding`; `tech_robomodding_m` | `OR` between two distinct robomodding technologies. Neither is individually mandatory; no justified unique continuation was found. |
| 19 | Genetic Healthcare — `tech_frontier_health` | `tech_basic_health`; `tech_genome_mapping` | `tech_basic_health`: explicit building upgrade [building_medical_1](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/07_amenity_buildings.txt:732) → [building_medical_2](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/07_amenity_buildings.txt:826). |
| 20 | Growth Chamber — `tech_growth_chamber_1` | `tech_stingers`; `tech_mauler_growth_1`; `tech_stinger_growth_1`; `tech_weaver_growth_1`; `tech_harbinger_growth_1` | `tech_stingers` is directly mandatory; the other matching candidates occur in `OR`. Preferring the mandatory one is a possible layout rule, not a game family marker. |
| 21 | Advanced Growth Chamber — `tech_growth_chamber_2` | `tech_growth_chamber_1`; `tech_mauler_growth_2`; `tech_stinger_growth_2`; `tech_weaver_growth_2`; `tech_harbinger_growth_2` | `tech_growth_chamber_1` is directly mandatory; the other matching candidates occur in `OR`. Preferring the mandatory one is a possible layout rule, not a game family marker. |
| 22 | Habitat Expansion — `tech_habitat_2` | `tech_habitat_1`; `tech_starbase_4` | `tech_habitat_1`: explicit building upgrade [building_hab_capital](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/00_capital_buildings.txt:1010) → [building_hab_major_capital](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/00_capital_buildings.txt:1146). |
| 23 | Advanced Space Habitation — `tech_habitat_3` | `tech_habitat_2`; `tech_starbase_5` | `tech_habitat_2`: explicit building upgrade [building_hab_major_capital](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/00_capital_buildings.txt:1146) → [building_hab_system_capital](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/00_capital_buildings.txt:1292). |
| 24 | Juggernaut — `tech_juggernaut` | `tech_starbase_5`; `tech_arkship_construction`; `tech_battleships` | Combines two `OR` groups. Global optimization selects `tech_starbase_5`, but this does not establish an explicit family continuation. |
| 25 | Kinetic Artillery — `tech_kinetic_artillery_2` | `tech_mass_drivers_5`; `tech_kinetic_artillery_1` | `tech_kinetic_artillery_1`: explicit component upgrade [KINETIC_ARTILLERY_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_projectile.txt:916) → [KINETIC_ARTILLERY_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_projectile.txt:984). |
| 26 | Giga Cannon — `tech_mass_accelerator_2` | `tech_mass_drivers_5`; `tech_mass_accelerator_1` | `tech_mass_accelerator_1`: explicit component upgrade [MASS_ACCELERATOR_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_extra_large.txt:282) → [MASS_ACCELERATOR_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_extra_large.txt:360). |
| 27 | Mega-Engineering — `tech_mega_engineering` | `tech_starbase_5`; `tech_arkship_tier_3`; `tech_battleships` | Joins multiple branches and two `OR` groups. Optimization chooses `tech_arkship_tier_3` for path count; its own effects differ from candidate effects. |
| 28 | Military Arkships — `tech_military_arkship` | `tech_destroyers`; `tech_arkship_construction` | `tech_arkship_construction` is directly mandatory; the other matching candidates occur in `OR`. Preferring the mandatory one is a possible layout rule, not a game family marker. |
| 29 | Modular Engineering — `tech_modular_engineering` | `tech_starbase_3`; `tech_waystation_2` | `OR` between a starbase and a waystation. New construction-cost modifiers do not match parent modifiers; inspected signals do not identify one source chain. |
| 30 | Improved Reactor Boosters — `tech_reactor_boosters_2` | `tech_fusion_power`; `tech_reactor_boosters_1` | `tech_reactor_boosters_1`: explicit component upgrade [REACTOR_BOOSTER_1](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:4) → [REACTOR_BOOSTER_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:29). |
| 31 | Advanced Reactor Boosters — `tech_reactor_boosters_3` | `tech_antimatter_power`; `tech_reactor_boosters_2` | `tech_reactor_boosters_2`: explicit component upgrade [REACTOR_BOOSTER_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:29) → [REACTOR_BOOSTER_3](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:54). |
| 32 | Thermodynamic Yield Control — `tech_repeatable_weapon_type_explosive_damage` | `tech_missiles_3`; `tech_swarmer_missiles_2` | Repeatable explosive-weapon improvement after an `OR` of two technologies. The local heuristic selects `tech_swarmer_missiles_2`; the global objective permits different choices, including a separate path. |
| 33 | Miniaturized Pre-Igniters — `tech_repeatable_weapon_type_explosive_fire_rate` | `tech_missiles_3`; `tech_swarmer_missiles_2` | Same alternative structure as the damage improvement, with a separate fire-rate modifier. The local heuristic again selects `tech_swarmer_missiles_2`, creating competing continuations. |
| 34 | Cross-Model Standardization — `tech_robomodding_points_1` | `tech_robomodding`; `tech_droid_workers` | New trait-point modifiers do not match parent effects. Both parents have other continuations; selecting one needs further evidence. |
| 35 | Fungible Circuitry — `tech_robomodding_points_2` | `tech_robomodding_points_1`; `tech_synthetic_workers` | `tech_robomodding_points_1`: the sole candidate sharing actual modifier keys. |
| 36 | Corps of Engineers — `tech_space_defense_station_improvement` | `tech_starbase_4`; `tech_modular_engineering` | Both structural experiments prefer `tech_modular_engineering`. Upgrade cost/speed modifiers differ from the parent's construction modifiers; this remains a structural candidate. |
| 37 | Metacognitive Faith — `tech_transcendent_faith` | `tech_consecration_fields`; `tech_galactic_administration` | `tech_consecration_fields` stands out through a single dependent and equal `potential`. Its unlocked buildings are not connected by an observed direct `upgrades` link; evidence remains incomplete. |
| 38 | Volcanic Terraforming — `tech_volcanic_terraforming` | `tech_terrestrial_sculpting`; `tech_volcano` | Structure prefers `tech_volcano`. However, the new technology is used in `common/terraform`, while the other candidate unlocks terraforming. Continuation count alone is insufficient to identify the family. |
| 39 | Xeno Relations — `tech_xeno_relations` | `tech_xeno_diplomacy`; `tech_galactic_administration` | `tech_xeno_diplomacy`: explicit building upgrade [building_embassy](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/02_government_buildings.txt:763) → [building_grand_embassy](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/02_government_buildings.txt:843). |

## Proposals for discussion

- Use explicit object upgrades as strong continuation evidence: verify exact references first, then map the objects' technology prerequisites.
- Use shared actual modifiers as additional evidence of related effects, without deriving it from names or descriptions.
- Approved as L-08: prefer a mandatory prerequisite over an alternative-group member among candidates selected under L-07. Preserve the `OR` group and every game dependency.
- Apply the user's independent-branch idea with confirmed continuations in mind. Do not treat any other dependent research as proof that a predecessor is already “occupied”.
- Consider allowing a separate branch to begin where several families merge. Its placement will still require a decision on which incoming branch it should sit near.

The current database provides the graph, modifiers and conditions; `upgrades_to`/`upgrades` data would require separate enrichment. This is proposed future work, not an implemented backend change.

No universally verified signal was found that unambiguously identifies the game family in all 39 cases. The research provides reproducible signals with differing evidence strength and concrete counterexamples to simple structural rules. Further decisions belong in the [chain and sorting document](TECHNOLOGY_CHAINS_AND_SORTING_EN.md) after discussion.

## Artifacts and verification

- `data/chain_analysis/audit_ambiguities.py` → `ambiguities.json`: all 39 cases, candidates, fields, direct mandatory status and results of nine comparisons.
- `data/chain_analysis/audit_unlocks.py` → `unlock_evidence.json`: 83 read files with SHA-256 hashes, 1892 objects, 60 positive witnesses, unexpanded inserts and unresolved upgrade targets. No syntax errors or duplicate keys were found among the inspected objects.
- `data/chain_analysis/audit_path_cover.py` → `path_cover_experiment.json`: global experiment and all feasible parents for each case at the same continuation maximum.
- Matching size was checked against an independent exhaustive method on 80 small random graphs. For the full graph, 12 traversal-order permutations preserved the maximum and every reported forced choice.
- The analysis uses base technology representations. Manual variants and a particular country's state were not evaluated.
- Source database SHA-256: `a3ef07a166dee5b7be4a17608e20c6545a99321247802268939985b92689c858`.

Run the research scripts using Python at `data/.venv/Scripts/python.exe` with `-B`; run `audit_ambiguities.py` first, then `audit_unlocks.py` and `audit_path_cover.py`. These are temporary analysis tools in the ignored `data/` directory.

[Русская версия](RESEARCH_AMBIGUOUS_CHAINS_RU.md).
