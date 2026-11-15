# Tass Cheat Tool Extender — Russian localization specification

## Contents

- [1. Status and stage boundaries](#1-status-and-stage-boundaries)
- [2. Source baseline and scope](#2-source-baseline-and-scope)
- [3. Translation and new descriptions](#3-translation-and-new-descriptions)
- [4. Structure and installation](#4-structure-and-installation)
- [5. Preserve formatting](#5-preserve-formatting)
- [6. Terminology and glossary](#6-terminology-and-glossary)
- [7. Localization fixes](#7-localization-fixes)
- [8. Effects on shared game strings](#8-effects-on-shared-game-strings)
- [9. Deliverables](#9-deliverables)
- [10. Synthetic validation](#10-synthetic-validation)
- [11. In-game testing](#11-in-game-testing)
- [12. Sources and baseline fingerprints](#12-sources-and-baseline-fingerprints)

## 1. Status and stage boundaries

**Approved by the user on 2026-11-14 with the instruction to start implementation. Implemented in version 0.0.1; version 0.0.2 fixes precursor display, and 0.0.3 shortens planetary decision descriptions at the user's request. In-game verification of the changes is pending.**

Extending policies to ten levels is implemented in 0.0.4 under the separately approved [level specification](TZ_LEVELS_EN.md). This document retains the scope of the original localization stage; its 1667 Russian values are preserved.

Project: **Tass Cheat Tool Extender**. ID and directory: **`TCTE`**. The first stage provides complete Russian localization of the installed **Tass Cheat Tool** version, fills 704 empty descriptions based on active code, and applies the two specific localization reference fixes described in section 7. Approval covers the extended scope, including descriptions and substitutions.

Compatibility with Tass Cheat Tool is mandatory: the extender runs alongside the base mod and uses its identifiers and behavior. The user explicitly permits the project to override base-mod functions in later development. This does not introduce such changes into this stage: new cheats and changes to effects, restrictions, events, policies, GUI, or balance require a separate specification.

Compatibility patches for other mods and support for older Tass Cheat Tool versions are outside this stage. Russian Localization Fix RE supplies preferred terminology but does not become a mandatory TCTE dependency.

## 2. Source baseline and scope

- Base mod: `E:/SteamLibrary/steamapps/workshop/content/281990/682851228/`.
- Its manifest: `name="Tass Cheat Tool"`, `version="20261012"`, `supported_version="v4.5.*"`, Workshop ID `682851228`.
- Installed game: Stellaris **Cygnus v4.5.4 (1b4f)**, confirmed by `launcher-settings.json`.
- The base mod contains English and Simplified Chinese localization, with no Russian localization of its own.
- Code contains **94 policies in 13 categories**. The five English files contain **1,666 unique keys**, with no duplicates.

Source paths below are relative to the base-mod directory. All output files belong in `TCTE/localisation/replace/`.

| English source | Keys | Russian output file |
| --- | ---: | --- |
| `localisation/english/tass_l_english.yml` | 53 | `tcte_tass_l_russian.yml` |
| `localisation/english/tass_event_l_english.yml` | 154 | `tcte_tass_event_l_russian.yml` |
| `localisation/english/tass_names_l_english.yml` | 19 | `tcte_tass_names_l_russian.yml` |
| `localisation/english/tass_policy_l_english.yml` | 1,386 | `tcte_tass_policy_l_russian.yml` |
| `localisation/replace/tass_replace_l_english.yml` | 54 | `tcte_tass_replace_l_russian.yml` |
| Missing key referenced by code, section 7 | 1 | `tcte_fixes_l_russian.yml` |
| **TCTE total** | **1,667** | **6 localization files** |

These are entry counts, not counts of independent sentences to translate. Of the 1,666 source values, **729 contain alphabetic text outside control tokens**, **231 contain only references, codes, numbers, and punctuation**, and **706 are empty**. The first group includes repeated policy levels and the `tass_mod` brand marker, which is preserved.

Coverage follows the English keys. Chinese files contain no additional keys; `NAME_leader_tass`, absent from Chinese, exists in English with an empty value and must remain empty.

Of the 706 originally empty values, **fill 704 with new Russian descriptions**. Keep only `NAME_leader_tass` and `edict_tass_edict_cheat_test_desc` empty: the former is a name with no references found, and the latter belongs to a fully commented-out test edict. Key and file counts remain unchanged: **1,667 entries in 6 files**.

## 3. Translation and new descriptions

Translate all user-facing text within this set: the opening message and precursor selection; the main menu and its resources, leaders, technology, ascension, Shroud, ships, and special actions sections; policies and categories; decisions, edicts, civic, traits, modifiers, ship names, the paradise system, and its portal.

Translate text inside values. Existing `tass_*`, `policy_*`, `NAME_*`, `mod_*`, and other keys remain unchanged. Apply the `tcte_` prefix to new filenames and future identifiers owned by the extender. Do not rename `TASS_CHEAT_WORMHOLE`, which is already referenced by base-mod code.

Write substantive descriptions for the 704 empty description values from code, following the requirements below; preserve the two empty exceptions in section 2. Keep references to game names, ruler names, and the current colony dynamic. Copy originally nonempty values consisting only of numbers, icons, and references unchanged, except for the explicit exception in section 7. Do not require Cyrillic in every entry.

Preserve `Tass`, `Tass Cheat Tool`, `Tass Cheat Tool Extender`, and the `(§GTass§!)` marker. Translate other displayed names, including ship classes and designs, using game terminology and context. Do not reproduce English spelling errors in Russian.

Use consistent templates for repeated labels:

| Source concept or template | Proposed Russian translation |
| --- | --- |
| Cheat Main Menu | Главное меню читов |
| Unmodified | Без изменений |
| Enhance | Усиление |
| `$tass_enhance$ Lv1` | `$tass_enhance$ ур. 1` |
| `$tass_enhance$(Monthly) Lv1` | `$tass_enhance$(ежемесячно) ур. 1` |
| Monthly `£...£` | Ежемесячно `£...£` |
| Return / Exit | Назад / Выход |
| Outside Paradise | Уединённый рай |
| Paradise Portal | Портал в Уединённый рай |

Preserve color codes in originally nonempty values even when omitted from this template table for brevity. Do not change their level numbers, policy numbering, resource amounts, or other numeric values. New descriptions display and validate numeric values according to this section's rules.

Check label meaning against code. For example, `Scout` in `tass_policy_cheat_fleet_sensor` concerns sensor and hyperlane detection ranges, not spawning a scout ship. `Readme.txt` mentions a level 3 arkship, but the English tooltip and `tass_cheat_events_hide.txt` specify level 2; preserve **2** in the translation.

New descriptions are distributed as follows:

| Group | Descriptions | Evidence for the text |
| --- | ---: | --- |
| Policy categories | 13 | Policies actually assigned to each category |
| Policies | 94 | Purpose, available options, and their differences |
| Policy options | 585 | Modifiers, conditions, and effects of the specific option |
| Planetary decisions | 4 | Availability, target, and invoked effects/events |
| Active edicts with empty descriptions | 7 | Edict conditions and events implementing their effects |
| Colony Infrastructure deposit | 1 | Permanent and conditional deposit modifiers |
| **Total** | **704** | |

For every description, follow the actual execution chain: object definition, `potential`/`allow`, `modifier`, conditional modifiers, effects, associated events, and `on_actions`. For example, situation-acceleration edicts are implemented in `tass_cheat_events_hide.txt`, with their timing confirmed by `on_monthly_pulse_country` in `tass_on_actions.txt`; an empty edict `effect` does not mean the edict does nothing.

Describe purpose, target, relevant conditions, the type of change, and, where useful to the player, magnitude and timing. Distinguish percentage modifiers, flat additions, one-time grants, and monthly production; do not promise a fixed final amount if other modifiers affect it. Do not present conditional gestalt or nomad bonuses as unconditional. Describe a zero option as applying no enhancement from that policy, without promising to reverse earlier irreversible actions.

Use concise, specific wording. Do not replace the name with a generic “Improves the selected parameter” or duplicate one generic text across different effects. Shared templates are acceptable only for matching effect structures with verified parameters for each option. Descriptions should explain purpose and conditions without copying the entire effects tooltip already shown alongside them.

User clarification for planetary decisions: each authored `decision_*_desc` must be one short sentence of no more than 12 words, preferably fewer than 10. Count words after expanding localization references. Purpose and target are sufficient for these four descriptions; detailed conditions and effect magnitudes need not be copied from the tooltip. The `decision_*_tooltip` entries retain their details and are not shortened in this iteration. Check the limit against both Russian localization baselines. The Effects block in the supplied screenshot uses tooltips; shortening `_desc` does not change that text.

Reuse existing term localization through `$key$` references in new text. Display variable-backed values through supported substitutions in the correct scope instead of hardcoding their current values. Validate reference chains, variable existence, and context availability; do not invent value accessors. If exposing a variable requires code changes, obtain separate approval for those changes and do not substitute a constant. A number that is itself a code constant may be included with source evidence. If a suitable string already exists, reference it instead of copying its text; phrase the sentence so that the reference needs no manual inflection.

Examples of new descriptions supported by current code:

| Key | Proposed Russian description | Evidence |
| --- | --- | --- |
| `tass_policy_cheat_energy_1_desc` | `$energy$: +100% к производству.` | `common/policies/tass_cheat_policy_01_02_energy.txt`: option `_1`, `country_energy_produces_mult = 1` |
| `tass_policy_cheat_energy_6_desc` | `$energy$: +200 к базовому ежемесячному производству.` | The same file: option `_6`, `country_base_energy_produces_add = 200` |
| `decision_tass_cheat_open_menu_desc` | `Открывает меню «$tass_cheat.1.name$».` | `common/decisions/000_tass_cheat_decisions.txt`: `is_capital = yes`, event `tass_cheat.1` in owner scope |

These illustrate the description method, not a complete set of finished texts. Maintain evidence for all 704 entries in `TMP/TCTE/description_sources.json`: description key → source files, identifiers, lines, and confirmed effects/conditions. Also record sources and scopes for references and variables. Version 0.0.1 extends this mapping with finished texts, code ranges, constants, and reference sources; the new descriptions require no new dynamic expressions.

## 4. Structure and installation

After approval, create `TCTE/descriptor.mod` with these fields:

```text
name="Tass Cheat Tool Extender"
version="0.0.1"
supported_version="v4.5.*"
dependencies={
    "Tass Cheat Tool"
}
```

The `v` prefix in `supported_version` is mandatory. The first localization release is `0.0.1`; preparing this specification is not a mod release.

Use the six files listed in section 2. Do not copy `common`, `events`, `interface`, graphics, or English/Chinese localization from the base mod. Do not add `replace_path` or auxiliary effects to implement translation.

For game testing, install the distribution through `Documents/Paradox Interactive/Stellaris/mod/`: a `TCTE` directory and an external `TCTE.mod` file containing manifest metadata and the correct `path`. The game installation and Workshop directories remain read-only.

TCTE must load after Tass Cheat Tool. **The agent does not modify the playset:** the user adds and enables the mod. Installation does not occur during specification preparation.

## 5. Preserve formatting

Each localization file uses UTF-8 with BOM, an `l_russian:` header, and an `_l_russian.yml` filename suffix. Each entry occupies one physical line.

For the five translated files, preserve source key order, indentation, colons, quotation marks, the absence of a numeric index after the colon, and other entry structure. Use **CRLF** in `tcte_tass_names_l_russian.yml`, matching its English source; use **LF** in the other five output files. Comments remain English.

Preserve the exact number and sequence of `$...$`, `[...]`, `§` color codes, `£...£` icons, and escape sequences. Sources contain both `\n` and `\t`: do not convert them to physical newlines or tabs or double their escaping. Do not change `[Root.GetName]`, `[Root.GetRulerTitle]`, or other expressions.

Do not expand references manually for grammatical inflection: construct the Russian sentence around the retained substitution. Do not silently repair source control tokens. Section 7 lists the permitted reference replacements, including the five references fixed in 0.0.2; validate the additional missing entry separately.

For the 704 originally empty descriptions, filling the value may introduce references, supported variable substitutions, color codes, and escaped line breaks where needed. Preserve entry structure. Comparing their tokens and numbers against an empty source is inapplicable: instead validate syntax, target existence, scope availability, and agreement with code. This exception permits filling empty values, not changing tokens in existing text being translated.

## 6. Terminology and glossary

Lookup order: installed English game localization → the same key in `Localisation_Base/1-Prio_Russian_Localization_Fix_RE/replace/` → other Russian Localization Fix RE files → `Localisation_Base/2-Prio_Vanilla/`. Also consult the shared `Glossary/` for concepts already verified.

The following initial mappings were verified. None of these keys was found in `replace`; the selected Russian sources have priority 2. Matching English and Russian filenames allow the lookup to be reproduced.

| English term | Russian term | Key | Filename without language suffix |
| --- | --- | --- | --- |
| The Shroud | Покров | `THE_SHROUD_TITLE` | `shroud` |
| Attunement | Резонанс | `concept_attunement` | `civic_and_origin_concepts` |
| Arkship | Корабль-ковчег | `trait_pc_ark_preference_short` | `nomads_1` |
| Waystation | Маршрутная станция | `starbase_waystation_1` | `nomads_1` |
| Pops | Поселения | `concept_pops` | `concepts` |
| Decisions | Решения | `DECISIONS_TITLE` | `megacorp` |
| Edicts | Указы | `EDICTS` | `main_3` |
| Policies | Политика | `POLICIES` | `main_3` |
| Ascension Perks | Бонусы за стремление | `ASCENSION_PERKS` | `utopia` |
| Empire Size | Размер государства | `concept_empire_size` | `concepts` |
| Fleet Command Limit | Предел управления флотилии | `MOD_COMMAND_LIMIT_ADD` | `modifiers_1` |
| Naval Capacity | Вместимость флота | `NAVY_SIZE_TITLE` | `main_2` |
| Research Alternatives | Альтернативные исследования | `MOD_COUNTRY_NUM_TECH_ALTERNATIVES_ADD` | `modifiers_1` |
| Habitability | Пригодность | `HABITABILITY` | `main_1` |
| Gestalt Consciousness | Гештальт-сознание | `ethic_gestalt_consciousness` | `main_1` |

This is an initial set, not a limit on terminology research. Distinguish naval capacity from fleet command limit, and ascension perks from ascension paths and planetary ascension. Also verify resources, armies, diplomacy, espionage, nomad, and Shroud patron terminology.

During implementation, extend the shared JSON glossary. New terms may go in `Glossary/tcte_terms.json`; existing terms, such as Ascension Perks and Ascension Perk Slot, must extend their existing entries. Check uniqueness across the entire `Glossary` directory, not separately per mod.

One term has one entry containing `english`, `russian`, and a `sources` array. Each reference records the key, English and Russian files, line numbers, and Russian source priority using the established schema. Different keys and grammatical forms of a term do not create new entries. Repeated policy-level templates must not become hundreds of glossary terms.

## 7. Localization fixes

The initial 0.0.1 implementation includes two fixes that do not require gameplay code changes:

| TCTE key | Source state | Planned value |
| --- | --- | --- |
| `mod_fleet_command_limit_add` | `$mod_fleet_command_limit_mult$`; target not found in Tass Cheat Tool, game localization, or the prepared Russian base | `$MOD_COMMAND_LIMIT_ADD$` |
| `TASS_CHEAT_WORMHOLE` | Referenced by `name` in `common/bypass/tass_bypasses.txt:39`, but not defined in localization | `$BYPASS_TASS_CHEAT_WORMHOLE$` |

The first fix belongs among the 54 entries in `tcte_tass_replace_l_russian.yml`. Its corrected target exists in the game. This is an explicit exception to unchanged reference tokens and does not change the modifier or its numeric value.

The second fix adds one entry to `tcte_fixes_l_russian.yml`, referencing the translated portal name from `tcte_tass_l_russian.yml`. Since base-mod code already uses this identifier, do not add the `tcte_` prefix to it.

Static inspection confirms the missing targets but does not replace testing their display in-game. Any further defects requiring additional keys, reference changes, or gameplay changes must be described to the user and approved separately.

**Clarification for the user's bug report dated 2026-11-14 — version 0.0.2.** Five precursor buttons in the startup window exposed Russian Localization Fix RE's declension metadata. Replace the `*_precursor_civ` strings intended for grammatical processing with existing screen titles for the same civilizations:

| TCTE key | New value |
| --- | --- |
| `tass_cheat.0.vultaum` | `$precursor.1.name$` |
| `tass_cheat.0.yuht` | `$precursor.500.name$` |
| `tass_cheat.0.first_league` | `$precursor.1000.name$` |
| `tass_cheat.0.irassian` | `$precursor.1500.name$` |
| `tass_cheat.0.cybrex` | `$precursor.2000.name$` |

This is a targeted exception to preserving original references to repair the reported defect. Do not duplicate translations, override shared game keys, or change event selection effects. Entry and file counts remain unchanged. Recursively check all TCTE static references for exposed `&!` and `|||` metadata using both vanilla and Russian Localization Fix RE sources. Verify that the previous version produces exactly these five failures and the corrected version produces none.

## 8. Effects on shared game strings

Include all 54 entries from `tass_replace_l_english.yml`. **32 keys are explicitly defined in vanilla localization**; no explicit definitions for the other **22** were found in the inspected vanilla files. The latter group also uses shared modifier names and must not be treated as isolated to Tass menus.

Overriding a key affects every interface location using it. For example, compact production labels containing icons and “Ежемесячно” can appear outside the cheat menu. This deliberately carries the base mod's formatting into Russian; it does not alter resource calculations.

Keep the full list of 54 keys and sources for the 32 overlaps in [VANILLA_CHANGES_EN.md](VANILLA_CHANGES_EN.md). Do not copy entire vanilla files. Functions, gameplay definitions, and physical installed game files are not modified. All 54 Russian entries are included in version 0.0.1.

## 9. Deliverables

After implementation, the game distribution contains exactly **7 files**: `descriptor.mod` and the **6** Russian localization files from section 2. The external `TCTE.mod` is created for local installation and contains that installation's path.

Working materials:

- `TCTE/Docs/TZ_RU.md` and `TZ_EN.md`: this specification;
- `TCTE/Docs/CHANGELOG_RU.md` and `CHANGELOG_EN.md`: changes for each iteration;
- `TCTE/Docs/VANILLA_CHANGES_RU.md` and `VANILLA_CHANGES_EN.md`: shared override scope;
- after implementation, `TCTE/Docs/README_RU.md` and `README_EN.md`: installation and game testing;
- the shared `Glossary/`;
- temporary audit data, validation, reports, and the distribution archive in `TMP/TCTE/`.

Exclude documentation, the glossary, and temporary files from the game distribution. Do not perform Git operations. See [README_EN.md](README_EN.md) for the implementation contents, installation, and validation results.

## 10. Synthetic validation

After implementation:

1. Compare the source baseline against section 12. If it has changed, repeat the audit and obtain approval for scope changes instead of automatically applying old counts.
2. Verify exact coverage: five sets of **53 / 154 / 19 / 1,386 / 54** keys plus the separate `TASS_CHEAT_WORMHOLE` entry; **1,667 unique entries** overall, with no gaps or duplicates.
3. Validate UTF-8 BOM, headers, filenames, LF/CRLF, entry structure, and quotation marks. For originally nonempty values, compare control tokens, escapes, and every number against the sources; allow only the exact exception from section 7. Validate new descriptions under the separate requirements in sections 3 and 5.
4. Verify the exact set of **704** new nonempty Russian descriptions and that only `NAME_leader_tass` and `edict_tass_edict_cheat_test_desc` remain empty. For every new text, check its code evidence, conditions, amounts, timing, references, and variables, including their scopes; numeric constants must be supported by sources, and variable values must not be replaced with constants. Originally reference-only and numeric values remain unchanged except for the stated reference fix. Review all **729** original values containing alphabetic text for translation completeness; do not flag the `Tass` brand as untranslated.
5. Check repeated templates, policy numbering, 94 option sets, and 13 categories. Supplement searches for residual English outside tokens with manual review of proper names.
6. Validate static `$...$` references against TCTE, base-mod, and game localization: targets must exist and references must not form cycles. Check both section 7 entries separately. Compare dynamic `[...]` expressions against their sources rather than evaluating them without the game.
7. Verify keys against actual decisions, edicts, policies, events, ships, and the portal. Do not automatically classify technical slot names and other internal identifiers as missing localization.
8. Validate glossary JSON, source priorities and existence, and the absence of duplicate terms or references across the shared directory.
9. Check the manifest, dependency, `supported_version="v4.5.*"`, distribution contents, installed file consistency, and absence of gameplay changes outside localization. Game and Workshop sources must remain unchanged.
10. Check RU/EN pairs, tables of contents, links, changelog, and the shared-key list. Save results under `TMP/TCTE/`; do not report game testing as completed.

## 11. In-game testing

The user selects Russian and loads TCTE after Tass Cheat Tool. Check:

- the opening message and precursor selection in a new game;
- opening the main menu through the capital decision and entering every section, including return/exit buttons and unavailability conditions;
- 13 policy categories, all 94 names, level and monthly-option labels, and modifier tooltips;
- decisions and edicts, civic and trait tooltips, summoned leaders and ships;
- the Shroud section and attunement, ascension paths, and ascension perks;
- nomad, arkship, and waystation options when the relevant content is available;
- the paradise system and portal, including the wormhole type name in tooltips;
- shared modifier labels, including fleet command limit, inside and outside Tass menus.

For new descriptions, verify that text appears, accurately describes the selected level and conditions, and does not fully duplicate the adjacent automatic tooltip. For dynamic substitutions actually used, change the relevant value or context and verify that the text updates. Mark unavailable test scenarios as untested; do not introduce gameplay mechanisms solely to test a substitution.

Check name substitutions, readability at the selected UI scale, colors, icons, `\n` and `\t`, clipped text, and unresolved keys. Mark items unavailable without particular DLC or game state as untested; testing must not disable base-mod conditions. GUI expansion for longer translations is outside this stage: first use shorter wording without losing meaning.

## 12. Sources and baseline fingerprints

Installed files are authoritative. `Readme.txt` provides an overview, but behavior is checked against code. Preparation inspected the base mod's localization, manifest, decisions, policies and categories, events, traits, ship declarations, and bypass definitions. Static auditing is not a complete functional test of Tass Cheat Tool.

English file SHA-256 fingerprints at preparation time:

| File | SHA-256 |
| --- | --- |
| `tass_l_english.yml` | `6bccb876e7e3ae62ae60ba2405d071fccadec24fb29676649f91c82b9583a996` |
| `tass_event_l_english.yml` | `fa909d6e39c8c786a77209b506b545a3b6ef2c1cc70bfaa1c2dfedcc1b4358e2` |
| `tass_names_l_english.yml` | `addbadbabcb9ed0820375d396c65a88f8b094ef633f7921ac68236446edb0ebc` |
| `tass_policy_l_english.yml` | `0db48d14bfb5b77d69d515cd1b586338dca1298446ad264c31375aeb9ee6a742` |
| `tass_replace_l_english.yml` | `738c7384b15fa11418f3e66d9f63b05eaf280b3bc059570a3f17131ba7b082f5` |

Supplementary research materials: [localization audit](../../TMP/TCTE/localisation_audit.json) and [terminology sources](../../TMP/TCTE/terminology_sources.json). They reside in the ignored temporary directory and are not required documentation dependencies: scope, exceptions, priorities, and fingerprints are recorded above.

[Русское ТЗ](TZ_RU.md) · [Changelog](CHANGELOG_EN.md).
