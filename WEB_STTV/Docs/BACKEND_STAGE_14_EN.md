# WEB_STTV — reusable element library

## Contents

- [Commands](#commands)
- [Configuration and files](#configuration-and-files)
- [Prepared representation](#prepared-representation)
- [Freshness and failures](#freshness-and-failures)
- [Application and analytics](#application-and-analytics)
- [Measurements](#measurements)
- [Validation](#validation)
- [Limitations](#limitations)

## Commands

Approved [stage 14](TZ_BACKEND_STAGE_14_EN.md) is implemented. Both modes passed complete builds of the fifteen-database set.

From `WEB_STTV`, select **one** mode:

```powershell
$env:PYTHONPATH = 'src/backend'
# Prepare libraries from source and build all fifteen databases.
& ./data/.venv/Scripts/python.exe -B -m sttv.database_sets --rebuild-libraries
# Verify and load saved libraries, then build the databases again.
& ./data/.venv/Scripts/python.exe -B -m sttv.database_sets --reuse-libraries
```

To prepare or verify libraries without building databases:

```powershell
& ./data/.venv/Scripts/python.exe -B -m sttv.libraries --rebuild-libraries
& ./data/.venv/Scripts/python.exe -B -m sttv.libraries --reuse-libraries
```

Both CLIs support `--variables` and `--config`. Single build: `python -B src/backend/main.py --config <single_build_config> --reuse-libraries`; the single-build configuration contains `sources`, `outputs`, `parser` and `libraries`. Python API: `build_database_set(..., library_mode='rebuild' | 'reuse')`, `build(..., library_mode=...)`.

`rebuild` always prepares libraries anew. `reuse` verifies the existing snapshot and never recreates it automatically on failure. Both modes build user-facing databases anew. Omitting the mode or passing both switches is an error.

## Configuration and files

`config/backend.json` selects `config/libraries.json` through `base`/`path`. Each library defines `id`, `kind`, its directory variable name, `pattern`, `recursive`, `encoding` and `output`. `manifest` and `report` are configurable as well. Outputs resolve under `WORK_DIR`; sources are confined to `STELLARIS_ROOT`. Duplicate reading options have been removed from parser configurations.

| Kind | Variable | Default JSON |
| --- | --- | --- |
| Inline templates | `INLINE_SCRIPTS_DIR` | `libraries/inline_scripts.json` |
| Effects | `SCRIPTED_EFFECTS_DIR` | `libraries/scripted_effects.json` |
| Triggers | `SCRIPTED_TRIGGERS_DIR` | `libraries/scripted_triggers.json` |
| Calculations | `SCRIPT_VALUES_DIR` | `libraries/script_values.json` |
| Shared static variables | `SCRIPTED_VARIABLES_DIR` | `libraries/scripted_variables.json` |

The snapshot manifest is `libraries/manifest.json`; the operation report is `reports/libraries.json`. Libraries have independent format and preparation versions. The interface still opens only the fifteen files in `data/databases/`; library JSON is not part of that selection.

The schema generator produces four additional contracts: `libraries.schema.json`, `library.schema.json`, `library_manifest.schema.json`, `library_report.schema.json`. There are 22 active schemas. JSON uses LF newlines, two-space indentation and readable Unicode.

## Prepared representation

A snapshot contains tables of sources, definitions, environments and plans. `$ref` references inside service JSON are object-table indices. They retain shared fragments and environment relationships; they are neither Python addresses nor game-command references.

A plan stores token ranges and kinds, parameters with original coordinates, conditional-fragment presence and prepared nodes for constant bodies. Loading JSON does not parse the game source text again.

A constant body produces an independent tree. Parameterized bodies reuse complete unchanged tokens; inserted fragments and composition boundaries are parsed again to preserve textual semantics. Conditions, defaults and nested calls retain shared parser rules. Discarded branches are not expanded.

Preparation occurs once per operation. Each dataset member has independent counters, call history and local environments. Shared definitions and plans contain no primary-document invocation state. Coordinates, original text, history, logical wrappers and `script_value` boundaries are preserved.

## Freshness and failures

Verification covers inventory, source-byte SHA-256, resolved roots, reading options, syntax, substitution, call, variable and exception rules, and the preparation version. Additions, deletions, renames and content changes require `rebuild`; matching timestamps and sizes are insufficient. Authorized extensionless exception files are included.

Changes to primary objects, translations or output database paths alone do not invalidate libraries. Inputs are checked again before publication. `reuse` reads sources to verify hashes; it is not an offline mode without game files.

Damaged JSON, mismatching hashes, unknown versions, incomplete sets, invalid references and plan ranges produce diagnostics. Recovery requires explicit `--rebuild-libraries`. Library JSON structure is checked once on loading, not on each invocation.

Preparation writes temporary files, then replaces artifacts and finally the manifest. This is not a transaction across all files. An interrupted publication is detected through inventory and hashes. `.sttv-libraries.lock` in each output directory for libraries, the manifest and the report prevents concurrent writes even when processes select different manifest names. A lock left by a terminated process is removed manually only after confirming that the owner has stopped; another process's lock is never removed automatically.

## Application and analytics

`libraries.operation.library_operation(settings, mode)` owns the snapshot lifetime. Inside it, `sources.expansion.expansion_context()` creates an independent context. Analytical entry points `script.audit_corpus`, `database.audit_values` and `database.audit_build` accept the same switches. Syntax-only parsing needs no library.

| Modules | Responsibility |
| --- | --- |
| `libraries/configuration.py`, `inventory.py` | Paths, inventory, hashes and freshness |
| `libraries/snapshot.py` | Preparation and consumer contexts |
| `libraries/codec.py`, `references.py`, `payloads.py` | Service graph and reference validation |
| `libraries/storage.py`, `validation.py` | Persistence and verified loading |
| `libraries/operation.py`, `ownership.py` | Mode, directory ownership, shared snapshot and report |
| `script/prepared.py`, `metrics.py` | Plans, reuse and measurements |

## Measurements

`reports/libraries.json` records mode, status, `library_set_id`, JSON bytes, definition/file counts by kind, plan preparations, loads, contexts and uses. `source_reads` counts initial library-service source reads; `verification_reads` separately counts its freshness reads. Existing database reports retain logical source and expansion counters.

`prepare_` and `apply_` prefixes separate freshly lexed tokens, replayed tokens, syntax parses, constant instantiations and plan uses. `dynamic_parsing` time is included in `application`; pre-publication verification also belongs to the enclosing operation. Nested intervals must not be added as independent durations.

Acceptance artifacts reside in `data/stage14/`: `acceptance_summary.json`, `rebuild_acceptance.json`, `reuse_acceptance.json`, stage 13 reference hashes and an isolated reference implementation.

Complete sequential builds on this machine:

| Mode | Total seconds | Minutes | Peak process working set, GiB |
| --- | ---: | ---: | ---: |
| Stage 13 reference | 2,065.194 | 34.4 | 1.65 |
| Stage 14, `rebuild` | 1,763.117 | 29.4 | 2.04 |
| Stage 14, `reuse` | 2,035.117 | 33.9 | 2.50 |

In `rebuild`, preparation took 22.326 s and saving took 112.336 s. In `reuse`, loading and validating the library JSON took 56.375 s. Library-service input verification took 0.872 and 0.943 s respectively, including initial reads and subsequent checks. These are individual real runs, not guarantees for another invocation.

In this measurement, `reuse` was slower than `rebuild`, although loading cost less than preparation plus saving. Insertion application took 371.269 s instead of 277.565 s; unchanged database hashing, validation and writing also took longer. The `reuse` acceptance run partially overlapped tests and frontend streaming of the set. These runs do not isolate mode, load and memory effects; loading saved JSON cannot be assumed to be unconditionally the fastest mode.

The five library JSON files total 535,747,873 bytes (approximately 511 MiB). Preparation produced 4,689 plans: 632 inline files, 1,691 effects, 1,692 triggers and 674 script values; 2,917 shared static definitions were saved separately. `reuse` prepared zero plans and loaded five artifacts. One snapshot served fifteen contexts in each mode.

Application performed 103,071 plan uses and 79,185 constant-tree instantiations. It replayed 8,078,298 tokens and lexed 4,777,195 tokens afresh. Counts match between modes. Initial library-source reads covered 750 files; subsequent verification performed another 1,500 reads. These metrics do not imply offline operation without reading game sources.

Reference microbenchmarks ran after the full builds completed: medians of three series of 120 top-level calls. Each example's trees and history match the old mechanism by SHA-256. Work counters and `tracemalloc` were collected in a separate pass so memory instrumentation would not distort timing.

| Case | Unique templates | Before, s | After, s | Freshly lexed tokens, before → after |
| --- | ---: | ---: | ---: | ---: |
| Parameterless | 1 | 0.840 | 0.326 | 144,960 → 1,260 |
| Parameters | 1 | 0.611 | 0.326 | 60,000 → 24,120 |
| Conditional fragments | 1 | 0.604 | 0.341 | 77,880 → 25,470 |
| Nested inline calls | 2 | 1.540 | 0.571 | 91,200 → 14,507 |
| Dynamic constructs | 1 | 0.617 | 0.381 | 44,640 → 29,328 |
| Mixed insertion kinds | 5 | 2.876 | 2.669 | 307,257 → 21,297 |

In the mixed example, parser instances decreased from 10,923 to 8,045; peak traced Python allocations increased from 1,035,978 to 1,080,085 bytes. All six memory, lexical/syntax work and timing measurements are recorded in `*_benchmark_work.json`, `*_benchmark_final.json` and the aggregate report. Reduced repeated work is demonstrated by counters and cannot be attributed solely to a warm disk cache.

## Validation

The complete backend suite passed 230 tests. After the final directory-ownership change, 18 library tests, including one new test, and 21 builder/settings/variable integration tests passed. In total, 231 unique backend tests were checked.

Frontend: 33 checks passed without skips, including streamed opening of all fifteen real databases with `STTV_DATABASE_DIR=data/databases`. Results contain 679 technologies, 1,506 components, 498 buildings and catalogs for the other twelve kinds; sixteen previously researched relationship examples were confirmed. The 214 missing-localization warnings remain. A browser run and game launch were unnecessary.

Both complete builds match each other and stage 13 byte for byte: fifteen files, 11,762,739,507 bytes and 450 documents. The `set_id`, hashes of 1,612 game/localization inputs, logical counters and member statuses match. Product builds do not add a second complete audit of persisted databases; hash comparison was performed separately for acceptance.

`database.audit_values --reuse-libraries` checked three real fragments and four calls to vanilla definitions: nested arguments, scopes, defaults and conditional fragments; 300 nodes. Sources remained unchanged. Reports are saved in `data/stage14/analytics_acceptance.json` and `analytics_library_report.json`.

## Limitations

Processing remains sequential. Parallel execution, incremental library rebuilding and caching of completed expansions were not added. The snapshot consumes extra memory and disk space; freshness verification, JSON loading and object restoration have their own costs. Builds preserve complete game trees, localization and `sttv.parse_database` format version `6`. Launching the game is unnecessary for this stage.
