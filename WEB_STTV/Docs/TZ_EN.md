# Stellaris Technological Tree View — technical specification

## Contents

- [Document status](#document-status)
- [Organizing specifications by stage](#organizing-specifications-by-stage)
- [1. Languages and technical foundation](#1-languages-and-technical-foundation)
- [1.1. Selected technologies](#11-selected-technologies)
- [1.2. Responsibility boundaries](#12-responsibility-boundaries)
- [1.3. Types and data format](#13-types-and-data-format)
- [1.4. Launch and portable distribution](#14-launch-and-portable-distribution)
- [1.5. Planned validation](#15-planned-validation)
- [1.6. Decisions for subsequent parts](#16-decisions-for-subsequent-parts)
- [2. Project structure and coding principles](#2-project-structure-and-coding-principles)
- [2.1. Directories and working folder](#21-directories-and-working-folder)
- [2.2. Modularity and configuration](#22-modularity-and-configuration)
- [2.3. File size](#23-file-size)
- [3. First backend stage — database building](#3-first-backend-stage--database-building)
- [3.1. Goal and stage boundaries](#31-goal-and-stage-boundaries)
- [3.2. Inputs and settings](#32-inputs-and-settings)
- [3.3. Responsibility separation](#33-responsibility-separation)
- [3.4. Source reading and parsing](#34-source-reading-and-parsing)
- [3.5. Strict model construction](#35-strict-model-construction)
- [3.6. Technology names](#36-technology-names)
- [3.7. Validation and diagnostics](#37-validation-and-diagnostics)
- [3.8. Saving and rebuilding](#38-saving-and-rebuilding)
- [3.9. Invocation and implementation deliverables](#39-invocation-and-implementation-deliverables)
- [3.10. Acceptance criteria](#310-acceptance-criteria)

## Document status

Approved and implemented [backend stage 17](TZ_BACKEND_STAGE_17_EN.md) and [frontend stage 4](frontend/TZ_FRONTEND_STAGE_4_EN.md): manifests, separate documents, object indexes, verification on read and full audit. Current instructions are in the [backend guide](BACKEND_STAGE_17_EN.md) and [frontend guide](frontend/FRONTEND_STAGE_4_EN.md). Earlier formats and launch procedures below are historical.

Approved and implemented [stage 16 — technology parent and child enrichment](TZ_BACKEND_STAGE_16_EN.md): a Python operation using prepared databases, 13 configurable criteria, named combinations, variants and separate input/result revisions. All 679 base decisions matched the analytical reference. See the [guide](BACKEND_STAGE_16_EN.md) for running and verification; grid layout and frontend integration remain subsequent stages.

Implemented and verified the approved [stage 15 — parallel file processing](TZ_BACKEND_STAGE_15_EN.md): ten workers within one database, validation before intermediate JSON writing, streaming merging and identity derived from document hashes. All three complete builds match; see the [implementation guide](BACKEND_STAGE_15_EN.md).

Implemented [stage 14 — reusable element library](TZ_BACKEND_STAGE_14_EN.md) provides persistent library JSON, configured paths and sources, explicit `--rebuild-libraries` and `--reuse-libraries` modes, freshness verification and prepared template reuse. Both modes passed full acceptance; results are in the [guide](BACKEND_STAGE_14_EN.md). Stage 15 builds on this library mechanism.

Approved and implemented: [stage 13 — validation and build optimization](TZ_BACKEND_STAGE_13_EN.md): direct node-type dispatch, preparing rules once, a shared traversal and document processing. The complete build became 2.66 times faster while all databases remained byte-identical. Results and measurement boundaries are in the [stage 13 guide](BACKEND_STAGE_13_EN.md).

Approved and implemented: [backend stage 12](TZ_BACKEND_STAGE_12_EN.md) and [frontend stage 3](frontend/TZ_FRONTEND_STAGE_3_EN.md): fifteen localized databases, formatted JSON and streaming set opening. Current results are in the [stage 12 guide](BACKEND_STAGE_12_EN.md) and [frontend guide](frontend/FRONTEND_STAGE_3_EN.md).

Approved and implemented: [backend stage 11](TZ_BACKEND_STAGE_11_EN.md) and [frontend stage 2](frontend/TZ_FRONTEND_STAGE_2_EN.md): three localized databases, joint opening and explicit upgrade data. Their historical invocation and formats are in the [backend guide](BACKEND_STAGE_11_EN.md) and [frontend guide](frontend/FRONTEND_STAGE_2_EN.md). Version-four formats and single-file opening below are historical.

The [stage-ten specification — localization in the database](TZ_BACKEND_STAGE_10_EN.md) is approved and implemented. RU/EN names and descriptions reside beside objects in the same database, with static references and variant description inheritance. Current formats, invocation, and verification are in the [stage-ten guide](BACKEND_STAGE_10_EN.md).

The [stage-nine specification — script value expansion](TZ_BACKEND_STAGE_9_EN.md) is approved and implemented. Historical formats, architecture, and results: [stage-nine guide](BACKEND_STAGE_9_EN.md).

The preceding effect/trigger expansion stage remains documented in the [stage-eight specification](TZ_BACKEND_STAGE_8_EN.md) and [its historical guide](BACKEND_STAGE_8_EN.md).

**Concept change dated 2026-11-15.** The [new direction](CONCEPT_EN.md#internal-data) saves parsing results as JSON and enriches them through separate actions in later stages. The previous model and implemented requirements remain documented below; they do not constrain the new format. The transition is implemented in stage six: [transition guide](BACKEND_STAGE_6_EN.md). Static-variable substitution is documented in the [historical stage-seven guide](BACKEND_STAGE_7_EN.md). The stage-one domain model below remains historical; shared development principles still apply.

Project: **Stellaris Technological Tree View**, directory: `WEB_STTV`.

**On 2026-11-15, the user approved the first backend stage and authorized implementation.** Section 1 describes the complete product's technical foundation, section 2 its structure and general coding principles, and section 3 the approved scope of the first backend stage.

The first stage is implemented and validated. This document builds on the [concept](CONCEPT_EN.md) and [database model](DATABASE_MODEL_EN.md). The builder, configuration, and schemas are present; operation, implementation boundaries, and validation results are documented in a [separate guide](BACKEND_STAGE_1_EN.md). The UI and portable distribution remain for subsequent stages.

## Organizing specifications by stage

Each subsequent stage is documented as a separate pair of files in `Docs/`, with `_RU` and `_EN` suffixes. Names identify the area and stage number, for example `TZ_BACKEND_STAGE_2_RU.md` and `TZ_BACKEND_STAGE_2_EN.md`.

A stage specification contains its status, goal, boundaries, requirements, and acceptance criteria. Shared principles, the technical foundation, and data models are referenced through links to the relevant documents and sections rather than copied. Stage requirement changes are reflected in both language versions; approval applies to the specific stage specification.

The current document retains shared decisions and the already drafted first backend stage. Subsequent stages are not appended here as large sections: links to their separate specifications are added to the README document list.

## 1. Languages and technical foundation

The main programming languages are **Python and TypeScript**. HTML and CSS provide interface structure and styling. JSON is the format for the internal database and structured data exchange. The portable Windows distribution is packaged using **PyInstaller in one-folder mode (`onedir`)**.

### 1.1. Selected technologies

| Application part | Technology | Responsibility |
| --- | --- | --- |
| Initial information collection | Python | Read selected directories directly, pass data in memory, and retain provenance |
| Information transformation | Python | Parse game syntax, resolve variables and references, apply localization priorities, build relationships, and prepare the database and images |
| Local service | Python | Manage source settings, initiate collection and rebuilding, and provide prepared data to the interface |
| Interactive interface | TypeScript | The tree, cards, zooming, panning, and technology selection |
| Markup and styling | HTML + CSS | Card and panel structure, images, colors, and element arrangement |
| Storage and data exchange | JSON | The internal database and structured messages between application parts |
| Windows packaging | PyInstaller, `onedir` | An executable, bundled Python, dependencies, and built interface files in one directory |

### 1.2. Responsibility boundaries

The initial interface tool selection is refined in the [separate technology stack specification](frontend/TZ_TECH_STACK_EN.md): React and TypeScript, plain CSS, Vite, React's built-in state facilities, and independent database processing modules in a Web Worker.

The three processes from the concept remain separate: reading source information, transformation into the database, and presentation. Reading and transformation are distinct Python stages passing data in memory. No source copy or persistent intermediate snapshot is created. A future local service will connect the builder to the user interface.

Python reads game sources and produces the prepared semantic model of technologies: definitions, relationships, prepared text, and provenance. Parsing game-file syntax belongs to this part; JSON describes prepared data and is not an assumption about the format of original game scripts.

TypeScript receives the prepared model and handles presentation and user interaction. Game variables, localization priorities, and source references are resolved during database preparation in Python. Card placement on screen and handling user actions belong to the interface.

Browsing uses the completed database and prepared images. Collection and transformation are triggered separately from ordinary card viewing. Original game directories are read-only.

### 1.3. Types and data format

Interactive interface code is written in TypeScript and transformed into JavaScript for execution in the browser. Types describe technologies, relationships, sources, and processing states; type checking helps detect inconsistent field usage during development. [TypeScript documentation](https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html).

TypeScript type checking does not replace validation of loaded JSON contents. The first database requires a machine-readable schema and contextual checks under section 3. Future interface message formats and a specific validation library have not been selected yet.

The Python side uses the standard `json` module for reading and writing JSON. The first database is one JSON file following the [data model](DATABASE_MODEL_EN.md); diagnostics are stored in a separate report. There is no persistent intermediate snapshot. Image preparation belongs to later stages. [Python documentation](https://docs.python.org/3/library/json.html).

### 1.4. Launch and portable distribution

This section describes the future user distribution. Portable packaging is deferred for the first frontend stage: the interface is tested from the development environment, and a prepared database is opened only through explicit user action under the [startup and database opening specification](frontend/TZ_DATABASE_OPENING_EN.md). File API reading and the TypeScript adapter run in a browser Web Worker; viewing does not require a Python service. Database generation and enrichment remain separate Python processes, independent of interface startup and page refresh.

The target platform is Windows. The user extracts the application directory and runs its `.exe`. The executable starts the local Python service and opens the prepared web interface in a browser.

The distribution contains the Python interpreter, required dependencies, and built interface files. Users do not need a separate installation of Python, a web server, or interface build tools. PyInstaller supports bundling Python and its dependencies in this way; `onedir` is the selected mode. [PyInstaller documentation](https://pyinstaller.org/en/stable/operating-mode.html#bundling-to-one-folder).

Settings reside in the application directory; working data resides in configurable `WORK_DIR`, defaulting to `data` within the application. Internal references use relative paths. External sources are selected by the user and may need to be selected again after moving the application. Browsing an existing database together with its future images remains independent of access to original directories.

The initial user distribution has an empty database and offers source setup. Development and build tools are used when preparing the distribution; the user runs the completed application.

### 1.5. Planned validation

Implementation of this part includes the following planned checks:

1. TypeScript type checking and successful compilation of the interface into browser-executable files.
2. Responsibility separation: game definitions and localization are processed in Python, and the interface receives prepared data.
3. JSON writing and reading, followed by separate validation of structure and required fields once the schema is defined.
4. Launching the completed Windows distribution without separately installed Python, a web server, or interface build tools.
5. Moving the application directory with its completed database and images: checking internal paths and browsing while original game directories are unavailable.

These are planned checks for the complete product. JSON reading, writing, and schema validation passed in the first backend stage; the interface and portable distribution have not been created or tested. Remaining scenarios will be refined after the remaining specification parts are defined.

### 1.6. Decisions for subsequent parts

- Further tools for displaying and laying out links; React and Vite for the initial interface are already selected in a separate specification.
- Card design, technology details, navigation, and other interface features.
- The local service library, data exchange commands, and processing progress presentation.
- Image preparation tools and further source expansion.
- Future interface message formats and database model extensions after the first stage.
- Specific Python, React, TypeScript, Vite, PyInstaller, and dependency versions; interface build configuration.
- Supported Windows versions and architectures, browsers, and local service lifecycle.

Remaining components and details are discussed separately. Agreed initial interface decisions are refined by documents under `Docs/frontend/`.

## 2. Project structure and coding principles

### 2.1. Directories and working folder

| Path relative to `WEB_STTV` | Purpose |
| --- | --- |
| `src/frontend/` | Future interface code |
| `src/backend/` | Python code: builder, data processing, and subsequent local service |
| `data/` | Default working folder: database, reports, temporary output, and validation materials |
| `Docs/` | Bilingual documentation |
| `global_variables.json` | Shared project variables, including sources and `WORK_DIR` |
| `config/` | Configurable processing parameters; created during implementation |
| `schemas/` | Declared structures and data validation rules; created during implementation |

`WORK_DIR` initially equals `"data"`. A relative path is resolved against the project/product directory, not the terminal's current directory. An absolute path is also allowed. Changing `WORK_DIR` selects the location of subsequent builds and checks; existing files are not automatically moved or deleted.

The database, reports, and temporary build files reside within the permitted working folder. During agent work, this folder must remain inside the repository. Normalized final paths are checked before writing: output must not target source directories or escape the working folder. Game and Workshop files are always read-only.

The root `.gitignore` contains `/WEB_STTV/data/`. A different working folder requires a separately configured ignore rule; the application performs no Git operations. Existing research materials in `TMP/WEB_STTV/` are not moved and do not become product inputs.

### 2.2. Modularity and configuration

- Code must be modular, extensible, and maintainable. Each module has a clear responsibility; extending one stage should not require rewriting the others.
- Extract repeated logic into shared functions and helpers, following DRY. Group helpers by purpose; avoid a miscellaneous file of unrelated functions and abstractions without a current need.
- Store configurable paths, source ordering, reading parameters, and output filenames in separate configuration files. Do not duplicate paths or parameters in code or hardcode a particular machine's directories.
- Allowed data structures and supported constructs are declared separately from user settings. A setting must not permit unknown fields or disable mandatory schema validation.
- Code, comments, and field names are written in English. Russian technology names remain localization data.
- Do not introduce old-format compatibility, fallback mechanisms, or dependencies unnecessary for this stage.

### 2.3. File size

The target for an ordinary code file is **up to 200 lines**. Physical lines, including comments and blank lines, are counted; the rule also applies to test code.

- **201–300 lines:** review the structure and identify independent parts or repeated operations worth extracting. This is a review threshold rather than a requirement to fragment a cohesive function artificially.
- **More than 300 lines:** extract independent parts into modules or helpers.
- An exception is allowed when a large block cannot reasonably be divided into functional components. Document the specific reason; large files are not automatically exceptions.

Do not reduce line counts by compressing expressions or impairing readability. Documentation, JSON schemas, and game data are not code files and are not split solely to meet this limit.

## 3. First backend stage — database building

### 3.1. Goal and stage boundaries

The stage delivers a runnable Python builder that reads configured sources and produces the first JSON database version under `DATABASE_MODEL_EN.md`, plus a separate report. The builder operates independently and supports later invocation from a local service.

Game definition inputs are limited to `TECH_PATH`: base `*.txt` files, `category/*.txt`, `tier/*.txt`, and local variables from these files. Localization supplies only Russian and English technology and variant names.

This stage excludes the interface, HTTP service, images, `.exe` packaging, save-game reading, modded technology overrides, and game definitions from other directories. Resolving references inside localization text and localizing descriptions also remain outside scope.

### 3.2. Inputs and settings

Shared variables are read from `global_variables.json`: `WORK_DIR`, `STELLARIS_ROOT`, `TECH_PATH`, `WORKSHOP_DIR`, `RU_LOC_TIER_1`, `RU_LOC_TIER_2`, `RU_LOC_TIER_3`, and `EN_LOC_TIER_1`. Their values are not duplicated in another configuration file.

Implementation creates `config/backend.json` with build parameters:

- Reading profiles: named input variables, relative subdirectories, file patterns, recursion, encoding, and expected localization language.
- Russian source order `RU_LOC_TIER_1` → `RU_LOC_TIER_2` → `RU_LOC_TIER_3`; separate English source `EN_LOC_TIER_1`.
- Output paths relative to `WORK_DIR`: default `database.json` and `reports/build_report.json`.

Technologies are read from the three specified directories without a general recursive game scan. Each localization directory is searched for `*.yml`, including subdirectories. Reading uses UTF-8 with BOM support; decoding errors are reported without replacing damaged characters. Changing a source profile does not automatically support a new data kind.

`${NAME}` substitution uses declared variables without executing code. Unknown names, circular references, invalid setting types, or unavailable selected directories are preparation errors. `TECH_PATH`, `RU_LOC_TIER_3`, and `EN_LOC_TIER_1` are relative to `STELLARIS_ROOT`; `WORK_DIR` is relative to the product directory. A missing localization key differs from an inaccessible directory: an unavailable source must not be silently skipped.

### 3.3. Responsibility separation

Modules within `src/backend/` separate the following responsibilities; individual files follow section 2:

| Part | Responsibility |
| --- | --- |
| Settings and sources | Validate configuration, resolve paths, select files, and read only permitted sources |
| Game-script parser | Parse syntax while retaining order, repetitions, and source positions |
| Model conversion | Handle declared fields and commands, local variables, requirements, and variants |
| Localization | Parse entries and select names by key and priority |
| Data validation | JSON schema, contextual restrictions, and relationships between records |
| Storage and reporting | Write validated output and diagnostics within `WORK_DIR` |
| Build orchestration | Invoke stages sequentially and return status without duplicating their logic |

Reading and transformation exchange data in memory. Separate OS processes, a persistent source cache, and repeated full-game scans are unnecessary. Sources are reread on an explicit new build rather than when viewing output.

### 3.4. Source reading and parsing

Files are traversed in a reproducible order by relative path. The parser retains definition IDs, files and lines, nesting, operators, scalar tokens, element order, and repeated assignments. Comments and quotes are handled as syntax: a comment marker inside a string must not truncate its value. Syntax errors must not silently discard definitions.

The initial parse tree exists only in memory and is not the working database model. An arbitrary syntactically valid field in it is not yet supported. Source `.txt` and `.yml` files are not copied into the working folder; no persistent parse snapshot is written either. A report may include a small fragment of the problematic line for diagnostics.

### 3.5. Strict model construction

The normative reference is the [first database model](DATABASE_MODEL_EN.md). Its `format_version` is `1`; technology records have `source`, `name`, `name_sources`, and `fields`. Conditional variants are nested in `fields.technology_swap`; no separate `parent_id` is created.

Implementation must provide `schemas/database.schema.json` and explicitly declared rules for nested commands: contexts, scopes, operators, arguments, types, and cardinalities. Rules must cover the examined supported constructs; this is a verifiable deliverable, not permission to accept everything encountered automatically. Unknown fields, commands, and invalid forms are errors with separate diagnostics. The schema is closed at every level, including `ScriptBlock` and union alternatives.

Conversion preserves every supported value, including explicit empty, zero, and false values, repetitions, and source order. Absent fields do not receive assumed defaults. Conflicting repetitions are retained through `RepeatedValue` under the model and noted in the report; no arbitrary value is chosen.

Only results unambiguously derivable from declared inputs are computed: local numeric chains within one file, the logical structure of `prerequisites`, and verifiable technology, category, and known-tier references. Derived relationships may be built in memory for validation without introducing extra database collections. No external definitions are read, and no research-audit values are substituted.

Unresolved local references, ambiguity, and variable cycles retain `resolved: null` with diagnostics under the model. Known external references are retained only in their declared form. `potential`, `starting_potential`, weights, and variant triggers remain distinct; they must not become extra predecessor requirements or be assumed to hold.

### 3.6. Technology names

After parsing definitions, collect the required keys: base technology IDs and variant `name_key` values. Handle each language independently. Select only names, retaining the key, source, file, and line.

Follow model rules: per-key priority, fallback only when a key is absent, explicit empty strings remain empty, and missing names and provenance are `null`. Do not substitute identifiers, another language, or newly written translations. Preserve markup, grammar markers, references, and control sequences without evaluation.

Identical duplicates in the selected source produce deterministic provenance by path and line; conflicting values of a selected key within one tier are an error. Check the file's language header. A missing translation is a model-permitted warning rather than a reason to discard the technology.

### 3.7. Validation and diagnostics

The JSON schema checks fields, types, requiredness, allowed values, and absence of extra properties. Separate checks cover contextual commands, unique IDs, reference correctness, `all` / `any` groups, the requirement graph, variants, and name provenance. Cycle checks do not extend to every technology mention inside arbitrary conditions.

The report contains final status, processed file, technology, and variant counts, error and warning counts, and a diagnostic list. Each diagnostic contains severity, a stable code, stage, description, and, when available, source name, relative file path, line, definition ID, and problematic field path. Unavailable information is explicitly absent or `null` according to the declared report structure. The report has its own validated schema; these fields are not added to the database.

Configuration, reading, syntax, unknown-construct, and schema errors, duplicate base IDs, and broken internal references prevent a successful build. Model-permitted missing names, unresolved references, and retained repetitions are reported separately rather than treated as errors solely for having an allowed form. Unexpected errors must not be masked by empty values or a successful status.

### 3.8. Saving and rebuilding

Each build rereads selected sources completely and constructs new output. Path or priority changes apply to the next run. The previous database is not a source of missing data and does not supplement new inputs.

New JSON is written to a temporary file within `WORK_DIR`, read back, and validated before replacing the working database. Errors before replacement leave the previous database unchanged. A failed first build must not substitute partial output for an absent database. The temporary file is placed beside the target; replacement must prevent observing a partially written database. Report-writing failures are also surfaced to the caller rather than hidden.

A successful database is saved as UTF-8 with reproducible output order. Identical inputs and settings produce an identical database file. Timestamps and build progress belong in the report. Sources are required for rebuilding; a completed database can be read and schema-validated while the game is unavailable.

### 3.9. Invocation and implementation deliverables

Initial build invocation uses a Python command from `src/backend/`, accepting shared-variable and processing-configuration files. Exit code `0` means success; a nonzero code means failure. A shared build function returns a structured result and is called by this command; conversion logic does not depend on a terminal or future web server.

Implementation deliverables are modular backend code, processing configuration, the database schema and command rules, a report schema, checks, and bilingual launch instructions. The database and report are created in `WORK_DIR`. At this stage, `src/frontend/` remains the location for subsequent interface development.

Research scripts in `TMP/WEB_STTV/` are validation materials rather than product dependencies. Specific dependencies and versions are recorded when preparing implementation and must be necessary for this scope. Shipping the portable application and performing section 1's interface checks are not completion criteria for this stage.

### 3.10. Acceptance criteria

1. The builder obtains all paths and configurable parameters from configuration. Check relative and absolute `WORK_DIR`, invocation from another current directory, substitutions, invalid settings, and inaccessible sources.
2. Verify unchanged sources and absence of source copies in the working folder. Reject source writes caused by invalid output-path settings.
3. Small control datasets cover strings, comments, nesting, operators, variables, repetitions, and syntax errors without losing source positions.
4. The database matches its declared schema; unknown fields or nested commands, invalid types, and extra properties produce diagnosed errors. Nested-command support is explicitly listed and tested.
5. Check local variable chains, external and cyclic references, `all` / `any`, absent and empty values, `RepeatedValue`, variants, and inter-record references.
6. Check both languages, priorities, incomplete translations, empty strings, identical and conflicting duplicates, BOM, and preserved markup. The database contains no localized descriptions.
7. Build from the current sources and compare the definition inventory against input files. Research counts of 679 technologies and 206 variants are references for that same file set, not program constants.
8. Rebuilding identical sources produces an identical database. A changed source or priority appears after rebuilding; previous-build data is not mixed in.
9. Verify preservation of the previous database after a pre-replacement error, a correct report, a nonzero failure code, and reading the completed database without sources. Write scenarios use the permitted working folder.
10. Review module separation, repeated logic, absence of configurable constants in code, and file sizes under section 2. List justified exceptions separately.

First-stage criteria were checked on 2026-11-15: 29 synthetic scenarios, a current-source build, inventory and value comparison, reproducibility, and source integrity. Details are listed in the [validation results](BACKEND_STAGE_1_EN.md#validation). Synthetic checks do not establish game-engine behavior.

[ТЗ на русском](TZ_RU.md) · [Project overview](../README_EN.md).
