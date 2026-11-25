# RUS_FIX_FIX — affected files and functions

## Contents

- [4.6.0 baseline](#460-baseline)
- [Compatibility areas](#compatibility-areas)

## 4.6.0 baseline

The [complete 285-file inventory](../../TMP/RUS_FIX_FIX/files.json) records paths, sizes, Workshop matches and shared paths with vanilla and UIOD. 254 paths coincide with vanilla. The audit checked 33 DLC archives for intersecting paths and English or Russian localization. Results describe the inputs before edits. At audit time, local runtime files matched upstream 4.5.4 apart from the user’s manifest.

## Compatibility areas

Version `4.5.13` changes five Russian localisation files, `scripted_loc_l_russian.yml`, `apocalypse_l_russian.yml`, `wilderness_l_russian.yml`, `strange_worlds_l_russian.yml` and `nemesis_content_l_russian.yml`. The review covered `GetPlanetMoon_RULOC`, `GetSabotagedStarbaseTitle`, the preset definitions in `common/agreement_presets/`, the `ring_feeder` building and the sabotage flag in `espionage_event_effects.txt`. For leader biographies, the branches of `GetJob_gender_lower_FR` were matched to the author’s `background_job_rinfix`. [Evidence by key](../../TMP/RUS_FIX_FIX/older_forms_review.json).

Version `4.5.12` adds entries in 33 files under `localisation/russian/`. Updates to existing entries also touch `toxoids_l_russian.yml`, bringing the total to 34. Checked stratum names in `common/pop_categories/00_social_classes.txt` and `02_other_categories.txt`, the `is_warmongers_empire` condition, and selectors for precursors, leaders and revolts. Checked precursor site requirements against `has_accessible_precursor_system` and its callers in `common/artifact_actions/artifact_actions.txt`. Repair descriptions refer to `ship_orbit_repair` and `station_self_repair` in `common/static_modifiers/02_static_modifiers.txt` and to timing and speed parameters in `common/defines/00_defines.txt`. Compared internal name formats with vanilla localization. [Paths and keys](../../TMP/RUS_FIX_FIX/remaining_46_review.json) · [Effective text and source checks](../../TMP/RUS_FIX_FIX/remaining_46_result.json).

Version `4.5.11` changes six files under `localisation/russian/` named `main_2_l_russian.yml`, `modifiers_1_l_russian.yml`, `paragon_2_l_russian.yml`, `ancient_relics_l_russian.yml`, `leaders_l_russian.yml` and `triggers_effects_l_russian.yml`. Vanilla functions `triggered_gifted_name` and `triggered_gifted_desc` in `common/scripted_loc/08_scripted_loc_paragon.txt` select the trait text. `GetDelegateSubclassSubtitle` in `common/scripted_loc/16_scripted_loc_forceofwill.txt` selects the Delegate subtitle. Governor effects were checked against `skill_official_colony_governor` in `common/static_modifiers/00_static_modifiers.txt` and its two values in `common/scripted_variables/00_scripted_variables.txt`. [Keys, branches and sources](../../TMP/RUS_FIX_FIX/leaders_46.json).

Version `4.5.10` adds entries in four files under `localisation/russian/`. Ethic requirements are in `main_2_l_russian.yml`, attraction labels in `main_1_l_russian.yml` and `modifiers_1_l_russian.yml`, and population ideology conditions in `triggers_effects_l_russian.yml`. Ethic tiers were checked against `common/scripted_triggers/00_scripted_triggers.txt`, and government requirements against `common/governments/civics/00_civics.txt` and `common/governments/authorities/00_authorities.txt`. Vanilla examples use `pop_ideology_amount` and `pop_ideology_percentage` for counts and percentages. [Keys and source locations](../../TMP/RUS_FIX_FIX/ethics_ideology_46.json).

Version `4.5.9` updates `localisation/russian/astral_rifts_3_l_russian.yml`. Branches were checked against `events/astral_rifts_3_events.txt`, which selects ordinary and Lost Makers descriptions and the 19 variants for sharing a technology. For event 3055, the comparison also covers `GetResearchers` in `common/scripted_loc/00_scripted_loc.txt`, `GetSkinType` in `common/scripted_loc/09_scripted_loc_astral_planes.txt`, and upstream inflected body-covering names in `astral_planes_l_russian.yml`. [Affected localization keys](../../TMP/RUS_FIX_FIX/astral_rifts_4.5.9.json).

Version `4.5.8` adds entries to `localisation/russian/economic_modifiers_l_russian.yml` and `localisation/russian/megacorp_l_russian.yml`. The two sets of labels follow `planet_purge_jobs` in `common/economic_categories/01_job_categories.txt` and `ship_cultural_envoy` in `common/economic_categories/00_common_categories.txt`. The vanilla `GetCulturalEnvoyNamePlural` function in `common/scripted_loc/16_scripted_loc_forceofwill.txt` selects the displayed ship name. [Verification of all 205 entries](../../TMP/RUS_FIX_FIX/economic_modifiers_46.json).

Version `4.5.7` adds one key each to `random_names/pop_faction_formats_l_russian.yml`, `wilderness_l_russian.yml` and `paragon_2_l_russian.yml` under `localisation/russian/`. Vanilla generates the official modifier from the `leader_officials` category. The author’s faction generator uses `{interlink}`, which resolves to the same name as the restored format. Both vanilla languages define the `…_uncapped_max` Orchard Forest key. Its use in a specific UI element has yet to be observed.

Version `4.5.6` adds entries to seven `localisation/russian/*_l_russian.yml` files with the following stems: `civic_and_origin_concepts`, `federations`, `federations_anniversary`, `main_1`, `megacorp`, `modifiers_1`, `nemesis_intel`. Each reference matches both English and Russian Stellaris 4.6.0. [Paths, keys and resolved text](../../TMP/RUS_FIX_FIX/aliases_4.5.6.json).

Local version `4.5.5` updates `localisation/russian/utopia_ascension_l_russian.yml` to restore the vanilla keys `triggered_opinion_cyborgs_absolute` and `triggered_opinion_synthetics_absolute` used by `common/opinion_modifiers/00_opinion_modifiers.txt`.

| Area | Affected files and functions |
| --- | --- |
| Localization | 242 files: 233 in `localisation/russian/` and 9 in `localisation/replace/`. Read 942 source files across four datasets (4.6 EN/RU, the Russian snapshot and the author’s entries). All entries parsed. Vanilla Russian has 14 keys with conflicting definitions that require file-level review. |
| Interface | All 19 upstream `.gui` files share paths with vanilla and UIOD. Together with two `.gfx` files, all 21 differ from vanilla at the byte level. Both versions of all 21 files parsed. Widget name differences highlight structural changes. Also check bindings and dimensions where identifiers agree. [Window comparison](../../TMP/RUS_FIX_FIX/interface.json). |
| Jobs and categories | `common/pop_jobs/02_specialist_jobs.txt` defines `culture_worker` separately. The localization mod defines 73 auxiliary jobs and four categories. Among the names used in yes/no expressions in the jobs file, 87 are vanilla scripted triggers. The others are the built-in `always` and the missing `bureaucrat_is_culture_worker`. |
| Inflection, names and factions | Checked literal `localization_key` and `default` references in the two `common/scripted_loc/` files: 753 distinct keys in the background file and 158 in the general file. Found one extra leading underscore. All 661 distinct empire and 168 faction name parts respectively resolve in the effective Russian localization. [Name generators](../../TMP/RUS_FIX_FIX/name_generators.json). |
| Empire presets | Reference files are `prescripted_countries/00_top_countries.txt`, `88_astral_planes_prescripted_countries.txt`, `89_first_contact_prescripted_countries.txt`, `90_toxoids_prescripted_countries.txt` and `default.txt`. Test `florin` as a separate custom preset. The user’s log confirms that four other presets are hidden. |
| Fonts and graphics | One font declaration and 10 files under `gfx/` include OrbitronCYR, two 3A font sets, four single-pixel category icons and a logo. The OrbitronCYR reference resolves. Both 3A atlases are 512 × 512. The medium descriptor names a PNG alongside the supplied DDS, and the small descriptor omits a page line. Rendered behavior requires testing in game. |
| Manifest and picture | The local mod has its own display name. The thumbnail is byte-identical to upstream. |

[Script and resource checks](../../TMP/RUS_FIX_FIX/compatibility_checks.json) · [Definition inventory](../../TMP/RUS_FIX_FIX/scripts.json) · [Draft specification](TZ_COMPAT_46_EN.md).
