# Stellaris Parser — game data preparation

## Contents

- [Installation](#installation)
- [Localization](#localization)
- [Game scripts](#game-scripts)

## Installation

Install the tool and document format library from the monorepo root using Python 3.12+. The installed module accepts commands from any working directory.

```powershell
python -m pip install ./Instruments/Document_Package ./Instruments/Stellaris_Parser
```

## Localization

`prepare` accepts a source configuration and an output directory. `localization.languages` lists headers and tiers in descending priority. `localization.directories` maps each tier to its directory. Relative source paths resolve against the configuration file. The output contains `manifest.json`, `batches/` and `prepare_report.json`. [WEB_STTV configuration](../../WEB_STTV/config/parser_sources.json)

```powershell
python -m stellaris_parser prepare --config WEB_STTV/config/parser_sources.json --output TMP/WEB_STTV/packages/localization
```

## Game scripts

Set `roots` to the selected mod and game directories in priority order. The first file at a relative path wins. `parse` only requires `roots` in the configuration. Set `syntax_directory` to select another rules directory. `libraries.json` configures library paths and encoding. The result includes the expanded syntax tree, static variable substitutions and expansion metadata. [Rules](stellaris_parser/config/libraries.json)

```powershell
python -m stellaris_parser parse --config WEB_STTV/config/parser_sources.json --output TMP/WEB_STTV/physics.json common/technology/00_phys_tech.txt
```
