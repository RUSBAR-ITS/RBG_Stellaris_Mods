# Stellaris Technological Tree View

## Contents

- [Project](#project)
- [Status](#status)
- [Directory structure](#directory-structure)
- [Global variables](#global-variables)
- [Documents](#documents)

## Project

**Stellaris Technological Tree View**, project directory: `WEB_STTV`.

A local interactive web reference for Stellaris technologies. Its primary view is a dependency tree made of technology cards with vanilla images. Data is collected from user-selected sources and transformed into the reference application's internal database. The intended distribution is portable on Windows and requires no separate web-server installation.

## Status

The approved [fourth parser stage](Docs/TZ_BACKEND_STAGE_4_EN.md) is implemented: a separate logical-operator configuration, `LogicalOperation` nodes, and an `inline_script` expansion function with an empty stub. All 101 tests pass; the vanilla corpus yielded 36,026 logical nodes and 6,885 skips. The database matched an independently transformed baseline; inline contributions are temporarily excluded. [Current interface, configuration, and verification](Docs/BACKEND_STAGE_4_EN.md).

Implemented the approved [third stage](Docs/TZ_BACKEND_STAGE_3_EN.md): an independent parser and two compact syntax configurations. All 79 tests pass; 2,235 vanilla files parse successfully and the database matches the baseline byte for byte. Game-command semantic validation is separate from the parser. [Settings, interface, and limitations](Docs/BACKEND_STAGE_3_EN.md).

The approved [second backend stage](Docs/TZ_BACKEND_STAGE_2_EN.md) is implemented: module packages, permanent schema generation, shared field contracts, JSON profiles and a separate analyzer. All 54 tests pass; database bytes match stage one. [Settings, operations and limitations](Docs/BACKEND_STAGE_2_EN.md).

As of 2026-11-15, the approved [first backend stage](Docs/TZ_EN.md#3-first-backend-stage--database-building) is implemented: a standalone Python builder with a strict JSON model, RU/EN names, validation, and a separate report. Current sources produce 679 technologies and 206 variants; all 885 records have names in both languages. First-stage checks are retained. [Operation, structure, and validation results](Docs/BACKEND_STAGE_1_EN.md).

[Technology tree research](Docs/RESEARCH_TECH_TREE_EN.md) of the installed Stellaris v4.5.4 was completed before further design, covering definitions, logical dependencies, tiers, eligibility, variants, and repetition. These findings are not a new approved specification part.

Builder code is in `src/backend/`, and the validated database is at `data/database.json`. The UI, HTTP service, images, and portable distribution are not implemented yet; no software release version has been assigned. TypeScript, HTML/CSS, and PyInstaller in `onedir` mode are agreed for subsequent stages. The research audit remains in `TMP/WEB_STTV/` and is not a product input.

## Directory structure

| Path | Purpose |
| --- | --- |
| `src/frontend/` | Interface code |
| `src/backend/` | Python processing and subsequent local-service code |
| `config/` | Reading, priorities, active profile, analysis sources, output paths, and syntax in `parser/` |
| `schemas/` | Generated closed application schemas |
| `profiles/` | Supplied game-rule profiles |
| `data/` | Default working folder for the database, reports, temporary output, and checks |
| `Docs/` | Russian and English documentation |

`WORK_DIR` configures the working folder. Relative values are resolved against the `WEB_STTV`/product directory; absolute paths are also allowed. Changing the setting does not move existing data. The root `.gitignore` includes `/WEB_STTV/data/`; a different working folder is ignored separately when needed. The setting is applied on each builder invocation.

Sources are read directly from selected directories in read-only mode. Source-file copies and a persistent intermediate snapshot are not created; parsing and transformation operate on in-memory data. Rebuilding requires sources; reading a completed database does not.

## Global variables

The shared [global_variables.json](global_variables.json) file stores project variables that have already been defined. It will grow as new variables are identified for any part of the application; its purpose is not limited to parsing.

| Variable | Purpose | Current value |
| --- | --- | --- |
| `WORK_DIR` | Product and validation working folder, relative to the project directory by default | `data` |
| `STELLARIS_ROOT` | Absolute path to the installed game root | `E:/SteamLibrary/steamapps/common/Stellaris` |
| `TECH_PATH` | Path to the technology directory relative to `STELLARIS_ROOT` | `common/technology` |
| `WORKSHOP_DIR` | Absolute path to Stellaris Steam Workshop mods | `E:/SteamLibrary/steamapps/workshop/content/281990` |
| `RU_LOC_TIER_1` | Russian localization, highest priority: the Russian Localization Fix RE mod's `replace` directory | `${WORKSHOP_DIR}/681483874/localisation/replace` |
| `RU_LOC_TIER_2` | Russian localization, second priority: the same mod's `russian` directory | `${WORKSHOP_DIR}/681483874/localisation/russian` |
| `RU_LOC_TIER_3` | Russian localization, third priority: vanilla, relative to `STELLARIS_ROOT` | `localisation/russian` |
| `EN_LOC_TIER_1` | English localization: vanilla, relative to `STELLARIS_ROOT` | `localisation/english` |

`TECH_PATH`, `RU_LOC_TIER_3`, and `EN_LOC_TIER_1` are relative to `STELLARIS_ROOT`. `${WORKSHOP_DIR}` in the other two paths denotes substitution of the variable with that name. This is a configuration-file convention: JSON stores ordinary strings and does not perform substitution itself. Paths use forward slashes `/`, consistent with the previously defined variables.

Russian text is selected per key in the order `RU_LOC_TIER_1` → `RU_LOC_TIER_2` → `RU_LOC_TIER_3`, moving to the next source if the key is absent. English text for the same key comes from `EN_LOC_TIER_1`. Russian and English localization are treated separately; key availability is checked independently for each language.

Absolute source roots belong to the current environment. Game and localization directories are read-only; `WORK_DIR` is intended for writing output. Variable loading, reference substitution, and name selection are implemented in the builder.

## Documents

- [Project concept](Docs/CONCEPT_EN.md).
- [Specification: technical foundation, coding principles, and first backend stage](Docs/TZ_EN.md).
- [First backend stage: operation, modules, diagnostics, and validation](Docs/BACKEND_STAGE_1_EN.md).
- [Second-stage backend specification: modules, schemas, rule profiles, and analyzer — implemented](Docs/TZ_BACKEND_STAGE_2_EN.md).
- [Second stage: profiles, analyzer and programmatic operations](Docs/BACKEND_STAGE_2_EN.md).
- [Third-stage specification: parsing engine and syntax configuration — implemented](Docs/TZ_BACKEND_STAGE_3_EN.md).
- [Third stage: configurations, nodes, programmatic interface, and validation](Docs/BACKEND_STAGE_3_EN.md).
- [Keywords and values: agreed classification](Docs/KEYWORDS_AND_VALUES_EN.md).
- [Fourth-stage specification: logical operators and the inline_script handler — implemented](Docs/TZ_BACKEND_STAGE_4_EN.md).
- [Fourth stage: interface, configurations, skips, and verification](Docs/BACKEND_STAGE_4_EN.md).
- [Stellaris v4.5.4 technology tree research](Docs/RESEARCH_TECH_TREE_EN.md).
- [Technology object model: fields, types, and nested structures](Docs/TECHNOLOGY_MODEL_EN.md).
- [Stage-one JSON database model: technology structure and RU/EN names](Docs/DATABASE_MODEL_EN.md).
- [Changelog](Docs/CHANGELOG_EN.md).
- [Обзор на русском](README_RU.md).
