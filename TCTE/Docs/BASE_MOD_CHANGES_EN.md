# TCTE — Tass Cheat Tool overrides

## Contents

- [Version 0.0.8 scope](#version-008-scope)
- [Files and policies](#files-and-policies)
- [Resource menu](#resource-menu)
- [Species modification](#species-modification)
- [Extra envoys](#extra-envoys)
- [Preserved behavior and validation](#preserved-behavior-and-validation)

## Version 0.0.8 scope

TCTE overrides 97 Tass files: 94 policy files, two event files, and one static-modifier file. The standalone override of one vanilla trigger is recorded separately in [VANILLA_CHANGES_EN.md](VANILLA_CHANGES_EN.md).

Under the approved [specification](TZ_LEVELS_EN.md), TCTE overrides 94 policy files from Tass Cheat Tool version `20261012`. Workshop originals are unchanged. Each file uses the same relative path `common/policies/<filename>` inside TCTE; source policy IDs are preserved. New options use `tcte_policy_<name>_<regular|monthly>_<level>`.

All 94 policies contain ten regular levels; 18 resource policies also contain ten monthly levels. The Unmodified option is retained separately. Totals: 112 tracks and 1214 options, including 629 new options. Each new level doubles the preceding level's numeric modifiers within its own track.

## Files and policies

Table paths are relative to `common/policies/` in both Tass and TCTE. Option counts include Unmodified.

| File | Policy ID | Options |
| --- | --- | ---: |
| `tass_cheat_policy_01_01_all_resources.txt` | `tass_policy_cheat_all_production` | 11 |
| `tass_cheat_policy_01_02_energy.txt` | `tass_policy_cheat_energy` | 21 |
| `tass_cheat_policy_01_03_minerals.txt` | `tass_policy_cheat_minerals` | 21 |
| `tass_cheat_policy_01_04_food.txt` | `tass_policy_cheat_food` | 21 |
| `tass_cheat_policy_01_05_research_resources.txt` | `tass_policy_cheat_research_resources` | 21 |
| `tass_cheat_policy_01_06_alloys.txt` | `tass_policy_cheat_alloys` | 21 |
| `tass_cheat_policy_01_07_consumer_goods.txt` | `tass_policy_cheat_consumer_goods` | 21 |
| `tass_cheat_policy_01_08_trade.txt` | `tass_policy_cheat_trade` | 21 |
| `tass_cheat_policy_01_09_unity.txt` | `tass_policy_cheat_unity` | 21 |
| `tass_cheat_policy_01_10_influence.txt` | `tass_policy_cheat_influence` | 21 |
| `tass_cheat_policy_01_11_volatile_motes.txt` | `tass_policy_cheat_volatile_motes` | 21 |
| `tass_cheat_policy_01_12_exotic_gases.txt` | `tass_policy_cheat_exotic_gases` | 21 |
| `tass_cheat_policy_01_13_rare_crystals.txt` | `tass_policy_cheat_rare_crystals` | 21 |
| `tass_cheat_policy_01_14_living_metal.txt` | `tass_policy_cheat_sr_living_metal` | 21 |
| `tass_cheat_policy_01_15_dark_matter.txt` | `tass_policy_cheat_sr_dark_matter` | 21 |
| `tass_cheat_policy_01_16_zro.txt` | `tass_policy_cheat_sr_zro` | 21 |
| `tass_cheat_policy_01_17_nanites.txt` | `tass_policy_cheat_nanites` | 21 |
| `tass_cheat_policy_01_18_minor_artifacts.txt` | `tass_policy_cheat_minor_artifacts` | 21 |
| `tass_cheat_policy_01_19_astral_thread.txt` | `tass_policy_cheat_astral_threads` | 21 |
| `tass_cheat_policy_01_20_crisis.txt` | `tass_policy_cheat_crisis` | 11 |
| `tass_cheat_policy_01_21_cost.txt` | `tass_policy_cheat_all_cost` | 11 |
| `tass_cheat_policy_01_22_upkeep.txt` | `tass_policy_cheat_all_upkeep` | 11 |
| `tass_cheat_policy_01_23_storage.txt` | `tass_policy_cheat_storage` | 11 |
| `tass_cheat_policy_02_01_research_speed.txt` | `tass_policy_cheat_research_speed` | 11 |
| `tass_cheat_policy_02_02_research_options.txt` | `tass_policy_cheat_research_options` | 11 |
| `tass_cheat_policy_02_03_workforce.txt` | `tass_policy_cheat_workforce` | 11 |
| `tass_cheat_policy_02_04_auto_workforce.txt` | `tass_policy_cheat_auto_workforce` | 11 |
| `tass_cheat_policy_02_05_civil_construction.txt` | `tass_policy_cheat_civil_construction` | 11 |
| `tass_cheat_policy_02_06_military_construction.txt` | `tass_policy_cheat_military_construction` | 11 |
| `tass_cheat_policy_02_07_mega_construction.txt` | `tass_policy_cheat_mega_construction` | 11 |
| `tass_cheat_policy_02_08_colony_development.txt` | `tass_policy_cheat_colony_development` | 11 |
| `tass_cheat_policy_02_09_terraforming_speed.txt` | `tass_policy_cheat_terraforming_speed` | 11 |
| `tass_cheat_policy_03_01_founder_species_growth.txt` | `tass_policy_cheat_founder_species_growth` | 11 |
| `tass_cheat_policy_03_02_pop_growth.txt` | `tass_policy_cheat_pop_growth` | 11 |
| `tass_cheat_policy_03_03_pop_bonus.txt` | `tass_policy_cheat_pop_bonus` | 11 |
| `tass_cheat_policy_03_04_pop_assemble.txt` | `tass_policy_cheat_pop_assemble` | 11 |
| `tass_cheat_policy_03_05_modify_species.txt` | `tass_policy_cheat_modify_species` | 11 |
| `tass_cheat_policy_04_01_housing.txt` | `tass_policy_cheat_planet_housing` | 11 |
| `tass_cheat_policy_04_02_amenities.txt` | `tass_policy_cheat_planet_amenities` | 11 |
| `tass_cheat_policy_04_03_crime.txt` | `tass_policy_cheat_planet_crime` | 11 |
| `tass_cheat_policy_04_04_planet_stability.txt` | `tass_policy_cheat_planet_stability` | 11 |
| `tass_cheat_policy_04_05_decision_enact.txt` | `tass_policy_cheat_decision_enact` | 11 |
| `tass_cheat_policy_04_06_planetary_ascension.txt` | `tass_policy_cheat_planetary_ascension` | 11 |
| `tass_cheat_policy_05_01_army_damage.txt` | `tass_policy_cheat_army_damage` | 11 |
| `tass_cheat_policy_05_02_army_defense.txt` | `tass_policy_cheat_army_defense` | 11 |
| `tass_cheat_policy_05_03_army_disengage.txt` | `tass_policy_cheat_army_disengage` | 11 |
| `tass_cheat_policy_05_04_army_exp.txt` | `tass_policy_cheat_army_exp` | 11 |
| `tass_cheat_policy_06_01_fleet_damage.txt` | `tass_policy_cheat_fleet_damage` | 11 |
| `tass_cheat_policy_06_02_fleet_accuracy.txt` | `tass_policy_cheat_fleet_accuracy` | 11 |
| `tass_cheat_policy_06_03_fleet_fire_rate.txt` | `tass_policy_cheat_fleet_fire_rate` | 11 |
| `tass_cheat_policy_06_04_fleet_range.txt` | `tass_policy_cheat_fleet_range` | 11 |
| `tass_cheat_policy_06_05_fleet_damage_reduction.txt` | `tass_policy_cheat_fleet_damage_reduction` | 11 |
| `tass_cheat_policy_06_06_fleet_defense.txt` | `tass_policy_cheat_fleet_defense` | 11 |
| `tass_cheat_policy_06_07_fleet_hardening.txt` | `tass_policy_cheat_fleet_hardening` | 11 |
| `tass_cheat_policy_06_08_fleet_evasion.txt` | `tass_policy_cheat_fleet_evasion` | 11 |
| `tass_cheat_policy_06_09_fleet_disengage.txt` | `tass_policy_cheat_fleet_disengage` | 11 |
| `tass_cheat_policy_06_10_fleet_regeneration.txt` | `tass_policy_cheat_fleet_regeneration` | 11 |
| `tass_cheat_policy_06_11_fleet_sensor.txt` | `tass_policy_cheat_fleet_sensor` | 11 |
| `tass_cheat_policy_06_12_fleet_speed.txt` | `tass_policy_cheat_fleet_speed` | 11 |
| `tass_cheat_policy_06_13_fleet_travel.txt` | `tass_policy_cheat_fleet_travel` | 11 |
| `tass_cheat_policy_06_14_fleet_exp.txt` | `tass_policy_cheat_fleet_exp` | 11 |
| `tass_cheat_policy_06_15_bioship.txt` | `tass_policy_cheat_bioship_growth` | 11 |
| `tass_cheat_policy_06_16_navy_size.txt` | `tass_policy_cheat_navy_size` | 11 |
| `tass_cheat_policy_06_17_station_cap.txt` | `tass_policy_cheat_station_cap` | 11 |
| `tass_cheat_policy_06_18_defense_cap.txt` | `tass_policy_cheat_defense_cap` | 11 |
| `tass_cheat_policy_07_01_leader_skill.txt` | `tass_policy_cheat_leader_skill` | 11 |
| `tass_cheat_policy_07_02_leader_option.txt` | `tass_policy_cheat_leader_option` | 11 |
| `tass_cheat_policy_07_03_leader_exp.txt` | `tass_policy_cheat_leader_exp` | 11 |
| `tass_cheat_policy_08_01_size_penalty.txt` | `tass_policy_cheat_size_penalty` | 11 |
| `tass_cheat_policy_08_02_war_exhaustion.txt` | `tass_policy_cheat_war_exhaustion` | 11 |
| `tass_cheat_policy_08_03_governing_ethic.txt` | `tass_policy_cheat_governing_ethic` | 11 |
| `tass_cheat_policy_08_04_council_agenda.txt` | `tass_policy_cheat_council_agenda` | 11 |
| `tass_cheat_policy_08_05_edict_efficiency.txt` | `tass_policy_cheat_edict_efficiency` | 11 |
| `tass_cheat_policy_09_01_exploration.txt` | `tass_policy_cheat_exploration` | 11 |
| `tass_cheat_policy_09_02_first_contact.txt` | `tass_policy_cheat_first_contact` | 11 |
| `tass_cheat_policy_09_03_encryption.txt` | `tass_policy_cheat_encryption` | 11 |
| `tass_cheat_policy_09_04_cloaking.txt` | `tass_policy_cheat_cloaking` | 11 |
| `tass_cheat_policy_09_05_domestication.txt` | `tass_policy_cheat_domestication` | 11 |
| `tass_cheat_policy_10_01_intel.txt` | `tass_policy_cheat_intel` | 11 |
| `tass_cheat_policy_10_02_spy_network.txt` | `tass_policy_cheat_spy_network` | 11 |
| `tass_cheat_policy_10_03_operation.txt` | `tass_policy_cheat_operation` | 11 |
| `tass_cheat_policy_11_01_communication.txt` | `tass_policy_cheat_communication` | 11 |
| `tass_cheat_policy_11_02_relation.txt` | `tass_policy_cheat_relation` | 11 |
| `tass_cheat_policy_11_03_acceptance.txt` | `tass_policy_cheat_acceptance` | 11 |
| `tass_cheat_policy_11_04_diplo_weight.txt` | `tass_policy_cheat_diplo_weight` | 11 |
| `tass_cheat_policy_11_05_federation.txt` | `tass_policy_cheat_federation` | 11 |
| `tass_cheat_policy_11_06_galactic_community.txt` | `tass_policy_cheat_galactic_community` | 11 |
| `tass_cheat_policy_12_01_shroud.txt` | `tass_policy_cheat_shroud` | 11 |
| `tass_cheat_policy_12_02_patron.txt` | `tass_policy_cheat_patron` | 11 |
| `tass_cheat_policy_12_03_psionic_aura.txt` | `tass_policy_cheat_psionic_aura` | 11 |
| `tass_cheat_policy_12_04_psionic_resistance.txt` | `tass_policy_cheat_psionic_resistance` | 11 |
| `tass_cheat_policy_13_01_nomads_arkship.txt` | `tass_policy_cheat_nomads_arkship` | 11 |
| `tass_cheat_policy_13_02_nomads_economy.txt` | `tass_policy_cheat_nomad_economy` | 11 |
| `tass_cheat_policy_13_03_nomad_reserve.txt` | `tass_policy_cheat_nomad_reserve` | 11 |

## Resource menu

Under the [resource menu specification](TZ_RESOURCES_EN.md), override `events/tass_cheat_events_4_resources.txt`, whose only event is `tass_cheat.4`. It opens six categories instead of a flat grant list. The existing call from `tass_cheat.1` remains intact, including in 0.0.6 with the species modification toggle.

The new `events/tcte_resource_menu_events.txt` adds categories `tcte_resources.1`–`.6` and amount menus `tcte_resources.101`–`.126`. Each of 26 resources has six amounts; granting an amount reopens the same menu. Original restrictions, country scope, illustration, and main-menu flag behavior are retained. New RU/EN strings are added in `tcte_resource_menu_l_russian.yml` and `tcte_resource_menu_l_english.yml`.

Checked every transition, 156 grants, nine conditions, and localization references. These events do not change capacities or add automatic grants. Evidence and exact ID map: [resource_menu_sources.json](../../TMP/TCTE/resource_menu_sources.json); [validation](../../TMP/TCTE/resource_menu_validation.json).

## Species modification

The [specification](TZ_SPECIES_EN.md) adds two overrides at their original relative paths in 0.0.6:

- `common/static_modifiers/tass_cheat_static_modifiers.txt`: changes six bonuses of `modifier_tass_extra_species_modding` from +50/+5 to +100/+30 for `BIOLOGICAL`, `ROBOT`, and `MACHINE`. The other five modifiers are preserved.
- `events/tass_cheat_events_1_country.txt`: replaces the original species modification option in `tass_cheat.1` with mutually exclusive enable/remove options, both returning to the same menu. Within 0.0.6, all other options, their order, presentation, menu flag, and actions were preserved, including envoys and the resource menu entry. The subsequent envoy change in 0.0.8 is described below.

The modifier ID is retained; an already-active cheat is detected using `has_modifier`. Enabling is permanent; removal affects only this modifier. The new label and tooltips add three keys per language with the `tcte_` prefix. Additional trait removal permission is implemented in a vanilla trigger and recorded in the separate inventory. [Validation](../../TMP/TCTE/species_modding_validation.json).

## Extra envoys

Under the [separate specification](TZ_ENVOYS_EN.md), version 0.0.8 changes only `tass_cheat.1.extra_envoy` in the already overridden `events/tass_cheat_events_1_country.txt`. It opens `tcte_envoys.1` with a new tooltip; the old +20 grant and modifier-based lock are removed from this path. The old modifier definition and its effect in saves are preserved. Other main-menu blocks remain unchanged.

New TCTE files: `events/tcte_envoy_menu_events.txt`, `common/technology/tcte_envoy_technologies.txt`, `localisation/replace/tcte_envoy_menu_l_russian.yml`, and `localisation/english/tcte_envoy_menu_l_english.yml`. One event contains six cumulative grants and Back. One repeatable technology adds +5 capacity per level; +5/+10/+25/+50/+100/+500 grants award 1/2/5/10/20/100 levels. No additional Tass or vanilla file overrides are introduced.

Navigation, amounts, 176 modeled scenarios, sources, and localization were checked. [Report](../../TMP/TCTE/envoy_menu_validation.json); the user verifies engine behavior of technology levels and envoys.

## Preserved behavior and validation

Preserved all 585 original options, categories, policy and option conditions, AI weights, and neutral options. Regular and monthly options remain mutually exclusive within one policy. Differences between track restrictions are preserved, including consumer goods and minor artifacts. In 0.0.6, all 94 policy files match 0.0.4 byte for byte, and the resource menu matches 0.0.5. Apart from the main and resource menus, Tass events are not overridden; edict, decision, and GUI code remains intact.

Structural validation and comparison of original blocks confirmed unchanged existing options. Checked 1200 numeric components of new options and their localization. The user must verify loading overrides after Tass and applying modifiers in-game. Report: [level validation](../../TMP/TCTE/level_validation_report.json).

Russian overrides of original Tass strings are listed in the [README](README_EN.md). Shared vanilla keys are tracked separately in [VANILLA_CHANGES_EN.md](VANILLA_CHANGES_EN.md). [Русский](BASE_MOD_CHANGES_RU.md).
