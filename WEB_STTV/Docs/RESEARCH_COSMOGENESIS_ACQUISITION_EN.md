# Cosmogenesis technology acquisition and DLC restrictions

## Contents

- [Status and scope](#status-and-scope)
- [The two acquisition paths](#the-two-acquisition-paths)
- [Direct grants and generic mechanisms](#direct-grants-and-generic-mechanisms)
- [Impact on current filtering](#impact-on-current-filtering)
- [Random-grant follow-up](#random-grant-follow-up)
- [Implementation conclusion](#implementation-conclusion)

## Status and scope

Research dated 2026-11-19, requested by the user during [stage 21](TZ_BACKEND_STAGE_21_EN.md). The purpose is to examine acquisition of `tech_cosmogenesis_world` and `tech_cosmogenesis_escort` before propagating restrictions through `has_technology`.

Installed sources: Cygnus v4.5.4 (1b4f), according to `launcher-settings.json`. Checks covered references in game TXT files, definitions and calling chains, local engine documentation, and the completed DLC matrix. The game was not launched and its sources were not modified. The generator version of the local `effects.log` / `triggers.log` was not independently confirmed; these are supplementary evidence, not an in-game engine test.

The examined setting is normal acquisition in a new campaign with a fixed DLC set. Console grants, mods, and saves whose DLC set changed after acquisition were not tested. This is not an exhaustive acquisition analysis for all technologies.

## The two acquisition paths

| Technology | Its own conditions | Where research becomes available |
| --- | --- | --- |
| `tech_cosmogenesis_world` | `weight = 0`; `potential`: The Machine Age **AND** `has_ascension_perk = ap_cosmogenesis` | `crisis_cosmogenesis_level_1` → `on_unlock` → `add_cosmogenesis_level_1_perks` → `add_research_option` |
| `tech_cosmogenesis_escort` | `weight = 0`; `potential`: The Machine Age **AND** `country_uses_bio_ships = no` | `crisis_cosmogenesis_level_2` → `on_unlock` → `add_cosmogenesis_level_2_perks` → non-biological-ship branch → `add_research_option` |

Definitions: [world](/E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_machine_age_tech.txt:351), [escort](/E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_machine_age_tech.txt:197). Research-option effects: [level 1](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/02_machine_age_effects.txt:15), [level 2](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/02_machine_age_effects.txt:29). Callers: [level 1](/E:/SteamLibrary/steamapps/common/Stellaris/common/crisis_levels/00_crisis_levels.txt:375), [level 2](/E:/SteamLibrary/steamapps/common/Stellaris/common/crisis_levels/00_crisis_levels.txt:397).

Both levels belong to [cosmogenesis_path](/E:/SteamLibrary/steamapps/common/Stellaris/common/crisis_paths/00_cosmogenesis_paths.txt:3). The path is activated by `ap_cosmogenesis.on_enabled`; the perk requires The Machine Age in `potential`: [perk definition](/E:/SteamLibrary/steamapps/common/Stellaris/common/ascension_perks/00_ascension_perks.txt:330). The discovered `activate_crisis_progression = cosmogenesis_path` call is in this perk. `has_machine_age_dlc` expands to `host_has_dlc = "The Machine Age"`: [source](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:444).

Level 2 additionally requires `tech_cosmogenesis_crisis_1` and 4000 crisis currency. These are progression conditions, not DLC settings, and are not evaluated here.

`add_research_option` adds a permanent research option until researched; it does not complete research. The chain therefore explains acquisition despite zero weight: special option unlock → research. [Effect documentation](</C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/logs/script_documentation/effects.log:1220>).

## Direct grants and generic mechanisms

- No direct grants of these two IDs through `give_technology` or `research_technology` were found in the examined game TXT files. The two stated `add_research_option` calls were found; other exact references check ownership or use the technology as a requirement.
- According to local documentation, `copy_random_tech_from`, used for research theft, requires `weight > 0` and a satisfied `potential`. Both definitions have zero weight. This mechanism therefore does not substantiate a bypass. [Documentation](</C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/logs/script_documentation/effects.log:1985>), [actual use](/E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_operations_events_1.txt:840).
- Documentation also says `copy_techs_from` honours weights and weight modifiers. The existence of bulk copying does not itself prove these technologies can be granted. [Documentation](</C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/logs/script_documentation/effects.log:1805>).
- `give_technology` is described as an immediate grant, but its documentation does not establish a universal `potential` check. Such effects must be investigated separately for other technologies. [Documentation](</C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/logs/script_documentation/effects.log:93>).
- `add_random_research_option` and internal NPC mechanisms were not analysed to establish all engine rules. Absence of an exact ID reference does not exclude every dynamic route. [Random-option documentation](</C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/logs/script_documentation/effects.log:1971>).

No confirmed normal acquisition route without The Machine Age was found for these two technologies. This is narrower than “a false `potential` always prevents ownership of any technology”.

## Impact on current filtering

The stage 21 report retained eight paths to The Machine Age through these references:

| Consumers | Condition form | Consequence |
| --- | --- | --- |
| `tech_lathe_resonator`, `tech_lathe_overclocker`, `tech_lathe_preserver`, `tech_lathe_life_support`, `tech_lathe_cogitator`, `tech_lathe_validator` | The Machine Age **AND** `ap_cosmogenesis` **AND** `has_technology = tech_cosmogenesis_world` | All six already have their own direct DLC restriction. An unknown final condition does not prevent hiding them without Machine Age. |
| `tech_missiles_1`, `tech_torpedoes_1` | Conventional ships **OR** `tr_nanotech_4` **OR** `crisis_level_2` **OR** `has_technology = tech_cosmogenesis_escort` | Excluding one alternative does not exclude the whole technology. Conventional-ship routes remain in reference mode. |

Sources: [Lathe conditions](/E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_machine_age_tech.txt:420), [missiles](/E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_weapon_tech.txt:744), [torpedoes](/E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_weapon_tech.txt:1038).

Completed-matrix check: all 43 profiles without `dlc032` hide the six Lathe technologies; missiles and torpedoes remain visible. This checks the current reference mode without a fixed empire. The eight unresolved paths must not be described as eight incorrectly displayed cards.

## Random-grant follow-up

Implementation of the approved addendum traversed the corpus AST, including calls without a literal technology ID. After confirmed domain filters, four `add_random_research_option` locations allowing rare technologies remain for both targets: `machine_age_crisis_events.txt`, `shroud_forged_events.txt`, `overlord_specialist_events.txt`, and `shroud_events.txt`. Command addresses and conditions are recorded in `data/stage21_acquisition/acquisition_summary.json` and the `dlc_none_analysis.json` graph.

For example, [shroud_events.txt:1247](/E:/SteamLibrary/steamapps/common/Stellaris/events/shroud_events.txt:1247) uses `ignore_rare = no`. Documentation lists selection parameters and defaults but does not establish `potential` or zero-weight checks. Missing Machine Age therefore closes the normal crisis route without proving every random route impossible. Both `has_technology` results remain **unknown**, with specific reasons. Uncertainty asserts neither actual availability nor impossibility.

`copy_random_tech_from` and `copy_techs_from` use their own documented constraints; those are not transferred to random research options. Reports distinguish source parsing coverage from engine-semantic coverage.

## Implementation conclusion

Confirmed acquisition chains pass through a DLC-dependent perk and crisis levels. The implementation connects research unlocks to calling effects and progression conditions; recursively inspecting `technology.potential` alone is not a substitute. `crisis_paths` and `crisis_levels` now belong to the 30-kind registry.

Following the approved [addendum](TZ_BACKEND_STAGE_21_ACQUISITION_EN.md), `has_technology` uses the general acquisition analysis without exceptions for these IDs. Results and verification boundaries are documented in the [stage 21 guide](BACKEND_STAGE_21_EN.md). The uncertain engine semantics have not been tested in game.

[Русская версия](RESEARCH_COSMOGENESIS_ACQUISITION_RU.md).
