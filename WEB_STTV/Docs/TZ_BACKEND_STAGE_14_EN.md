# WEB_STTV — backend stage 14: reusable element library

## Contents

- [1. Status and objective](#1-status-and-objective)
- [2. Existing implementation](#2-existing-implementation)
- [3. Contents and scope](#3-contents-and-scope)
- [4. Library configuration](#4-library-configuration)
- [5. Invocation modes](#5-invocation-modes)
- [6. Persistent representation](#6-persistent-representation)
- [7. Template preparation and application](#7-template-preparation-and-application)
- [8. Freshness and persistence](#8-freshness-and-persistence)
- [9. Integration and invocation state](#9-integration-and-invocation-state)
- [10. Validation and diagnostics](#10-validation-and-diagnostics)
- [11. Measurements and acceptance](#11-measurements-and-acceptance)
- [12. Implementation structure](#12-implementation-structure)
- [13. Related documents](#13-related-documents)

## 1. Status and objective

**Approved by the user on 2026-11-18. Implementation and acceptance are complete; commands, measurements and limitations are in the [stage guide](BACKEND_STAGE_14_EN.md).**

Prepare a reusable Stellaris element library persisted as JSON. Use it in memory while expanding primary documents to reduce repeated reading, parameter discovery and parsing of unchanged insertion fragments. One library snapshot serves all members of a build with identical inputs and settings.

The user has agreed to JSON persistence between runs, separate switches for rebuilding and reusing libraries, and configuration of library contents, addresses and adjustable parameters. The concrete contracts below were approved with this specification.

Parallel execution belongs to a subsequent stage. This stage establishes a suitable boundary between immutable definitions and per-document processing state. No speedup is promised in advance.

## 2. Existing implementation

- `script/inlining/loader.py` already caches inline file text in memory. A file is not reread for every invocation within one context.
- `sources/scripted.py` reads effect, trigger and value definitions and builds an index. Each definition body remains available as source text with coordinates and an environment.
- `script/inlining/expansion.py`, `script/scripted/expansion.py` and `script/values/expansion.py` invoke `parse_source()` again after substitution for every call body. Substitution also repeats lexical scans.
- `database/collection.py` creates a new expansion context for each dataset member; libraries and shared variables are prepared again for the next database.
- Since stage 13, output documents are processed, enriched, validated and written individually without retaining the entire database. Preserve this workflow and the absence of repeated complete audits.

Merely storing source text in JSON does not satisfy this task: prepared structures must be used directly during expansion.

## 3. Contents and scope

| Library | Source through `global_variables.json` | Purpose |
| --- | --- | --- |
| `inline_scripts` | `INLINE_SCRIPTS_DIR` | Templates invoked by relative path, including nested calls |
| `scripted_effects` | `SCRIPTED_EFFECTS_DIR` | Named effects |
| `scripted_triggers` | `SCRIPTED_TRIGGERS_DIR` | Named triggers preserving existing logical-result boundaries |
| `script_values` | `SCRIPT_VALUES_DIR` | Named calculations; game calculations are not evaluated |
| `scripted_variables` | `SCRIPTED_VARIABLES_DIR` | Shared static definitions as supporting snapshot data, not a new call kind |

Local variables of primary documents do not become global. Local declarations in library files retain their own environments. Library directories remain excluded from independent object enumeration.

Includes preparation, persistence, verified loading, template application, snapshot sharing across fifteen databases and single builds, and the necessary settings, schemas and reports. Analytical operations using the same expander obtain the library through the shared mechanism. Syntax-only parsing remains independent of the library.

Excludes multiprocessing, MongoDB, new UI, changes to the fifteen user-facing datasets, caching completed expansions by argument combinations, incremental partial library rebuilds, game-rule changes, new import exceptions and removal of expansion history. `scripted_actions`, `on_actions` and `events` remain ordinary datasets: similar names do not make them substitution libraries.

## 4. Library configuration

The proposed separate configuration is `config/libraries.json`. Backend configuration selects its path using the standard `base`/`path` reference; the expander does not hardcode it. Entries have a stable library `id` and a supported preparation-handler `kind`. Placement and reading settings are data; handler algorithms remain code.

| Configuration field | Requirement |
| --- | --- |
| `format_version` | Configuration contract version |
| `libraries[].id`, `libraries[].kind` | Unique, validated library identity and preparation type |
| `libraries[].source.variable` | Existing directory variable name rather than a duplicate path value |
| `libraries[].source.pattern`, `recursive`, `encoding` | Per-library file pattern, recursion and encoding |
| `libraries[].output` | Library JSON path relative to `WORK_DIR` |
| `manifest` | Saved snapshot manifest path relative to `WORK_DIR` |
| `report` | Preparation or loading report path relative to `WORK_DIR` |

Initial outputs: `libraries/inline_scripts.json`, `libraries/scripted_effects.json`, `libraries/scripted_triggers.json`, `libraries/script_values.json`, `libraries/scripted_variables.json`; manifest: `libraries/manifest.json`; report: `reports/libraries.json`. These are shipped configuration values, not mechanism constants. Settings can change all addresses.

Syntax, case sensitivity, parameters, directives, expansion limits and exceptions remain in existing `config/parser/*.json`. Move duplicated directory-reading settings from parser configuration into library configuration, updating schemas and consumers; competing sources of values are not allowed. The inline reference extension remains a reference-resolution rule, while enumeration patterns determine input selection.

Resolve input paths from `STELLARIS_ROOT` using existing rules. Outputs retain `WORK_DIR` restrictions, input/output separation and distinct-path checks. Known file exceptions include explicitly authorized extensionless targets even when `*.txt` does not match them. Do not introduce arbitrary access outside permitted roots.

Format and preparation implementation versions are technical compatibility markers, not user switches. Do not introduce a game command registry or a universal configuration language for implementing algorithms.

## 5. Invocation modes

| CLI switch | API `library_mode` | Behavior |
| --- | --- | --- |
| `--rebuild-libraries` | `rebuild` | Prepare every library from current sources, save a fresh snapshot and use it |
| `--reuse-libraries` | `reuse` | Validate the saved snapshot and its freshness, then load it without preparing templates again |

The switches are mutually exclusive. Operations requiring expansion must receive the mode explicitly; neither switch or both switches is an argument error before building begins. The API requires the same explicit decision. There is no hidden automatic rebuild mode or mode selection based on file existence.

In `reuse`, a missing, incomplete, damaged or stale snapshot produces diagnostics explaining the cause and pointing to `--rebuild-libraries`. This mode does not modify saved libraries; report writing is allowed. Unavailable game sources prevent freshness verification: offline trust in an old snapshot is outside this stage.

In `rebuild`, the existing snapshot is not an input to preparation. Prepare the complete set independently of its state. A new build invocation with this switch actually prepares libraries again rather than presenting reuse as rebuilding.

Provide a separate preparation/loading operation without building user-facing databases, and expose the same switches in the dataset-set CLI. Programmatic single builds and analytical operations use the same service; no interactive console dialog is introduced. Documentation labels new commands as available only after implementation.

## 6. Persistent representation

A snapshot consists of one manifest and five library JSON files. These are internal working artifacts, not additional frontend dataset members. JSON uses UTF-8 without BOM, LF, two-space indentation, readable Unicode and a final newline.

Minimum snapshot manifest:

| Field | Content |
| --- | --- |
| `format`, `format_version` | Library contract, independent of the user-facing database format |
| `preparation_version` | Preparation algorithm version; meaningful algorithm changes require a version change |
| `library_set_id` | Identity of the complete saved library contents |
| `input_fingerprint` | Fingerprint of preparation inputs and relevant settings |
| `sources` | Inventory: root, relative path, source-byte SHA-256 and library membership |
| `configuration` | Fingerprints of applied rules, exceptions and input-selection settings |
| `artifacts` | Library identities, paths, versions and file SHA-256 values |

`library_set_id` does not replace user-facing `dataset.set_id`. Avoid circular hashes: hashed library payloads do not contain their own final set identity. Timing, invocation date and absolute working paths do not determine library contents.

A template entry contains its `kind`, exact name or path, lookup key under current case rules, source and spans, original fragments for `raw` and diagnostics, a prepared `plan`, parameter and conditional-fragment descriptions, nested-call references and the definition environment description. Shared source fragments may live in a source table referenced by entries rather than copying an entire file into each entry.

The `plan` distinguishes constant parts, substitution locations and conditional parts. Constant regions are represented by reusable nodes or tokens. Parameterized nested paths or names remain template expressions rather than prematurely selected targets. Dynamic regions may contain complete constructs, not just scalar values.

Add exact machine-readable plan definitions to the existing schema generator together with configuration, manifest and report extensions. Field names, service-record variants and references are explicit; game command values remain unrestricted. No independent manual command registry is required.

JSON contains no Python objects, `pickle`, memory addresses, current arguments, counters, stacks or concrete invocation IDs. Definition references use stable identities. Loading reconstructs prepared structures without reparsing source text through the game parser.

## 7. Template preparation and application

Preparation inventories inputs, reads and hashes source bytes, prepares shared static definitions, and collects inline templates and named definitions, including definitions introduced by root inline insertions. It then prepares plans, validates service references, saves the snapshot and exposes it to consumers. A shared physical source is read once for preparation; verification reads are accounted for separately.

Preparation order supports forward references and definitions in other files. Nested calls remain until template application: preparation does not recursively expand every library. Do not require unbound argument values or resolve a dynamic target before it has been computed.

An invocation obtains an immutable plan, creates an independent call environment, applies arguments and conditions, instantiates the result and expands selected nested calls. Static variables, logical wrappers and `script_value` boundaries retain existing semantics. Preserve game statement order.

Required properties:

- Constant parts are not reread or fully rescanned for parameters and lexed again on every invocation. Repeated calls use prepared structures.
- Substitution in command names, keys, paths, strings and formulas, empty arguments and arguments containing multiple constructs retain textual semantics. Fragment composition handles token boundaries and escaping; replacing only `Scalar.text` is insufficient.
- Regions whose structure depends on arguments may require parsing the supplied fragment or assembling prepared tokens. Measure this work. Returning to the previous complete textual pipeline for every call does not qualify as library optimization.
- Defaults, conditional fragments and case sensitivity follow active configuration. A discarded branch does not invoke nested calls, require their parameters or fail because their targets are absent.
- Arguments are passed explicitly; a nested call does not inherit all parent bindings. Argument and definition environments remain distinct, including existing ambiguous-static-environment diagnostics.
- Game conditions, game scopes and `script_values` arithmetic are not evaluated against an empire state. Preparing plans does not extend the current parser's semantic scope.
- Repeated invocations receive independent mutable result trees. Mutating one result does not alter the library or other results.

Invocation, cycle, depth, expanded-node, missing-argument and unused-argument checks remain active. Optimized paths do not bypass them. An unsupported plan construct requires explicit diagnostics and resolution within this specification; no silent fallback to the old engine is introduced.

## 8. Freshness and persistence

For `reuse`, validate the format, preparation version, all artifact integrity, internal references and consistency with current inputs. Library JSON is checked once when loading the snapshot, not on each call or again for each dataset.

`input_fingerprint` covers the selected library inventory, source-byte SHA-256 values, resolved roots and relative names, reading parameters, active syntax, substitution, static-variable, call-resolution and exception rules. Adding, deleting, renaming or changing a file, including an authorized extensionless exception, makes the snapshot stale. Modification time and size alone are insufficient.

Changes to primary object files, translations or output database paths alone do not require library recreation. Identify relevant configuration sections explicitly: do not invalidate on every change to a large `backend.json`, and do not omit settings affecting prepared results. Contract or preparation algorithm changes require `rebuild`; automatic migrations are unnecessary.

Freshness verification requires reading source bytes to compare hashes. Do not describe it as a disk-free mode. Deduplicate shared inputs and verification within an operation across fifteen consumers; retain pre-publication checks of source contents and directory membership. A detected change stops the operation rather than silently initiating rebuilding.

Write `rebuild` results to temporary files inside `WORK_DIR`. After successful preparation and input verification, publish artifacts, followed by the complete manifest. `reuse` rejects incomplete sets and mismatching hashes. Atomic replacement of individual files is not a transaction across the set. If publication is interrupted, report the state and the need to rebuild; unsuccessful library preparation does not replace user-facing databases.

A completed snapshot remains usable if later processing of a primary document fails. A primary-document error does not itself corrupt the library. Concurrent writers targeting the same library directory are unsupported in this stage and must produce a clear ownership-conflict failure rather than mixing files.

## 9. Integration and invocation state

The dataset-set or standalone operation owns the snapshot. Prepare/load it once for identical inputs and rules. `sources/expansion.py` receives the prepared library instead of rereading library directories for each member. A change in relevant settings must not silently reuse a snapshot from another context.

Separate immutable definitions and plans from `Coordinator`, mutable variable tables, environment-specific resolution caches, statistics, call chains and history. Counters and identities continue to follow the established order of current sequential builds. Preparation service records do not become invocation history of primary documents.

Preserve template and argument provenance, original and generated spans, `parent_id`, insertion addresses, negative/comparison trigger wrappers and independent calculation scopes. Root definitions do not become calls merely because their names match. Existing source exceptions apply in their original context; a correction for one call site does not modify a shared template.

Single builds, set builds and analytics retain used-source information and diagnostics in both modes. Separate logical-operation counters from physical reads and preparations: library reuse must not make source or expansion statistics zero.

User-facing databases retain `sttv.parse_database` version `6`, complete contents, localization, formatting, document order and the current `dataset.set_id` algorithm. Changing service IDs for future parallelism is not required at this stage. Library JSON files are not added to the frontend's fifteen-file selection.

## 10. Validation and diagnostics

Preserve validation boundaries: configuration and snapshot at preparation/loading, concrete invocation during application, finished document once before writing. Do not restore repeated full audits of user-facing output in ordinary builds. Artifact hashes do not prove expansion algorithm correctness.

Library diagnostics distinguish missing snapshots, incompatible versions, changed inputs/rules, damaged JSON, checksum mismatches, invalid plan references, unknown library kinds, unsafe paths and write failures. For `reuse`, identify concrete differences and the need for explicit `rebuild`.

Expansion errors retain the primary document, definition file, coordinates, arguments, call chain and existing cause code where the cause is unchanged. Do not mask failures with empty insertions. Unused arguments and applied exceptions remain visible; loading a cache must not hide them.

Reports contain mode, status, `library_set_id`, reuse rejection reason, file and definition counts by kind, physical reads, plan preparations, loads and uses, artifact sizes, and input verification, preparation, loading, persistence and application times. Separately measure required parsing of dynamic regions. Library metrics and versions do not become game-node fields.

## 11. Measurements and acceptance

| Area | Required scenarios |
| --- | --- |
| Configuration | Relocate inputs and outputs through configuration; missing variables; path/ID collisions; extensionless inline-exception target |
| Modes | Exactly one switch; `rebuild` ignores the old snapshot; `reuse` neither prepares plans, rewrites libraries nor repairs them automatically |
| Freshness | Byte changes with unchanged size/time; additions/deletions/renames; rule, exception or preparation-version changes; translation and unrelated primary-file changes do not invalidate |
| Format | Load in a fresh process; corrupted JSON/hash/reference/version; mixed or incomplete artifacts |
| Parameters | Defaults, empty values, case rules, composite keys, strings/escaping, formulas, blocks and complete constructs supplied as arguments |
| Nesting | All four call kinds in mixed chains, dynamic paths/names, explicit forwarding, discarded branches, cycles and limit boundaries |
| Environments | Global/local static variables, identical arguments in distinct environments, original provenance and independent repeated-call results |
| Integration | One snapshot across fifteen datasets, single build, analytics, independent syntax parser, duplicate definitions and root definitions |
| Failures | Preparation/write errors, input mutation during a run, unavailable inputs, interrupted publication and directory ownership conflicts |

Before replacing the mechanism, preserve reference expansion results on fixed inputs. Compare game trees, statement order, provenance/history metadata, localization and diagnostics. Equal node counts do not replace content comparison. Stage 13's fifteen published files are a valid reference only if inputs match.

For repeated insertions, run at least three comparable measurements of the current and new paths and compare medians: parameterless, parameterized, conditional, mixed nested calls and dynamic fragments. Record call counts, unique plans, lexical/syntax parses and memory use. The old path is an acceptance reference, not a production fallback engine.

Run one complete build with `rebuild`, then one with `reuse` in a fresh process on unchanged inputs. Separately measure library preparation/verification/loading, expansion, remaining build work, peak memory and JSON sizes. Both paths must produce mutually byte-identical user-facing databases and match the stage 13 reference when inputs are identical; this is optimization acceptance, not comparison with an old database on every product run.

Demonstrate reduced repeated preparation across members and repeated parsing of constant fragments. Report source SHA-256 verification cost separately. Do not attribute gains solely from a warm disk cache to the algorithm. If large expansion cases do not improve or the full build regresses, investigate and document the cause before declaring the optimization successful.

Run existing backend and frontend-adapter checks; with an unchanged UI contract, a new large browser run is unnecessary without an additional reason. Artifacts belong under `WORK_DIR/stage14/`. Update the bilingual guide, README and changelog with actual results. Launching the game is unnecessary; game sources remain read-only.

## 12. Implementation structure

Proposed module group: `src/backend/sttv/libraries/`, covering settings, inventory/fingerprinting, plan models, preparation, persistence/loading and the operation service. Dynamic-fragment parsing and plan application remain alongside `script/`; the call coordinator does not become file storage.

Share parameter, conditional, static-environment and provenance rules. Do not maintain divergent semantic implementations for preparation and normal expansion. Update the schema generator, entry points, builders, reports and tests with the contract; modules follow shared specification size and DRY requirements.

Implementation order after approval: reference cases and measurements → configuration and snapshot model → plan preparation/application → persistence and explicit modes → shared builder lifecycle → equivalence/performance checks → documentation. Nothing in this specification authorizes multiprocessing or game-rule changes without a separate stage.

## 13. Related documents

- [Shared project principles](TZ_EN.md).
- [Stage 13: validation and build optimization](TZ_BACKEND_STAGE_13_EN.md) and [results](BACKEND_STAGE_13_EN.md).
- [Inline insertions](TZ_BACKEND_STAGE_5_EN.md), [static variables](TZ_BACKEND_STAGE_7_EN.md).
- [Effects and triggers](TZ_BACKEND_STAGE_8_EN.md), [script values](TZ_BACKEND_STAGE_9_EN.md).
- [Fifteen user-facing datasets](TZ_BACKEND_STAGE_12_EN.md).
- [Русская версия](TZ_BACKEND_STAGE_14_RU.md).
