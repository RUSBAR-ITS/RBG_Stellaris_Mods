# Document and game image loader

## Contents

- [Running the loader](#running-the-loader)
- [Uploading images over SSH](#uploading-images-over-ssh)
- [Inputs and documents](#inputs-and-documents)
- [Publication and recovery](#publication-and-recovery)
- [Checks](#checks)

## Running the loader

From the repository root, install the loader and its package reader into your Python environment. Use Python 3.10 or later.

```powershell
python -m pip install ./Instruments/Document_Package ./WEB_STTV/src/loader
sttv-loader create --config WEB_STTV/config/loader.json --profile network
sttv-loader load --config WEB_STTV/config/loader.json --profile network
sttv-loader verify --config WEB_STTV/config/loader.json --profile network
```

`create` adds missing collections and preserves existing contents. `load` reads prepared JSON and replaces the configured collections after verification. For a full reload of the test VM use its maintenance certificate to drop the database, then run these three commands. [Stand maintenance](../../../Instruments/WEB_STTV/README_EN.md#full-test-server-reload)

The `network` profile uses Vault and a certificate from the Windows certificate store to obtain the MongoDB password and trusted CA. The `local` profile reads the password from the configured environment variable and the CA from a file. Both use TLS and SCRAM-SHA-256. [Configuration](../../config/loader.json)

## Uploading images over SSH

Use the image extra on the Windows workstation with Stellaris installed. From the repository root run

```powershell
python -m pip install ./Instruments/Document_Package "./WEB_STTV/src/loader[images]"
sttv-loader upload-images --config WEB_STTV/config/loader_images.json
```

`game_root` points to the Stellaris installation and `descriptor_directory` to the prepared DLC descriptor JSON files. The command selects technology and category icons, the three research area icons, seven inline game-text icons and declared DLC thumbnails from the game. Prepared PNG files appear under `run_directory/artifacts/` at game-relative paths. [Configuration](../../config/loader_images.json) · [Selection rules](Docs/TZ_IMAGE_UPLOAD_EN.md) · [Inline icons](../../Docs/frontend/TZ_TOOLTIP_INLINE_ICONS_AND_TRAITS_EN.md)

The SSH user needs write access to the existing `destination_root`. The supplied configuration targets `/home/ansible/web-sttv/assets` on `stellaris-wiki`. Ubuntu needs `python3`. The loader verifies the host key against `known_hosts` and retrieves SSH credentials through the Windows certificate and Vault. The command runs independently of MongoDB and document import.

A repeat invocation compares per-file SHA-256 digests and transfers only changes. After an interrupted transfer, rerun the same command. Each invocation writes a report under `run_directory/reports/upload-images-*.json` with selected, transferred and skipped counts by group, errors and elapsed time.

## Inputs and documents

Policies and bypass types use the game key of the root block. The `policies` collection stores options and the flags they set. The `bypass` collection stores bypass definitions with their game localization keys. [Specification and checks](Docs/TZ_POLICIES_AND_BYPASS_EN.md)

`input_root` and `scratch_directory` are relative to the configuration directory. Each entry in `sources` maps an input path relative to `input_root` to a collection. Script directories are scanned recursively for JSON. The most specific mapping applies to a nested directory or individual file.

| `identity` value | Document and key |
| --- | --- |
| `key` | Definition keyed by its block name |
| `field` | Match the field name (such as an event's `id`) case-insensitively. Preserve its value verbatim as `_id`. Multiple matching fields in one object are ambiguous. |
| `anonymous`, `fragments` | Definition keyed by `{root, file, item}`. The position is zero-based and precedes filtering |
| `file` | All entries of a single DLC descriptor keyed by `{root, file}` |
| `package` | Localization package entry with its original composite key |

`root_types` restricts the block names to import. `containers` specifies a path through wrapping blocks. The game collection exposes `source`, `pointer` and the queryable `tree`. The configured `provenance` collection stores source locations under the same key. The `history_collection` stores expansion history once per file, including files with zero imported objects.

## Publication and recovery

The loader stages collections, checks the final BSON size, reads back the data and compares the reconstructed trees. Each document has a 16 MiB limit. Collection renames occur in sequence. External readers can see collections from different versions during promotion.

After failure, the `sttv__publication` journal lets the loader restore the previous set or finish cleaning up a committed load. After an abrupt exit, repeat `load` from the same workspace with the same `scratch_directory`. The separate `verify` command checks the published data in read-only mode.

## Checks

Run the image preparation checks with `python -m unittest discover -s WEB_STTV/src/loader/tests -p "test_image*.py" -v`. For the transfer check, set `STTV_IMAGE_TEST_CONFIG` to an image configuration targeting a dedicated writable Ubuntu test directory. The test leaves its PNGs in a unique subdirectory there. It changes one image, truncates a transfer during replacement, checks the previous target digest and retries.

Run `python -m unittest discover -s WEB_STTV/src/loader/tests -v` from the repository root. To enable the integration test, set `STTV_LOADER_TEST_CONFIG` to a configuration for a dedicated empty database whose name starts with `sttv_loader_test_`. The test recreates that database and drops it on completion.

Five tests passed on local MongoDB 8.0.12, including source location write failure, interrupted publication and recovery. The installed CLI imported and verified 2 technologies, 15 events, 19 terraforming transitions, 36 DLC entries, 1 descriptor and 1,000 localization entries. Five additional large events were written to MongoDB and reconstructed for comparison. The largest provenance document among the five was 14,729,102 bytes for `nomads.4100`.
