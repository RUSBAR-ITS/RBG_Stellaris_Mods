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

The approved [stage-ten specification — localization in the database](Docs/TZ_BACKEND_STAGE_10_EN.md) is implemented. RU/EN names and descriptions reside beside technologies and variants in `enrichments.localization`. A separate operation expands static references, retains original text and sources, inherits missing descriptions, and safely updates the same database. Game trees and the general-purpose parser are preserved; possible reference-specific database cleanup remains a future stage.

The backend continues to expand inline insertions, named effects, triggers, and calculations, binding parameters and static variables. `script_value` nodes preserve calculation bodies and evaluation scopes; shared history preserves invocation provenance. Game conditions and arithmetic are not evaluated; no command profile is used.

The [current guide](Docs/BACKEND_STAGE_10_EN.md) describes operation and limitations. The verified enriched database is `data/stage10/database.json`, its report is `data/stage10/localization_report.json`, and the unenriched baseline is `data/stage10/database_unenriched.json`. Standard and previous outputs are preserved. Database format: `sttv.parse_database`, version 4; build report version: 5; localization report version: 1. Reading requires neither the game nor repeated expansion; older databases must be rebuilt before enrichment.

All 184 tests passed, including 30 new checks. Rebuilt 35 files, preserving 82,246 game nodes. Enriched 679 technologies and 206 variants: 885 names and 885 descriptions per language, including 81 inherited variant descriptions. All 3,540 fields, trees, and history were independently compared; repeated execution produces an identical database. No errors or warnings occurred. Database size: 140,937,166 bytes. Verification reports are under `data/stage10/`.

The stage-nine full audit had 1,466 successful inputs, two documentation exclusions, and 21 failing files. Causes and limitations remain in [its guide](Docs/BACKEND_STAGE_9_EN.md); reports and lists are under `data/stage9/`. Localization did not repeat a full-game traversal. Guides for stages 1–9 are historical.

The backend is in `src/backend/`. The first frontend, version `0.0.1`, is implemented in `src/frontend/` using React, TypeScript, plain CSS, Vite, and prepared database processing in a Web Worker. It includes RU/EN, two themes, variants, scrolling, opening states, and diagnostic reports. Connecting lines are not drawn yet. The build, 16 unit scenarios, and 10 browser scenarios were checked; the [guide](Docs/frontend/FRONTEND_STAGE_1_EN.md) describes results and limitations. A Python service, images, and portable packaging remain future stages; PyInstaller `onedir` is agreed for portable distribution.

## Running the frontend

From `WEB_STTV` with Node.js 24 installed: `npm ci`, then `npm run dev`. The address is `http://127.0.0.1:5173/`. This computer also has a local Node.js copy under `data/`; the exact command without a system installation is in the [guide](Docs/frontend/FRONTEND_STAGE_1_EN.md#running).

Click Open database and select `data/stage10/database.json`. Startup and page refresh neither invoke the generator nor automatically open a database. State does not persist between sessions.

## Directory structure

| Path | Purpose |
| --- | --- |
| `src/frontend/` | Interface code |
| `src/backend/` | Python processing and subsequent local-service code |
| `config/` | Sources, output paths, eight parser configurations, and a separate localization configuration |
| `schemas/` | Thirteen generated configuration, database, and report schemas |
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

`INLINE_SCRIPTS_DIR` is used for inclusion expansion. For example, `script = technologies/rare_technologies_weight_modifiers` refers to `STELLARIS_ROOT/INLINE_SCRIPTS_DIR/technologies/rare_technologies_weight_modifiers.txt`. The directory is read-only; templates are loaded through reached calls, including nested ones.

Nested calls, argument substitution, and invocation history are implemented. Metadata is excluded from analytical traversal; the current representation is described in the [stage-nine guide](Docs/BACKEND_STAGE_9_EN.md).

During enrichment, Russian text is selected per key in the order `RU_LOC_TIER_1` → `RU_LOC_TIER_2` → `RU_LOC_TIER_3`, moving to the next source if the key is absent. English text for the same key comes from `EN_LOC_TIER_1`. Russian and English localization are treated separately; key availability is checked independently for each language.

Absolute source roots belong to the current environment. Game and localization directories are read-only; `WORK_DIR` is intended for writing output. The builder loads settings, expands inline calls, named effects, triggers, and script values, and substitutes static variables. It does not require localization directories; names and descriptions are added by a separate operation on a completed database.

## Documents

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
