# Stellaris Parser — game data preparation

## Contents

- [Installation](#installation)
- [Full preparation](#full-preparation)
- [Localization](#localization)
- [Game scripts](#game-scripts)

## Installation

Install the tool and document format library from the monorepo root using Python 3.12+. The installed module accepts commands from any working directory.

```powershell
python -m pip install ./Instruments/Document_Package ./Instruments/Stellaris_Parser
```

## Full preparation

Run the WEB_STTV reference profile from the monorepo root. Rebuild the libraries on the first run.

```powershell
python -m stellaris_parser prepare-all --config WEB_STTV/config/parser_sources.json --rebuild-libraries
```

On subsequent runs, `--reuse-libraries` verifies the saved libraries. The `batch.workers` setting limits the number of script workers. One additional process starts building the RU/EN dictionary at the beginning of the run. Exit code 0 means both tasks succeeded.

`TMP/WEB_STTV/database-inputs/artifacts/` contains `scripts/` with expanded TXT and DLC documents, `localization/` with the dictionary, and `libraries/` with five libraries and their manifest. The profile sets the output directories and the exact source paths or globs (`batch.sources`). [Reference profile](../../WEB_STTV/config/parser_sources.json) · [Specification](Docs/TZ_PREPARE_ALL_EN.md)

## Localization

`prepare` accepts a source configuration and an output directory. `localization.languages` lists headers and tiers in descending priority. `localization.directories` maps each tier to its directory. Relative source paths resolve against the configuration file. The output contains `manifest.json`, `batches/` and `prepare_report.json`. [WEB_STTV configuration](../../WEB_STTV/config/parser_sources.json)

```powershell
python -m stellaris_parser prepare --config WEB_STTV/config/parser_sources.json --output TMP/WEB_STTV/packages/localization
```

## Game scripts

The technology directory example can be run from the monorepo root. Check the game path in `roots`. Put a mod root first to override game files. Configured output paths resolve relative to the configuration file. [Example configuration](examples/parser.json)

```powershell
$config = 'Instruments/Stellaris_Parser/examples/parser.json'
python -m stellaris_parser parse-batch --config $config --rebuild-libraries
python -m stellaris_parser parse-batch --config $config --reuse-libraries --workers 2 common/technology/tier
python -m stellaris_parser parse --config $config --reuse-libraries --output TMP/Stellaris_Parser/run-01/artifacts/physics.json common/technology/00_phys_tech.txt
```

The first invocation prepares five library JSON files and a manifest in `artifacts/libraries`, then writes one expanded document per source under `artifacts/scripts`, preserving source-relative paths. Each main document contains `items` and its `metadata.expansions` history. The subsequent invocations verify and reuse the libraries. Rebuild after a diagnostic identifying changed library inputs.

Set `batch.directories`, `exclude_files`, `output` and `workers` to select directories, exact file exclusions, the output directory and the worker limit. Library source paths and output filenames are configured separately. [Library settings](stellaris_parser/config/libraries.json) · [Specification and acceptance criteria](Docs/TZ_BATCH_PARSE_EN.md)
