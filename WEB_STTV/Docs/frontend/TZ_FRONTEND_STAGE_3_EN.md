# Stellaris Technological Tree View — frontend stage 3 specification: opening 15 databases

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Opening and state](#2-opening-and-state)
- [3. Worker preparation](#3-worker-preparation)
  - [Approved addition: streaming JSON](#approved-addition-streaming-json)
- [4. Addressing and catalogs](#4-addressing-and-catalogs)
- [5. Localization](#5-localization)
- [6. Diagnostics and configuration](#6-diagnostics-and-configuration)
- [7. Verification and acceptance](#7-verification-and-acceptance)
- [8. Related documents](#8-related-documents)

## 1. Status and scope

Approved by the user on 2026-11-18. Implementation and acceptance checks are complete. The complete published set opened successfully in the built interface; results are recorded in the [stage guide](FRONTEND_STAGE_3_EN.md). The user agreed to open the complete 15-database set and localize new objects in RU/EN. [Backend stage 12](../TZ_BACKEND_STAGE_12_EN.md) defines membership and preparation rules.

This stage extends loading, addressing, catalogs and the shared localization index. The technology field retains its current presentation. New object screens, lines, functional technology classification, new chain rules and evaluation of game conditions are outside scope.

Once approved, this specification replaces stage-two requirements for three files, allowed roles and retaining all full trees in the Worker. Other agreed UI behavior remains in force.

## 2. Opening and state

One “Open database set” button invokes a multiple-file picker. The user selects exactly 15 JSON files in any order and with arbitrary filenames. Required roles come from shared `config/datasets.json`; each file declares its role in `dataset.kind`.

Acceptance conditions:

- `format = sttv.parse_database`, `format_version = 6`.
- Exactly one file for every agreed role, with no missing, duplicate or unknown roles.
- One shared nonempty SHA-256-shaped `set_id`.
- Data required by current adapters and indexes are available.

The aggregate build report is not a set member. Do not substitute older files or open incomplete sets. Do not discover neighboring files automatically. Checking `set_id` does not mean recomputing all database hashes in the browser.

Application startup and page refresh do not open files, invoke generation or access game sources. Closing the picker without selection preserves the current screen. After a new selection, release the previous operation and field according to the existing replacement model.

Retry uses the same 15 selected `File` objects; cancel terminates the Worker and restores the initial state. Ignore obsolete `operationId` responses. Errors never publish a partial field. Send one `ready` only after preparing the complete set.

## 3. Worker preparation

Keep `reading`, `parsing`, `preparing` phases and current-file/total progress. Counters and messages must not hardcode three. Display dataset names through UI localization.

Process files sequentially: read → parse JSON → check metadata → adapt required data. Release source text after parsing and the full tree after extracting that member's compact data. Do not retain 15 full ASTs and their text copies simultaneously. The main thread receives only catalogs, localization, existing links, set information and diagnostics.

Finalize cross-file checks for existing adapters after all members are processed. Selection order must not affect the result: a required technology may be read after its building. Keep current component/building `objectRequirements`, `objectUpgrades` and `upgradeEvidence`; do not extend them to new kinds without agreed domain rules.

The Worker retains selected `File` references and node addresses. Releasing an AST does not remove data from its source JSON. A future detailed-tree viewer can reread the corresponding file; that viewing mechanism is not implemented now. Extract conditions and variants required by the current interface before releasing the tree.

An individual file may still be large. Measure time, sizes and available memory metrics in real testing, particularly for `events.json`. Do not claim volume support without successfully opening the full set. If normal JSON parsing of one member exceeds runtime limits, record a blocker and separately agree changes to representation or reading; never silently exclude events or accept a partial set.

### Approved addition: streaming JSON

The user approved streaming reads after the formatted component file of 871,070,973 bytes caused `File.text()` to return an empty string in Chromium 159.0.8154.6. The Worker decodes a UTF-8 byte stream and parses JSON chunks without constructing a string for the entire file.

The first pass extracts set metadata and the document count without retaining game trees. The second pass feeds documents individually to the adapters, preserving original JSON Pointer indices. It retains adapter-consumed fields and localization; expansion metadata, coordinates, and game fields unused by the UI remain in the source file. Compact catalogs accumulate, and cross-object references are checked after reading the complete set. JSON property order is not restricted to metadata appearing first.

Parsing checks JSON structure across chunk boundaries inside strings, Unicode, and numbers. An incomplete or malformed late fragment fails without a partial `ready`. Cancellation terminates the Worker and its read. These changes preserve the database format, do not invoke generation, and do not remove data from files.

## 4. Addressing and catalogs

Extend qualified node references `{database, pointer}`: `database` is one of 15 roles and `pointer` is a JSON Pointer within its file. Store one `setId` on the overall result. Qualify internal enrichment references with the owning role during adaptation.

Add compact definition catalogs for new kinds. Each record contains its root definition reference, construct type, game ID where available, and references/IDs of available localized texts. Preserve source order in record lists; game-ID indexes are separate and do not replace lists. Do not copy full effect/event bodies into `ready`.

Existing technology, component and building catalogs retain fields required by the UI. New kinds need not masquerade as technologies or supply `tier`, `area`, `nameId`, `descriptionId` or technology requirements when these do not exist.

- Event identity comes from `id`; keys such as `country_event` are types. Index every description at its own address without selecting an active variant.
- `terraform_link` has no game ID: address it using `{database, pointer}`, retain `from`/`to` and their localization references. Do not merge equal planet-class pairs.
- For repeated `on_actions` fragments, the name index leads to an array of definitions. Do not select a fragment or execute the handler.
- Check duplicate IDs for named singleton objects within their own kind. Equal IDs in different kinds are valid.
- Directives, variables, expansion metadata and localization nodes are not separate game objects.

References and catalogs prepare future analysis; this stage does not build a new action → handler → event behavioral graph.

## 5. Localization

Extend the shared `database` text-source index with all 15 databases. Keep the UI-text contract: source, string ID, system language. Do not introduce a text source per dataset kind.

Backend rules determine whether targets have names, descriptions, or both. Inapplicable text roles may be absent for hidden events or technical handlers. A missing translation for a selected key is a warning; missing required enrichment for a declared target is a preparation error.

Include targets on `title`, `desc`, nested description texts, `activity_key`, `from`/`to` and roots according to configuration and persisted enrichments. Traversal must not turn raw strings in expansion metadata into duplicate targets.

Index saved `requested_key` values. Matching text for one key/language combines origins; conflicting found text is an error identifying both sources. Qualify `recordRef`, inheritance and other node references with their database role. Do not resolve strings again, evaluate conditions or format game markup. RU/EN switching uses prepared indexes.

## 6. Diagnostics and configuration

Use the shared role registry for file selection, metadata, diagnostics and counters. Individual adaptation and textual-role rules remain declarative. Do not duplicate opening logic per kind. Generated schemas agree with the backend.

Wrong-file-count messages include actual and expected counts; technical reports identify missing/duplicate roles, filename, phase and qualified address where available. Dataset labels reside in UI dictionaries. Keep diagnostic JSON export with line breaks and two-space indentation.

Frontend checks set contracts and consumed data without repeating complete backend AST validation, call expansion or game-command semantic validation.

## 7. Verification and acceptance

1. Open a fixture set in different orders and with arbitrary filenames; results are identical. Cover every kind and same IDs/node paths in different databases.
2. Test 14/16 files, duplicate/unknown roles, a report instead of a database, version 5, mixed `set_id`, malformed JSON and missing consumed data. No partial `ready` is sent.
3. Cover name-only/description-only enrichment, conditional event descriptions, zero text targets, terraforming endpoint localization, string conflicts and all origins.
4. Verify repeated transitions and handler fragments, real ID uniqueness, no invented game ID for `terraform_link`, and no false technology requirements.
5. Verify cancel, retry, replacement, stale Worker replies and progress on late files. No full ASTs enter the main thread; previous full trees do not accumulate in the Worker.
6. Open the complete real set built by stage 12 using formatted JSON. Record browser, total/maximum file size, duration and available memory metrics. Small-fixture loading is not a full-set validation claim.
7. Regress technologies/variants, both languages, themes, tooltips, menu, status and existing component/building links. New chains or sorting must not appear implicitly.
8. Update guides, messages, RU/EN changelogs and the interface version under existing rules. Keep code modular and reuse parsing/indexing logic. Portable distribution remains separate.

## 8. Related documents

- [Backend stage 12](../TZ_BACKEND_STAGE_12_EN.md).
- [Previous frontend stage](TZ_FRONTEND_STAGE_2_EN.md).
- [Worker result](TZ_WORKER_RESULT_EN.md).
- [Technology chain rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [Русская версия](TZ_FRONTEND_STAGE_3_RU.md).
