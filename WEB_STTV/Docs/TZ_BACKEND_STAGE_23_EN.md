# Stage 23 — separating the parser, loader and server

## Contents

- [Objective](#objective)
- [Components](#components)
- [MongoDB connections](#mongodb-connections)
- [Working directory and cleanup](#working-directory-and-cleanup)
- [Document package](#document-package)
- [Transition from stage 22](#transition-from-stage-22)
- [Acceptance](#acceptance)

## Objective

**Approved.** Extract Stellaris Parser as an independent tool for the game and mods. Separate the WEB_STTV loader and server. Use the stage 22 dictionary to verify JSON preparation on the game workstation, publication in MongoDB and retrieval of a document by the server.

Stage 22 used a single entry point. The implementation and verification commands are in the [stage 23 guide](BACKEND_STAGE_23_EN.md).

## Components

Paths are relative to the monorepo root.

| Component | Responsibility | Input and output |
| --- | --- | --- |
| `Instruments/Stellaris_Parser/` — Stellaris Parser | Reads sources from the game and the selected mod, parses scripts, expands insertions and substitutes static variables. For localization it retains every definition and selects the source string according to configured priorities. | Source directories, parser configuration and output directory → JSON package and report |
| `WEB_STTV/src/backend/sttv/loader/` — loader | Accepts `load` and `verify` to transfer finished documents, compare contents and publish a collection. | Explicit package path and `WEB_STTV/config/loader.json` → published collection or verification result |
| `WEB_STTV/src/backend/sttv/server/` — server | Serves HTTP requests and reads published MongoDB documents. Localization provides the first read test. | `WEB_STTV/config/server.json` and `wiki.localization` → document by `_id` |

Stellaris Parser owns its `stellaris_parser` Python package, entry point, syntax rules, configuration, tests, dependencies and usage guide. The calling project supplies its sources, priorities and output location. The parser must run independently of WEB_STTV from any working directory without importing `sttv` or PyMongo or connecting to Vault. The versioned package format connects the parser to the loader.

Technology relationships, DLC filtering and localization enrichment belong to the server. Once game objects have been imported, the frontend will retrieve the tree through the server API. In stage 23 the server reads the published localization dictionary from MongoDB.

## MongoDB connections

The loader and server each read their own configuration. In both, the `mongodb` block specifies an active profile and named `local` and `network` profiles. Each profile defines the host, port, database, user, authentication database and mechanism, trusted CA and secret reference. The client uses the selected profile and includes its name in connection errors. Passwords and private keys stay outside configuration files and reports.

| Component | Default profile on the test system | Details |
| --- | --- | --- |
| Windows loader | `network` → `192.168.1.36:27017` | Gets the password and CA through its configured Vault access. The command takes the input package path. |
| Ubuntu server on the MongoDB host | `local` → `127.0.0.1:27017` | Uses a secret accessible to the service and the test system's public CA at `/etc/wiki-tls/ca.pem`. The HTTP bind address and port are configured separately. |

Both test profiles use `wiki` for the database and `authSource`, SCRAM-SHA-256 and TLS with hostname verification. Loopback refers to the host running the component. A server running on another host selects `network` in its own configuration.

## Working directory and cleanup

The default WEB_STTV working directory is `TMP/WEB_STTV/` relative to the monorepo root, or `D:\Repos\RBG_Stellaris_Mods\TMP\WEB_STTV` on the workstation. The path is configurable. Document preparation, reports, loader scratch files, Vite and Playwright use dedicated subdirectories. Each tool cleans only its own output. Other mods pass their own output location to Stellaris Parser. The Ubuntu server gets its runtime paths from its configuration.

The user will manually clear the contents of `WEB_STTV/data/` and `TMP/WEB_STTV/`. The tools and reference inputs below now reside outside these directories. As part of stage 23, update `WORK_DIR`, frontend build paths, test commands and current instructions. After cleanup, prepare the localization JSON package in the new working directory. The game installation, other `TMP` directories and published MongoDB collections are outside the cleanup scope.

| Item | Location and use |
| --- | --- |
| Markdown checks | [Instructions](../../Instruments/Documentation/README_EN.md). The command takes the project root. |
| Syntax, frequency, scalar and inline research | [Stellaris Parser tools](../../Instruments/Stellaris_Parser/tools/README_EN.md). Pass the source and report directories on the command line. |
| Empire condition inventory and DLC matrix checks | [WEB_STTV tools](../../Instruments/WEB_STTV/README_EN.md). The caller selects the snapshot. |
| 60 upgrade witnesses, 679 parent decisions and 12 control pairs | [Tree reference fixtures](../tests/fixtures/technology_tree/README_EN.md). The frontend test and backend check use permanent paths. |

The retained reference fixtures can be used to compare results when tree calculations and DLC filtering move to the server.

## Document package

A package is a movable directory containing a manifest and batches of finished JSON documents. The manifest declares the common format version, logical collection name, total document count and ordered batches with counts and SHA-256 digests. Each batch path resolves within the package directory. The server address, database name and credentials belong to the loader configuration. The first destination is `wiki.localization`.

The local parser assigns each document its final `_id`. The loader preserves its type, value and field order for composite identifiers. Verification compares the full document by `_id`. It must work independently of physical order in MongoDB and of the batch that supplied a document. The same format supports a composite localization identifier and a string technology identifier.

## Transition from stage 22

1. Extract common package reading and writing from the localization import. Keep game document construction, translation priorities, conflict handling and preparation reporting with the local component. The [stage 22 specification](TZ_BACKEND_STAGE_22_EN.md) defines the localization document fields.
2. Split source settings from destination settings. Provide a local preparation command and separate `load` and `verify` loader commands taking an explicit package path. Document commands and dependencies for each part.
3. Move Vault connectivity, staging collection writes, full comparison and publication by rename into the loader. Use a loader-owned temporary location for the public CA so a package can be opened read-only.
4. Create the server entry point and implement a MongoDB lookup by compound localization `_id`. Deployment of a new public API and server-side enrichment require their own specification.
5. Prepare the dictionary in the common format and compare it with the stage 22 baseline. The first technology import follows in the next stage. A small fixture with a string `_id` and a nested document is enough to exercise a second data kind here.

## Acceptance

- Run Stellaris Parser in a separate environment without the WEB_STTV tree and prepare the dictionary. Compare `definitions`, `selected`, raw markup and priorities with the baseline. Configure a different mod directory and parse a sample with the same parser.
- From a different directory, load the transferred package with MongoDB and Vault access. Keep the game, Workshop, parser globals and original working directory unavailable in this scenario. Package contents are identical before and after the operations.
- From the Windows workstation, first run `verify` against the existing `wiki.localization`. The stage 22 snapshot has 153,242 RU documents, 150,258 EN documents and 453,781 definitions. Then check repeated publication and readback. A mid-batch failure leaves the last published collection available.
- Use the same loader for the second-kind fixture in an isolated test collection. Check shuffled batch order, nested data, a duplicate `_id`, a damaged batch and removal of an obsolete record upon replacement.
- Verify independent selection of both connection profiles in each component. Exercise the Windows network connection and use the server component on the MongoDB host to read the RU and EN `tech_titans` documents. Report which connections were exercised on the test system.
- Start acceptance with an empty `TMP/WEB_STTV/` working directory. Prepare, verify and load the localization package, then read the published strings through the server. Check frontend build and test paths with fixtures. All operations must complete without recreating `WEB_STTV/data/`. Server startup and API requests must not initiate an import.
