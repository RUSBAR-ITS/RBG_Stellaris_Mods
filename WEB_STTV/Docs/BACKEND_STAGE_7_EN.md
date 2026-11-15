# Stellaris Technological Tree View — stage seven backend

## Contents

- [Status and process](#status-and-process)
- [Invocation and outputs](#invocation-and-outputs)
- [Configuration and scopes](#configuration-and-scopes)
- [Tree and metadata](#tree-and-metadata)
- [Modules and schemas](#modules-and-schemas)
- [Errors and diagnostics](#errors-and-diagnostics)
- [Verification](#verification)
- [Limitations](#limitations)

## Status and process

This document preserves stage seven. Current implementation: [stage eight](BACKEND_STAGE_8_EN.md).

The approved [stage-seven specification](TZ_BACKEND_STAGE_7_EN.md) is implemented. Builds read shared static variables, parse independent scripts, expand nested `inline_script` calls, substitute `@name` values, and persist trees as JSON. Game sources are read-only. The [stage-six guide](BACKEND_STAGE_6_EN.md) preserves the previous state.

## Invocation and outputs

Standard invocation from the repository root:

```powershell
& WEB_STTV/data/.venv/Scripts/python.exe -B WEB_STTV/src/backend/main.py
```

The CLI retains `--variables` and `--config`; no interactive dialogue was added. Normal invocation writes configured `data/database.json` and `data/reports/build_report.json`. Stage verification uses separate `data/stage7/database.json` and `data/stage7/build_report.json`; checks do not automatically replace the previous standard database.

Python interfaces `sttv.builder.build(variables_path, config_path)` and `sttv.database.storage.read_database(path)` remain available. Loading JSON requires no game and performs no substitution. Resolving values in an older database requires rebuilding.

## Configuration and scopes

`SCRIPTED_VARIABLES_DIR = common/scripted_variables` is relative to `STELLARIS_ROOT`. The directory is required but may be empty. Shared files are read separately and excluded from independent documents alongside inline-template and scripted-effect libraries. File links cannot escape the library root; sources and configurations are protected from writes.

The sixth selection, `parser.static_variables` in [backend.json](../config/backend.json), points to [static_variables.json](../config/parser/static_variables.json). It supports `product` / `work` bases, pattern, recursive traversal, encoding, prefix, name regular expression, case sensitivity, and chain limit. Defaults: `*.txt`, recursive, `utf-8-sig`, `@`, `[A-Za-z_][A-Za-z0-9_]*`, case-sensitive, depth 64.

Shared chains resolve in the shared scope. Each document has an isolated local declaration table; local names override shared names without changing already resolved shared chains. Collect declarations before resolving references, allowing forward references. A repeated name in one scope is an error even when values match. These are backend implementation rules, not claims about every engine edge case.

Substitution follows complete inline expansion. Argument `VALUE = @cost`, inserted as `amount = $VALUE$`, uses the caller document's local value. Template caches do not retain these results across documents. Static variables in `inline_script` paths are not resolved.

## Tree and metadata

Only complete unquoted scalars in values and lists are replaced. Numeric spelling, quoting, and scalar literal kind come from declarations. Keys, tags, comments, strings such as `"@name"`, composite names, and formulas remain unchanged.

The database schema remains `sttv.parse_database`, version 1. Replaced values' `raw` and `text` contain literals; `span` and `origin` identify the original reference use site. Local declarations remain unchanged. Node order/count, coordinates, and `inline_scripts` history are preserved; there is no separate variable history, before/after copy, or additional metadata field.

Builds and corpus audits use the same processor. Analysis skips complete top-level declarations and counts working values after substitution while retaining earlier filters. Metadata is excluded from counting.

## Modules and schemas

| Module | Responsibility |
| --- | --- |
| `script/variables/rules.py` | Configuration checks, name recognition, and location-aware diagnostics |
| `script/variables/table.py` | Tables, isolated scopes, chains, cycles, and depth without recursive reference traversal |
| `script/variables/processor.py` | Working-value traversal preserving provenance and declarations |
| `sources/static_variables.py` | Read-only shared-library reading, physical-file deduplication, and hashes |
| `schema_generation/static_variables.py` | Configuration and report-counter declarations |

Added the ninth schema, `parser_static_variables.schema.json`; updated generated `backend.schema.json` and `report.schema.json`. The structure of `database.schema.json` is unchanged. Schemas are still generated through `python -B -m sttv.schema_generation` with `PYTHONPATH` configured.

## Errors and diagnostics

Unknown references, cycles, excessive depth, repeated names, unresolved parameters, nested declarations, and block/formula declarations cause errors. Shared-library errors stop the build before documents; per-file failures are collected in the report. Errors prevent new database publication and preserve the previous successful database.

The operational report format is 3. `static_variable_sources` maps shared files' relative paths to SHA-256. `counts.static_variables` contains `files`, `global_definitions`, `local_definitions`, `references`, and `substituted`. The last two counters concern working uses only. Shared files do not increase `selected_files`; failed-run counts describe the portion actually processed.

Diagnostics identify sources and coordinates; unknown/cyclic/deep-reference messages contain name chains, and duplicate messages identify both declarations. Inline failures retain their provenance and caller document. Input manifests and aggregate counters are not stored in database metadata.

## Verification

```powershell
$env:PYTHONPATH = "$PWD/WEB_STTV/src/backend;$PWD/WEB_STTV/src/backend/tests"
& WEB_STTV/data/.venv/Scripts/python.exe -B -m unittest discover -s WEB_STTV/src/backend/tests
& WEB_STTV/data/.venv/Scripts/python.exe -B -m database.audit_build
& WEB_STTV/data/.venv/Scripts/python.exe -B -m script.audit_corpus
```

All 104 tests passed. Coverage includes scopes, chains, case handling, errors, depth boundaries, nested insertions, history and coordinates, absence of variable metadata, library refresh, path protection, and preserving previous databases.

Technology verification compares every result field against the source tree and independent substitution of the current game's numeric declarations, then checks byte-identical rebuilding. Its report is `data/stage7/real_validation_report.json`. Corpus auditing writes `data/stage7/corpus_report.json` and new lists under `data/stage7/text_frequency/`; previous lists are preserved.

Actual technology build: 35 files, 67,513 nodes, 1,929 substituted references, and 301 expanded inline calls from 10 templates; no errors or warnings. Read 2,917 shared declarations from 23 files and three local declarations. The 107,461,800-byte JSON was identical after rebuilding; every field passed independent comparison. Sources and previous standard outputs were unchanged.

Full audit: of 2,238 TXT files, excluded 631 inline templates, 43 effect files, and 23 shared-variable files. Among 1,541 independent inputs, 1,522 files passed, two documentation TXT files were skipped, and 17 files failed. Performed 37,115 substitutions across 37,116 visited working references; counters include the processed part of the failing file. Successful documents contain 3,503,951 persisted nodes. New lists contain 54,136 frequency entries, 33,871 scalar values, and 4,257 scalar assignments.

Failure comparison: `data/stage7/failure_comparison.json`. The previous 14 `CLASS` and two `RELIC` failures remain. The previously fixed color file and three tradition files now pass the full run. The new failure is `unknown_static_variable` for `@max_unlocked_council_positions` in `common/script_values/01_script_values_paragon.txt:365`; no declaration exists in the loaded library or local file. The full corpus result is `partial`; no value was guessed or source repaired. Game sources, inline templates, variable library, and previous research lists were preserved.

## Limitations

Formulas are not evaluated; declarations containing formulas or blocks are rejected. Game-state variables, localization, scripted effects/triggers, and additional parameter forms are not expanded. `CLASS` and `RELIC` issues remain separate tasks. A partial corpus report is not a successful working database.

The complete tree is held in memory; detailed inline provenance continues to affect JSON size. No new substitution metadata is added. Modifying game files and verifying runtime game behavior are outside this stage.
