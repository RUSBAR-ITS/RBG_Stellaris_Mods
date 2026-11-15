# Stellaris Technological Tree View — concept

## Contents

- [Concept status](#concept-status)
- [Purpose and primary view](#purpose-and-primary-view)
- [Local launch and portability](#local-launch-and-portability)
- [Three data processes](#three-data-processes)
- [Internal data](#internal-data)
- [Sources and localization](#sources-and-localization)
- [First launch](#first-launch)
- [Updating and rebuilding the database](#updating-and-rebuilding-the-database)
- [Open decisions](#open-decisions)

## Concept status

Project: **Stellaris Technological Tree View**, directory: `WEB_STTV`. This document describes the standalone application concept and **is not a technical specification**. The technical foundation and coding principles remain in the [general specification](TZ_EN.md).

**User decision dated 2026-11-15:** JSON containing parsing results becomes the primary database. Mandatory conversion to a strict technology domain model and validation of game names against a profile are dropped from the target design. Enrichment by specific fields and rules belongs to later stages.

The transition is implemented under the approved [stage-six specification](TZ_BACKEND_STAGE_6_EN.md). The current process, format, and verification results are described in the [guide](BACKEND_STAGE_6_EN.md).

The [previous database model](DATABASE_MODEL_EN.md) and [stage-five guide](BACKEND_STAGE_5_EN.md) describe the historical implementation. Game files are read-only. The interface and portable distribution are not implemented yet.

## Purpose and primary view

The reference application helps users explore Stellaris technologies and their relationships using data from a selected game installation.

The primary view is an interactive dependency tree made of technology cards. Cards use the corresponding vanilla images. The tree is built from the internal database derived from game data and updated after the database is rebuilt.

The exact card content, presentation of details, branch layout, and controls remain to be discussed. A separate catalog view, search, and filters have not been defined yet.

## Local launch and portability

The target platform is Windows. A portable distribution is envisaged as one directory containing an executable, settings, and application data. The user does not need to install a separate web server.

The discussed launch approach is an executable that opens the web interface in a browser and starts the required local service. The first specification part selects Python for processing and the local service, TypeScript and HTML/CSS for the interface, and PyInstaller in `onedir` mode for packaging. The builder dependency and verified environment are listed in the [guide](BACKEND_STAGE_1_EN.md#environment-setup); UI and service libraries are not selected yet.

Settings reside in the application directory; the completed database, reports, and future prepared images reside in configurable `WORK_DIR`, defaulting to `data` within the application. Code is divided into `src/frontend` and `src/backend`. Internal references use relative paths. External source paths are chosen by the user; moving the application may require updating those paths before the next refresh.

A completed database with future prepared images allows browsing without access to the original game directories. During development, the working folder remains inside the repository; `data` also serves product checks. Earlier research materials remain in `TMP/WEB_STTV/` and are not application dependencies.

## Three data processes

Parsing results are persisted as JSON and become a self-contained, manageable database. Subsequent actions use this structure without requiring game definitions to be parsed again.

| Process | Input | Output |
| --- | --- | --- |
| Reading and parsing | Selected sources and parser settings | JSON containing parsed structure, expanded inclusions, and provenance; separate diagnostics |
| Enrichment — later stages | Saved JSON, processing rules, and necessary additional sources | Data prepared by specific fields and rules |
| Presentation — later stages | Data prepared for viewing and images | The tree, cards, and user interaction |

```mermaid
flowchart LR
    sources[Selected sources] --> parse[Parsing and inclusion expansion]
    parse --> database[JSON containing parsing results]
    database --> enrich[Enrichment by fields and rules]
    enrich --> view[Tree and cards]
```

Saving parsing results does not depend on localized names, computed values, or a prepared tree. Enrichment runs as separate actions. Specific fields, rules, action order, and storage of their results will be agreed later. `inline_script` expansion remains part of source processing; call history stays separate from game-data analysis.

## Internal data

The primary database is a JSON representation of parsing results. It preserves constructs supported by the parser: names, operators, values, nesting, order, repeated entries, and provenance. An unknown field or command name alone does not justify rejecting storage. Closed technology-field lists and command profiles no longer define the target storage foundation.

Format `sttv.parse_database` version 1 stores source-file trees in the `documents` array, preserving node kinds, order, and repetition. It is defined in the [stage-six specification](TZ_BACKEND_STAGE_6_EN.md#5-persisted-json-format). This is a convention for representing parser output; storage does not require listing all game fields and commands. Reading, syntax, and expansion errors continue to produce diagnostics; incomplete output must not be published as a success.

| Material | Purpose |
| --- | --- |
| Source settings | Selected paths and source priorities |
| Parsing-results database | Saved definition structure and provenance |
| Service metadata | Inline-call history and source mappings outside game-data analysis |
| Enriched data | Names, relationships, and other information from later stages; placement not yet selected |
| Processing report | Checks and diagnostics separate from the database |
| Prepared images | Interface images from later stages |

JSON containing parsing results is persisted; original game files are not copied into the product. The previous technology model does not constrain the new format. The user distribution still starts with an empty database populated from selected sources.

## Sources and localization

The user selects the directories from which the application obtains game data. The developer's particular paths are not mandatory application settings.

Localization belongs to subsequent enrichment and retains an ordered list of sources. Priority applies **to each key individually**: the value from the highest-priority source containing that key is selected. If the key is absent, lookup continues in the next source. This allows incomplete translations to be supplemented by subsequent sources. The selected text's provenance is retained.

The current Russian translation order in this repository provides an example:

1. `Localisation_Base/1-Prio_Russian_Localization_Fix_RE/replace/`.
2. Other files under `Localisation_Base/1-Prio_Russian_Localization_Fix_RE/`.
3. Vanilla localization under `Localisation_Base/2-Prio_Vanilla/`.

This example illustrates configurable priorities. It does not make a particular localization mod a mandatory application dependency.

The known installed game path for research in the current environment is `E:\SteamLibrary\steamapps\common\Stellaris\`. It is strictly read-only. Individual technology definitions reside in `common/technology/`; related variables, localization, and images are also read from sources as processing requires.

Support for modded game definitions and their merging rules has not been defined. Localization priorities do not themselves establish override order for game code.

## First launch

Intended workflow for the future application:

1. The user launches the application; an empty database opens source setup.
2. The user selects the required directories.
3. The application reads and parses sources, then saves the results as JSON.
4. Separate actions enrich data by agreed fields and rules, requesting additional sources where needed.
5. The reference opens when the data required for viewing is ready. Enrichment, images, and the interface belong to later stages; exporting structure alone does not imply a ready tree.

Subsequent launches use saved results. Working with these results does not require selecting source directories or parsing the game again.

## Updating and rebuilding the database

Reparsing rereads selected sources in read-only mode and creates new JSON results. This requires source-directory access. After a game update, reparsing uses the updated files.

Enrichment works with saved JSON. Additional sources are needed only for the relevant actions, such as localization lookup. Changing enrichment rules alone does not require reparsing game definitions when the required structure is already saved.

Reading, parsing, or saving failures must not replace the working database with partial output. Checks, enriched-data updates after reparsing, and status presentation will be defined in the relevant stage specifications. Validating game commands against the old profile is not a prerequisite for saving structural results in the new concept.

## Open decisions

The following topics remain for further discussion:

- Technology card content and details, tree navigation, search, and filters.
- Interface languages and display of missing names; retrieving RU/EN names belongs to enrichment.
- Presentation of availability conditions, conditional technology variants, and links to other game objects.
- Handling mods, DLC, and multiple source sets.
- Enrichment actions, their order and rules, and storage and updates of their results.
- The interface framework, graph library, specific versions of selected technologies, build details, and Windows environment requirements.
- Future interface presentation of source errors, unresolved references, and interrupted processing.

These topics do not automatically add features. Implementation scope will be recorded separately in a technical specification after discussion.

[Концепт на русском](CONCEPT_RU.md) · [Project overview](../README_EN.md).
