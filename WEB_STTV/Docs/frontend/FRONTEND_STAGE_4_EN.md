# Frontend 0.0.4 — opening a database set directory

## Contents

- [Starting and selecting a directory](#starting-and-selecting-a-directory)
- [Loading and references](#loading-and-references)
- [Verification](#verification)
- [Limitations](#limitations)

## Starting and selecting a directory

Implemented [frontend stage 4](TZ_FRONTEND_STAGE_4_EN.md) together with [backend stage 17](../BACKEND_STAGE_17_EN.md). From `WEB_STTV`, run `npm ci`, then `npm run dev`; open `http://127.0.0.1:5173/`.

On this computer, Node.js is available in the working directory:

```powershell
$env:PATH="$PWD/data/frontend-tools/node-v24.22.3-win-x64;$env:PATH"
$env:npm_config_cache="$PWD/data/npm-cache"
npm run dev
```

Click “Open database set” and select **`data/stage17/database_set`** for this iteration's acceptance set. Future builds normally use `data/database_set`, configured in `config/storage.json`. Select the root containing `manifest.json`, not `documents`, individual JSON files or reports.

Startup and refresh neither open data nor invoke the builder. Select the directory again after backend enrichment. Cancel, retry, replacement and report export remain in the menu. Browsers without directory selection receive a dedicated RU/EN message.

## Loading and references

The Worker reads the manifest and verifies that every declared file is present. It then loads kinds configured in `config/frontend/opening.json`, initially technologies only. Other files, including unreferenced old versions, are not read merely to register the set. Kinds and documents have loading states; reports separately record hash verification coverage.

SHA-256 uses `@noble/hashes` 2.4.0 during UTF-8 streaming parsing. Full AST and history are not transferred to the main thread; names, descriptions, variants and compact catalogs are retained. Visible cards do not imply that other kinds were checked.

The internal controller exposes `loadDatasets(kinds)`, `resolveObjects([{database,id}])` and `resolveNodes([{database,document_id,pointer}])`. The latter loads indexed root objects, including anonymous terraforming transitions. All fragments of one `on_actions` ID are returned. Indexed documents are read once per successful snapshot request sequence.

Requests carry operation IDs, request IDs and snapshot revisions. Lazy-loading failures retain prepared technologies; partial results are not published. Report version 3 includes the root, revisions, indexed counts, loading states, hash coverage, bytes, timing and document-qualified diagnostics.

## Verification

TypeScript and the production build passed, alongside 37 synthetic tests. Two real-file checks run separately and also passed. Coverage includes adapters, streaming JSON and hashing across UTF-8 boundaries, cancellation, stale responses, retries, fragments, anonymous objects, unused-file corruption and preservation of prepared data after lazy-loading failure.

All 14 Chromium browser scenarios passed, including the real set, menu, language, theme, variants, tooltips, scrolling, report export, cancellation and a large document with `File.text()` and `File.arrayBuffer()` forbidden. Parsing and hashing do not require a full file string.

Real initial opening prepared 679 technologies: 35 of 450 documents verified, 415 unread. A separate Node.js loader measurement took 2.601 s; browser opening took 4.105 s, including 3.526 s reading documents. Explicitly requesting all remaining kinds during acceptance took 164.587 s total, read 11,049,350,511 bytes and retained 1506 components, 498 buildings, the other 12 catalogs and all 60 control upgrade witnesses. These are different scenarios; normal opening does not load all kinds.

The browser reported 37,300,000 bytes of used main-thread JS heap after opening; this does not measure Worker memory. A 732,381,133-byte event document streamed in 14.202 s with a matching byte hash. These are individual measurements on the current computer without clearing the OS cache.

Reports: `data/stage17/browser_real_set.json`, `frontend_catalog_report.json`, `large_stream_probe.json`; test logs are in the same working directory.

## Limitations

Selecting 15 old monolithic files has been removed. Directory access is not retained between sessions and the browser does not write databases. Grid changes, sorting and using stored parents for placement remain separate work. Unverified files may contain errors discovered only on request or by the backend's full audit.

[Русская версия](FRONTEND_STAGE_4_RU.md) · [Backend](../BACKEND_STAGE_17_EN.md).
