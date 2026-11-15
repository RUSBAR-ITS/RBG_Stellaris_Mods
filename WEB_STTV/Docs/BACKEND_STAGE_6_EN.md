# Stellaris Technological Tree View — stage six backend

## Contents

- [Status and purpose](#status-and-purpose)
- [Building and loading](#building-and-loading)
- [Configuration and sources](#configuration-and-sources)
- [Persisted structure](#persisted-structure)
- [Modules and schemas](#modules-and-schemas)
- [Errors and publication](#errors-and-publication)
- [Verification](#verification)
- [Limitations and subsequent stages](#limitations-and-subsequent-stages)

## Status and purpose

This guide preserves stage-six behavior. The current build adds static-variable substitution: [stage-seven guide](BACKEND_STAGE_7_EN.md).

The approved [stage-six specification](TZ_BACKEND_STAGE_6_EN.md) is implemented. The backend reads selected scripts, parses them, expands nested `inline_script` calls, and persists syntax trees as JSON. All sources are read-only.

The game-command profile, registry, recommendation analyzer, and closed technology conversion have been removed. Localization and evaluation are not part of this build. Game names are preserved independently of their presence in the previous profile.

Earlier guides and the [domain database model](DATABASE_MODEL_EN.md) are historical. The new format has identifier `sttv.parse_database`, version `1`, and is incompatible with the previous domain formats 1 and 2.

## Building and loading

The backend uses Python and the dependency in [requirements.txt](../src/backend/requirements.txt): `jsonschema==4.26.0`. The current environment has a prepared virtual environment at `WEB_STTV/data/.venv`. Run from the repository root:

```powershell
& .\WEB_STTV\data\.venv\Scripts\python.exe -B .\WEB_STTV\src\backend\main.py
```

The CLI accepts `--variables` and `--config`; defaults select `global_variables.json` and `config/backend.json` relative to the product directory. The process working directory does not affect resolution of these paths. Success returns exit code 0 and a JSON report on stdout; failure returns exit code 1 and a report on stderr.

For Python calls, add `WEB_STTV/src/backend` to `PYTHONPATH`:

```python
from pathlib import Path
from sttv.builder import build
from sttv.database.storage import read_database

product = Path("D:/Repos/RBG_Stellaris_Mods/WEB_STTV")
report = build(product / "global_variables.json", product / "config/backend.json")
database = read_database(product / "data/database.json")
```

`read_database(path)` validates persisted structure and metadata. It requires no game, Workshop, parser configuration, or reparsing. It returns ordinary dictionaries and arrays without restoring parser objects.

## Configuration and sources

[backend.json](../config/backend.json) has three sections:

- `sources`: an array of `variable`, `pattern`, `recursive`, and `encoding` settings. Defaults select `TECH_PATH`, `*.txt`, recursive traversal, and `utf-8-sig`.
- `parser`: selection of five configurations from `config/parser/` — lexical notation, constructs, logical operators, inline expansion, and exceptions. Each supports `product` and `work` bases.
- `outputs`: `database.json` and `reports/build_report.json`, relative to `WORK_DIR`.

Require `STELLARIS_ROOT`, `WORK_DIR`, `INLINE_SCRIPTS_DIR`, `SCRIPTED_EFFECTS_DIR`, `SCRIPTED_VARIABLES_DIR`, and variables named by selected sources. Workshop and localization remain in the shared variables file for future enrichment but are optional for this operation.

Sources remain inside `STELLARIS_ROOT`. Selection includes `category` and `tier` as ordinary files. Identical physical files are processed once; conflicting encodings for one file produce an error. Relative paths determine document order. An empty script is persisted with empty `items`; selecting no files is an error.

Templates under `INLINE_SCRIPTS_DIR` are excluded from independent selection. They are read only through reached calls. The template cache lasts for one operation; the next build reads current files.

`SCRIPTED_EFFECTS_DIR` identifies the named-effect library, defaulting to `common/scripted_effects` relative to `STELLARIS_ROOT`. The directory and all descendants are excluded from independent selection by the shared builder/corpus filter. Effect calls remain ordinary tree nodes; their expansion is not implemented yet. The path must remain inside the game, but the excluded library need not exist unless explicitly selected as a source.

`SCRIPTED_VARIABLES_DIR` similarly identifies the static-variable library: `common/scripted_variables` relative to `STELLARIS_ROOT`. The directory and descendants are excluded from independent traversal and counted separately in corpus reports. Substitution of `@name` is not implemented yet; the library is not read for values. The path remains inside the game; the excluded library need not exist unless explicitly selected as a source. The next full audit writes results under `data/stage6/without_scripted_libraries/`, preserving previous reports.

`WORK_DIR` defaults to `data`; another relative or absolute path inside the repository is supported. Writes cannot overlap sources, code, configuration, or other protected material. Source TXT files are not copied into the working directory.

Targeted exception in [constructs.json](../config/parser/constructs.json): `trait_bg_active_glow` joins `rgb` and `hsv` in `tagged_blocks`. This preserves the observed declaration without `=` as a `tagged_block`. No missing operator is inserted; arbitrary other names without an operator remain rejected. This is an agreed parser exception, not confirmation that the engine accepts this declaration.

[exceptions.json](../config/parser/exceptions.json) is selected through `parser.exceptions` in `backend.json` and validated against `parser_exceptions.schema.json`. In `inline_script_files`, the key is the invocation name before automatic extension addition, `file` is the exact filename relative to `INLINE_SCRIPTS_DIR`, and `reason` explains the exception:

```json
{
  "format_version": 1,
  "inline_script_files": {
    "traditions/tr_purity_imperfection_remediation_wilderness": {
      "file": "traditions/tr_purity_imperfection_remediation_wilderness",
      "reason": "The installed vanilla template is shipped without the .txt extension."
    }
  }
}
```

Matching is exact after normalizing path separators and Windows case; duplicate normalized names are rejected. An exception takes priority over normal `.txt` addition. Unlisted calls retain the previous extension rule. If the explicitly named file is missing, the operation fails without searching alternatives. Exceptions disallow patterns, absolute paths, `..`, NTFS streams, and escaping `INLINE_SCRIPTS_DIR` after resolving filesystem links. Files are only read as text and parsed; history, coordinates, and hashes retain the actual path. Exception reasons do not participate in analytics.

The exception configuration is required; an empty `inline_script_files` represents no exceptions. A missing or invalid configuration blocks the build. Outputs cannot overwrite the configuration itself. The targeted `trait_bg_active_glow` syntax allowance remains in `constructs.json`.

## Persisted structure

The root contains `format`, `format_version`, and `documents`. Each document contains `source`, `items`, and `metadata`. Full field details: [the result format specification](TZ_BACKEND_STAGE_6_EN.md#5-persisted-json-format).

There are seven node kinds: `scalar`, `formula`, `block`, `tagged_block`, `conditional`, `assignment`, and `logical_operation`. A node contains `kind`, its syntax fields, `span`, and `origin`. Order, repeated entries, case, quotes, parameters, formulas, and source coordinates are preserved. Numbers, `yes`/`no`, and `@name` remain text inside scalar nodes.

A technology is currently an ordinary tree entry. The database does not compute cost, eligibility, or dependencies, collect localized names, or merge repeated definitions.

Invocation nodes are absent after expansion. History resides in `document.metadata.inline_scripts`. `insertion.container` addresses a node array inside the same document; `index` and `count` define the insertion range. Arguments, nested calls, and zero-length insertions are preserved. Metadata does not participate in frequency statistics.

Complete source text, tokens, separate comments, and whitespace formatting are not persisted. `origin` retains template, substitution, and composed-text fragment information. The database supports tree analysis; byte-for-byte source reconstruction is not provided.

## Modules and schemas

| Module | Responsibility |
| --- | --- |
| `sources/` | Configuration, path protection, file selection, reading, and hashes |
| `script/` | Lexer, parser, syntax nodes, traversal, and serialization |
| `script/inlining/` | Templates, arguments, substitution, and recursive expansion |
| `database/` | Document container, history checks, reading, and publication |
| `common/` | JSON, diagnostics, paths, and temporary-file publication |
| `schema_generation/` | Generation of eight structural application schemas |

Active schemas are `backend.schema.json`, `database.schema.json`, `report.schema.json`, and five `parser_*.schema.json` files, including the new exceptions schema. The database schema describes node kinds and metadata without enumerating permitted game names. The generator does not read the game. From the repository root:

```powershell
$env:PYTHONPATH = "$PWD/WEB_STTV/src/backend"
& .\WEB_STTV\data\.venv\Scripts\python.exe -B -m sttv.schema_generation
```

Research and `language/keywords/` remain available but are not builder inputs. The working directory may still contain old reports and the registry from earlier stages; current code neither reads nor updates them.

## Errors and publication

Syntax errors, unavailable sources, expansion errors, damaged nodes, and invalid history links block publication. An unknown game name, repeated field, or unevaluated ordinary variable is not itself an error.

A processing failure preserves the previous successful database. Prepared JSON is validated, written to a temporary file, read back, and used to replace the destination. Database and report are published separately: a report failure after database replacement returns failure with `database_written: true`.

Report version 2 includes selected, parsed, and failed file counts, node counts, inline statistics, diagnostics, and source SHA-256 hashes. `sources` paths are relative to `STELLARIS_ROOT`; `inline_sources` paths are relative to `INLINE_SCRIPTS_DIR`. Node counts include scalar keys and values but exclude history.

## Verification

Initial results are under `data/stage6/`; the previous audit after excluding scripted effects is under `data/stage6/without_scripted_effects/`. Future corpus audits after excluding static variables write reports and lists under `data/stage6/without_scripted_libraries/`. Original lists in `data/text_frequency/` are preserved. Run automated checks from the repository root:

```powershell
$env:PYTHONPATH = "$PWD/WEB_STTV/src/backend;$PWD/WEB_STTV/src/backend/tests"
& .\WEB_STTV\data\.venv\Scripts\python.exe -B -m unittest discover -s WEB_STTV/src/backend/tests -v
& .\WEB_STTV\data\.venv\Scripts\python.exe -B WEB_STTV/src/backend/tests/database/audit_build.py
& .\WEB_STTV\data\.venv\Scripts\python.exe -B WEB_STTV/src/backend/tests/script/audit_corpus.py
```

- All 111 baseline tests passed; after removing previous mechanisms and adding new checks, all 78 current tests passed.
- Technology set: 35 files, 67,513 nodes, and 301 expanded calls from 10 templates; no errors or warnings.
- Every persisted tree field was compared against parser objects independently of the serializer. Rebuilding produced the same SHA-256. Sources and templates remained unchanged.
- Database size: 107,520,690 bytes, approximately 102.5 MiB. The reference build took 62.181 seconds in the current environment while the corpus audit ran in parallel; this is a measurement, not a timing guarantee.
- Full `common/` and `events/` audit: 1,583 files and 3,681,397 nodes passed JSON writing, reading, and history checks. The directory of 631 templates was excluded from independent inputs; two documentation TXT files were explicitly excluded. The same 22 inputs failed, with file names and error codes matching stage five. The frequency and both scalar lists matched byte for byte. Details are in `data/stage6/corpus_report.json` and `acceptance_report.json`.

- After excluding scripted effects, all 80 tests passed. Repeat audit: 1,542 successful files, 3,510,653 nodes, and 20 previously known failed inputs. Excluded 43 effect files and 631 inline templates; the two documentation TXT files remain skipped. There are no new failures, and technology selection is unchanged. Sources, templates, and previous research lists are preserved. Results: `data/stage6/without_scripted_effects/corpus_report.json`.

- After adding the `trait_bg_active_glow` exception, all 17 targeted syntax/configuration tests passed. The actual `01_trait_colors.txt` parsed; its JSON passed schema validation and round-trip loading, preserving color values. Unconfigured names without `=` remain rejected. The full audit was not rerun; the previous corpus report is preserved. Targeted report: `data/stage6/known_input_issues/validation_report.json`.

- After connecting the exception file, all 87 tests passed. Three tradition files (`01_cloning.txt`, `01_mutation.txt`, `01_purity.txt`) passed complete parsing, expansion, JSON schema validation, and history checks: 75 calls from 16 templates, four references to the permitted extensionless file, and no expansion errors. Checked exact permissions, absence of alternative lookup, configuration failures, preserved provenance, cycles, and template-root confinement. Game sources and templates remained unchanged; the full corpus was not rerun. Report: `data/stage6/inline_exceptions/validation_report.json`.

## Limitations and subsequent stages

The complete database is loaded into memory. JSON size reflects detailed trees and node provenance; compression, indexes, and splitting into multiple files were not added.

Known stage-five syntax and expansion limitations remain. The corpus audit may complete partially and does not publish a partial working database. A successful technology build does not imply support for every game script.

Enrichment, RU/EN names, evaluation, dependencies, UI, and portable distribution require subsequent specifications. In-game verification is unnecessary for this operation: it reads files without modifying the game or mods.
