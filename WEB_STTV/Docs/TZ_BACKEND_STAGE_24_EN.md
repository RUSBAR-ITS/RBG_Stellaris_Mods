# Stage 24 — standalone MongoDB loader

## Contents

- [Purpose](#purpose)
- [Startup and data sources](#startup-and-data-sources)
- [Database and collection management](#database-and-collection-management)
- [One object per document](#one-object-per-document)
- [Game tree and source locations](#game-tree-and-source-locations)
- [Current implementation](#current-implementation)
- [Loader checks](#loader-checks)

## Purpose

**Approved.** The loader is a standalone WEB_STTV application. On an explicit user command, it reads prepared JSON files from disk and publishes documents to MongoDB. It transfers document contents without enrichment.

The agreed project root for the loader is `WEB_STTV/src/loader/`. It will contain the loader’s `pyproject.toml`, source code and tests.

## Startup and data sources

The user runs `sttv-loader` with the loader’s own configuration, `WEB_STTV/config/loader.json`. The configuration specifies the paths and names of input files or directories, their destination collections and the MongoDB connection profile. The loader opens those sources itself. The saved JSON and configuration suffice for another load. The loader runs independently of the parser process, its settings and its run information.

## Database and collection management

Give the loader a database management module. Two independent commands are proposed.

- `drop` deletes the entire database named in the selected profile. Deletion requires an explicit invocation of this command.
- `create` creates the collections listed in the configuration, including collections for empty directories. Running it again creates any missing collections and preserves existing data. Creating the first collection also creates the database. [MongoDB documentation](https://www.mongodb.com/docs/manual/core/databases-and-collections/).

Changing the game version requires a full database rebuild. The user runs `drop` to remove the entire target database, then `create` and `load` to import the new version. Within one version, the same set of JSON files can be loaded again.

The configuration explicitly maps each input directory to a destination collection. For example, `scripts/common/technology/` can map to `technologies` and `scripts/events/` to `events`. A nested directory with its own mapping, such as `technology/category/`, uses that mapping. Each file is imported under one mapping.

## One object per document

The loader identifies objects according to the input directory’s rules. One game object with its nested fields forms one MongoDB document. An input file can yield zero, one or multiple documents. For localization, the import unit remains one prepared entry with its composite `_id`.

| Source | Unit of import | Example from the prepared JSON |
| --- | --- | --- |
| Technologies | One top-level technology definition | The two definitions in `00_strange_worlds_tech.json` produce two documents |
| Events | One event definition with an `id` in its body | `apocalypse_events.json` contains 15 events. The `namespace = apoc` declaration supplies file context |
| Terraforming | Each individual `terraform_link` definition | `00_basic_terraform_links.json` contains 19 transitions. The two variable declarations in the same file supply context |

For each anonymous definition, the loader builds a technical `_id` with the fields `root`, `file`, and `item`, in that order. It takes `root` and `file` from `source.root` and `source.file` in the input JSON. The integer `item` is the definition’s zero-based index in the top-level `items` array before filtering for import.

For example, the two `pc_nuked → pc_hive` transitions in `02_special_terraform_links.json` have distinct keys. The first has `_id` equal to `{"root":"STELLARIS_ROOT","file":"common/terraform/02_special_terraform_links.txt","item":92}`, and the second has `item` equal to `167`. Rebuilding from the same JSON reproduces the keys regardless of file processing order or working directory. Reordering definitions within the source array can change their keys.

## Game tree and source locations

The loader separates the tree and its source locations when importing each script object. The rule applies to objects of every size. Prepared localization documents retain their existing format.

| Data | Storage |
| --- | --- |
| Game object | One document in the game collection. Its `tree` field contains ordinary nested BSON documents and arrays. It preserves game keys, operators, values, order, repetitions and nesting. The game collection alone supports queries on game fields. The `source` and `pointer` fields identify the input file and the object's position in it. |
| Node locations | One document with the same `_id` type and value in the associated provenance collection. The loader configuration specifies both collection names, for example `events` and `events_provenance`. Integer indices into the object's tables take the place of the parser's `origin` and `span` records in `tree`. The loader preserves the distinction between a missing field and `null`. |
| File expansion history | One metadata document per source file, including files with an empty object list. A separate collection named in the configuration uses `{root, file}` from `source` as its key. It preserves the full input `metadata` section, including expansion order, `id`, `parent_id` and insertion paths. History positions remain relative to the original file. |

Each object's provenance tables store identical entries once. This applies to `span` and `generated_span` coordinates, source roots and file paths, expansion identifiers and the `origin` records that reference them. All tables are readable BSON. The loader must be able to reconstruct the exact source node from its references for verification. Game commands whose names coincide with metadata fields remain game data.

`create` covers the configured game and metadata collections. Before publication, `load` checks the size of each complete BSON document, including its wrapper, against the 16 MiB limit. `verify` checks that the provenance belongs to the object, resolves its references and compares the reconstructed tree and file history with the input JSON. On failure, previously published trees and their metadata must remain consistent.

An in-memory check of the proposed format on the current inputs found that both documents fit the limit for each of the five events whose original trees exceeded 16 MiB. For `colony.9850`, the tree is 6.23 MiB and the provenance document is 13.84 MiB. The largest provenance document among the five is 14.05 MiB for `nomads.4100`. All five source trees were reconstructed. The largest of the 619 file history documents measured separately is 6.15 MiB.

## Current implementation

The standalone loader reads sources from its configuration. For installation, commands and verification results, see the [loader guide](../src/loader/README_EN.md).

## Loader checks

- Install only the loader and its dependencies. In a separate working directory, place the configuration and a small localization fixture at the configured input path.
- Load the fixture into an isolated collection, repeat the load with the same files, and run verification. The documents and their identifiers must match on both runs.
- Trigger a failure before publication. The destination collection must retain the previously published data.
- In a dedicated test database, create the configured collections, including an empty one. Run `create` again after inserting a document, verify it is preserved, then run `drop` and recreate the collections.
- Use small fixtures to cover multiple objects in one file, a file containing only directives, a nested directory with its own collection and two anonymous definitions with the same `from`/`to` pair. Check the number, destinations and contents of imported documents.
- Check the exact anonymous `_id` values against source positions, including a fixture with a directive before a definition. After recreating the test database, load copies of the same JSON files from a different directory in reverse file order. The set of `_id` values must match the first run.
- Query a nested game field in the MongoDB game collection. Use a fixture with repeated coordinates and a nested expansion to check deduplication, exact node reconstruction and the reference to file history. Verification must detect a broken reference. Test publication failure when writing metadata fails.
