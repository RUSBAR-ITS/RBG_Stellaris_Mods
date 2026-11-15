# Tass Cheat Tool Extender — affected vanilla files and functions

## Contents

- [Current state](#current-state)
- [Species modification trigger](#species-modification-trigger)
- [Version 0.0.1 impact](#version-001-impact)
- [Shared key list](#shared-key-list)
- [Change boundaries](#change-boundaries)

## Current state

Version 0.0.8 changes one vanilla trigger: `can_remove_beneficial_genetic_traits`. The set of 54 shared localization keys is preserved. New options, events, and keys use the `tcte_` prefix; Tass Cheat Tool overrides are listed separately in [BASE_MOD_CHANGES_EN.md](BASE_MOD_CHANGES_EN.md). The resource menu uses standard `add_resource` and references existing names; vanilla resource definitions and capacities remain unchanged.

Version 0.0.1, implemented on 2026-11-14 under the approved [specification](TZ_EN.md). All 54 shared keys listed below are included. Russian labels change; gameplay functions and effects are not overridden. Physical game and Workshop files remain unchanged.

Version 0.0.2 retains the same shared-key set. Five Tass precursor buttons now reference existing `precursor.1.name`, `precursor.500.name`, `precursor.1000.name`, `precursor.1500.name`, and `precursor.2000.name`. These vanilla keys are referenced only; their definitions are not overridden.

Version 0.0.8 introduces no additional vanilla overrides: the envoy menu uses its own `tcte_tech_extra_envoys` and standard `give_technology`, `while`, and `envoys_add`. Vanilla technologies, the envoy class, and defines are unchanged.

## Species modification trigger

In TCTE 0.0.7, `common/scripted_triggers/tcte_species_traits_triggers.txt` contains only `can_remove_beneficial_genetic_traits`. Its source is `common/scripted_triggers/05_scripted_triggers_traits.txt` from installed Stellaris `v4.5.*`. The full copy is removed from TCTE; the other 49 definitions load from vanilla. The physical game file is unchanged.

The override retains the ID for existing calls. The TCTE filename sorts after the source filename; no `replace_path` is used. Our trigger block remains byte-identical to 0.0.6. [Standalone override validation](../../TMP/TCTE/trigger_override_validation.json); actual engine loading requires user testing in-game.

The existence check for `from`, the modifying country, is retained. Within that scope, permission is **the original tradition condition OR (player AND `tech_gene_expressions` AND `modifier_tass_extra_species_modding`)**. The new branch does not apply to AI. Disabling the cheat closes only this additional path; normal tradition permission remains available.

`can_remove_vocational_genetic_traits`, technology, tradition, and individual trait definitions are unchanged. The added condition applies only where the general trigger is called; other trait restrictions remain applicable. The vanilla trigger ID is retained for existing calls. [Specification](TZ_SPECIES_EN.md), [256 tested combinations](../../TMP/TCTE/species_modding_truth_table.json), [report](../../TMP/TCTE/species_modding_validation.json).

## Version 0.0.1 impact

Russian localization reproduces 54 shared keys from Tass Cheat Tool version `20261012`'s `localisation/replace/tass_replace_l_english.yml`. Output: `TCTE/localisation/replace/tcte_tass_replace_l_russian.yml`.

32 keys have explicit definitions in installed English game localization and the prepared Russian vanilla base. The other 22 are not explicitly defined in the inspected vanilla files; this does not mean their names are used exclusively by Tass.

Modifier labels are affected everywhere the interface uses these keys. Numeric effects and gameplay functions do not change. The 32 overlaps come from:

- `main_3_l_english.yml` / `main_3_l_russian.yml`;
- `megacorp_l_english.yml` / `megacorp_l_russian.yml`;
- `modifiers_1_l_english.yml` / `modifiers_1_l_russian.yml`;
- `infernals_crisis_l_english.yml` / `infernals_crisis_l_russian.yml`.

English sources reside in `E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/`; Russian table sources reside in `Localisation_Base/2-Prio_Vanilla/russian/`. Terminology selection still follows Russian Localization Fix RE priority as specified. Line numbers refer to the inspected snapshot.

## Shared key list

| Shared key | Explicit source in the Russian vanilla base |
| --- | --- |
| `mod_country_energy_produces_mult` | `megacorp_l_russian.yml:1969` |
| `mod_country_minerals_produces_mult` | `megacorp_l_russian.yml:1965` |
| `mod_country_food_produces_mult` | `megacorp_l_russian.yml:1961` |
| `mod_country_physics_research_produces_mult` | `megacorp_l_russian.yml:1975` |
| `mod_country_society_research_produces_mult` | `megacorp_l_russian.yml:1973` |
| `mod_country_engineering_research_produces_mult` | `megacorp_l_russian.yml:1971` |
| `mod_country_alloys_produces_mult` | `megacorp_l_russian.yml:1967` |
| `mod_country_consumer_goods_produces_mult` | `megacorp_l_russian.yml:1985` |
| `mod_country_trade_produces_mult` | `main_3_l_russian.yml:3832` |
| `mod_country_unity_produces_mult` | `megacorp_l_russian.yml:1963` |
| `mod_country_influence_produces_mult` | `megacorp_l_russian.yml:1983` |
| `mod_country_volatile_motes_produces_mult` | `megacorp_l_russian.yml:1979` |
| `mod_country_exotic_gases_produces_mult` | `megacorp_l_russian.yml:1981` |
| `mod_country_rare_crystals_produces_mult` | `megacorp_l_russian.yml:1977` |
| `mod_country_sr_living_metal_produces_mult` | Not found |
| `mod_country_sr_dark_matter_produces_mult` | Not found |
| `mod_country_sr_zro_produces_mult` | `modifiers_1_l_russian.yml:716` |
| `mod_country_nanites_produces_mult` | Not found |
| `mod_country_minor_artifacts_produces_mult` | Not found |
| `mod_country_astral_threads_produces_mult` | `megacorp_l_russian.yml:1987` |
| `mod_country_menace_produces_mult` | Not found |
| `mod_country_advanced_logic_produces_mult` | Not found |
| `mod_country_feral_insight_produces_mult` | Not found |
| `mod_country_entropy_crystals_produces_mult` | Not found |
| `mod_country_integrity_produces_mult` | Not found |
| `mod_country_base_energy_produces_add` | `modifiers_1_l_russian.yml:674` |
| `mod_country_base_minerals_produces_add` | `modifiers_1_l_russian.yml:675` |
| `mod_country_base_food_produces_add` | `modifiers_1_l_russian.yml:676` |
| `mod_country_base_physics_research_produces_add` | Not found |
| `mod_country_base_society_research_produces_add` | Not found |
| `mod_country_base_engineering_research_produces_add` | Not found |
| `mod_country_base_alloys_produces_add` | `modifiers_1_l_russian.yml:70` |
| `mod_country_base_consumer_goods_produces_add` | `modifiers_1_l_russian.yml:69` |
| `mod_country_base_trade_produces_add` | Not found |
| `mod_country_base_unity_produces_add` | `modifiers_1_l_russian.yml:680` |
| `mod_country_base_influence_produces_add` | `modifiers_1_l_russian.yml:693` |
| `mod_country_base_volatile_motes_produces_add` | `modifiers_1_l_russian.yml:711` |
| `mod_country_base_exotic_gases_produces_add` | `modifiers_1_l_russian.yml:712` |
| `mod_country_base_rare_crystals_produces_add` | `modifiers_1_l_russian.yml:710` |
| `mod_country_base_sr_living_metal_produces_add` | `modifiers_1_l_russian.yml:713` |
| `mod_country_base_sr_dark_matter_produces_add` | `modifiers_1_l_russian.yml:714` |
| `mod_country_base_sr_zro_produces_add` | `modifiers_1_l_russian.yml:715` |
| `mod_country_base_nanites_produces_add` | `modifiers_1_l_russian.yml:71` |
| `mod_country_base_minor_artifacts_produces_add` | Not found |
| `mod_country_base_astral_threads_produces_add` | `megacorp_l_russian.yml:1988` |
| `mod_country_base_menace_produces_add` | Not found |
| `mod_country_base_advanced_logic_produces_add` | Not found |
| `mod_country_base_feral_insight_produces_add` | Not found |
| `mod_country_base_entropy_crystals_produces_add` | `infernals_crisis_l_russian.yml:12` |
| `mod_country_base_integrity_produces_add` | Not found |
| `mod_fleet_command_limit_add` | Not found |
| `mod_shipclass_research_station_build_speed_mult` | Not found |
| `mod_shipclass_observation_station_build_speed_mult` | Not found |
| `mod_shipclass_starbase_build_speed_mult` | Not found |

## Change boundaries

All 54 keys override or add localization for shared modifiers; they are not new TCTE functions. `mod_fleet_command_limit_add` replaces its unresolved reference with `$MOD_COMMAND_LIMIT_ADD$`; `MOD_COMMAND_LIMIT_ADD` itself is not overridden.

The other 1,612 source Tass keys do not overlap explicitly defined keys in the inspected vanilla localization. The additional `TASS_CHEAT_WORMHOLE` serves an existing base-mod bypass type and references `$BYPASS_TASS_CHEAT_WORMHOLE$`.

Physical installed game files remain unchanged. Version 0.0.7 distributes only the listed trigger override; other definitions from its source file are not copied into TCTE. Shared strings match the original 0.0.1 distribution and are retained in 0.0.8. Tass overrides are recorded in the separate base-mod inventory.

[Русская версия](VANILLA_CHANGES_RU.md) · [Changelog](CHANGELOG_EN.md).
