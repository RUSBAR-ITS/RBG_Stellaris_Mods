# Tass Cheat Tool Extender

## Contents

- [Purpose and requirements](#purpose-and-requirements)
- [Policy levels](#policy-levels)
- [Resource grants](#resource-grants)
- [Advanced species modification](#advanced-species-modification)
- [Extra envoys](#extra-envoys)
- [Localization contents](#localization-contents)
- [Installation](#installation)
- [Validation](#validation)
- [In-game testing](#in-game-testing)
- [Source mod details](#source-mod-details)
- [Working materials](#working-materials)

## Purpose and requirements

**Tass Cheat Tool Extender**, ID **TCTE**, version **0.0.8**. The mod localizes Tass Cheat Tool into Russian, extends policies to ten levels, adds resource and cumulative envoy menus, and provides a species modification toggle with additional permission to remove beneficial traits.

The required dependency is **Tass Cheat Tool**, Workshop ID `682851228`, verified version `20261012`. The target Stellaris version is `v4.5.*`; the installed baseline was Cygnus `v4.5.4 (1b4f)`. Load TCTE after the base mod. Russian Localization Fix RE supplied preferred terminology and is not a mandatory dependency.

## Policy levels

All 94 policies provide ten regular levels; 18 resource policies also provide ten monthly levels. Together with 94 Unmodified options, this makes 1214 options. Added 629 options; all 585 original options retain their values and conditions.

Each new level doubles the preceding level's modifiers within its own track. For example, energy production levels 6–10 provide +20000%, +40000%, +80000%, +160000%, and +320000%; monthly energy at level ten adds +2560000. These are modifier values, not a promise of the same change to the final statistic after other effects and engine limits.

Regular and monthly tracks remain options of one policy: only one option is selected at a time. Their restrictions are preserved separately as in Tass. New negative modifiers are also doubled under the approved specification; extreme values need in-game verification.

TCTE overrides 94 base-mod files under `common/policies/`. Inventory: [Tass Cheat Tool changes](BASE_MOD_CHANGES_EN.md). Rules and acceptance criteria: [level specification](TZ_LEVELS_EN.md).

## Resource grants

Path: planetary decision → main cheat menu → Add resources. Select one of six categories, then a resource and an amount. All 26 resources from the original menu are included. Each grant reopens the same resource's amount menu; Back returns one level.

| Resources | Six one-time grant amounts |
| --- | --- |
| Standard scale | 1000, 5000, 10000, 50000, 100000, 1000000 |
| Influence | 50, 100, 200, 300, 500, 1000 |
| Minor Artifacts | 100, 250, 500, 1000, 1500, 2000 |
| Astral Threads | 25, 50, 100, 200, 300, 500 |

Tass conditions for DLC, empire type, and special paths are preserved. Amounts specify one grant call; storage capacity is not increased. Full categories and acceptance criteria: [resource menu specification](TZ_RESOURCES_EN.md).

## Advanced species modification

The main-menu cheat adds +100 trait points and +30 trait picks to each of `BIOLOGICAL`, `ROBOT`, and `MACHINE`. While `modifier_tass_extra_species_modding` is active, the entry becomes Remove Advanced Species Modification. Both actions return to the main menu. Removal withdraws the cheat bonuses while retaining species traits, technologies, and traditions.

For the player country, `can_remove_beneficial_genetic_traits` additionally succeeds when both Targeted Gene Expressions (`tech_gene_expressions`) and the modifier are present. Disabling the cheat withdraws this additional permission. Original tradition conditions and other restrictions of individual traits remain applicable. The technology is not granted automatically; the +100/+30 bonuses are available without it. [Specification and acceptance criteria](TZ_SPECIES_EN.md).

## Extra envoys

Path: planetary decision → main cheat menu → Extra Envoys. Grants are +5, +10, +25, +50, +100, and +500. They stack: +5 → +10 → +25 adds +40, and two +500 grants add +1000. After each grant the envoy menu reopens; Back returns to the main menu.

Grants use levels of a new repeatable technology, adding +5 capacity per level. It has zero normal research draw weight, is not a starting technology, and is granted without notifications. No separate country modifier is added. An existing +20 bonus in a save remains and does not block the new grants.

The game creates assignable envoys after capacity changes. Updates while paused, after a tick, and after loading a save require in-game testing. [Specification and acceptance criteria](TZ_ENVOYS_EN.md).

## Localization contents

| File under `localisation/replace/` | Entries |
| --- | ---: |
| `tcte_tass_l_russian.yml` | 53 |
| `tcte_tass_event_l_russian.yml` | 154 |
| `tcte_tass_names_l_russian.yml` | 19 |
| `tcte_tass_policy_l_russian.yml` | 1386 |
| `tcte_tass_replace_l_russian.yml` | 54 |
| `tcte_fixes_l_russian.yml` | 1 |
| `tcte_policy_levels_l_russian.yml` | 1258 |
| `tcte_resource_menu_l_russian.yml` | 224 |
| `tcte_species_modding_l_russian.yml` | 3 |
| `tcte_envoy_menu_l_russian.yml` | 18 |
| **Russian total** | **3170** |

New options receive 1258 English names and descriptions in `localisation/english/tcte_policy_levels_l_english.yml`; the resource menu adds 224 keys in `localisation/english/tcte_resource_menu_l_english.yml`. Version 0.0.6 adds three keys per language in `tcte_species_modding_l_russian.yml` and `tcte_species_modding_l_english.yml`. All ten localization files from 0.0.5 remain byte-identical; the enable option uses the updated +100/+30 tooltip instead of the old +50/+5 text. Version 0.0.8 adds 18 keys in each of `tcte_envoy_menu_l_russian.yml` and `tcte_envoy_menu_l_english.yml`; the previous twelve files remain byte-identical. The distribution contains ten Russian and four English files, with 3170 RU and 1503 EN keys.

All 729 original values containing alphabetic text are translated; the Tass brand is retained. **704 descriptions** were authored: 13 categories, 94 policies, 585 options, 4 decisions, 7 edicts, and 1 colony deposit. Only `NAME_leader_tass` and the commented-out test edict's `edict_tass_edict_cheat_test_desc` intentionally remain empty.

Original keys, order, entry shells, control tokens, and numbers in nonempty originals are preserved. Files use UTF-8 BOM; the names file retains CRLF and the others use LF. New descriptions reuse existing localization references for names and terms. Their numbers are supported by code literals; no new variable getters were needed.

Version 0.0.1 includes two reference fixes: `mod_fleet_command_limit_add` references `$MOD_COMMAND_LIMIT_ADD$`; the new `TASS_CHEAT_WORMHOLE` entry references `$BYPASS_TASS_CHEAT_WORMHOLE$`.

Version 0.0.2 fixes five precursor buttons that exposed Russian Localization Fix RE's grammatical metadata. They use the existing screen titles for the Vultaum Star Assembly, Yuht Empire, First League, Irassian Concordat, and Cybrex. References remain the mechanism for terminology reuse; translations are not copied into TCTE. See the exact replacements in [specification section 7](TZ_EN.md#7-localization-fixes).

In 0.0.3, the four authored planetary decision descriptions are shortened to one sentence of at most 12 words after reference expansion. Detailed tooltips are preserved. The Effects block in the decision list uses tooltips, so shortening `_desc` does not change that text.

54 shared modifier labels also apply outside Tass menus. Their list, including 32 explicit vanilla overlaps, is recorded in [VANILLA_CHANGES_EN.md](VANILLA_CHANGES_EN.md).

## Installation

The local runtime is installed at `C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/mod/TCTE/`. Its external descriptor is `C:/Users/RUSBAR/Documents/Paradox Interactive/Stellaris/mod/TCTE.mod`.

For testing, the user adds **Tass Cheat Tool Extender** to the desired playset after **Tass Cheat Tool** and selects Russian as the game language. The agent did not modify playsets.

[TCTE_0.0.8.zip](../../TMP/TCTE/TCTE_0.0.8.zip) contains 116 runtime files: the descriptor, 94 policy files, four event files, one static-modifier file, one trigger file, one technology file, and fourteen localization files. For manual transfer, extract it into a user mod directory and create an external `TCTE.mod` containing the manifest metadata and a `path` pointing to that directory. Documentation, the glossary, and temporary reports are excluded.

When updating manually from 0.0.6, remove the previous `common/scripted_triggers/05_scripted_triggers_traits.txt` from the user mod directory. Version 0.0.7 instead provides `common/scripted_triggers/tcte_species_traits_triggers.txt` with only the modified trigger.

## Validation

Synthetic checks passed: exact key coverage and uniqueness; encoding, line endings, and syntax; preservation of original tokens, escaping, and numbers; 704 authored descriptions and two retained empty values; references without missing targets or cycles in both vanilla Russian and the preferred localization base; constant and terminology evidence; manifest and distribution contents.

The original 134 Tass Cheat Tool files were verified by SHA-256. Each new description has code ranges, effects, conditions, and reference sources recorded. Direct and nested localization for new descriptions needs no additional runtime scope. Original dynamic expressions remain unchanged.

Validation introduced in 0.0.2 recursively detects grammatical metadata exposed through static references. It reproduces five defective buttons in the 0.0.1 distribution and finds none in the current version. In 0.0.3, each decision description is also checked for length and a single sentence against both Russian baselines; the other 1663 values match 0.0.2.

Version 0.0.4 additionally validates all 94 overrides, 112 tracks, ordering of 1214 options, inherited conditions, and 1200 numeric components of new levels. Existing options were compared structurally and as original blocks; the six previous localization files match the 0.0.3 archive byte for byte. New RU/EN references were checked against English, vanilla Russian, and preferred Russian baselines; DLC titles retain their source localization spelling.

Version 0.0.5 checks 33 events, every transition, 156 grants, six amounts per resource, nine availability conditions, and 224 new keys per language. Recursive references were checked against both Russian baselines and English. All 102 previous runtime files other than the manifest match 0.0.4; only the version changed in the manifest. Preserved policies and previous translations are verified by fingerprints without changing their implementation.

Version 0.0.6 checks six bonuses, four button visibility states, eight enable/remove transitions, and 256 combinations of trait removal conditions. Comparison with the sources confirms preservation of the other 49 vanilla triggers, remaining main-menu options, and other Tass modifiers. All 106 previous runtime files except the manifest match 0.0.5. New references expand against English and both Russian baselines without grammatical metadata.

Version 0.0.7 replaces the full vanilla-file copy with a standalone override of one trigger; the other 49 definitions are omitted from TCTE. Confirmed byte-identical trigger content, preservation of 110 other runtime files, all 256 condition combinations, and absence of the old file from the archive. Filename order and a static loading model were checked; actual engine override behavior requires in-game verification. [0.0.7 report](../../TMP/TCTE/trigger_override_validation.json).

Version 0.0.8 checks six envoy grants, 176 sequences in an arithmetic model, reopening and Back, a technology without ownership restrictions or automatic grants, 18 new strings per language, and references against three baselines. Other main-menu blocks and 110 previous runtime files remain byte-identical. [Envoy validation](../../TMP/TCTE/envoy_menu_validation.json). The arithmetic model does not replace engine testing of technology stacking.

Reports: [species modification](../../TMP/TCTE/species_modding_validation.json), [resource menu](../../TMP/TCTE/resource_menu_validation.json), [original localization](../../TMP/TCTE/validation_report.json), [levels and new localization](../../TMP/TCTE/level_validation_report.json), [precursor regression](../../TMP/TCTE/precursor_regression.json), [decision description changes](../../TMP/TCTE/decision_regression.json), [description evidence](../../TMP/TCTE/description_sources.json), [level evidence](../../TMP/TCTE/level_sources.json), [installation](../../TMP/TCTE/installation_report.json), [documentation](../../TMP/TCTE/documentation_validation.json). **Changes in versions 0.0.2–0.0.8 have not yet been confirmed in-game.** Restart the game after updating and perform the checks below.

## In-game testing

1. Check the startup message and precursor selection, the capital decision opening the main menu, navigation, and return buttons.
2. Review 13 categories and 94 policies: ten regular and, where present, ten monthly levels, descriptions, availability conditions, and tooltips. Check the first new and tenth levels, switching tracks, and returning to Unmodified without accumulating previous modifiers.
3. Check decisions, situation acceleration edicts, and a monthly tick; required buildings, traditions, and pauses should match the descriptions.
4. Check ships and leaders, the Shroud, attunement, and ascension paths; where content is available, check nomads, arkships, and waystations.
5. Check Outside Paradise, the portal name, and shared modifier labels, including fleet command limit.
6. Check colors, icons, names, line breaks, and readability at the chosen UI scale. Scenarios unavailable because of DLC or game state remain untested.

7. Open the resource menu and check categories, all six standard amounts and the smaller scales, repeated grants without leaving, every Back button, availability conditions, and behavior at full storage.

8. Check +100/+30 for all three archetypes, button changes on enabling and removing the modifier, an already-active modifier, and re-enabling. Using Quick Learners without a permitting tradition, test all four technology/cheat combinations; with the tradition, permission must remain without the cheat. Check existing species templates after disabling the bonuses.

9. In the envoy menu, test all six grants, +500 twice, +5/+10/+25, Back, and reopening without extra grants. Test assignment, pause/tick updates, save/load, envoy death and replacement, regular and gestalt empires, and the old +20 bonus. Check there are no notifications, normal research offers for the service technology, or changes to current research. [Full checklist](TZ_ENVOYS_EN.md#6-validation-and-acceptance).

Complete checklists are in the [localization specification](TZ_EN.md#11-in-game-testing), [level specification](TZ_LEVELS_EN.md#6-validation-and-acceptance), [resource specification](TZ_RESOURCES_EN.md#7-validation-and-acceptance), and [species modification specification](TZ_SPECIES_EN.md#5-validation-and-acceptance). GUI changes are outside this stage.

## Source mod details

- The crime policy title mentions both crime and deviancy, but its code defines only `planet_crime_mult`, without a separate `planet_crime_no_happiness_mult`. The added description follows that code; behavior was not changed.
- The original infrastructure tooltip associates five build queue slots with an arkship. The deposit's `planet_building_capacity_add = 5` is unconditional; only base ship speed is gated by a nomadic owner. The added deposit description follows the code, while the existing nonempty tooltip retains its source meaning as required by the specification.
- Some extreme levels set modifiers below −100%. Descriptions state modifier values without promising negative costs, immunity, or bypasses of engine limits.

Correcting existing effects or source tooltips requires a separate user decision. Level extension is implemented under its separately approved specification.

## Working materials

[Localization specification](TZ_EN.md), [level specification](TZ_LEVELS_EN.md), [resource specification](TZ_RESOURCES_EN.md), [species modification specification](TZ_SPECIES_EN.md), [envoy specification](TZ_ENVOYS_EN.md), [changelog](CHANGELOG_EN.md), [shared game keys](VANILLA_CHANGES_EN.md), [base-mod changes](BASE_MOD_CHANGES_EN.md), [glossary](../../Glossary/tcte_terms.json).

The initial glossary added 55 terms. Version 0.0.5 adds Biomass and 12 sources. Version 0.0.6 adds the technology and three archetypes with eight sources, bringing the shared glossary to 66 unique terms at that stage. Version 0.0.8 adds Envoy and Envoy Capacity with eight sources, for 68 unique terms. One term may have multiple sources; one source line may support multiple different terms.

Temporary research, build, and validation scripts and the archive reside under `TMP/TCTE/`. They are not runtime mod content. [Русский](README_RU.md).
