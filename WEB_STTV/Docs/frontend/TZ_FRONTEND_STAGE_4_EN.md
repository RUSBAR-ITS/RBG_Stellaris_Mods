# Frontend stage 4 — opening a database directory through its manifest

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Directory selection](#2-directory-selection)
- [3. Preparing data](#3-preparing-data)
- [4. Reading and hashing](#4-reading-and-hashing)
- [5. Snapshots and references](#5-snapshots-and-references)
- [6. Worker and application state](#6-worker-and-application-state)
- [7. Diagnostics and reports](#7-diagnostics-and-reports)
- [8. Tests and acceptance](#8-tests-and-acceptance)

## 1. Status and scope

**Approved by the user on 2026-11-19 and implemented.** Completed verification, running and limitations are documented in [the stage guide](FRONTEND_STAGE_4_EN.md).

Replace selection of 15 monolithic JSON files with opening a directory in the new format. Preserve cards, RU/EN names and descriptions, variants, theme, menu, opening states, cancellation, retry and reports. Sorting and placement remain unchanged; using stored `parent_tech`/`children` for a new grid and invoking Python from the browser remain separate stages.

Do not add automatic building, startup opening, cross-session permission restoration, HTTP API or browser writes to the database. Do not support the old 15-file opening route alongside the new one. Previous specifications remain historical records.

## 2. Directory selection

The existing “Open database set” action opens a single-folder picker. Expect the set root containing the manifest. Startup and page refresh read nothing before an explicit user action.

Use `<input type="file" webkitdirectory>` and a relative-path file map. The browser provides `File` entries with `webkitRelativePath`, allowing reconstruction of the selected directory structure. Enumerating files does not itself read their contents. References: [directory selection](https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/webkitdirectory) and [relative paths](https://developer.mozilla.org/en-US/docs/Web/API/File/webkitRelativePath).

Remove one common leading directory segment and look for the manifest only at the selected root. Obtain its name from shared storage configuration, default `manifest.json`; do not duplicate it in components. If directory selection is unsupported, show a localized message rather than falling back to a monolithic database.

Check all declared paths against selected files. A missing document makes the set incomplete even if the current field does not need it. Equal filenames in different subdirectories are valid; conflicting normalized relative paths are errors. Ignore unrelated files and unreferenced old versions without reading them. Do not recursively discover manifests or guess the intended set.

A manifest path cannot grant access to an arbitrary disk file: use only user-selected `File` objects. Reject URLs, absolute paths and root escapes. Do not send data to external services.

## 3. Preparing data

Initial opening reads the manifest and all `technologies` documents needed by the existing adapter. Prepare the full technology catalog, variants, technology prerequisites and localization from them. The other 14 kinds are unnecessary for the current field and must not be read solely to register the set or calculate counts.

All 15 kinds appear in the manifest catalog; availability and loading are distinct states. File, type and ID information is available immediately, while content requires an explicit consumer request to the reader. Kind/document state distinguishes `not_loaded`, `loading`, `loaded`, `failed`. Do not represent an unloaded kind as a successfully read empty object array.

The reader supports loading a complete kind and objects by `ObjectRef`: find required documents through the index and read each once. Fragment kinds return all records for an ID; anonymous objects use `NodeRef`. These are internal interfaces; no new building or event browsing buttons are added.

Component, building and other-kind adapters retain their extraction behavior but run on demand rather than being mandatory opening steps. Prepare cross-kind evidence only after its required inputs have loaded. Extraction rules remain unchanged. Field readiness means its technology data is ready, not that the entire set has been parsed.

Configure initial kinds in `config/frontend/opening.json`, proposed `initial_datasets = ["technologies"]`. Do not introduce another hardcoded list of 15 kinds; use the existing shared registry. The new manifest and reference contract follows the backend specification.

## 4. Reading and hashing

Retain Worker streaming JSON parsing and adapt it to standalone documents. One byte pass computes SHA-256, decodes UTF-8 and extracts a compact projection. Remove the former full-content pass for the header followed by another for objects: the manifest provides metadata, and the main pass verifies the document envelope.

For large documents, do not use `File.text()` or accumulate an entire `ArrayBuffer`. Unneeded node projections and history remain in the file without being copied to the main thread. Fields unnecessary for viewing are not deleted from the database itself.

Native `SubtleCrypto.digest()` requires a complete buffer rather than streaming input, as stated in its [documentation](https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/digest). Propose a small hashing module using incremental SHA-256 from `@noble/hashes`: [library API](https://github.com/paulmillr/noble-hashes#implementations). Import only the required function and pin a compatible version in dependencies and the lockfile during implementation. Do not implement a custom cryptographic algorithm.

A file projection becomes available only after successful size, hash, envelope and indexed-entry checks. A hash mismatch is a set-read error with an exact location. Unread documents remain `not_checked`. A separate backend command audits the complete set; no audit button is added in this stage.

Retain one Worker; ten processes refers to Python. A new browser Worker pool is out of scope. Cache verified compact data only within the currently opened snapshot and release it when closing/changing the set; later sessions recheck used files.

## 5. Snapshots and references

Pin manifest `set_id` and `snapshot_revision` after reading. `SttvNodeRef` becomes `{database, document_id, pointer}` instead of addressing a global document position. Update adapters, localization, inherited descriptions, reports and diagnostics. Variants use nested pointers within the same document.

Do not mix files from a new snapshot into an opened one. An on-disk manifest change does not trigger automatic reopening or recalculation. After external enrichment the user selects the directory again. If a previously selected `File` becomes unavailable, report the error and offer reopening.

Language, theme and variant switching continue using prepared technologies without rereading documents. Localization remains on database objects and is not duplicated in the manifest. Calculated relationships remain in source files without becoming a new layout algorithm in this iteration.

## 6. Worker and application state

The opening message supplies the selected file map and operation ID. The Worker reads the manifest, checks the catalog and loads initial kinds. Add kind/object loading requests carrying request IDs and snapshot revisions; responses belong only to that snapshot. Coalesce simultaneous requests for the same document to avoid duplicate reads.

`ready` contains the technology catalog, inventory of all manifest kinds, loading states, loaded-object localization and diagnostics. Exclude complete ASTs and unloaded-kind content. Metadata presence in `ready` must not imply full database verification.

Retain existing UI states and actions. Initial opening publishes the field only after all its required inputs are ready. Cancellation stops the Worker and reading; ignore stale responses. Retry uses files selected in the current session; closing/selecting a new directory releases the previous snapshot. A subsequent loading failure is not a successful empty result and does not destroy previously verified technology data.

Add RU/EN labels, hints and messages to existing dictionaries; reuse UI components and styling tokens. The status bar reports manifest selection/reading and required-document preparation without a new panel or redesign requirements.

## 7. Diagnostics and reports

Update the report with selected root name, revisions, declared kinds/documents/objects, actually loaded and verified documents, unloaded kinds, bytes read, timing and errors. Distinguish indexed object counts from loaded object counts.

Use `NodeRef` and relative paths. Include expected/actual values for hash mismatch. Distinguish missing files, invalid formats, ambiguous IDs, invalid references and corruption. Retain existing prerequisite diagnostics, including unsupported negative requirements.

## 8. Tests and acceptance

Test root selection, picker cancellation, missing manifest, incomplete set, extra files, equal filenames in different folders, path conflicts and incompatible versions. Add new-format synthetic sets and adapter/protocol/localization tests.

Instrument reads: opening reads no bytes from the other 14 kinds; event requests open only containing documents; repeated requests do not reread them. Corrupt loaded files cause errors; unused corrupt files are never reported verified. Check SHA-256 against Python byte fixtures, including UTF-8 and chunk boundaries.

Test large documents without full-string loading, interrupted streams, responsiveness, cancellation and stale-response rejection. Test snapshots changing between openings, nested variants, inherited descriptions, anonymous objects and every `on_actions` fragment.

On the real stage 17 set, compare technology catalogs and texts with the previous frontend; verify language, theme, menu, tooltips, variants and report saving. Separately request remaining kinds and compare compact data with previous results, normalizing only references. Run typecheck, build, affected TypeScript tests and browser scenarios.

Measure opening time, actual bytes read and memory. Manifest counts do not replace measurements. Completed verification and measurements are documented in the stage guide. Update bilingual launch instructions and changelog and increment the frontend patch version during implementation.

[Backend specification](../TZ_BACKEND_STAGE_17_EN.md) · [Historical stage 3](TZ_FRONTEND_STAGE_3_EN.md) · [Русская версия](TZ_FRONTEND_STAGE_4_RU.md).
