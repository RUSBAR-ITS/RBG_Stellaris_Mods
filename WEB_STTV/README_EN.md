# Stellaris Technological Tree View

## Contents

- [Project](#project)
- [Status](#status)
- [Running the frontend](#running-the-frontend)
- [Directory structure](#directory-structure)
- [Global variables](#global-variables)
- [Documents](#documents)

## Project

**Stellaris Technological Tree View**, project directory: `WEB_STTV`.

A local interactive web reference for Stellaris technologies. The first interface displays cards by research area and tier, names and descriptions in tooltips, and manual variants. Vanilla images belong to later stages. Data is collected from user-selected sources and transformed into the reference application's internal database. The intended distribution is portable on Windows and requires no separate web-server installation.

## Status

Implemented and verified [stage 15: parallel file processing](Docs/TZ_BACKEND_STAGE_15_EN.md). The default is ten workers within one database, with intermediate JSON and streaming merging. Configuration, operation and measurement details are in the [stage 15 guide](Docs/BACKEND_STAGE_15_EN.md).

Implemented [stage 14 — reusable element library](Docs/TZ_BACKEND_STAGE_14_EN.md): persistent JSON, explicit preparation/reuse modes and one snapshot for the entire build. Both modes passed full acceptance; commands and architecture are in the [stage 14 guide](Docs/BACKEND_STAGE_14_EN.md).

The backend builds fifteen localized databases; [frontend `0.0.3`](Docs/frontend/TZ_FRONTEND_STAGE_3_EN.md) remains active. The complete set occupies 10.95 GiB. In stage 15, `reuse` took 34:44 with one worker and 8:20 with ten, a 4.17-fold speedup; ten-worker `rebuild` took 8:31. Process-tree peak memory was 4.09 / 21.34 / 20.92 GiB respectively. All three sets are byte-identical; relative to stage 14, only the shared `set_id` changed. All 240 backend tests and 33 frontend checks passed. Measurement conditions and limits are recorded in the stage 15 guide.

Database format: `sttv.parse_database`, version `6`, with a shared `dataset.set_id`. JSON is multiline with two-space indentation and readable Unicode. Complete trees, provenance and localization remain in the files. The frontend reads streams and stores compact catalogs. Game conditions are not evaluated; the existing card layout is preserved.

See the [backend guide](Docs/BACKEND_STAGE_15_EN.md) and [frontend guide](Docs/frontend/FRONTEND_STAGE_3_EN.md). Historical stages and results remain available. Portable distribution, images and state persistence remain separate tasks.

## Running the frontend

From `WEB_STTV` with Node.js 24: `npm ci`, then `npm run dev`. Open `http://127.0.0.1:5173/`. This computer also has a prepared Node.js copy under `data/`; see the [guide](Docs/frontend/FRONTEND_STAGE_3_EN.md#running-and-selecting-files).

Click Open database set and select all fifteen JSON files in `data/databases/` together. Do not select reports from `data/reports/`. Build separately: `$env:PYTHONPATH="src/backend"`, then `python -B -m sttv.database_sets --rebuild-libraries`. Startup and refresh neither invoke generation nor automatically open databases.

## Directory structure

| Path | Purpose |
| --- | --- |
| `src/frontend/` | Interface code |
| `src/backend/` | Python processing and subsequent local-service code |
| `config/` | Sources, output paths, parser, library and localization configurations |
| `schemas/` | Twenty-three generated configuration, database, and report schemas |
| `data/` | Default working folder for the database, reports, temporary output, and checks |
| `Docs/` | Russian and English documentation |
| `Docs/frontend/` | Interface concept and subsequent frontend documentation |

`WORK_DIR` configures the working folder. Relative values are resolved against the `WEB_STTV`/product directory; absolute paths inside the repository are also allowed. Changing the setting does not move existing data. The root `.gitignore` includes `/WEB_STTV/data/`; a different working folder is ignored separately when needed. The setting is applied on each builder invocation.

Sources are read directly from selected directories in read-only mode. Parsing results are persisted as JSON for subsequent enrichment without copying source files. Rebuilding requires sources; reading a completed database does not.

## Global variables

The shared [global_variables.json](global_variables.json) file stores project variables that have already been defined. It will grow as new variables are identified for any part of the application; its purpose is not limited to parsing.

| Variable | Purpose | Current value |
| --- | --- | --- |
| `WORK_DIR` | Product and validation working folder, relative to the project directory by default | `data` |
| `STELLARIS_ROOT` | Absolute path to the installed game root | `E:/SteamLibrary/steamapps/common/Stellaris` |
| `TECH_PATH` | Path to the technology directory relative to `STELLARIS_ROOT` | `common/technology` |
| `COMPONENTS_DIR` | Component directory relative to `STELLARIS_ROOT` | `common/component_templates` |
| `BUILDINGS_DIR` | Building directory relative to `STELLARIS_ROOT` | `common/buildings` |
| `INLINE_SCRIPTS_DIR` | Directory containing `inline_script` templates, relative to `STELLARIS_ROOT` | `common/inline_scripts` |
| `SCRIPTED_EFFECTS_DIR` | Named-effect library relative to `STELLARIS_ROOT`, excluded from independent traversal | `common/scripted_effects` |
| `SCRIPTED_TRIGGERS_DIR` | Named-trigger library relative to `STELLARIS_ROOT`, indexed separately and excluded from independent traversal | `common/scripted_triggers` |
| `SCRIPTED_VARIABLES_DIR` | Static-variable library relative to `STELLARIS_ROOT`, read separately for substitution; excluded from independent traversal | `common/scripted_variables` |
| `SCRIPT_VALUES_DIR` | Calculation library relative to `STELLARIS_ROOT`, indexed separately and excluded from independent traversal | `common/script_values` |
| `WORKSHOP_DIR` | Absolute path to Stellaris Steam Workshop mods | `E:/SteamLibrary/steamapps/workshop/content/281990` |
| `RU_LOC_TIER_1` | Russian localization, highest priority: the Russian Localization Fix RE mod's `replace` directory | `${WORKSHOP_DIR}/681483874/localisation/replace` |
| `RU_LOC_TIER_2` | Russian localization, second priority: the same mod's `russian` directory | `${WORKSHOP_DIR}/681483874/localisation/russian` |
| `RU_LOC_TIER_3` | Russian localization, third priority: vanilla, relative to `STELLARIS_ROOT` | `localisation/russian` |
| `EN_LOC_TIER_1` | English localization: vanilla, relative to `STELLARIS_ROOT` | `localisation/english` |

`TECH_PATH`, `INLINE_SCRIPTS_DIR`, `SCRIPTED_EFFECTS_DIR`, `SCRIPTED_TRIGGERS_DIR`, `SCRIPTED_VARIABLES_DIR`, `SCRIPT_VALUES_DIR`, `RU_LOC_TIER_3`, and `EN_LOC_TIER_1` are relative to `STELLARIS_ROOT`. `${WORKSHOP_DIR}` in the other two paths denotes substitution of the variable with that name. This is a configuration-file convention: JSON stores ordinary strings and does not perform substitution itself. Paths use forward slashes `/`, consistent with the previously defined variables.

`INLINE_SCRIPTS_DIR` is used for inclusion expansion. For example, `script = technologies/rare_technologies_weight_modifiers` refers to `STELLARIS_ROOT/INLINE_SCRIPTS_DIR/technologies/rare_technologies_weight_modifiers.txt`. The directory is read-only. Templates selected by configuration are prepared into a shared library; reached calls, including nested ones, use its prepared plans.

Nested calls, argument substitution, and invocation history are implemented. Metadata is excluded from analytical traversal; the current representation is described in the [stage-nine guide](Docs/BACKEND_STAGE_9_EN.md).

During enrichment, Russian text is selected per key in the order `RU_LOC_TIER_1` → `RU_LOC_TIER_2` → `RU_LOC_TIER_3`, moving to the next source if the key is absent. English text for the same key comes from `EN_LOC_TIER_1`. Russian and English localization are treated separately; key availability is checked independently for each language.

Absolute source roots belong to the current environment. Game and localization directories are read-only; `WORK_DIR` is intended for writing output. The builder loads settings, expands inline calls, named effects, triggers, and script values, and substitutes static variables. The general tree builder does not require localization; the set coordinator then enriches all fifteen trees and publishes them together.

## Documents

- [Stage 15: parallel file processing and database merging](Docs/TZ_BACKEND_STAGE_15_EN.md).
- [Stage 15 implementation guide](Docs/BACKEND_STAGE_15_EN.md).
- [Stage 14: preparing and reusing libraries](Docs/TZ_BACKEND_STAGE_14_EN.md).
- [Stage 13: optimized validation, measurements and acceptance](Docs/BACKEND_STAGE_13_EN.md).
- [Approved stage 13 specification: validation and build optimization](Docs/TZ_BACKEND_STAGE_13_EN.md).

- [Stage 12: building and verifying fifteen databases](Docs/BACKEND_STAGE_12_EN.md).
- [Frontend 0.0.3: streaming set opening](Docs/frontend/FRONTEND_STAGE_3_EN.md).

- [Stage 12 specification: extended database set](Docs/TZ_BACKEND_STAGE_12_EN.md).
- [Frontend stage 3 specification: opening 15 databases](Docs/frontend/TZ_FRONTEND_STAGE_3_EN.md).
- [Stage 11: building three localized databases](Docs/BACKEND_STAGE_11_EN.md).
- [Frontend stage 2: set opening and upgrade data](Docs/frontend/FRONTEND_STAGE_2_EN.md).

- [First frontend: running, implementation, and checks](Docs/frontend/FRONTEND_STAGE_1_EN.md).

- [Initial interface: window layout, simple design, and UI kit — concept](Docs/frontend/CONCEPT_EN.md).
- [Initial interface UI element list](Docs/frontend/UI_ELEMENTS_EN.md).
- [Frontend technology stack specification: React, TypeScript, CSS, and Vite](Docs/frontend/TZ_TECH_STACK_EN.md).
- [Frontend structure specification: code, UI kit, configuration, and assets](Docs/frontend/TZ_STRUCTURE_EN.md).
- [Worker protocol specification: database opening, stages, result, errors, and cancellation](Docs/frontend/TZ_WORKER_PROTOCOL_EN.md).
- [Worker result specification: ready container, catalog, and representation identity — partial model](Docs/frontend/TZ_WORKER_RESULT_EN.md).
- [Technology requirements specification: prerequisites tree, counting, and links](Docs/frontend/TZ_TECHNOLOGY_REQUIREMENTS_EN.md).
- [Localization index record specification: states, provenance, and errors](Docs/frontend/TZ_LOCALIZATION_INDEX_EN.md).
- [Diagnostics specification: shared record, codes, and error response](Docs/frontend/TZ_DIAGNOSTICS_EN.md).
- [Diagnostic report saving specification: menu action and current attempt JSON](Docs/frontend/TZ_DIAGNOSTIC_REPORT_EN.md).
- [Stage ten: localization invocation, database format, and verification](Docs/BACKEND_STAGE_10_EN.md).
- [Stage ten specification: RU/EN names and descriptions in the database — implemented](Docs/TZ_BACKEND_STAGE_10_EN.md).
- [Backend stage 11 specification: three localized databases — draft for approval](Docs/TZ_BACKEND_STAGE_11_EN.md).
- [Frontend stage 2 specification: three-database set opening and object links — draft for approval](Docs/frontend/TZ_FRONTEND_STAGE_2_EN.md).
- [Stage nine specification: script value expansion — implemented](Docs/TZ_BACKEND_STAGE_9_EN.md).
- [Stage eight specification: effect and trigger expansion — implemented](Docs/TZ_BACKEND_STAGE_8_EN.md).
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
- [Stage-seven specification: static-variable substitution without replacement history — implemented](Docs/TZ_BACKEND_STAGE_7_EN.md).
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

- [Stage-seven backend: static variables and verification](Docs/BACKEND_STAGE_7_EN.md).

- [Stage-eight backend: mixed expansion and verification](Docs/BACKEND_STAGE_8_EN.md).

- [Stage-nine backend: script values, formats, and verification](Docs/BACKEND_STAGE_9_EN.md).
