# RUS_FIX_FIX for Stellaris 4.6 — draft specification

## Contents

- [Purpose](#purpose)
- [Baseline](#baseline)
- [Approved first step](#approved-first-step)
- [Changes](#changes)
- [Translation editing](#translation-editing)
- [Acceptance](#acceptance)

## Purpose

Provide a temporary local update of Russian Localization Fix RE until its author releases an update. The working project is `RUS_FIX_FIX`. The first step was approved separately. The remaining changes are proposed for discussion. Preserve the author’s Russian terminology, inflection and interface adjustments. Use one copy of the localization mod. With UI Overhaul Dynamic, load the localization mod first. The upstream Workshop item retains its ID.

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

1. Reconcile all nineteen window files with the 4.6 layouts, preserving the author’s Russian adjustments. Seven files lack named elements found in the current game. Examples include megastructure modules, planetary ideology information and ideology entries in the outliner. Preserve the author’s deliberate ship-prefix field behavior. Check both font definition files, atlases, Cyrillic glyphs and scaling under both interfaces.
2. Align auxiliary jobs with 4.6 conditions. Remove the obsolete bureaucrat branch at `fake_jobs_rinfix:421` and verify terminology for the separate `culture_worker` job. At `scripted_loc_rinfix:729`, use the existing `evosymbiont_plural_rinfix_cases` key and check the inflected output.
3. Restore the complete current definitions for `knights`, `resistance`, `certeran_covenant` and `plantoid_humans`, carrying over their specific title or adjective. When overriding a vanilla file, preserve its sibling presets and order. Test the author’s `florin` and the `default` template separately. Vanilla specifies the species, origin, ship and other fields. The upstream entry sets the ship prefix. Validate the result in empire creation.
4. Fill localization gaps and reconcile outdated tooltips with the English mechanics. English distinguishes regen rating, fixed daily regen and regen speed, while existing Russian repair-speed strings refer specifically to docked ships. Update related labels together so the out-of-combat bonus reads correctly. For 31 hidden strings, EN and RU point to the same existing key that resolves to Russian. Verify these aliases in context.
5. Preserve the local display name, set `supported_version="v4.6.*"`, and increment the patch component. Launcher installation and publication are separate operations.

## Translation editing

For each key, check the English source, caller and vanilla Russian proposal. Consult the author’s `replace` tier, regular translations and the prepared vanilla baseline, in that order, then verify substitutions against 4.6. Use adjacent entries to establish register. Commands use the infinitive. Mechanic labels use a short noun phrase. Use the author’s Russian terms for hull, armor, shields and space fauna. Preserve meaningful numbers, concept links, colors, icons, nonbreaking spaces and required case forms. Provide title and sentence variants wherever the caller distinguishes them.

The [translation draft](../../TMP/RUS_FIX_FIX/translation_draft_46.json) contains 18 proposals: all 15 English keys missing in Russian, plus three examples from overridden files. It identifies English sources, vanilla Russian where available and the author’s reference entries. For example, restore `$TECH$` in `ADD_RESEARCH_OPTION_TITLE` so the user sees the technology name. Reuse `$galactic_community_delegate$` for “Delegate” and `$getenvoy_normal$` for lowercase “envoy”.

## Acceptance

- Check coverage in the effective game and local mod files, resolved keys and references and conflicting duplicates. Use the repository parser to check substitutions against English, grammar, concept links, dynamic values, BOM and entry syntax. Document intentional exceptions to the hidden-key list.
- Check both name generators, auxiliary jobs and scripted localization. Compare new terms with the glossary and record verified terms with their sources.
- The user tests the Russian game with the local mod, then with the local mod above UIOD. Inspect the planet window, outliner, federation, Galactic Community and megastructure modules. Check the four empire presets with their applicable DLC, empire creation, generated names and factions, job case forms, repair concepts and research tooltips. Compare a fresh log with the baseline run. The static audit covers file behavior rather than a playthrough.
