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

The approved [stage-six specification](Docs/TZ_BACKEND_STAGE_6_EN.md) is implemented: sources → parser and `inline_script` expansion → JSON containing file trees. The profile, command registry, dependent analyzer, and previous domain conversion have been removed. Localization and dependency computation belong to subsequent enrichment stages.

The [stage-six guide](Docs/BACKEND_STAGE_6_EN.md) describes operation, format, modules, and limitations. The standard database is `data/database.json`; the report is `data/reports/build_report.json`. The new format is `sttv.parse_database`, version 1; loading requires neither the game nor parser configuration.

All 87 current tests passed. The reference technology build contains 35 files, 67,513 nodes, and 301 expanded calls from 10 templates, with no errors or warnings; JSON matches parser trees and is reproducible byte for byte. The last full audit before targeted exceptions had 1,542 successful files and 20 problematic inputs, excluding 43 effect files and 631 inline templates. Its report and lists are under `data/stage6/without_scripted_effects/`; initial results remain under `data/stage6/`.

Targeted exceptions subsequently passed checks on the color file and three tradition files. All 75 tradition calls expanded, including four references to the explicitly permitted extensionless file; report: `data/stage6/inline_exceptions/validation_report.json`. The full audit was not rerun.

Sources and previous research lists are preserved. Guides for stages 1–5 describe historical implementations. The current database does not retrieve RU/EN names or compute relationships; those operations will be designed separately.

Code is in `src/backend/`. The UI, HTTP service, images, and portable distribution are not implemented yet; no software release version is assigned. TypeScript, HTML/CSS, and PyInstaller in `onedir` mode are agreed for subsequent stages.

## Directory structure

| Path | Purpose |
| --- | --- |
| `src/frontend/` | Interface code |
| `src/backend/` | Python processing and subsequent local-service code |
| `config/` | Sources, output paths, and five parser configurations including exceptions |
| `schemas/` | Eight generated configuration, syntax-tree, and report schemas |
| `data/` | Default working folder for the database, reports, temporary output, and checks |
| `Docs/` | Russian and English documentation |

`WORK_DIR` configures the working folder. Relative values are resolved against the `WEB_STTV`/product directory; absolute paths inside the repository are also allowed. Changing the setting does not move existing data. The root `.gitignore` includes `/WEB_STTV/data/`; a different working folder is ignored separately when needed. The setting is applied on each builder invocation.

Sources are read directly from selected directories in read-only mode. Parsing results are persisted as JSON for subsequent enrichment without copying source files. Rebuilding requires sources; reading a completed database does not.

## Global variables

The shared [global_variables.json](global_variables.json) file stores project variables that have already been defined. It will grow as new variables are identified for any part of the application; its purpose is not limited to parsing.

| Variable | Purpose | Current value |
| --- | --- | --- |
| `WORK_DIR` | Product and validation working folder, relative to the project directory by default | `data` |
| `STELLARIS_ROOT` | Absolute path to the installed game root | `E:/SteamLibrary/steamapps/common/Stellaris` |
| `TECH_PATH` | Path to the technology directory relative to `STELLARIS_ROOT` | `common/technology` |
| `INLINE_SCRIPTS_DIR` | Directory containing `inline_script` templates, relative to `STELLARIS_ROOT` | `common/inline_scripts` |
| `SCRIPTED_EFFECTS_DIR` | Named-effect library relative to `STELLARIS_ROOT`, excluded from independent traversal | `common/scripted_effects` |
| `WORKSHOP_DIR` | Absolute path to Stellaris Steam Workshop mods | `E:/SteamLibrary/steamapps/workshop/content/281990` |
| `RU_LOC_TIER_1` | Russian localization, highest priority: the Russian Localization Fix RE mod's `replace` directory | `${WORKSHOP_DIR}/681483874/localisation/replace` |
| `RU_LOC_TIER_2` | Russian localization, second priority: the same mod's `russian` directory | `${WORKSHOP_DIR}/681483874/localisation/russian` |
| `RU_LOC_TIER_3` | Russian localization, third priority: vanilla, relative to `STELLARIS_ROOT` | `localisation/russian` |
| `EN_LOC_TIER_1` | English localization: vanilla, relative to `STELLARIS_ROOT` | `localisation/english` |

`TECH_PATH`, `INLINE_SCRIPTS_DIR`, `SCRIPTED_EFFECTS_DIR`, `RU_LOC_TIER_3`, and `EN_LOC_TIER_1` are relative to `STELLARIS_ROOT`. `${WORKSHOP_DIR}` in the other two paths denotes substitution of the variable with that name. This is a configuration-file convention: JSON stores ordinary strings and does not perform substitution itself. Paths use forward slashes `/`, consistent with the previously defined variables.

`INLINE_SCRIPTS_DIR` is used for inclusion expansion. For example, `script = technologies/rare_technologies_weight_modifiers` refers to `STELLARIS_ROOT/INLINE_SCRIPTS_DIR/technologies/rare_technologies_weight_modifiers.txt`. The directory is read-only; templates are loaded through reached calls, including nested ones.

Nested calls, argument substitution, and invocation history are implemented. Metadata is excluded from analytical traversal; the current representation is described in the [stage-six guide](Docs/BACKEND_STAGE_6_EN.md).

During future enrichment, Russian text is selected per key in the order `RU_LOC_TIER_1` → `RU_LOC_TIER_2` → `RU_LOC_TIER_3`, moving to the next source if the key is absent. English text for the same key comes from `EN_LOC_TIER_1`. Russian and English localization are treated separately; key availability is checked independently for each language.

Absolute source roots belong to the current environment. Game and localization directories are read-only; `WORK_DIR` is intended for writing output. The builder loads variables and expands inline calls. Localization directories are not required; retrieving names belongs to future enrichment.

## Documents

- [Language construct catalog](language/README_EN.md).
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
- [Fifth-stage specification: inline_script expansion and invocation history — implemented](Docs/TZ_BACKEND_STAGE_5_EN.md).
- [Stage-six specification: parsing results database and backend simplification — implemented](Docs/TZ_BACKEND_STAGE_6_EN.md).
- [Stellaris v4.5.4 technology tree research](Docs/RESEARCH_TECH_TREE_EN.md).
- [Technology object model: fields, types, and nested structures](Docs/TECHNOLOGY_MODEL_EN.md).
- [Stage-one JSON database model: technology structure and RU/EN names](Docs/DATABASE_MODEL_EN.md).
- [Changelog](Docs/CHANGELOG_EN.md).
- [Shared repository TODO: CLASS and RELIC](../TO_DO_EN.md).
- [Investigation of the missing genetic tradition template](Docs/RESEARCH_MISSING_TRADITION_TEMPLATE_EN.md).
- [Обзор на русском](README_RU.md).

- [Backend: inline_script expansion](Docs/BACKEND_STAGE_5_EN.md).

- [Backend: parsing results database](Docs/BACKEND_STAGE_6_EN.md).
- [Inline_script path exceptions](config/parser/exceptions.json): exact permitted files and reasons; application rules are described in the backend guide.
