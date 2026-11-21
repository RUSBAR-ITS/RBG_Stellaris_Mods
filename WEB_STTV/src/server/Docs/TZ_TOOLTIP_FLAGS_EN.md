# Specification. Game meanings of flags in technology tooltips

## Contents

- [Coverage](#coverage)
- [Empire and species](#empire-and-species)
- [Projects and discoveries](#projects-and-discoveries)
- [Discovered resources](#discovered-resources)
- [Policies](#policies)
- [Ignored conditions](#ignored-conditions)
- [Display and acceptance](#display-and-acceptance)

## Coverage

The survey covers four sections of all 679 base technology documents in MongoDB after script expansion, for Stellaris Cygnus v4.5.4 (1b4f). Across 85 technologies, `potential` and `weight_modifier` contain 100 checks of 32 distinct technical flags. Of those, 28 checks affect availability and 72 affect draw weight. Neither `prerequisites` nor `allow` contains any. A further 12 technologies contain 13 checks of three policy flags. The complete tooltip inventory contains 35 values, 113 checks and 97 technologies.

The tables give affirmative descriptions and the game code supporting them. Assignments were confirmed for 31 technical flags. The only global flag is `l_cluster_opened`. The other 31 technical flags belong to a country. Policy flags form a separate type and already have a source of localized labels.

## Empire and species

| Flag | Meaning in the game | Script evidence |
|---|---|---|
| `has_market_access` | The empire has access to the Galactic Market. | [on_action_events_2.txt:268](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_2.txt:268) · [galactic_community_events.txt:694](E:/SteamLibrary/steamapps/common/Stellaris/events/galactic_community_events.txt:694) |
| `first_spynetwork` | The player empire has established a spy network in another regular empire. | [nemesis_espionage_events.txt:22](E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_espionage_events.txt:22) · [nemesis_espionage_events.txt:58](E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_espionage_events.txt:58) |
| `chosen_empire` | This empire is the Chosen. | [special_system_initializers.txt:2704](E:/SteamLibrary/steamapps/common/Stellaris/common/solar_system_initializers/special_system_initializers.txt:2704) · [special_system_initializers.txt:2719](E:/SteamLibrary/steamapps/common/Stellaris/common/solar_system_initializers/special_system_initializers.txt:2719) |
| `synthetic_empire` | This is a synthetic empire. | [machine_age_situation_events_2.txt:649](E:/SteamLibrary/steamapps/common/Stellaris/events/machine_age_situation_events_2.txt:649) · [unique_system_events.txt:971](E:/SteamLibrary/steamapps/common/Stellaris/events/unique_system_events.txt:971) |
| `machine_subspecies` | The empire began with a secondary species with the Mechanical or Machine trait. | [species_subspecies.txt:17](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/game_start/species_subspecies.txt:17) · [species_subspecies.txt:28](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/game_start/species_subspecies.txt:28) |
| `non_lithoid_subspecies` | The empire’s starting setup provides food for its secondary species. | [species_subspecies.txt:59](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/game_start/species_subspecies.txt:59) · [01_start_of_game_effects.txt:2263](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/01_start_of_game_effects.txt:2263) · [01_start_of_game_effects.txt:3057](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/01_start_of_game_effects.txt:3057) |
| `found_presapients` | The empire knows of pre-sapient species. | [uplifting_events.txt:202](E:/SteamLibrary/steamapps/common/Stellaris/events/uplifting_events.txt:202) · [game_start.txt:588](E:/SteamLibrary/steamapps/common/Stellaris/events/game_start.txt:588) · [00_policies.txt:4277](E:/SteamLibrary/steamapps/common/Stellaris/common/policies/00_policies.txt:4277) |
| `bio_cloning` | The empire chose cloning as its path of biological development. | [biogenesis_events.txt:3255](E:/SteamLibrary/steamapps/common/Stellaris/events/biogenesis_events.txt:3255) · [biogenesis_events.txt:3267](E:/SteamLibrary/steamapps/common/Stellaris/events/biogenesis_events.txt:3267) · [biogenesis_events.txt:3453](E:/SteamLibrary/steamapps/common/Stellaris/events/biogenesis_events.txt:3453) |
| `covenant_end_of_the_cycle` | The empire made a covenant with the End of the Cycle. | [shroud_shadows_scripted_effects.txt:2409](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/shroud_shadows_scripted_effects.txt:2409) · [shroud_shadows_scripted_effects.txt:2420](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/shroud_shadows_scripted_effects.txt:2420) · [utopia_shroud_events.txt:6466](E:/SteamLibrary/steamapps/common/Stellaris/events/utopia_shroud_events.txt:6466) |

`first_spynetwork` records the first qualifying network. The event requires `is_ai = no` and a target of the default country type. `synthetic_empire` can be set when a synthetic country is created or during digitization. `non_lithoid_subspecies` records how the secondary species was handled at game start. The setup has distinct machine, lithoid and infernal branches, plus special handling for `is_guided_sapience_empire`. Testing the present population would give a different result.

## Projects and discoveries

| Flag | Meaning in the game | Script evidence |
|---|---|---|
| `colossus_project` | The Colossus Project has been completed. | [apocalypse_events.txt:575](E:/SteamLibrary/steamapps/common/Stellaris/events/apocalypse_events.txt:575) · [apocalypse_events.txt:581](E:/SteamLibrary/steamapps/common/Stellaris/events/apocalypse_events.txt:581) |
| `can_build_star_eaters` | The empire has unlocked construction of Star-Eaters. | [nemesis_crisis_endgame.txt:233](E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_crisis_endgame.txt:233) · [nemesis_crisis_endgame.txt:242](E:/SteamLibrary/steamapps/common/Stellaris/events/nemesis_crisis_endgame.txt:242) |
| `origin_shoulders_closure` | The empire reached the conclusion of its On the Shoulders of Giants story. | [origin_events_2.txt:2686](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_2.txt:2686) · [origin_events_2.txt:2993](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_2.txt:2993) |
| `artifact_yuht_research_completed` | The empire completed the Secrets of the Yuht artifact project. | [ancient_relics_arcsite_events_2.txt:6724](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:6724) · [ancient_relics_arcsite_events_2.txt:6766](E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:6766) |
| `finish_shroud_forged_liberation_flag` | The Forged by the Shroud situation ended in the liberation of the Shroud-Forged. | [03_origin_situations.txt:261](E:/SteamLibrary/steamapps/common/Stellaris/common/situations/03_origin_situations.txt:261) |
| `encountered_first_lgate` | The empire has encountered its first L-Gate. | [apocalypse_events.txt:92](E:/SteamLibrary/steamapps/common/Stellaris/events/apocalypse_events.txt:92) · [distant_stars_events_3.txt:2402](E:/SteamLibrary/steamapps/common/Stellaris/events/distant_stars_events_3.txt:2402) |
| `completed_lcluster_chain` | The empire has collected all the insights needed to open the L-Cluster. | [00_scripted_effects.txt:3268](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:3268) · [00_scripted_effects.txt:3274](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:3274) |
| `l_cluster_opened` | Access to the L-Cluster has been opened. | [distant_stars_events_3.txt:1338](E:/SteamLibrary/steamapps/common/Stellaris/events/distant_stars_events_3.txt:1338) |
| `advanced_identity_creation` | The empire gained access to advanced methods for creating synthetic identities. | [machine_age_situation_events_2.txt:1164](E:/SteamLibrary/steamapps/common/Stellaris/events/machine_age_situation_events_2.txt:1164) · [machine_age_situation_events_2.txt:1199](E:/SteamLibrary/steamapps/common/Stellaris/events/machine_age_situation_events_2.txt:1199) · [origin_events_machine_age.txt:2100](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_machine_age.txt:2100) |
| `synth_queen_knowledge` | Cetana granted the empire knowledge towards researching Cetana’s Thought. | [02_machine_age_effects.txt:3477](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/02_machine_age_effects.txt:3477) |
| `cosmogenesis_aborted` | The empire agreed to halt Cosmogenesis at the materialist Fallen Empire’s demand. | [machine_age_crisis_events.txt:2617](E:/SteamLibrary/steamapps/common/Stellaris/events/machine_age_crisis_events.txt:2617) · [machine_age_crisis_events.txt:2623](E:/SteamLibrary/steamapps/common/Stellaris/events/machine_age_crisis_events.txt:2623) |
| `has_quantum_catapult_insight` | The empire used the Gain Quantum Catapult Insight astral action. | [astral_planes_actions.txt:69](E:/SteamLibrary/steamapps/common/Stellaris/common/astral_actions/astral_planes_actions.txt:69) |
| `starfire_cannon_unlocked` | The outcome at the empire’s home star unlocked Starfire Cannon research. | [infernals_1_events.txt:1100](E:/SteamLibrary/steamapps/common/Stellaris/events/infernals_1_events.txt:1100) · [infernals_1_events.txt:1338](E:/SteamLibrary/steamapps/common/Stellaris/events/infernals_1_events.txt:1338) · [infernals_1_events.txt:5506](E:/SteamLibrary/steamapps/common/Stellaris/events/infernals_1_events.txt:5506) |
| `has_encountered_psionic_auras` | The empire has encountered a psionic aura. | [psionic_auras_scripted_effects.txt:284](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/psionic_auras_scripted_effects.txt:284) · [00_auras.txt:989](E:/SteamLibrary/steamapps/common/Stellaris/common/patrons/psionic_auras/00_auras.txt:989) |
| `payback_researching_gene_clinics` | During the Healthcare Crisis, the empire increased funding for medical research. | [origin_events_4.txt:3124](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_4.txt:3124) · [origin_events_4.txt:3136](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_4.txt:3136) |
| `tech_mine_rare_crystals_culling_boost` | The empire has culled a Crystalline Entity. | [00_on_actions.txt:5494](E:/SteamLibrary/steamapps/common/Stellaris/common/on_actions/00_on_actions.txt:5494) · [origin_events_grand_archive.txt:7315](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_grand_archive.txt:7315) · [origin_events_grand_archive.txt:7323](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_grand_archive.txt:7323) |

The L-Gate flags record three independent facts. One empire can encounter a gate and another can collect the insights, while opening the L-Cluster is a galaxy-wide event. Both the supernova outcome and stellar stabilization can unlock Starfire Cannon research. For the Rare Crystal Mining bonus, the culling event checks the space fauna specimen’s ship type.

## Discovered resources

| Flag | Meaning in the game | Script evidence |
|---|---|---|
| `astral_threads_found` | The empire has discovered Astral Threads. | [on_action_events_1.txt:8094](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8094) · [origin_events_astral_planes.txt:23](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_astral_planes.txt:23) |
| `sr_living_metal_found` | The empire has discovered Living Metal. | [on_action_events_1.txt:8084](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8084) |
| `volatile_motes_found` | The empire has discovered Volatile Motes. | [on_action_events_1.txt:8054](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8054) |
| `exotic_gases_found` | The empire has discovered Exotic Gases. | [on_action_events_1.txt:8044](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8044) |
| `rare_crystals_found` | The empire has discovered Rare Crystals. | [on_action_events_1.txt:8034](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8034) |
| `sr_dark_matter_found` | The empire has discovered Dark Matter. | [on_action_events_1.txt:8074](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:8074) |

These flags record that the empire has discovered a resource. For empires with the `origin_riftworld` origin, Astral Threads count as discovered at game start.

## Policies

| Flag | Meaning in the game | Script evidence |
|---|---|---|
| `ai_outlawed` | Artificial intelligence is outlawed. | [00_policies.txt:4016](E:/SteamLibrary/steamapps/common/Stellaris/common/policies/00_policies.txt:4016) |
| `robots_outlawed` | Robotic workers are outlawed. | [00_policies.txt:4189](E:/SteamLibrary/steamapps/common/Stellaris/common/policies/00_policies.txt:4189) |
| `slavery_allowed` | Slavery is allowed. | [00_policies.txt:4745](E:/SteamLibrary/steamapps/common/Stellaris/common/policies/00_policies.txt:4745) |

These rows describe the selected option. The interface retains its existing localized policy and option labels from `wiki.policies` and `wiki.localization`. In particular, `robots_outlawed` belongs to the `robot_pops_outlawed` option of `robot_pop_policy`.

## Ignored conditions

| Check | Flag ID | RU/EN display rule |
|---|---|---|
| `has_country_flag` | `crystal_armor_1_weight` | Hide the condition. It is the only condition on the +5 bonus, so omit the entire modifier row. Omit the weight section heading when the section is empty. |

`crystal_armor_1_weight` occurs in Crystal-Infused Plating. Its base weight is zero and the flag check adds five. The check is present in the inspected scripts. Neither a setter nor an event sufficient to set it could be confirmed. Anomaly `anomaly.6890` passes the same technology to `add_tech_option_or_research_effect`, which grants a research option, progress or research points. That constitutes a separate acquisition route. [Weight check](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2009) · [Anomaly](E:/SteamLibrary/steamapps/common/Stellaris/events/anomaly_events_4.txt:3293) · [Effect body](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:4904)

The Cutholoid kill hypothesis was checked against v4.5.4. When a wild Cutholoid dies, `grand_archive.3025` can create debris. A science ship with a scientist spends 90 days studying it. `grand_archive.3026` offers two equally weighted rewards, 1,000 minerals or 200 rare crystals. This chain contains no assignment of the plating flag. The Annoyed Crystal anomaly spawns a different creature, a Crystalline Entity equipped with the biological plating component. With the hunting modifier active, `story.216` awards the player 500 minerals for destroying a crystalline fleet. Direct grants of the plating research option appear in `story.205` and `story.207`. [Cutholoid debris](E:/SteamLibrary/steamapps/common/Stellaris/events/grand_archive_events.txt:3593) · [Project completion](E:/SteamLibrary/steamapps/common/Stellaris/common/special_projects/04_projects_grand_archive.txt:168) · [Rewards](E:/SteamLibrary/steamapps/common/Stellaris/events/grand_archive_events.txt:3637) · [Annoyed Crystal](E:/SteamLibrary/steamapps/common/Stellaris/events/anomaly_events_4.txt:3256) · [Entity component](E:/SteamLibrary/steamapps/common/Stellaris/common/global_ship_designs/crystal_monster_designs.txt:940) · [Hunting reward](E:/SteamLibrary/steamapps/common/Stellaris/events/story_events.txt:2630) · [Research](E:/SteamLibrary/steamapps/common/Stellaris/events/story_events.txt:2563) · [Pacification](E:/SteamLibrary/steamapps/common/Stellaris/events/story_events.txt:2621)

The v2.2.0 tree snapshot records a base weight of zero and a +1 bonus for this flag. A March 2019 archive of the 2.2 game scripts gives +5. Across all 618 `.txt` files in its `common` and `events` directories, the only literal occurrence is the weight check. This establishes the age of the condition. No historical assignment of the flag for killing a creature has been confirmed. [v2.2.0 snapshot](/D:/Repos/stellaris-tech-tree/leguin-2.2.0/anomalies.json:168) · [Historical technology definition](https://gitlab.com/stellaris/game/-/blob/a0c3fbc8f0678b9b6dd0931a036a335cfb8e34fa/game/common/technology/00_eng_tech.txt#L1631)

This exception applies only when preparing the tooltip. Keep the original condition and operation in the database for further investigation.

## Display and acceptance

1. The server looks up a complete phrase by check type, flag ID and selected language. Additional RU/EN entries in the existing project localization dictionary suffice. Reuse game localization keys for names where their grammatical form fits. The frontend renders `text` with its existing component. This requires neither a new collection nor a search through events at hover time.
2. For displayed conditions, replace only the predicate label. Preserve order, subject, country or galaxy scope, nested AND/OR/NOT/NAND/NOR and numeric operations. When the group heading already supplies negation, keep its child phrase affirmative. These descriptions do not evaluate a running game.
3. Match ignored conditions by exact check type and flag ID before looking up a label. For an unknown flag in a future dataset or a missing translation in the selected language, keep the visible condition and its operation, display a localized neutral label and include type, ID, technology and section in diagnostics. Keep raw identifiers out of user-facing phrases.
4. Before publication, compare the actual set of check type/ID pairs against the tables, report newly encountered values and check both languages. For `tech_crystal_armor_1` in the current dataset, verify that the tooltip omits the technical ID, the +5 row, any placeholder and the empty weight heading. Check scopes and negation for `tech_repeatable_lcluster_clue`, discovery and culling as separate conditions for `tech_mine_rare_crystals`, and the event choice for `tech_frontier_health`. Compare existing policy labels and other predicates. Check the new API and browser output in RU and EN.

[Condition dictionary](TZ_TOOLTIP_DICTIONARY_EN.md) · [Русская версия](TZ_TOOLTIP_FLAGS_RU.md)
