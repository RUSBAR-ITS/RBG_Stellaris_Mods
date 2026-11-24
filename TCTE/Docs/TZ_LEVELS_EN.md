# Tass Cheat Tool Extender — specification for 10 policy levels

## Contents

- [1. Status and user decisions](#1-status-and-user-decisions)
- [2. Source baseline and scope](#2-source-baseline-and-scope)
- [3. Approved progression](#3-approved-progression)
- [4. Policy overrides](#4-policy-overrides)
- [5. Localization and documentation](#5-localization-and-documentation)
- [6. Validation and acceptance](#6-validation-and-acceptance)
- [Update for Tass 20261124](#update-for-tass-20261124)

## 1. Status and user decisions

**Approved by the user on 2026-11-14 with the instruction to start implementation. Implemented in version 0.0.4. Synthetic checks passed; in-game verification is pending.** This document covers the stage after [localization](TZ_EN.md).

The user requested ten levels and confirmed:

- preserve existing levels and extend enhancement through level ten;
- expand both tracks: regular enhancement and separate monthly resource additions.

The approved rule is **×2 for each new level**, including negative modifiers. Existing levels remain unchanged.

## 2. Source baseline and scope

The base mod is Tass Cheat Tool, Workshop ID `682851228`, version `20261012`; source directory: `E:/SteamLibrary/steamapps/workshop/content/281990/682851228/common/policies/`. The extension targets Stellaris `v4.5.*` and requires the base mod. Game and Workshop files are read-only.

Reparsed 94 files containing 94 policies; their SHA-256 hashes match the localization research baseline. Current contents:

| Policy group | Policies | Current enhancement levels | Levels after extension |
| --- | ---: | --- | --- |
| Regular track only | 44 | 5 | 10 |
| Regular and monthly tracks | 18 | 5 + 3 | 10 + 10 |
| Regular track only | 31 | 4 | 10 |
| Research alternatives | 1 | 3 | 10 |
| **Total** | **94** | **112 tracks** | **112 tracks of 10 levels** |

Each policy retains its separate Unmodified option, which is not one of the ten levels. The total rises from 585 to 1214 options: 94 neutral and 1120 enhanced options. **629 options** are added.

Monthly tracks exist for `energy`, `minerals`, `food`, `research_resources`, `unity`, `alloys`, `consumer_goods`, `trade`, `influence`, `volatile_motes`, `exotic_gases`, `rare_crystals`, `sr_living_metal`, `sr_dark_matter`, `sr_zro`, `nanites`, `minor_artifacts`, and `astral_threads`; prepend `tass_policy_cheat_` for the full ID.

Regular and monthly options remain within the same policy: selecting a monthly addition replaces that policy's percentage enhancement, as in the base mod. Splitting them into independently enabled policies is outside this stage. Edicts, decisions, and events are not extended.

## 3. Approved progression

Identify the final existing level `N` separately for each track. Preserve levels 1 through `N`, including their IDs, values, modifier sets, and conditions. For every numeric modifier at new level `L`, use:

`value(L) = value(N) * 2^(L - N)`, where `N < L <= 10`.

This doubles the modifier itself, not the final game statistic. Percentage coefficients retain their code units: for example, `1` means +100%, and `100` means +10000%. Scale all components of the last level together, preserving signs and relative proportions. Integer additions remain integers; do not round fractional coefficients with a loss of precision. Zero components remain zero.

Examples of complete tracks; new levels are bold:

| Level | Energy production | Base monthly energy | All-cost modifier | Additional research alternatives |
| ---: | ---: | ---: | ---: | ---: |
| 1 | +100% | +200 | −25% | +1 |
| 2 | +200% | +2000 | −50% | +2 |
| 3 | +500% | +20000 | −75% | +5 |
| 4 | +1000% | **+40000** | −100% | **+10** |
| 5 | +10000% | **+80000** | −1000% | **+20** |
| 6 | **+20000%** | **+160000** | **−2000%** | **+40** |
| 7 | **+40000%** | **+320000** | **−4000%** | **+80** |
| 8 | **+80000%** | **+640000** | **−8000%** | **+160** |
| 9 | **+160000%** | **+1280000** | **−16000%** | **+320** |
| 10 | **+320000%** | **+2560000** | **−32000%** | **+640** |

Negative modifiers occur in 20 policies, including costs, upkeep, housing, amenities, crime, fleet travel, and diplomacy. Existing tracks already reach −100% or −1000%. Under the approved rule, new levels continue increasing their absolute magnitude. This does not guarantee negative costs, bypassing engine limits, or a distinguishable practical effect at every new level. Existing levels are not corrected; engine-limit workarounds and new mechanics are outside this stage.

## 4. Policy overrides

Place overrides inside TCTE under `common/policies/`, using the same relative filenames as the 94 source files. TCTE loads after Tass Cheat Tool. Preserve original policy IDs for overrides, categories, `potential`, `allow`, AI settings, neutral options, and all existing options. Do not apply `replace_path` to the entire policy directory.

New options receive IDs prefixed with `tcte_`, such as `tcte_policy_energy_regular_6` and `tcte_policy_energy_monthly_4`. Do not reuse `tass_policy_cheat_energy_6`–`_8` for new regular levels: they already identify monthly levels 1–3. Distinguish the displayed level from the numeric suffix of an existing ID.

Each new option inherits the structure of its own track's last existing option; only the option name and numeric modifier values change according to the formula. Preserve that track's DLC, empire type, crisis path, and other conditions. For example, do not copy regular-track restrictions into monthly options when the source applies different conditions.

Option order: Unmodified, regular levels 1–10, then monthly levels 1–10 where present. Preserve modifier application, replacement, and removal behavior. Compatibility with base Tass is required; migration of earlier extension-specific options is unnecessary because none existed before this stage.

## 5. Localization and documentation

Add Russian and English names and descriptions for the 629 new options, using `tcte_` keys. Names retain Tass styling and display the actual level; monthly options carry a separate designation. Reuse suitable existing references, such as `$tass_enhance$`, instead of copying terms. English localization covers the new keys; existing TCTE files continue supplying translations of original keys.

New descriptions reflect all active modifiers and conditions under the localization specification. Numbers are code constants and must be produced from the same values written to each option, keeping text and effects consistent. Preserve BOM, language headers, control codes, and substitutions. Retain all 1667 existing Russian values; expect another 1258 Russian entries and the same number of English entries. Do not add helper keys without a need.

Update both README and changelog languages; separately list overridden base-mod files. No new vanilla definitions need to be overridden. Preserve `supported_version="v4.5.*"` and the Tass Cheat Tool dependency. After implementation, update the archive and connected local installation without changing playsets. Distribute only runtime files, excluding documentation, generators, and reports.

## 6. Validation and acceptance

Synthetic checks after implementation:

1. Recheck source SHA-256 hashes; if Tass has changed, repeat analysis of affected files.
2. Verify 94 unique policies, 112 tracks, 1214 options, and 629 new collision-free IDs; each track contains exactly levels 1–10, with the existing neutral option retained per policy.
3. Structurally compare all existing options and policy metadata with the source: values and conditions remain unchanged. Verify preservation of every component of compound modifiers and the conditions inherited by new options.
4. Verify the formula for each new value independently of the generator, numeric precision, monotonically increasing absolute magnitudes of nonzero modifiers, and separation of the two tracks.
5. Check description numbers against effects, all new RU/EN keys, duplicate keys, missing references, cycles, and grammatical metadata leaks. Compare old values with the 0.0.3 distribution.
6. Check the manifest, archive contents, installed-copy equality, unchanged game and Workshop files, documentation, and the separate list of affected definitions.

User testing in-game:

- confirm that loading after Tass displays ten regular levels and ten monthly levels where applicable, without duplicate policies;
- select the first new and tenth levels of a percentage, monthly, integer, negative, and compound track;
- check level changes, switching between regular and monthly tracks, and returning to Unmodified, with no accumulation of previously selected modifiers;
- check availability conditions, large-number display, scrolling, tooltips, and loading errors; separately assess actual behavior of negative modifiers and engine-limited statistics;
- agree on any subsequent adjustments based on results; passing static checks does not establish the actual effect of extreme values.

Result: 94 overrides, 112 tracks, and 1214 options; added 629 options and 1258 strings in each of Russian and English. Verified 1200 numeric components of new options. All 585 existing options and 1667 Russian values are preserved. Report: [level validation](../../TMP/TCTE/level_validation_report.json); [override inventory](BASE_MOD_CHANGES_EN.md).

Research material: [track audit](../../TMP/TCTE/level_extension_audit.json), [new level evidence](../../TMP/TCTE/level_sources.json). [Русское ТЗ](TZ_LEVELS_RU.md).

## Update for Tass 20261124

For Stellaris `v4.6.*` each of the ten active Ambitions policy levels includes `country_willpower_produces_mult` and accepts `ap_force_of_will` as an alternative prerequisite. Levels 1–5 follow Tass and levels 6–10 double each preceding coefficient. Verify all ten coefficients, each active level’s prerequisites, the neutral option and localization references.
