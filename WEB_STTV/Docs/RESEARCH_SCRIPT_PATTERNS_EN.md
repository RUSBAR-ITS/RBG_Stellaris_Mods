# Stellaris — basic vanilla script patterns

## Contents

- [Scope and method](#scope-and-method)
- [Complete directory statistics](#complete-directory-statistics)
- [Other file types](#other-file-types)
- [Lexical rules](#lexical-rules)
- [Structural forms](#structural-forms)
- [Variables and parameterized constructs](#variables-and-parameterized-constructs)
- [Context and domain meaning](#context-and-domain-meaning)
- [Automatically extractable information](#automatically-extractable-information)
- [Limitations and findings](#limitations-and-findings)
- [Verification and artifacts](#verification-and-artifacts)

## Scope and method

Date: 2026-11-15. Installed version: **Cygnus v4.5.4 (1b4f)**, read from `launcher-settings.json`.

Every file under `common/` and `events/` in `E:/SteamLibrary/steamapps/common/Stellaris/` was inventoried recursively. Inputs were limited to the installed vanilla game. Mods, the internet, external command registries and engine documentation logs were not used.

The purpose is to identify observed language forms for discussion of a future parser. This is research, not a specification or a product implementation change. Measurement scripts reside in `TMP/WEB_STTV/script_patterns/`; the product parser, schemas, profile and database were not changed.

Method: complete file manifest with SHA-256; reading every `.txt`; initial coverage check using the existing parser; independent structural scanning without a command dictionary; source inspection of unusual cases; exact reconstruction of significant tokens. Comments were counted separately from active text. Documentation shipped inside the game was used for explanation, with corresponding forms checked against actual script usage.

## Complete directory statistics

| Directory | All files | `.txt` | Other | Lines in `.txt` | Bytes in `.txt` |
|---|---:|---:|---:|---:|---:|
| `common/` | 2,073 | 2,067 | 6 | 1,029,494 | 21,678,343 |
| `events/` | 171 | 171 | 0 | 596,440 | 12,300,222 |
| **Total** | **2,244** | **2,238** | **6** | **1,625,934** | **33,978,565** |

Every `.txt` decodes as UTF-8; 84 contain a UTF-8 BOM and 2,154 do not. No NUL bytes or CRLF line endings were found. Lines were counted with `splitlines()`, including a final fragment without a terminating newline.

Of the 2,238 `.txt` files, 2,150 contain structural text; 86 contain only comments, whitespace or nothing; two are prose documents with uncommented sentences:

- `common/HOW_TO_MAKE_NEW_SHIPS.txt`;
- `common/edicts/99_README_EDICTS.txt`.

The 86 files without structural text include instructions written entirely as comments. Example files containing active definitions were included as structural text. Neither the extension nor a `README` name alone determines how to process a file.

The complete breakdown across 250 directories directly containing files is in `corpus_summary.json → directories`; the full file manifest is in `baseline_audit.json → files`.

## Other file types

All six are under `common/`. Paths below are relative to the game root.

| Type | Path | Bytes |
|---|---|---:|
| JSON | `common/achievements/msgrdk_achievements.json` | 15,819 |
| CSV | `common/component_templates/mutation_weapon_components.csv` | 39,567 |
| ODS | `common/component_templates/mutation_weapon_components.ods` | 969,230 |
| CSV | `common/component_templates/weapon_components.csv` | 53,223 |
| ODS | `common/component_templates/weapon_components.ods` | 1,136,304 |
| No extension | `common/inline_scripts/traditions/tr_purity_imperfection_remediation_wilderness` | 80 |

The extensionless file was read separately: it contains `custom_tooltip_with_modifiers = tr_purity_imperfection_remediation_wilderness_tt`. Its content resembles an ordinary inline fragment, but whether the game loads it was not established. It is excluded from `.txt` and syntax-form counts. The other five files were inventoried and hashed, without analyzing their internal formats.

## Lexical rules

1. Spaces, tabs and line breaks separate elements. Braces express nesting; indentation does not describe it. Multiple entries may occupy one line.
2. `#` starts a comment outside a string. Commented examples do not count as command usage.
3. Double quotes delimit a string token. The corpus contains 89,906 such tokens: 89,402 values and 504 keys. There are 21 multiline strings in six files. Brackets inside strings do not alter outer nesting.
4. Unquoted atoms cannot be restricted to `A-Z/a-z/0-9/_`: `.`, `:`, `?`, `@`, `$`, `|`, `/`, hyphens and apostrophes occur. For example, `TOX1_FLEET_Avogadro's_Moles` appears in `common/name_lists/TOX1.txt:55`.
5. A number, `yes/no`, an identifier and a reference are different interpretations of scalar tokens. Preserve original spelling and quoting; determine domain types using field context. Integers, negative numbers and decimals occur; exponent notation was not found among unquoted numeric tokens.

| Operator outside strings, comments and formulas | Occurrences |
|---|---:|
| `=` | 1,102,564 |
| `>` | 3,674 |
| `>=` | 3,105 |
| `<` | 2,178 |
| `<=` | 544 |
| `!=` | 38 |

A separate `?=` operator was not observed. The corpus contains **`owner? = { ... }`**, with `?` attached to the scope name and a separate `=`. Keys containing `?` occur 3,018 times in 336 files. Preserve this distinction rather than normalizing it into another operator without verification.

## Structural forms

Counts describe source text before expansion. Nested elements are counted individually. Table examples are abbreviated to show their form.

| Form | Example | Occurrences | Files |
|---|---|---:|---:|
| Key, operator, scalar | `weight = 10`, `count >= 2` | 660,435 | 2,113 |
| Key, operator, block | `potential = { ... }` | 451,481 | 2,096 |
| Standalone scalar | `energy`, `optimize_memory`, `$TRIGGER$` | 62,787 | 761 |
| Anonymous block | `{ key = specialist_type value = specialist_none }` | 832 | 26 |
| Tagged block value | `value = rgb { 235 0 18 0 }` | 187 | 13 |
| Label followed by block without operator | `rgb { 142 188 241 }` | 90 | 2 |
| Conditional parameter fragment | `[[PARAM] ... ]`, `[[!PARAM] ... ]` | 53 | 13 |

Of the 90 labels followed by blocks without an operator, 89 are `rgb` in `common/colors/00_colors.txt`; one is the questionable `trait_bg_active_glow { ... }` entry discussed below. Color forms `rgb` and `hsv` occur as tagged values rather than ordinary command collections.

A container can contain named entries, scalars, anonymous blocks or combinations. There are 116 containers mixing standalone scalars with other forms. Examples:

- `common/inline_scripts/buildings/nomadic_cost_switcher_with_additional_trigger.txt:3`: an ordinary condition and a standalone `$TRIGGER$` inside one block;
- `common/scripted_effects/00_scripted_effects.txt:73`: the `optimize_memory` marker beside effects;
- `common/technology/00_biogenesis_tech.txt:795`: an ordinary technology and a logical group inside `prerequisites`.

There are 3,946 empty blocks. Maximum observed nesting is 16, with document depth 0; this includes brace blocks and conditional parameter fragments.

**Containers must preserve order and repeated keys.** There are 35,048 container/repeated-key pairs, not that many distinct containers. Repetitions occur in modifiers, options, effects and events; a dictionary replacing earlier values loses information. Numeric keys also occur: 7,140 uses, including random-choice branches.

Document roots include named objects, repeated event wrappers with an `id` field, variable assignments, bare-name lists and anonymous root blocks. A single object or one universal document schema cannot be required for every `.txt` file.

## Variables and parameterized constructs

| Family | Observation | Example source |
|---|---|---|
| `@name` definition and reference | 4,145 definitions; 30,363 scalar references | `common/agreement_presets/00_agreement_presets.txt:30` |
| `@[ ... ]` formula | 52 formulas | `common/component_templates/00_shroud_weapons.txt:118` |
| `@\[ ... ]` formula | 22 formulas with an escaped opening bracket | `common/scripted_effects/astral_planes_effects.txt:14` |
| `$PARAM$` substitution | Used in values, keys, strings, formulas and complete fragments | `common/inline_scripts/buildings/nomadic_cost_switcher_with_additional_trigger.txt:6` |
| Substitution with a default | 73 occurrences of `$PARAM\|default$` | `common/scripted_effects/00_scripted_effects.txt:4104` |
| Conditional fragment | Positive and negative forms | `common/scripted_effects/00_scripted_effects.txt:9006` and `:9009` |
| Scoped and prefixed references | `root.owner`, `event_target:name`, `value:name`, `trigger:name`, and combinations | `common/buildings/14_branch_office_buildings.txt:4432` |
| Pipe-delimited reference arguments | 689 unquoted scalar occurrences containing both `:` and `\|` | `common/artifact_actions/artifact_actions.txt:1052` |
| Inline fragment by path | 1,532 scalar and 5,353 block forms of `inline_script` | `common/technology/00_eng_tech.txt:497` and `:333` |

The 74 formulas contain `+`, `-`, `*`, `/`, parentheses and paired `| ... |`. `%` is listed in shipped documentation but was not found in active formulas in this corpus. Formulas were not evaluated; precedence was not inferred solely from symbol frequencies.

`common/scripted_effects/99_advanced_documentation.txt` explains parameters, defaults, conditional fragments and formulas. It describes `[[PARAM]` as testing that the parameter exists and is not `no`; the negative form covers the opposite case. Forms are confirmed in script, while actual engine execution was not tested.

Multiline strings can carry code: `common/buildings/01_pop_assembly_buildings.txt:1131` and `events/assimilation_events.txt:481`. Preserve the complete string first; possible substitution and subsequent parsing are separate operations. A `$PARAM$` cannot universally be assumed to represent just one identifier or number.

## Context and domain meaning

The same structural form, `name = { ... }`, represents object definitions, conditions, effects, scope transitions, modifier tables and call arguments. `OR`, `AND`, `NOT`, `if`, `limit`, `random_list` and `modifier` require no different kinds of bracket, but their meanings differ.

This separates three tasks:

1. Read syntax while preserving form, order, repetitions, quoting and coordinates.
2. Connect definitions, references, includes and parameters using source files.
3. Interpret only the fields and constructs required by the product through explicit contracts.

A compact grammar handles the first task. It neither proves an arbitrary command valid in every scope nor establishes every built-in engine function contract. Scripted trigger/effect names are extractable from files; complete built-in command contracts may be absent from the sources.

## Automatically extractable information

The following separate inventory was extracted from named definitions and file paths, without adding these names to the grammar:

| Source | Extracted |
|---|---:|
| `common/scripted_triggers/` | 1,693 named definitions and 12 `@` definitions |
| `common/scripted_effects/` | 1,691 named definitions and 24 `@` definitions |
| `common/script_values/` | 674 named definitions and one `@` definition |
| `common/scripted_variables/` | 2,917 `@` definitions |
| `common/inline_scripts/` | 617 `.txt` files containing structural text |

These are source-definition counts, not proof of usage or availability in every context. Inline parameters were collected as observed substitution names; requiredness, type and valid scope do not automatically follow.

Basis for further design: define a small set of syntax forms, independently extract definition catalogs from the game, and separately define the interpretation needed by the technology reference product. Tens of thousands of observed keys do not need to become a manually maintained syntax dictionary. This is a research conclusion; the active specification has not been revised.

## Limitations and findings

- `common/named_colors/01_trait_colors.txt:65` contains `trait_bg_active_glow { ... }`, whereas neighboring definitions use `=`. The probe preserves it as a label and block. Source files alone cannot establish whether it is valid syntax, engine tolerance or a typo; it does not establish a universal rule that `=` is optional.
- A vanilla file does not guarantee absence of mistakes or outdated examples. Observed syntax, commentary and engine confirmation are different kinds of evidence.
- Completeness is not established for future versions or every form accepted by the engine but absent here. Includes were not fully expanded, scripts were not executed, and country state was not simulated.
- The current product parser reported failures for 49 `.txt` files, including the ship prose document. Besides explicit failures, it can accept a formula or positive conditional fragment as ordinary atoms and lose the construct boundary. Successful return does not establish correct recognition of every form. No fixes were applied.

## Verification and artifacts

For 2,236 files, excluding the two separately reviewed prose documents, lexical reconstruction verified that no characters were skipped; structural reconstruction reproduced exactly **3,852,991 significant tokens**. There were no unresolved structural files or unknown lexical characters within the research recognizer's coverage. These checks establish text and structure preservation, not correct engine execution.

Rereading confirmed unchanged SHA-256 hashes for all 2,244 files. Game directories were read only. No in-game validation was performed.

Working artifacts reside in `D:/Repos/RBG_Stellaris_Mods/TMP/WEB_STTV/script_patterns/`:

- [corpus_summary.json](../../TMP/WEB_STTV/script_patterns/corpus_summary.json): summary and complete directory statistics.
- [baseline_audit.json](../../TMP/WEB_STTV/script_patterns/baseline_audit.json): file manifest, hashes, sizes, encodings and initial existing-parser check.
- [pattern_audit.json](../../TMP/WEB_STTV/script_patterns/pattern_audit.json): all counts, source examples, operators, keys and mixed containers.
- [definition_catalog.json](../../TMP/WEB_STTV/script_patterns/definition_catalog.json): extracted definitions and observed inline parameters.
- [audit_corpus.py](../../TMP/WEB_STTV/script_patterns/audit_corpus.py), [structure_probe.py](../../TMP/WEB_STTV/script_patterns/structure_probe.py), [measure_patterns.py](../../TMP/WEB_STTV/script_patterns/measure_patterns.py), [catalog_and_verify.py](../../TMP/WEB_STTV/script_patterns/catalog_and_verify.py): reproducible research measurements.
