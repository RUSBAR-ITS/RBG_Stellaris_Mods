# First backend stage — operation and structure

## Contents

- [Stage result](#stage-result)
- [Environment setup](#environment-setup)
- [Running and rebuilding](#running-and-rebuilding)
- [Settings and outputs](#settings-and-outputs)
- [Modules and strict model](#modules-and-strict-model)
- [Diagnostics and persistence](#diagnostics-and-persistence)
- [Validation](#validation)
- [Implementation boundaries](#implementation-boundaries)

## Stage result

**Historical guide.** Describes the implementation before the syntax-tree database transition. Current operation and format: [stage six](BACKEND_STAGE_6_EN.md).

The approved [first stage](TZ_EN.md#3-first-backend-stage--database-building) is implemented as a standalone Python JSON database builder. It reads technologies, categories, tiers, and RU/EN names from configured directories, validates the [database model](DATABASE_MODEL_EN.md), and saves the database and a separate report.

The builder does not modify sources. Parsing and conversion run in memory; source files and the intermediate parse tree are not copied into the working directory. The research audit is not a builder input.

## Environment setup

Run the following commands in PowerShell from `WEB_STTV`. Verified environment: Windows, Python **3.14.6**, `jsonschema==4.26.0`. This stage requires an installed Python interpreter; portable packaging belongs to subsequent stages.

The dependency is pinned in [requirements.txt](../src/backend/requirements.txt). JSON Schema Draft 2020-12 validation uses [jsonschema](https://pypi.org/project/jsonschema/); its API is described in the [official documentation](https://python-jsonschema.readthedocs.io/en/stable/validate/).

Prepare the environment inside the default working directory:

```powershell
New-Item -ItemType Directory -Force data/tmp | Out-Null
$env:TEMP = (Resolve-Path data/tmp).Path
$env:TMP = $env:TEMP
python -m venv data/.venv
./data/.venv/Scripts/python.exe -B -m pip install --no-cache-dir --disable-pip-version-check -r src/backend/requirements.txt
```

The environment has already been prepared in the current workspace. Changing `WORK_DIR` changes builder output placement but does not move the Python environment.

## Running and rebuilding

Default invocation:

```powershell
./data/.venv/Scripts/python.exe -B src/backend/main.py
```

Every invocation rereads sources and fully rebuilds the database. Run the command again after changing directories or priorities. The previous database is not used to fill gaps.

Alternative configuration files can be passed explicitly:

```powershell
./data/.venv/Scripts/python.exe -B src/backend/main.py --variables global_variables.json --config config/backend.json
```

Default configuration and relative `WORK_DIR` values are based on the product directory, not the terminal's current directory. Relative `--variables` and `--config` arguments follow normal terminal-relative resolution.

The CLI returns **0** on success and **1** on build failure. It prints the complete JSON report to stdout on success and stderr on failure. Invalid command-line arguments are handled by `argparse` with exit code 2.

The future service integration entry point is `sttv.builder.build(variables_path, config_path)`: two configuration paths in, a report dictionary out. It does not depend on the CLI or UI. To validate a completed database without sources, use `sttv.database.validation.validate_database(database, registry)`; it returns without a value on success and raises `BuildError` for a model violation.

## Settings and outputs

| File | Purpose |
| --- | --- |
| [global_variables.json](../global_variables.json) | Source roots, localization paths, `WORK_DIR` |
| [config/backend.json](../config/backend.json) | Reading profiles, language-source order, output filenames |
| [schemas/database.schema.json](../schemas/database.schema.json) | Closed database schema, format 1 |
| [schemas/backend.schema.json](../schemas/backend.schema.json) | Closed build-configuration schema |
| [schemas/report.schema.json](../schemas/report.schema.json) | Closed report schema |
| `profiles/stellaris_4_5_4.json` (removed in stage six) | Declared contexts, commands, arguments, operators, and scopes |

Primary outputs are `data/database.json` and `data/reports/build_report.json`. Stage two also writes `data/rules/script_rules.json` and `data/reports/generation_report.json`; their names are configured under `rules`. Their relative names are configured under `outputs`; `WORK_DIR` determines their absolute location.

`TECH_PATH` resolves within `STELLARIS_ROOT`. Relative localization directories also resolve against the game root. Global-variable substitution does not execute code; unknown names and cycles are rejected. An unavailable configured source is an error, while a missing individual translation is a warning.

Output paths cannot escape `WORK_DIR`, overlap each other or configuration files, or enter source directories or the product's code, schemas, configuration, or documentation. Changing the working directory does not move or delete previous data.

The root `.gitignore` excludes `data/`. An alternative working directory requires its own ignore rule.

## Modules and strict model

| Modules in `src/backend/sttv/` | Responsibility |
| --- | --- |
| `sources/settings.py`, `sources/files.py` | Configuration, path resolution, reproducible file selection and reading |
| `script/parser.py` | Structural parsing; tokenization and configuration are separate [stage-three modules](BACKEND_STAGE_3_EN.md) |
| `technologies/`, `script/variables.py` | Closed field contracts, record and local-variable conversion |
| `script/rules.py`, `rules/` | Nested-command validation against an explicit registry |
| `localization/names.py` | Names by key and priority, retaining source markup |
| `common/schema.py`, `database/validation.py` | JSON Schema, contextual validation, references and prerequisite graph |
| `common/`, `database/storage.py` | Strict JSON, writing, output replacement, diagnostics |
| `builder.py` | Build-stage orchestration |

`main.py` contains only the command-line entry point. Shared reading, serialization, validation, and path-resolution logic lives in separate functions.

The working registry is generated from an explicitly selected JSON profile, without automatic expansion from encountered words. It covers researched constructs in the current sources, including scope changes, numeric references, and parameters of known inline inclusions. The builder neither reads nor executes external script bodies; the separate analyzer is documented in the [second-stage guide](BACKEND_STAGE_2_EN.md). Unknown commands, invalid arguments, operators, or scopes cause failure.

Eligibility conditions, weights, and `technology_swap` remain separate from `prerequisites`. Variants are nested within the base technology. Repeated values retain their source lines; numeric references resolve only through unambiguous local definitions in the same file. External values remain `resolved: null`.

## Diagnostics and persistence

The report contains status, file and record counts, errors, warnings, and `database_written`, `registry_written`, `generation_report_written`. Diagnostics have a stable code, stage, message, and available source coordinates. The report is not embedded in the database.

| Situation | Result |
| --- | --- |
| Unknown field or command, broken reference, syntax/schema error | Error; no new database is published |
| Different values for a selected localization key within one tier | Error; priority does not hide conflicts within a tier |
| Missing name in one language | `null` name and provenance, warning |
| Explicitly empty name | Empty string with provenance; no lower-tier substitution |
| Ambiguous, cyclic, or external numeric variable | Reference with `resolved: null`, warning |
| Repeated singleton field | `occurrences` retaining source order and lines, warning |

The database is serialized to a temporary file beside its target, reread, and validated. An atomic file replacement then publishes it. A failure before replacement preserves the previous database; an unsuccessful initial build does not create a partial database. The report is also prepared before database replacement.

The database and report are separate files. If final report replacement fails after database replacement, the caller receives an error with `database_written: true`. A configuration error that occurs before a safe report path has been established is returned through the API/terminal without writing a disk report.

## Validation

Run synthetic checks from `WEB_STTV`:

```powershell
./data/.venv/Scripts/python.exe -B -m unittest discover -s src/backend/tests -v
```

All test fixtures and outputs use `data/tests/`; these tests do not require the game.

Historical first-stage results on 2026-11-15; the current 79 tests and vanilla corpus audit are documented in the [third-stage guide](BACKEND_STAGE_3_EN.md):

| Check | Result |
| --- | --- |
| Synthetic scenarios | **29 passed** |
| Current-source build | **679 technologies, 206 variants, 13 categories, 6 tiers** |
| RU/EN names | **885 of 885 records in each language** |
| Build errors | **0** |
| Warnings | **1,265 external variables, 7 repeated fields** |
| Comparison with independent research parsing | IDs, locations, and **7,337 field occurrences** match |
| Repeated build | Byte-identical database |
| Source integrity | Hashes of **741 files** unchanged |
| Python file sizes, including tests | All below 200 lines; no exceptions |
| Completed-database validation | Passes without reading sources |

The builder processed 509 files. Hash verification covered all 741 files in the configured profiles, including lower localization tiers that the builder can skip after finding all names.

Working evidence is saved in `data/reports/validation_report.json`, `data/reports/unittest_output.txt`, and `data/reports/build_report.json`. The additional comparison script at `data/validate_stage_one.py` is a working artifact using the research audit only as an independent validation reference; the runnable product does not depend on it.

## Implementation boundaries

The data builder is complete. The UI, directory-picker dialog, HTTP service, images, and portable distribution are not implemented yet. Localization includes names only. Game conditions, costs requiring external variables, and probabilities are not evaluated; engine behavior has not been tested.

The next stage requires a separate bilingual specification under the [stage-organization rule](TZ_EN.md#organizing-specifications-by-stage).

[Руководство на русском](BACKEND_STAGE_1_RU.md) · [Project overview](../README_EN.md).
