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
- `parser`: selection of four configurations from `config/parser/` — lexical notation, constructs, logical operators, and inline expansion. Each supports `product` and `work` bases.
- `outputs`: `database.json` and `reports/build_report.json`, relative to `WORK_DIR`.

Require `STELLARIS_ROOT`, `WORK_DIR`, `INLINE_SCRIPTS_DIR`, and variables named by selected sources. Workshop and localization remain in the shared variables file for future enrichment but are optional for this operation.

Sources remain inside `STELLARIS_ROOT`. Selection includes `category` and `tier` as ordinary files. Identical physical files are processed once; conflicting encodings for one file produce an error. Relative paths determine document order. An empty script is persisted with empty `items`; selecting no files is an error.

Templates under `INLINE_SCRIPTS_DIR` are excluded from independent selection. They are read only through reached calls. The template cache lasts for one operation; the next build reads current files.

`WORK_DIR` defaults to `data`; another relative or absolute path inside the repository is supported. Writes cannot overlap sources, code, configuration, or other protected material. Source TXT files are not copied into the working directory.

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
| `schema_generation/` | Generation of seven structural application schemas |

Retained schemas are `backend.schema.json`, `database.schema.json`, `report.schema.json`, and four `parser_*.schema.json` files. The database schema describes node kinds and metadata without enumerating permitted game names. The generator does not read the game. From the repository root:

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

Working results are under `data/stage6/`; original lists in `data/text_frequency/` are preserved. Run automated checks from the repository root:

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

## Limitations and subsequent stages

The complete database is loaded into memory. JSON size reflects detailed trees and node provenance; compression, indexes, and splitting into multiple files were not added.

Known stage-five syntax and expansion limitations remain. The corpus audit may complete partially and does not publish a partial working database. A successful technology build does not imply support for every game script.

Enrichment, RU/EN names, evaluation, dependencies, UI, and portable distribution require subsequent specifications. In-game verification is unnecessary for this operation: it reads files without modifying the game or mods.
