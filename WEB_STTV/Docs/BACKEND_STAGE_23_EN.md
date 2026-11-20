# Stage 23 — parser, loader and MongoDB server

## Contents

- [Components](#components)
- [Windows commands](#windows-commands)
- [Reading on Ubuntu](#reading-on-ubuntu)
- [Publication](#publication)
- [Verification](#verification)

## Components

Stellaris Parser prepares documents locally and assigns `_id`. The loader publishes a package directory to a collection. The server reads a document by `_id`. The first collection is `wiki.localization`. [Parser](../../Instruments/Stellaris_Parser/README_EN.md) · [Specification](TZ_BACKEND_STAGE_23_EN.md)

## Windows commands

Run from the monorepo root in an active Python 3.12+ environment. Before replacing a published dictionary, `verify` compares it with the package. `load` replaces the collection mapped to the logical package name in the loader configuration.

```powershell
$project = (Resolve-Path WEB_STTV).Path
$globals = Get-Content "$project/global_variables.json" -Raw | ConvertFrom-Json
$work = [IO.Path]::GetFullPath((Join-Path $project $globals.WORK_DIR))
$package = Join-Path $work 'packages/localization'

python -m pip install ./Instruments/Document_Package ./Instruments/Stellaris_Parser ./WEB_STTV/src/backend
python -m stellaris_parser prepare --config "$project/config/parser_sources.json" --output $package
python -m sttv.loader verify --config "$project/config/loader.json" --package $package
python -m sttv.loader load   --config "$project/config/loader.json" --package $package
python -m sttv.server --config "$project/config/server.json" --profile network read ru tech_titans
```

On a dedicated loader workstation install `Instruments/Document_Package` and `WEB_STTV/src/backend`. Copy the package and pass its absolute path to `--package`. The `network` profile retrieves the password and public CA through Vault with Windows certificate-store authentication. The loader places its temporary CA in its own scratch directory. [Loader configuration](../config/loader.json)

## Reading on Ubuntu

Install the same two packages in the service environment. Supply the `wiki` password via `STTV_MONGO_PASSWORD`. The `local` profile in `server.json` selects `127.0.0.1:27017`, SCRAM-SHA-256 and `/etc/wiki-tls/ca.pem`. HTTP defaults to `127.0.0.1:8788`. `GET /api/localization/ru/tech_titans` returns a document with `selected` and `definitions`. An absent key returns HTTP 404. [Server configuration](../config/server.json)

```sh
python -m sttv.server --config /path/to/server.json read en tech_titans
python -m sttv.server --config /path/to/server.json serve
```

## Publication

`manifest.json` contains the `stellaris.documents.v1` format, logical collection, total document count and ordered batch paths with counts and SHA-256 hashes. The loader checks hashes while reading, inserts into a private staging collection and compares documents by typed BSON `_id`. Composite key field order is significant. Following verification, MongoDB atomically renames the collection. A failed staging operation leaves the prior collection available.

## Verification

Windows preparation processed 706 files and 453,781 definitions. The original collection comparison, two publications and final comparison covered 303,500 documents. The transferred package retained identical file hashes. Reads exercised `local` on Ubuntu and `network` on Windows. The selected `tech_titans` strings were «Титаны» and `Titans`. An isolated collection covered string identifiers, nested data, shuffled batches, duplicates, damaged input and obsolete record removal. Frontend fixtures passed 71 unit and 24 browser checks. Nine browser and four unit scenarios require separate file inputs and were skipped.

The parser was installed independently of WEB_STTV and PyMongo. Checks covered mod file priority, nested expansion and static substitution. Parsing vanilla `00_phys_tech.txt` produced 69 top-level entries and 132 expansions. The independently installed loader completed a full comparison without the parser installed.

The earlier file-backed tree test `test_publication_reuse_force_and_other_inputs_unchanged` still expects 24 unchecked documents. Its fixture creates 30 documents. Reuse reads one and reports the remaining 29 as unchecked.
