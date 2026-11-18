# Stellaris Technological Tree View — starting technologies

## Contents

- [Scope and selection criterion](#scope-and-selection-criterion)
- [Summary](#summary)
- [Physics — 10](#physics--10)
- [Society — 16](#society--16)
- [Engineering — 16](#engineering--16)
- [Explicit no values](#explicit-no-values)
- [Relevance to chains](#relevance-to-chains)
- [Sources and verification](#sources-and-verification)

## Scope and selection criterion

List dated 2026-11-17, based on `data/stage10/database.json`: 679 base technologies. Objects with an explicit top-level `start_tech = yes` were selected. Names come from the database's Russian and English localization; `technology_swap` variants are not counted as separate technologies.

`start_tech` marks a starting technology; `starting_potential` provides additional starting eligibility conditions. General `potential` conditions may also be present. This is a list of definitions, not an evaluated starting set for a particular country. Additional technologies granted by effects, origins or events are outside this selection.

The tables reproduce `starting_potential` conditions from source code without comments or the enclosing braces. Multiple conditions are separated with semicolons. A dash indicates that this particular block is absent, not unconditional availability. The `potential` column marks the presence of a general condition block. The ID link points to the first `start_tech` line in the installed game.

## Summary

| Metric | Count |
| --- | ---: |
| Unique technologies with a `start_tech` field | 47 |
| With a `yes` value | 42 |
| With a `no` value | 5 |
| Field occurrences, including repetitions | 50 |
| Starting technologies with `starting_potential` | 19 |
| Starting technologies with `tier = 0` | 38 |
| Starting technologies with `tier = 1` | 4 |
| Starting technologies with nonempty `prerequisites` | 11 |

The `start_tech = yes` field is repeated twice in `tech_lasers_1`, `tech_mass_drivers_1` and `tech_wilderness_terraform`. Each technology is counted once; no conflicting values of this field occur in the selection.

## Physics — 10

| Name | ID and source | tier | starting_potential | potential |
| --- | --- | ---: | --- | --- |
| Scientific Method | [tech_basic_science_lab_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:37) | 0 | `is_low_tech_start = no` | — |
| Fission Power | [tech_fission_power](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:1491) | 0 | — | — |
| Hyperspace Travel | [tech_hyper_drive_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:2558) | 0 | `is_eager_explorer_empire = no` | — |
| Red Lasers | [tech_lasers_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_weapon_tech.txt:12) | 0 | — | — |
| Active Countermeasures | [tech_pd_tracking_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_weapon_tech.txt:899) | 0 | — | — |
| High-Energy Capacitors | [tech_power_plant_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:2300) | 0 | — | — |
| Reactor Boosters | [tech_reactor_boosters_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:1738) | 0 | — | — |
| Deflectors | [tech_shields_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:1789) | 0 | — | — |
| Space Exploration | [tech_space_exploration](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:10) | 0 | — | — |
| Subspace Drive | [tech_subspace_drive](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_first_contact_tech.txt:426) | 0 | `is_eager_explorer_empire = yes` | present |

## Society — 16

| Name | ID and source | tier | starting_potential | potential |
| --- | --- | ---: | --- | --- |
| Medical Care | [tech_basic_health](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:1256) | 0 | — | present |
| New Worlds Protocol | [tech_colonization_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:1087) | 0 | `is_nomadic = no` | present |
| Fruit Gardens | [tech_critter_feeder](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_plantoids_tech.txt:8) | 0 | `has_origin = origin_fruitful` | present |
| Synaptic Structures | [tech_hive_node](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:5861) | 0 | — | present |
| Holo-Entertainment | [tech_holo_entertainment](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:5534) | 0 | — | present |
| Hydroponics Farming | [tech_hydroponics](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:543) | 0 | — | present |
| Industrial Agriculture | [tech_industrial_farming](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:177) | 0 | — | — |
| Interplanetary Commerce | [tech_interplanetary_commerce](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:38) | 0 | — | present |
| Maulers | [tech_maulers](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:13) | 1 | `is_low_tech_start = no` | present |
| Planetary Defenses | [tech_planetary_defenses](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:7) | 0 | — | — |
| Unified Government | [tech_planetary_government](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:4610) | 0 | `is_low_tech_start = no` | — |
| Vector Lock Cannon | [tech_weaver_bio_anti_evasion_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:2038) | 1 | `is_low_tech_start = no` | present |
| Energy Burster | [tech_weaver_bio_evasion_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:1266) | 1 | `is_low_tech_start = no` | present |
| Weavers | [tech_weavers](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:193) | 1 | `is_low_tech_start = no` | present |
| Centers of Being | [tech_wilderness_node](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:5909) | 0 | — | present |
| Planetary Germination | [tech_wilderness_terraform](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_biogenesis_tech.txt:2637) | 0 | `is_wilderness_empire = yes` | present |

## Engineering — 16

| Name | ID and source | tier | starting_potential | potential |
| --- | --- | ---: | --- | --- |
| Interplanetary Expeditionary Forces | [tech_assault_armies](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:1809) | 0 | — | — |
| Industrial Base | [tech_basic_industry](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2312) | 0 | — | — |
| Corvettes | [tech_corvettes](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:26) | 0 | `is_low_tech_start = no`; `country_uses_bio_ships = no` | present |
| Flak Battery | [tech_flak_batteries_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_weapon_tech.txt:620) | 0 | — | — |
| Mass Drivers | [tech_mass_drivers_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_weapon_tech.txt:12) | 0 | — | — |
| Mechanized Mining | [tech_mechanized_mining](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2331) | 0 | `is_nomadic = no` | present |
| Nuclear Missiles | [tech_missiles_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_weapon_tech.txt:742) | 0 | — | present |
| Strategic Extraction | [tech_nomads_mechanized_mining](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_nomads_dlc_tech.txt:472) | 0 | `is_nomadic = yes` | present |
| Nanocomposite Materials | [tech_ship_armor_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:1822) | 0 | — | — |
| Orbital Energy Conversion | [tech_solar_panel_network](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:9) | 0 | `is_nomadic = no` | present |
| Offworld Construction | [tech_space_construction](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:3532) | 0 | — | — |
| Deep Space Defenses | [tech_space_defense_station_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2266) | 0 | `is_nomadic = no` | present |
| Starbase Construction | [tech_starbase_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:1130) | 0 | `is_nomadic = no` | present |
| Starport | [tech_starbase_2](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:1157) | 0 | `is_nomadic = no` | present |
| Chemical Thrusters | [tech_thrusters_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2078) | 0 | — | — |
| Waystations | [tech_waystation_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_nomads_dlc_tech.txt:491) | 0 | `is_nomadic = yes` | present |

## Explicit no values

These five technologies contain the field but are not marked as starting technologies:

| Name | ID and source | tier |
| --- | --- | ---: |
| Entropic Recursion | [tech_akx_worm_1](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_horizonsignal_tech.txt:3) | 3 |
| Doctrine: Strange Loop | [tech_akx_worm_2](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_horizonsignal_tech.txt:32) | 3 |
| Omega Theory | [tech_akx_worm_3](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_horizonsignal_tech.txt:61) | 3 |
| Enhanced Cryosleep Sedatives | [tech_enhanced_cryosleep_sedatives](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_strange_worlds_tech.txt:4) | 2 |
| Universal Macrophage | [tech_universal_marcophage](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_strange_worlds_tech.txt:17) | 3 |

## Relevance to chains

The tier-one starting technologies are `tech_maulers`, `tech_weavers`, `tech_weaver_bio_evasion_1` and `tech_weaver_bio_anti_evasion_1`.

Eleven starting technologies already have technology predecessors. For example:

- `tech_starbase_1` requires `tech_space_construction`, and `tech_starbase_2` requires `tech_starbase_1`; all three are marked as starting technologies.
- `tech_reactor_boosters_1` requires the starting technology `tech_fission_power`.
- `tech_weavers` requires the starting technology `tech_maulers`.

Therefore, `start_tech = yes` cannot be equated with having no incoming technology links or with `tier = 0`. How this flag should be used for chain construction remains to be decided in the [chain and sorting rules document](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).

## Sources and verification

- Database: `data/stage10/database.json`; SHA-256: `a3ef07a166dee5b7be4a17608e20c6545a99321247802268939985b92689c858`.
- Extract with IDs, bilingual names, tiers, predecessors, conditions and source coordinates: `data/chain_analysis/starting_technologies.json`.
- All 50 `start_tech` coordinates from the database were compared with a direct search across `E:/SteamLibrary/steamapps/common/Stellaris/common/technology/**/*.txt`; the sets matched. Values were checked against their source lines.
- All 19 `starting_potential` blocks were read from installed files using database origin coordinates. Conditions were not evaluated for an in-game country.
- The source database, product code and game files were not modified.

[Русская версия](STARTING_TECHNOLOGIES_RU.md).
