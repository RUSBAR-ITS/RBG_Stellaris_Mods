# WEB_STTV — validation and build optimization

## Contents

- [Invocation and output](#invocation-and-output)
- [Preparing rules](#preparing-rules)
- [Processing a document](#processing-a-document)
- [Writing and publication](#writing-and-publication)
- [Report measurements](#report-measurements)
- [Verification and performance](#verification-and-performance)
- [Optimization boundaries](#optimization-boundaries)

## Invocation and output

Implementation of approved [stage 13](TZ_BACKEND_STAGE_13_EN.md). The complete 15-database build and comparison with the control output succeeded.

The set build command from `WEB_STTV` remains:

```powershell
$env:PYTHONPATH = 'src/backend'
& ./data/.venv/Scripts/python.exe -B -m sttv.database_sets
```

Single build: `python -B src/backend/main.py --config <single_build_config>`. It uses a configuration with `sources` and `outputs`, unlike the set's shared `config/backend.json`. Source, localization and output settings are unchanged. Set results are 15 files at `data/databases/<kind>.json`; the frontend opens them only at the user's request. The database format remains `sttv.parse_database`, version `6`.

## Preparing rules

The sole structural rule source is `schemas/database.schema.json`, produced by the existing `schema_generation` generator. At operation entry the schema is checked and converted to validation functions; recursive references link those functions. Nine syntax node types are selected by `kind`. Regular expressions and type/condition dispatch tables are prepared in advance.

All members of a build share this preparation. The next operation creates a fresh rule snapshot. Small configuration and report schemas are also reused only within an operation. Results are not cached across runs.

The mechanism supports constraints used by the current contract; an unfamiliar constraint raises `unsupported_schema`. No second game command registry is introduced. The general JSON Schema validator remains the test oracle.

Code responsibilities:

| Module | Responsibility |
| --- | --- |
| `common/schema.py` | Prepared schema lifetime within one operation |
| `database/checks/` | Constraint preparation, branch selection and document context |
| `database/validation.py` | Shared database and document validation interface |
| `database/history.py`, `database/enrichment.py` | Provenance references, expansion history and localization |
| `database/collection.py`, `database_sets/member.py` | Sequential document production and enrichment |
| `database/streaming.py` | Document validation, canonical hash and formatted writing |

## Processing a document

One source file goes through reading, parsing and expansion, static-variable substitution, serialization, localization target selection and attachment. The completed document is then checked once and written to temporary JSON. References to its tree are released before the next document.

Structural validation also counts syntax nodes and indexes containers, provenance and localized nodes. These indexes finish checks for forward references, expansion parents and cycles, insertion addresses, calculations and localization inheritance. No additional full traversal searches for these values.

Document ordinals are preserved: `/documents/N/...` addresses do not restart for each file. Duplicate ID indexes, shared sources and cumulative counts belong to the whole database. An error in a late document prevents publication of the prepared member.

## Writing and publication

Output remains regular JSON with two-space indentation, LF, readable Unicode and a trailing newline. Canonical SHA-256 is computed incrementally over the previous byte sequence. Performance measurements do not enter the database or its hash.

The build neither rereads temporary databases nor revalidates unchanged trees. Adding `dataset` after determining the shared `set_id` uses the existing byte copy with a header. Inputs are rechecked before publication; `flush`, `fsync`, temporary cleanup and atomic replacement of individual files are preserved. Replacing all 15 files is not a single transaction: partial failures remain visible in the report.

Separate database reading uses the same validator. Standalone localization checks its input and the modified result — two different data states.

In a single build, database replacement time is recorded before saving the report once. If saving the report fails after successful replacement, the operation returns an error with `database_written = true`; the published database is not reported as unwritten.

## Report measurements

Build and set reports contain `performance`:

- `rule_preparations` — rule preparation count; a successful set operation has one.
- `validated_documents` — number of finally validated documents.
- `documents` — source, node count, outcome and validation time per document.
- `timings` — seconds for preparing rules and sources, parsing/expansion/serialization, localization, validation, hashing, writing, input verification and publication, where applicable.

Member validation time and document details are available in `datasets.<kind>.performance` of the set report. A member's total duration includes all its phases. Coordinator and nested intervals must not be added as independent measurements.

## Verification and performance

Six preserved documents were measured three times each with the previous and new complete validators. Both series include rule preparation; medians use identical data. Control sources, hashes, node counts and environment are recorded under `data/stage13/`.

| Sample | Validation speedup |
| --- | ---: |
| Typical technology document | 4.42× |
| Large technology document | 5.71× |
| Typical component document | 2.65× |
| Large component document | 6.08× |
| Typical event document | 2.50× |
| Large event document | 5.67× |

These measure the validator, not the complete build. Details: [baseline measurements](../data/stage13/baseline_validation.json), [comparison](../data/stage13/validation_benchmark.json).

Complete build on 2026-11-18:

| Measurement | Result |
| --- | --- |
| Coordinator duration: stage 12 → stage 13 | 5490.835 → 2061.189 s; 91.5 → 34.4 minutes |
| Complete build speedup | 2.66× |
| Full call duration, including report persistence | 2065.194 s |
| Process peak memory | 1,768,845,312 bytes, approximately 1.65 GiB |
| Rule preparations / document validations | 1 / 450 |
| Outputs | All 15 databases match control sizes and SHA-256 hashes |
| Contents | 450 documents, 15,599 definitions, 22,345 localization targets |
| Set size | 11,762,739,507 bytes, approximately 10.95 GiB |
| Inputs and identity | All 1625 inputs and the shared `set_id` match |

Memory was measured using Windows `GetProcessMemoryInfo.PeakWorkingSetSize` after the build, before independent output reads. There is no comparable measurement of the previous peak; no memory reduction factor is claimed. The previous 91-minute build was not repeated: preserved output with identical inputs and settings was used.

Across the complete run, validation took 273.4 s, parsing/expansion/serialization 671.6 s, canonical hashing 365.3 s, and JSON writing 459.7 s. Remaining time covers preparation, localization, input checks and publication. Hashing and writing now take longer than validation; further optimization of those operations is outside this stage.

There are no errors or skipped documents. Previous diagnostics remain: 50 unused inline argument warnings, 40 exception applications, 218 missing localization field warnings and 52 unresolved reference warnings. Missing texts are not invented.

Details: [acceptance summary](../data/stage13/acceptance_summary.json), [file equality](../data/stage13/byte_comparison.json), [environment](../data/stage13/environment.json). Independent comparisons and frontend verification are excluded from build duration.

Passed **213 Python tests**: structural equivalence of all nine node types against the schema oracle, rule refresh between operations, document tree release, real localization addresses, duplicates, negative cases and publication failures. All 18 shipped schemas match the generator. The final run used no active development server: its test-directory watcher interfered with a directory rename on Windows.

Passed **33 frontend checks**, including independent streaming reads of the complete set. A browser test opened all fifteen files, displayed 679 cards and checked RU/EN, theme, tooltip and three Titan variants; no page errors occurred. Opening took 255.8 s. This verifies compatibility rather than optimizing the frontend. The compact catalog retained its 214 existing missing localization warnings.

Artifacts: [backend run](../data/stage13/regression.log), [frontend checks](../data/stage13/frontend_tests.log), [catalogs](../data/stage13/frontend_catalog_report.json), [browser](../data/stage13/browser_real_set.json), [interface screenshot](../data/stage13/real-night.png). TOCs in ten affected Markdown documents and links in the new guide were checked.

## Optimization boundaries

A member's documents are no longer retained together, but a single large document, shared template libraries and the localization index still require memory. Complete provenance and expansion history preserve the previous file sizes. Member source preparation is not parallelized.

Streaming reads of existing databases in separate Python operations were not added; the frontend keeps its existing streaming reader. Game grammar, exceptions and card ordering were not changed. Game sources remain read-only; launching Stellaris is not required for this stage.

[Русская версия](BACKEND_STAGE_13_RU.md).
