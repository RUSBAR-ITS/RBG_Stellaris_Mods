# RUS_FIX_FIX for Stellaris 4.6 — draft specification

## Contents

- [Purpose](#purpose)
- [Baseline](#baseline)
- [Approved first step](#approved-first-step)
- [Changes](#changes)
- [Economic modifier batch](#economic-modifier-batch)
- [Astral rift batch](#astral-rift-batch)
- [Ethics and population ideology](#ethics-and-population-ideology)
- [Leader details, assignments and recruitment](#leader-details-assignments-and-recruitment)
- [Remaining new Stellaris 4.6 entries](#remaining-new-stellaris-46-entries)
- [Retired numbering formats in name lists](#retired-numbering-formats-in-name-lists)
- [Inflections and remaining earlier entries](#inflections-and-remaining-earlier-entries)
- [Translation editing](#translation-editing)
- [Acceptance](#acceptance)

## Purpose

Provide a temporary local update of Russian Localization Fix RE until its author releases an update. The working project is `RUS_FIX_FIX`. The approved stages cover references to existing translations, economic modifiers, two astral rift storylines, ethics and population ideology tooltips, and leader details, assignments and recruitment. Version `4.5.12` addresses the remaining newly masked 4.6 entries and English keys missing a Russian translation. The remaining changes are proposed for discussion. Preserve the author’s Russian terminology, inflection and interface adjustments. Use one copy of the localization mod. With UI Overhaul Dynamic, load the localization mod first. The upstream Workshop item retains its ID.

## Baseline

Compared the installed Stellaris `v4.6.0` English and Russian files, the Russian snapshot in `Localisation_Base/2-Prio_Vanilla/`, both upstream localization tiers and Workshop item `681483874` version 4.5.4. Of 285 local files, 284 are byte-identical to Workshop. The user already changed the local display name and removed the Workshop ID. See the [vanilla inventory](VANILLA_CHANGES_EN.md).

| Group | Key-level findings | Treatment |
| --- | --- | --- |
| Russian game entries hidden by mod files | 2,312 keys in 105 files. Of these, 646 are new relative to the Russian snapshot. 1,666 were already absent from the mod against that snapshot. | Restore entries used by the game. Investigate older omissions against callers, replacements and grammar. |
| English source for these 2,312 entries | 1,514 have an English entry with the same key. The remaining 798 come from the Russian-specific `scripted_loc_l_russian.yml`. | Check the Russian caller, case forms and surrounding author entries for these 798. |
| Changed entries with existing translations | 933 keys changed in vanilla Russian and differ in the mod. Among them, 342 changed substitution tokens between the Russian snapshot and 4.6. | Start with the 342. Verify current English meaning. Also check for English semantic changes that went untranslated in vanilla Russian. This comparison has no historical English snapshot. |
| English keys missing in both Russian sources | 15 | Draft translations cover all 15. |
| New keys inherited from the game | 4,326 from the main Willpower file and 49 from ideology name parts | Keep suitable vanilla strings. Override individual entries where an editorial change is warranted. |
| Other candidates | 42 upstream keys disappeared from vanilla Russian. 68 multiword strings match English, including music, DLC titles and internal TODOs. | Trace uses before removal. Preserve proper names and check placeholders against the source. |

[Summary](../../TMP/RUS_FIX_FIX/summary.json) · [Hidden keys and source texts](../../TMP/RUS_FIX_FIX/missing.json) · [Changed translations](../../TMP/RUS_FIX_FIX/changed_author_review.json) · [Changed substitutions](../../TMP/RUS_FIX_FIX/placeholders_review.json).

## Approved first step

Restore two vanilla references in `localisation/russian/utopia_ascension_l_russian.yml`, next to the existing opinion modifier names.

| Key | Value in Stellaris 4.6.0 EN and RU | Resolved mod text |
| --- | --- | --- |
| `triggered_opinion_cyborgs_absolute` | `$opinion_cyborgs_fanatic$` | Злобные киборги |
| `triggered_opinion_synthetics_absolute` | `$opinion_synthetics_fanatic$` | Бездушные машины |

Both references are absent from the upstream mod. The author already defines both targets. For acceptance, compare the file before and after: only the two entries are added, preserving encoding and line endings. The parser must find each key exactly once and resolve both references. After loading the local copy in Russian, the two corresponding `Missing localization key` messages should disappear from a fresh `error.log`. Reaching the main menu is sufficient for this startup check.

## Changes

After the first step, 26 more references from the initial 31 candidates were restored. Version `4.5.6` contains all 28 references whose keys were added relative to the Russian snapshot. The three earlier entries for faction names, district limits and official energy income were reviewed and restored in version `4.5.7`. [Full batch and three-entry check](../../TMP/RUS_FIX_FIX/aliases_4.5.7.json). [Keys and verification results](../../TMP/RUS_FIX_FIX/aliases_4.5.6.json).

1. The target load order for the local build is `RUS_FIX_FIX → UI Overhaul Dynamic`. The installed UIOD for Stellaris 4.6 provides all 19 upstream `.gui` windows at the same paths, so porting those layouts is outside the required work. UIOD supplies the ship prefix field in empire creation, while the Russian localisation controls the displayed ship name format. UIOD ships its font definitions under a different path from both `interface/fonts.gfx` and `interface/load_screen_font.gfx`. Its font table declares some of the same names, including `load_screen`. Check Cyrillic rendering during the normal in-game test with this load order.
2. Align auxiliary jobs with 4.6 conditions. Remove the obsolete bureaucrat branch at `fake_jobs_rinfix:421` and verify terminology for the separate `culture_worker` job. At `scripted_loc_rinfix:729`, use the existing `evosymbiont_plural_rinfix_cases` key and check the inflected output.
3. Restore the complete current definitions for `knights`, `resistance`, `certeran_covenant` and `plantoid_humans`, carrying over their specific title or adjective. When overriding a vanilla file, preserve its sibling presets and order. Test the author’s `florin` and the `default` template separately. Vanilla specifies the species, origin, ship and other fields. The upstream entry sets the ship prefix. Validate the result in empire creation.
4. Fill localization gaps and reconcile outdated tooltips with the English mechanics. English distinguishes regen rating, fixed daily regen and regen speed, while existing Russian repair-speed strings refer specifically to docked ships. Update related labels together so the out-of-combat bonus reads correctly. For 31 hidden strings, EN and RU point to the same existing key that resolves to Russian. Verify these aliases in context.
5. Preserve the local display name, set `supported_version="v4.6.*"`, and increment the patch component. Launcher installation and publication are separate operations.

## Economic modifier batch

Version `4.5.8` implements the approved batch covering every newly masked entry in `economic_modifiers_l_russian.yml`. The `planet_purge_jobs` job category and the `ship_cultural_envoy` ship class each need 102 labels. Each group comprises four modifier forms for 25 resources and two aggregate modifiers. The shared `job_purge_plural_with_icon` entry in `megacorp_l_russian.yml` supplies the author's existing job name and its icon.

Use the author's production and upkeep templates. For jobs, preserve the localized Purge name, its icon and the population group size substitution where it affects the calculation. For ships, introduce the dynamic `$cultural_envoy_ship_plural$` name with the Russian equivalent of “ships of type …”. For flat ship upkeep, check each vanilla `*_upkeep_from` reference and use the corresponding Russian localization's defined `*_upkeep_for` reference when the original is missing.

Acceptance covers all 205 keys. Compare coverage and meaning with both vanilla languages, resolve references against the effective Russian localization, and verify all four ship names, icons, and the distinction between flat and percentage modifiers. Verify that existing upstream entries are preserved. Once the local mod is connected, the user can check job output and cultural envoy upkeep labels in game.

The [205 verified entries](../../TMP/RUS_FIX_FIX/economic_modifiers_46.json) include the English original, vanilla Russian text, translation used in the local build and resolved references. All 25 flat ship upkeep labels reference keys missing from the effective Russian localization. For each resource the parser found the author's corresponding upkeep label. Four ship names were traced to `GetCulturalEnvoyNamePlural`.

## Astral rift batch

Version `4.5.9` implements the approved batch for the two storylines involving the Baol and the Zroni in `astral_rifts_3_l_russian.yml`. Of 73 missing entries, 72 can be traced to a call in `events/astral_rifts_3_events.txt`, directly or through a nested description. Restore these entries for the ordinary outcomes and the Lost Makers origin. Also review 15 existing upstream entries against the changed vanilla text. Revise an existing entry only where its meaning or the way the text is assembled has changed.

Reuse the author's wording where vanilla splits an older paragraph. Preserve inflected names of systems and characters, dialogue formatting and technology references. Check new dialogue against the English original. For example, the choice in `astral_rift.3005.a.lost_makers` refers to the machines' original purpose. Record `astral_rift.3230.desc.lost_makers_link` as an exception. The inspected storyline contains no reference to it and vanilla inserts the same ending twice. Revisit it if a caller is found.

For acceptance, expand the ordinary and origin-specific descriptions of both storylines, including all 19 technology outcomes in event 3070. Check substitutions, paragraph breaks, quotation marks and color codes in the assembled text. Verify fragment order, unique endings and preservation of upstream entries outside the agreed edits. [Review of 73 missing and 15 existing entries](../../TMP/RUS_FIX_FIX/astral_rifts_46_review.json).

All 72 approved entries were added. Of the 15 existing entries reviewed, 13 were updated. The wording of `astral_rift.3010.desc.common.1` was retained. The author's leader gender and system name inflections were kept in `astral_rift.3099.desc`. Static checks covered 85 assembled texts. In-game checks can use the Grunur encounter in 3055 and the Far-Seer’s message in 3280 or 3285. [Results and assembled texts](../../TMP/RUS_FIX_FIX/astral_rifts_4.5.9.json).

## Ethics and population ideology

Version `4.5.10` implements the approved batch of 67 keys introduced since the previous Russian snapshot. These comprise 38 ethic requirements in `main_2_l_russian.yml`, 11 ethic attraction labels and two headings in `modifiers_1_l_russian.yml` and `main_1_l_russian.yml`, and 16 population ideology comparisons in `triggers_effects_l_russian.yml`. Use effective Russian localization keys for ethic names and the author's established wording for positive and negative requirements where it accurately describes the condition.

The `civic_tooltip_fan_*` labels and their negative counterparts must account for both values accepted by the vanilla checks, fanatic and absolute. The `tooltip_abs_*` and `tooltip_not_abs_*` labels refer only to the absolute ethic. The Fanatic Purifiers' `civic_tooltip_militarist_or_spiritualist` label describes one part of the civic's requirements. List all three values from `common/governments/civics/00_civics.txt`. Distinguish flat from percentage attraction. For population checks cover number and percentage, four ideology filters, and positive and negated comparisons.

Acceptance covers the English and Russian originals and resolution against the effective localization. Check reference cycles, colors, line breaks, numeric signs and formats, the selected ideology name, and the scope of negation. In game, the user can inspect a civic requirement, an attraction tooltip and a population condition naming an ideology.

The [67 restored entries](../../TMP/RUS_FIX_FIX/ethics_ideology_46.json) show the English source, vanilla Russian text and a preview with sample values. All eight vanilla `is_fanatic_*` checks accept the fanatic or absolute ethic. One of the Fanatic Purifiers' requirements accepts militarism, spiritualism or absolute xenophobia. The eight positive `tooltip_abs_*` labels are included because both vanilla languages define them. Individual UI callers for these labels have yet to be confirmed.

The parser found exactly one definition for each key across the effective localization. Reference and substitution checks used sample values, including positive and negated comparisons of population counts and percentages. After this batch, 274 newly masked keys remain relative to the previous Russian snapshot.

## Leader details, assignments and recruitment

Version `4.5.11` restores 53 missing entries in six Russian localization files. Seventeen in `main_2` cover assignments, positions, background, level and experience, including the ruler's ability to govern the capital. Another 25 in `modifiers_1` cover recruitment, age, lifespan, governor effects and science ship command. Eight in `paragon_2` concern the council, heirs and traits. One entry each belongs to `leaders`, `ancient_relics` and `triggers_effects`.

Update the three existing entries used to select the displayed text: `leader_trait_gifted`, `leader_trait_gifted_desc` and `delegate_subclass_tt`. Move the author's Gifted name and description to the regular branch. Use vanilla's `triggered_gifted_name` and `triggered_gifted_desc` to select the existing machine and hive translations. Restore the Willpower check in the delegate subtitle through `GetDelegateSubclassSubtitle`. Use the author's inflected Community or Imperium name in the base branch and the vanilla subtitle mentioning ideology spread when the expansion is present.

For acceptance, check all keys against both installed languages. Verify assignment targets, icons, the Alt key, current and next experience values, concept references and effect variables. Check the official governor's three job output bonuses and empire size from pops against the script. Verify Gifted for a regular empire, a hive and a machine intelligence, and the delegate subtitle for both DLC branches. In game, inspect Alt-expanded details, the assignment target and the trait displayed for the owner's empire type.

Checked the English and Russian source text for all 56 keys in the installed Stellaris 4.6.0 files. Each has exactly one active definition. Static checks covered three trait names and descriptions and both Delegate subtitles. In the official governor tooltip, the script values yield +2% job output for each of the three resource groups and −2% empire size from pops per skill level. Of the newly masked entries in the initial audit, 221 remain. [Checks and sample substitutions](../../TMP/RUS_FIX_FIX/leaders_46.json).

## Remaining new Stellaris 4.6 entries

The approved batch was implemented in `4.5.12` on top of `4.5.11`. Its scope was to cover all 221 newly masked Russian entries in the initial audit and 15 English keys without Russian text in a single stage. Restore 220 entries and translate the 15 English-only keys. Retain the documented exception for `astral_rift.3230.desc.lost_makers_link`. The batch adds 235 entries across 33 files. Nine Russian grammatical forms have no English counterpart. Check these against Russian scripted localization and the author's inflection tables.

The batch covers scenario and interface labels, names and grammar, effects and conditions, traditions, precursor stories, leader memorials and colony revolts. Review the 36 existing entries where vanilla references a new key or its selector. Update them where the current translation loses a branch, a substitution or a change in game mechanics. Preserve working upstream inflections and wording. For split event descriptions, review complete passages for each branch. Check figures and conditions in ship repair terminology against the English original and game definitions. Preserve name generator parameters and the author's ship prefix behavior.

Verify the exact additions, unique effective definitions, encoding, references, formatting, variables, inflections and alternate selector results. Reconcile the baseline audit and report the 1,663 older omissions separately. In game, check scenario selection, a faction name, repair tooltips, tradition branches and an event from each story group. [Keys, sources and 36 existing entries to review](../../TMP/RUS_FIX_FIX/remaining_46_review.json).

The post-write check confirmed 235 additions and 34 changes across 34 files. Each of the 269 keys has one effective definition. All bytes outside the edited entries match the previous build in those files. Checked links to 24 concepts and game objects and the branches of 18 scripted localization functions. Of the 36 existing entries reviewed, two already used the author's correct inflections for the Galactic Community and Imperium. The official ideology law cooldown now uses an existing upstream cooldown label. [Verification and sample outputs](../../TMP/RUS_FIX_FIX/remaining_46_result.json).

One documented rift exception remains among the new omissions. All 15 English-only entries now have Russian text. The 1,663 earlier omissions consist of 869 entries in 61 name lists, 789 in `scripted_loc_l_russian.yml`, and five in four other files. Older selector branches include five masked feminine leader class names, a missing vanilla `noclass_masc_RULOC` default and an unresolved `$orbital_ring_feeder$` reference in the existing sabotage label. These are recorded for the earlier localization review. In-game acceptance includes comparing job strata in a regular and a Warmongers empire, opening repair concepts and comparing a regular revolt outcome to submission to nomads.

## Retired numbering formats in name lists

The review covered all 869 earlier omissions in 61 name lists. The English and Russian localisation files in Stellaris 4.6.0 place these keys in their backwards-compatibility sections. The game and mod scripts and localisation references examined contain no calls to them. This port covers names produced by the current generators. Restoring retired templates for old saves is outside its scope.

Each of the 869 entries has a modern key. Its effective Russian text matches the author's translation, with `replace` taking priority. Generators call 868 of the modern keys directly. The exception is `HUMAN2_JANISSARYCORPS`. The HUMAN2 slave army uses `HUMAN2_PRIMITIVECORPS`, which also has an author translation. In 25 of the 869 modern templates the author uses wording that differs from Russian vanilla, including «отряд ополчения» for `HUMAN2_COLONIALGENDARMERIE`. All author variants are preserved. [Sources and generator calls](../../TMP/RUS_FIX_FIX/name_lists_46.json).

The earlier snapshot has 794 entries left to review, including 789 inflection and helper entries and five entries across four other files. For an in-game spot check, generate a defensive army using the HUMAN2 name list and check its number and the Russian name «отряд ополчения».

## Inflections and remaining earlier entries

The approved batch shipped in the local `4.5.13` build. All 794 remaining keys from the earlier snapshot were reviewed. The batch added 31 entries and corrected one existing label. Prefer the author's `replace` strings, followed by the author's regular files. Reference existing translations by key. Check the English text and 4.6.0 definitions when object names or conditions differ.

| Area | Requirement |
| --- | --- |
| Celestial body names, 5 keys | Forward gender, nominative and all five oblique cases from the author’s entries for planets, moons, arks, habitats and ring worlds. There are 34 effective Russian strings calling `GetPlanetMoon_RULOC`. Verify gender and each case substitution. |
| Population growth, 1 key | Restore the genitive «ежемесячного роста поселений органиков». Check all five consumers, including clone vats and budding. |
| Agreements, 20 keys | For agreement variants defined in the current game, reference the author's icon for the corresponding subject type. Check each preset ID and resolve its icon. Check icon visibility in the negotiation window in game. |
| Descriptions and labels, 5 keys | Use the author's relic description for the Celestial Tear. Link two Strange Worlds English keys to the author's descriptions. Link the station control restriction and the plural of presapient herds to the author's existing labels. |
| Sabotage, 1 existing entry | Use `$sm_ring_feeder$` and the author’s “name — sabotage” format for the Orbital Garden message. Check the selector condition, country flag and affected building key. |

The author’s `background_job_rinfix` handles a leader’s previous occupation. Check its branch for all 504 combinations of occupation and gender. The author provides a separate default. The author’s `paragon.553.desc` uses `GetTitle` and does not depend on the missing feminine outputs or misspelled default of vanilla `GetLeaderClass_RULOC`. The author’s ship name quotation marks are controlled by `PREFIX_NAME_FORMAT`. The current storm technology path already uses `gateway_tech_storm_prediction`.

All 794 keys have a recorded disposition. Each of the 32 changed entries has exactly one effective definition. Static checks verified 30 case forms, five growth tooltips, 20 icon references and the building name in the sabotage message. Of the 763 omissions left as they were, 50 had no literal caller in the data examined. Another 79 occur in selector branches without a caller in the effective Russian text. The signed-zero encryption variant also has a working unsigned-zero label. Their display depends on engine behaviour. This completes the review of the earlier localisation gap snapshot. [Results by key and substitution examples](../../TMP/RUS_FIX_FIX/older_forms_review.json).

## Translation editing

For each key, check the English source, caller and vanilla Russian proposal. Consult the author’s `replace` tier, regular translations and the prepared vanilla baseline, in that order, then verify substitutions against 4.6. Use adjacent entries to establish register. Commands use the infinitive. Mechanic labels use a short noun phrase. Use the author’s Russian terms for hull, armor, shields and space fauna. Preserve meaningful numbers, concept links, colors, icons, nonbreaking spaces and required case forms. Provide title and sentence variants wherever the caller distinguishes them.

The [translation draft](../../TMP/RUS_FIX_FIX/translation_draft_46.json) contains 18 proposals: all 15 English keys missing in Russian, plus three examples from overridden files. It identifies English sources, vanilla Russian where available and the author’s reference entries. For example, restore `$TECH$` in `ADD_RESEARCH_OPTION_TITLE` so the user sees the technology name. Reuse `$galactic_community_delegate$` for “Delegate” and `$getenvoy_normal$` for lowercase “envoy”.

## Acceptance

- Check coverage in the effective game and local mod files, resolved keys and references and conflicting duplicates. Use the repository parser to check substitutions against English, grammar, concept links, dynamic values, BOM and entry syntax. Document intentional exceptions to the hidden-key list.
- Check both name generators, auxiliary jobs and scripted localization. Compare new terms with the glossary and record verified terms with their sources.
- In game, check Russian text and Cyrillic rendering, including the loading screen, using the target order `RUS_FIX_FIX → UI Overhaul Dynamic`. Check the four empire presets with their applicable DLC, empire creation, displayed ship names, generated names and factions, job case forms, repair concepts and research tooltips. Compare a fresh log with the baseline run.
