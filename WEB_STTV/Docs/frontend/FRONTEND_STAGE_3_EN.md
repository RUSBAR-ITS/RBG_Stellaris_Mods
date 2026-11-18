# WEB_STTV — interface 0.0.3 and opening fifteen databases

## Contents

- [Running and selecting files](#running-and-selecting-files)
- [Streaming reads](#streaming-reads)
- [Catalogs and localization](#catalogs-and-localization)
- [Diagnostics](#diagnostics)
- [Verification and limitations](#verification-and-limitations)

## Running and selecting files

Run `npm run dev` from `WEB_STTV`, then open `http://127.0.0.1:5173/`. To use the prepared Node.js installation:

```powershell
$env:PATH = "$PWD/data/frontend-tools/node-v24.22.3-win-x64;$env:PATH"
npm.cmd run dev
```

Click Open database set and select all **fifteen JSON files in `data/databases/`**, built by [stage 12](../BACKEND_STAGE_12_EN.md). Do not select `reports/database_set.json`. Filenames and selection order are arbitrary: roles come from `dataset.kind`. Database version 6 and one shared `set_id` are required.

Startup and refresh neither read databases nor invoke generation. Cancelling the picker preserves the current screen. Selecting a new set replaces the previous one; Cancel terminates loading, and Retry repeats the entire selection.

## Streaming reads

Direct `File.text()` failed on the formatted 831 MiB component file: Chromium returned an empty string. The user approved streaming processing in the [specification](TZ_FRONTEND_STAGE_3_EN.md#approved-addition-streaming-json).

The Worker processes files sequentially. The first pass obtains metadata and document counts; the second sends individual documents to the adapters. UTF-8 and JSON are parsed in chunks without retaining a giant string or a complete file tree. Coordinates and expansion history are unnecessary for the current UI catalogs and remain available in the source JSON.

Cross-object references are checked after processing the complete set. The main thread receives one `ready` containing compact catalogs, localization and diagnostics. A late file error never publishes partial results. Source JSON files remain read-only.

## Catalogs and localization

Existing technologies, components, buildings and links remain available. Twelve new roles have `definitions` and `definitionIndex`: type, game ID where applicable, `{database, pointer}` and text references. Terraforming retains every transition and localized endpoint class; handlers retain all same-name fragments; events retain their game `id` and separate conditional descriptions.

All roles share one `database` localization index. Matching strings merge origins; conflicting resolved text stops opening. Missing translations produce warnings, while missing required enrichments produce errors. Technology layout, variants, themes, language and tooltips retain their previous behavior.

## Diagnostics

The status panel shows the phase, file number and localized role during preparation. Incorrect file counts include the expected count from the registry. The menu exports a technical report with files, roles, phase and error address where available. Unsupported versions, mixed sets, repeated roles and duplicate real IDs block opening.

## Verification and limitations

All 31 controlled streaming JSON and adapter tests, the TypeScript/Vite build and eleven controlled browser scenarios passed. Separate checks covered the 831 MiB component file, cancellation and reopening. Late file errors, incorrect member counts, mixed sets, duplicate IDs and localization conflicts do not publish partial results.

**The complete published set of fifteen databases opened successfully in the built interface** on Chromium 159.0.8154.6: 11,762,739,507 bytes were processed in **264.60 seconds (4 minutes 25 seconds)**. Files were supplied in reverse order. All 679 cards appeared; RU/EN, day/night themes, the Titans tooltip and variants were checked. One Worker was used and there were no page errors. Night-mode and tooltip screenshots were visually inspected.

At the end of the browser test, `performance.memory` reported 86.4 MB of used main-thread JS heap. This is neither peak consumption nor total browser memory; Worker memory was not separately measured. Opening time applies to this machine and dataset, not a performance guarantee.

Two additional real-data tests passed: 615 technology links, 720 object upgrade links and 138 technology upgrade pairs were preserved; all 60 previously researched examples for 16 technologies were confirmed. The compact main-thread result is 52,192,376 bytes when serialized as UTF-8 JSON; this is data size, not JS memory usage. The index retains 214 `missing_localization` warnings with no conflicting found texts. See the [catalog report](../../data/stage12/frontend_catalog_report.json).

Artifacts: [browser report](../../data/stage12/browser_real_set.json), [night interface](../../data/frontend-tests/real-night.png), and [tooltip](../../data/frontend-tests/real-tooltip.png). Database sizes and build time are recorded in the [backend guide](../BACKEND_STAGE_12_EN.md#verification).

New chain rules, screens for new objects, images, portable distribution and state persistence are outside this stage.

[Русская версия](FRONTEND_STAGE_3_RU.md).
