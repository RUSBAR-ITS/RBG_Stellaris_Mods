# WEB_STTV — fifteen localized databases

## Contents

- [Running](#running)
- [Configuration and format](#configuration-and-format)
- [Objects and localization](#objects-and-localization)
- [Import exceptions](#import-exceptions)
- [Publication and reports](#publication-and-reports)
- [Verification](#verification)

## Running

Implementation of [stage 12](TZ_BACKEND_STAGE_12_EN.md). From `WEB_STTV`:

```powershell
$env:PYTHONPATH = 'src/backend'
& ./data/.venv/Scripts/python.exe -B -m sttv.database_sets
```

An installed Python with project dependencies can replace the virtual environment path. `--variables` and `--config` select settings. Generation is explicit; the frontend never invokes it. Rebuild version 5 sets.

## Configuration and format

- `config/datasets.json`: shared registry of fifteen roles, directories, root types and identities, consumed by the backend, schema generator and frontend.
- `global_variables.json`: source roots, relative directories and `WORK_DIR`.
- `config/backend.json`: each member's sources and outputs, plus shared parser settings.
- `config/enrichment/localization.json`: languages, priorities and references to separate `config/enrichment/targets/<kind>.json` rules.

Databases use `sttv.parse_database`, version `6`, with `{kind, set_id}` metadata. Formatting is UTF-8 without BOM, Unicode, LF, two spaces and a final newline. The shared `set_id` derives from canonical member contents; formatted files retain the complete tree and provenance.

Roles: `technologies`, `components`, `buildings`, `megastructures`, `ship_sizes`, `starbase_levels`, `starbase_modules`, `starbase_buildings`, `terraform`, `deposits`, `pop_jobs`, `economic_categories`, `scripted_actions`, `on_actions`, `events`.

## Objects and localization

RU/EN names and descriptions reside in `enrichments.localization`. Targets may have both roles, one role, or no text. Russian priorities remain `RU_LOC_TIER_1` → `RU_LOC_TIER_2` → `RU_LOC_TIER_3`; English uses `EN_LOC_TIER_1`. Static references expand while dynamic substitutions remain intact.

Named definitions retain their IDs; events use their direct `id` field, while their root key identifies the event type. Duplicate real IDs within one role are diagnosed. Every conditional event description retains a separate address. Hidden events may have no localization.

Repeated `terraform_link` definitions retain their addresses without invented game IDs; `from` and `to` are localized. Same-name `on_actions` fragments are not merged. Service definitions with no text targets are valid. Game conditions are not evaluated.

## Import exceptions

`config/parser/source_exceptions.json` contains three narrowly scoped rules for four files. They correct one exact script-value separator, bind missing `RELIC` from the supplied `SELECTED_RELIC`, and supply the approved temporary `RANDOM = 0`. Conditions, provenance and logging are documented in the [addendum](SOURCE_IMPORT_EXCEPTIONS_EN.md).

Parameter names are case-insensitive. Structural expansion of `effect = no` retains the original argument in history; it neither executes the effect nor asserts engine behavior. A composed static reference resolves when all environments find the same declaration; different local declarations still produce an error.

## Publication and reports

Results reside in `WORK_DIR/databases/<kind>.json`; reports reside in `WORK_DIR/reports/`. Each member has build and localization reports. `database_set.json` is the aggregate report, not a sixteenth database. It includes durations, sizes, document/object/text-target counts, warnings, input hashes and publication results.

The coordinator prepares members sequentially and verifies unchanged inputs before publication. Preparation errors preserve previous databases. Individual files are replaced atomically; the complete set is published sequentially. Failures between replacements are reported, and the frontend rejects mixed `set_id` values.

## Verification

The full build on 2026-11-18 succeeded: 450 documents, 15,599 definitions and 22,345 localization targets, with no errors or skipped documents. All seven previously problematic files are included. All 1,625 input files were verified unchanged. All 203 Python tests passed, covering repeated definitions, text targets, exceptions, reproducibility, failure of the last member and partial publication; all 18 schemas match generator output.

| Database | Documents | Definitions | Localization targets |
| --- | ---: | ---: | ---: |
| `technologies` | 35 | 679 | 885 |
| `components` | 55 | 1506 | 1506 |
| `buildings` | 28 | 498 | 519 |
| `megastructures` | 30 | 164 | 164 |
| `ship_sizes` | 40 | 319 | 319 |
| `starbase_levels` | 8 | 41 | 41 |
| `starbase_modules` | 10 | 130 | 130 |
| `starbase_buildings` | 4 | 117 | 117 |
| `terraform` | 3 | 259 | 518 |
| `deposits` | 26 | 593 | 593 |
| `pop_jobs` | 22 | 367 | 367 |
| `economic_categories` | 8 | 270 | 270 |
| `scripted_actions` | 6 | 56 | 106 |
| `on_actions` | 4 | 489 | 0 |
| `events` | 171 | 10111 | 16810 |

Zero text targets for `on_actions` is expected. Targets include variants and individual text nodes; one target may contain a name and description in both languages.

Exceptions were applied 40 times: `RELIC` 30 times, temporary `RANDOM = 0` 9 times, and the extra separator once. In addition to these reported transformations, build reports contain 50 warnings about unused inline arguments. Localization has 218 missing-field records and 52 unresolved-reference records across both languages and all targets. These are source warnings; missing strings are not invented and unresolved references are retained.

The set occupies **11,762,739,507 bytes (10.95 GiB)**; `events.json` occupies **9,386,721,787 bytes (8.74 GiB)**. The full build took **5,490.835 seconds (91.5 minutes)**. Schema checks on the large event tree and preservation of complete provenance make this stage expensive in time and memory; these costs were not separately optimized.

Details: [aggregate report](../data/reports/database_set.json), [acceptance summary](../data/stage12/build_acceptance.json), and [interface verification](frontend/FRONTEND_STAGE_3_EN.md#verification-and-limitations). Game files were unchanged; running Stellaris was not required for these checks.

[Русская версия](BACKEND_STAGE_12_RU.md).
