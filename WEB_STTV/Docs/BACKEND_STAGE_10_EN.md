# Stellaris Technological Tree View — database localization, stage ten

## Contents

- [Process and invocation](#process-and-invocation)
- [Settings and sources](#settings-and-sources)
- [Object and text selection](#object-and-text-selection)
- [Database storage and reading](#database-storage-and-reading)
- [Refresh and diagnostics](#refresh-and-diagnostics)
- [Modules and schemas](#modules-and-schemas)
- [Verification](#verification)
- [Limitations](#limitations)

## Process and invocation

This stage implements the approved [localization specification](TZ_BACKEND_STAGE_10_EN.md). A separate operation reads a completed database, selects technologies and conditional variants, obtains RU/EN names/descriptions, and stores them beside objects in the same database. Game scripts do not need expanding again. The general-purpose parser retains its behavior; possible reference-specific database cleanup belongs to future stages.

From the repository root, with the prepared Python environment:

```powershell
$env:PYTHONPATH = "$PWD/WEB_STTV/src/backend"
& WEB_STTV/data/.venv/Scripts/python.exe -B -m sttv.enrichment.localization --config WEB_STTV/data/stage10/localization.json
```

The verification configuration points to `data/stage10/database.json` and `data/stage10/localization_report.json`. Without `--config`, defaults are `config/enrichment/localization.json`, database `data/database.json`, and report `data/reports/localization_report.json`. `--variables` replaces the `global_variables.json` path; default product files resolve independently of the current working directory. Exit code is 0 for success and 1 for failure; there is no interactive dialogue.

Programmatic invocation:

```python
from sttv.enrichment.localization import enrich_localization

result = enrich_localization(variables_path, config_path)
```

Both arguments are optional. The result is a report containing status, `database_written`, paths, counters, and diagnostics. The previous standard database is not automatically replaced and may have an older format. Before enriching it, run an ordinary rebuild: `python -B WEB_STTV/src/backend/main.py`. The completed stage-ten verification database does not need that rebuild.

## Settings and sources

Settings reside in [config/enrichment/localization.json](../config/enrichment/localization.json), separate from the eight parser configurations:

| Group | Purpose |
|---|---|
| `database`, `report` | Paths relative to configurable `WORK_DIR`; update the database in place |
| `selection` | `TECH_PATH`, pattern `*.txt`, excluding subdirectories by default |
| `keys` | Variant block `technology_swap`, field `name`, suffix `_desc` |
| `languages` | `l_russian` / `l_english` headers and ordered lists of source variables |
| `reading` | Recursive `*.yml` reading, `utf-8-sig` encoding |
| `references` | Delimiter `$`, ordinary key pattern, limits of 64 levels and 1,000,000 field characters |
| `inherit_description` | Inherit missing variant descriptions |

RU: `RU_LOC_TIER_1` → `RU_LOC_TIER_2` → `RU_LOC_TIER_3`. EN: `EN_LOC_TIER_1`. Paths are set in [global_variables.json](../global_variables.json); relative localization paths resolve against `STELLARIS_ROOT`, with `${...}` expanded by the shared configuration mechanism. Priority applies independently to every key, including references inside selected text.

Each configured source must exist and be readable. If a localization mod is unwanted or absent, remove its source explicitly from configuration. An existing empty directory is valid. Game-definition directories are not opened: `TECH_PATH` only matches paths of already persisted documents.

## Object and text selection

Select root block assignments in files directly under `TECH_PATH`; the `tech_` prefix is unnecessary. `category/` and `tier/` documents remain in the database without this stage's localization. For variants, read the single direct scalar `name` field in a direct `technology_swap` block; repeated names do not merge objects.

Base names use the technology identifier, descriptions the identifier plus `_desc`. Variants use their `name` and `name + "_desc"`. If a variant-specific description is absent across all tiers of a language, use its base description and retain a pointer to the base technology. Existing empty descriptions remain. Names do not inherit, and Russian text is not replaced with English.

Ordinary static `$key$` references expand recursively. Dynamic `[...]`, formatted `$KEY|...$`, icons, and game markup remain. Unknown ordinary tokens stay in the text and produce diagnostics. Original strings, whitespace, internal quotes, and sequences such as `\n` are retained. The number after a YML colon does not define priority.

Identical duplicates are allowed with deterministic file/line selection. Conflicting text in a selected tier blocks publication. Unreachable-key and overridden-tier duplicates are listed in the report without rejecting selected text.

## Database storage and reading

The `sttv.parse_database` format is **version 4**. Ordinary builds emit unenriched databases of this version. The nine syntax node kinds and game tree remain unchanged; an assignment may have this service section:

```text
node.enrichments.localization.ru.name
node.enrichments.localization.ru.description
node.enrichments.localization.en.name
node.enrichments.localization.en.description
```

Each field includes `requested_key`, the actually selected `key`, original `raw`, resolved `text`, source `{tier, file, line}`, `inherited_from`, and `unresolved_references`. `inherited_from` is a JSON Pointer from the database root to the base technology, or `null`. When inheriting, the request remains variant-specific while source and text describe the base technology. Missing text is `null`; found empty text is `""` with a populated source.

`sttv.database.storage.read_database(path)` checks schema, expansion history, field consistency, and inheritance without game access. Older formats require rebuilding. Analytical traversal does not enter `enrichments`; game nodes, keys, values, order, coordinates, and history remain unchanged.

## Refresh and diagnostics

Repeat execution replaces only localization. If selection narrows, old results are removed from excluded objects; no matching technologies is an error without database replacement. A complete parser rebuild does not transfer previous enrichment: run it separately afterward.

The database is written to a temporary file, reread and validated, then atomically replaces the previous file after input consistency checks. Checks cover database, configuration, and read-localization hashes, plus source file inventories. Writes stay inside repository `WORK_DIR`, separate from protected inputs. Concurrent writers to one database are unsupported.

The `sttv.localization_report` format, version 1, contains input and before/after database hashes, settings, selected sources for reached keys, duplicates, RU/EN counters, timing, and diagnostics. Reading errors, selected-text conflicts, cycles, limits, and invalid objects block publication. Missing text and unresolved ordinary tokens produce warnings. Successful inheritance has a separate counter and is not an error.

Database and report are not one transaction. If replacement succeeded but writing the report failed, the operation returns failure with `database_written: true`. Configuration failure before resolving a safe report path returns diagnostics programmatically/in the console without writing a file.

## Modules and schemas

Code lives in `src/backend/sttv/enrichment/localization/`, separating settings, target selection, line reading, indexing, references, attachment, input checks, reporting, and coordination. Shared configuration variable expansion moved to `common/variables.py`; the parser uses the same mechanism. Persisted enrichment validation is in `database/enrichment.py`.

All **13 schemas** are generated from `sttv/schema_generation/`. Added `localization.schema.json` and `localization_report.schema.json`; updated `database.schema.json`. Generate with `python -B -m sttv.schema_generation`, setting `PYTHONPATH` as in the invocation example. No game-command whitelist is required.

## Verification

- **184 tests passed**, including 30 new checks for priorities, text/escaping, references, inheritance, object selection, unchanged trees, repeatability, corruption, and publication failures. Results: `data/stage10/unit_tests.json`.
- Real-data verification: 35 files, 679 technologies, 206 variants, 885 names and descriptions per RU/EN language. Each language inherits 81 variant descriptions from base technologies. All 3,540 fields, sources, and reference chains were independently checked; trees and history remain unchanged. No errors or warnings occurred.
- Repeat enrichment produces an identical database; sources and previous outputs are preserved. Size increased from 138,156,360 to 140,937,166 bytes. Results: `data/stage10/real_validation_report.json`; operational report: `data/stage10/localization_report.json`.
- Python sources passed syntax checks; files do not exceed 160 lines. Previous outputs and manually curated frequency lists are not this stage's output destinations.

## Limitations

Only technologies and variants are localized. Full dictionaries are not copied into the database; reference sources are listed in the report. Images, UI, browser formatting, and dynamic substitution evaluation are not implemented. Game and localization mod files are read without changes. Full-corpus and in-game checks are not performed for this stage.

[Руководство на русском](BACKEND_STAGE_10_RU.md) · [Project overview](../README_EN.md).
