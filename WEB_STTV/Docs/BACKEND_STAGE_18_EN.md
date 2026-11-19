# Stage 18 — technology image preparation

## Contents

- [Result](#result)
- [Running](#running)
- [Configuration and storage](#configuration-and-storage)
- [Modules and diagnostics](#modules-and-diagnostics)
- [Validation](#validation)
- [Limitations](#limitations)

## Result

Implemented the approved [stage 18 specification](TZ_BACKEND_STAGE_18_EN.md). Preparation reads technology documents from an existing set, converts game DDS images into PNG and adds RU/EN category names. The other 14 document kinds are not loaded by this operation. Game sources remain read-only.

The current **`data/stage17/database_set` is already prepared** for [frontend 0.0.8](frontend/FRONTEND_STAGE_8_EN.md). The browser opens this directory without accessing the game. Rebuilding the source AST or recalculating the tree is unnecessary.

## Running

From `WEB_STTV`, with `src/backend/requirements.txt` installed:

```powershell
$env:PYTHONPATH="$PWD/src/backend"
python -B -m sttv.enrichment.assets --storage data/stage17/storage.json
```

On this computer, `data/.venv/Scripts/python.exe` can replace `python`. Pillow 12.2.0 is pinned in requirements; [DDS reader documentation](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#dds).

Without `--storage`, the set address comes from `config/enrichment/assets.json`, normally through `config/storage.json` to `data/database_set`. Additional arguments: `--variables` and `--config`. Default full report: `data/reports/assets.json`.

For an explicit new build including images:

```powershell
python -B -m sttv.database_sets --rebuild-libraries --prepare-assets
```

With a current library, replace `--rebuild-libraries` with `--reuse-libraries`. The build publishes its localized source set, then calls the same resource operation. If the second step fails, the report records failure; the source set remains published and resource preparation can be retried independently. Failure to publish the resource operation itself preserves the previous snapshot.

Python API: `prepare_assets(variables_path=None, config_path=None, *, storage_path=None)` from `sttv.enrichment.assets`. It returns a report without an interactive console dialog. Opening the application never invokes preparation.

## Configuration and storage

`config/enrichment/assets.json` defines sources, image selection fields, inheritance rules, PNG options, resource directory, reuse, localization and reporting. Translation priorities come from the existing localization configuration.

| Data | Location and contents |
| --- | --- |
| Image | `assets/<SHA-256>.png`, original dimensions and transparency |
| Technology/variant reference | `enrichments.presentation = { format_version: 1, icon_asset_id: ID or null }` |
| Shared registry | `manifest.presentation.files`: relative path, hash, MIME, bytes, width, height |
| Sources | `manifest.presentation.sources`: relative game path, source hash, result ID |
| Cost icons | `manifest.presentation.research_icons`: physics, society, engineering |
| Categories | `manifest.presentation.categories`: ID → RU/EN, raw/resolved string and provenance |

Base images use `icon` or the technology ID. `inherit_icon = yes` uses the base image; otherwise variants use their own `icon` or `name`. The missing-`inherit_icon` behavior is configured. Identical PNG content is deduplicated regardless of source filename.

Repeat preparation compares source bytes, settings and decoder version, then the prepared file size and hash. Changes to sources or parameters update the affected resource. `reuse: false` disables conversion reuse. Unchanged documents are not rewritten.

The presentation revision participates in the set snapshot. The new enrichment is excluded from semantic tree input hashes; existing rules for other enrichments are preserved. Manifest format remains version 1 with an additional block. There are 34 generated schemas in total.

## Modules and diagnostics

`enrichment/assets/` separates settings, representation selection, conversion/cache, categories and publication. It uses the existing set reader, localization mechanism and atomic manifest replacement. Schemas are declared in `schema_generation/assets.py`; resource auditing lives in `storage/assets.py`.

The report includes counters, consumed inputs, document coverage and timings. `references` counts converter requests, `reused` counts unique source paths and `unique_images` counts unique prepared content. These figures therefore differ. Inheriting variants refer to the already selected base image.

Missing/undecodable images produce warnings and `null`. Path errors, corrupt immutable files or publication failures stop the operation. The frontend shows a placeholder and retains diagnostics. Full audit now also checks presentation references and every declared PNG:

```powershell
python -B -m sttv.storage audit --manifest data/stage17/database_set/manifest.json --report data/stage18/full_audit.json
```

This command reads the entire set; it is provided for a separate audit and is not invoked when opening the interface.

## Validation

Results for the current implementation:

| Check | Result |
| --- | --- |
| Technologies / variants | 679 / 206; all 885 references checked |
| Prepared images | 791 PNG files, 5,032,468 bytes (4.80 MiB) |
| Categories | 13, all with RU/EN names |
| Missing sources | 0 |
| Repeat preparation | 12.69 s; 805 source images reused; 0 conversions, document writes or image bytes written |
| Preservation | All 35 documents match prior versions after removing only the new `presentation`; localization and trees are preserved |
| Selective reading | 35 of 450 documents; other kinds were not read |

Repeat timing includes input verification and localization loading on this computer, with resources already prepared; it is not the initial conversion time. Results: `data/reports/assets.json`, `data/stage18/acceptance.json`.

Passed 12 resource/storage checks, 8 set-build checks and 3 schema-generation checks. Covered dimensions and alpha, deduplication, inheritance, RU/EN priorities, changed source/settings, damaged PNG and interrupted manifest replacement. Audited all 791 images and 35 technology documents; a repeat full audit of the other 415 documents was not run in this iteration.

## Limitations

Resources cover technologies, variants and three research icons only. Conversion does not upscale source pixels: enlarging small game icons may look pixelated. No Stellaris launch is needed; card appearance is reviewed in the browser.
