# Stellaris 4.6.0 reward sources, leader trait data and condition text

## Contents

- [Reward sources](#reward-sources)
- [Data for the leader trait reference](#data-for-the-leader-trait-reference)
- [Names and conditions](#names-and-conditions)
- [Acceptance](#acceptance)

## Reward sources

Draft specification for build 4.6.0 (3d1a). The collection stage adds technology reward sources and data for a future leader trait reference. For technology rewards, add both complete directories in the table to the regular parser and loader profiles. Use the top-level block key as the document ID. Preserve provenance and expansion history through the existing loader.

| Directory under `common/` | Collection | Objects after expansion | Reward commands |
|---|---|---:|---|
| `menace_perks/` | `menace_perks` | 105 | 1 researched grant, 6 progress awards |
| `ideologies/tenets/` | `ideology_tenets` | 95 | 1 research option |

The server reads executable effects and records the path to each command and its recipient. For a crisis perk, resolve its level through the references in `crisis_levels.perks`. Keep level unlock requirements, perk or tenet requirements and effect branch guards attached to the relevant step. A source may also dispatch an event. Preserve that transition and its guards in the index. A tenet's `source_civic` identifies a civic or origin icon. Read selection conditions from `ethics` and `potential`.

Include both collections and their provenance in the dependencies of the derived data that read them. Input changes must refresh the acquisition index, tooltip content and dependent trees through existing revision and reset handling. The card and technology page consume the same server response.

## Data for the leader trait reference

Definitions and RU/EN strings already enter `traits` and `localization`. The 4.6.0 snapshot contains 797 traits with `leader_class`, including one with the scalar value `all`. For 299 definitions, `replace_traits` links a trait to a predecessor. Preserve these links, tier information, restrictions, modifiers and the order of icon layers. Building reference pages and computing all acquisition paths belong to the later reference stage.

| Source under the game root | Collection | Purpose |
|---|---|---|
| `common/leader_classes/` | `leader_classes` | Classes and their capabilities, including `envoy.can_have_traits = no`. Skip the documentation file `00_README.txt` when selecting definitions. |
| `common/game_rules/00_rules.txt` | `game_rules` | Shared selection rules for normal traits, council traits, subclasses and destiny traits with expanded calls. |
| `common/defines/00_defines.txt` | `defines` | One document per named section of constants. `NGameplay` contains the trait selection levels and limits. |
| `common/relics/` | `relics` | Relic activation effects, recipients and conditions for trait grants. Skip the documentation file `99_documentation.txt`. |
| `common/decisions/` | `decisions` | Decision effects, including leader class changes and trait grants. |
| `prescripted_countries/` | `prescripted_countries` | Preset empire and ruler definitions. Preserve the enclosing block of each `trait` field so ruler traits and species traits can be distinguished. |
| `common/named_colors/01_trait_colors.txt` | `named_colors` | Named layer colors with their original RGBA components. Load the named color from the `tagged_block` node for `trait_bg_active_glow { … }` and preserve its provenance. |

For every script directory in the table, import all files that contain definitions. Store one document per game object under its original key. Events and expansion libraries already participate in the build.

For icons, add `interface/icons/traits/leader_traits.gfx`, `interface/icons/traits/traits_shared.gfx` and `interface/leaders.gfx`. In the `sprites` collection, store each sprite definition by its `name`, including its texture path or reference to another sprite, frame count and selected frame when present. Follow layer and `background_icon` references down to DDS files, including direct paths. The existing image loader prepares and transfers PNGs. Multiple references can share one texture. Preserve layer order, colors and `visible` conditions for the future page.

## Names and conditions

After importing the sources, extend the shared server dictionary and condition handlers for RU and EN. Preserve the subject, operator, operand and nesting in the text.

| Game expression | Display |
|---|---|
| `on_ideology_momentum_positive` | Name the game action for positive ideological momentum. Preserve random event selection in the route. |
| `num_active_tenets > 0` | The empire has at least one active tenet. Display the actual comparison and number for other thresholds. |
| `ideology? = { … }` | Name the current participant's ideology and describe nested conditions in that scope. Preserve the optional scope transition and the actual referent of `prev`. |
| `free_building_slots > 0` | The colony being checked has a free building slot. Retain other thresholds when specified. |
| `is_country_type = rebel` | Display the country type in the selected language. |
| `GetCulturalEnvoyNamePlural` | In reference mode use the game's explicit `default = cultural_envoy_default_plural` key and the existing localization lookup. |

For `tech_galactic_halls`, verify the meaning of `mult = 2` specifically in `weight_modifier.modifier`. Display a multiplier once confirmed. If evidence is insufficient, record the original operation and the remaining limitation in the report. For event `forceofwill.1560`, convey that its title refers to a tenet selected in game without inventing a particular tenet. In the next audit separately recheck the precursor and ideology projection flags and `event_target:selected_precursor_system` recorded in the [4.6.0 acceptance report](STELLARIS_4_6_0_ACCEPTANCE_EN.md).

## Acceptance

1. Verify the export of both directories, unique game IDs and document fields against game files. The three variable declarations in the crisis perk file remain part of the source script. Build 4.6.0 yields 105 and 95 object documents respectively.
2. At crisis level two, unlocking `menp_force_of_will_cultural_envoys` grants the researched `tech_cultural_envoys`. At level five verify the independent 50% progress award for `tech_jump_drive_1` and the five cloaking branches. With First Contact enabled, the first unresearched technology in script order receives the cloaking award. With all five researched or the DLC disabled, no cloaking award is issued. The reference entry retains the DLC requirement.
3. For `tenet_lost_makers_yuht`, verify that it grants the `tech_ecological_adaptation` research option, requires the technology to be unresearched, and retains the ethic and the flag from `potential`. Match all eight commands to source objects, reward sections and source positions. Check event dispatches from the new sources for duplicate paths.
4. Rebuild the acquisition index and derived data, then repeat requests from saved collections. Inspect all 683 base technologies in RU and EN. Compare sections and previously verified rewards. Check markup, expandable details, unnamed actions and untranslated operands against the [baseline audit](STELLARIS_4_6_0_ACCEPTANCE_EN.md). Report outstanding cases by category.
5. Compare the imported trait sources with the export in a clean database. Check the four leader classes, the `can_leader_get_destiny_trait` rule and the game values `LEADER_SUBCLASS_CHOICE_LEVEL = 4` and `LEADER_DESTINY_CHOICE_LEVEL = 8`. Trace `r_odryskan_crystal` granting `leader_trait_maniacal` to a scientist, the class change and five grants in `decision_deploy_beholder`, and `trait_ruler_warlike` in the ruler block of the `warmongers` empire.
6. Check the data for future localization across all 797 traits. On 4.6.0, 228 RU and 230 EN traits lack a direct name key, and 234 RU and 236 EN traits lack a direct description key. For each missing field, follow the unambiguous `replace_traits` chain to an available string in the selected language. Check the tier against its game definition.
7. Resolve all 485 graphics references to 480 distinct DDS files and verify the corresponding published PNGs. Check the 11 colors in use and their values, all three `GFX_trait_tier` frames, and the conditional `trait_bg_active_glow` layer on the three `storm_rider` traits. These counts are baselines for build 4.6.0 (3d1a).
