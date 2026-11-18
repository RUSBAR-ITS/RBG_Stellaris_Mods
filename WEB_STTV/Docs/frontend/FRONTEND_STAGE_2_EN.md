# Stellaris Technological Tree View — opening a database set

## Contents

- [Running and opening](#running-and-opening)
- [Prepared data](#prepared-data)
- [Errors and reports](#errors-and-reports)
- [Validation](#validation)
- [Stage boundaries](#stage-boundaries)

## Running and opening

Implementation of [frontend stage 2](TZ_FRONTEND_STAGE_2_EN.md), interface version `0.0.2`. Run `npm run dev` from `WEB_STTV` with Node.js 24 and dependencies installed. Address: `http://127.0.0.1:5173/`. This workspace also provides local Node.js:

```powershell
& .\data\frontend-tools\node-v24.22.3-win-x64\node.exe .\node_modules\vite\bin\vite.js --host 127.0.0.1
```

Click **Open database set** and select all three files together:

- `data/databases/technologies.json`;
- `data/databases/components.json`;
- `data/databases/buildings.json`.

Order and filenames do not matter: content determines roles. All three files must belong to one version-five build. To update data, run the [backend command](../BACKEND_STAGE_11_EN.md#running) separately. Starting or refreshing the page never builds or opens databases.

One Worker reads files sequentially; the status panel displays the phase and file number. The technology field appears after the entire set is ready. Cancelling the picker preserves the current set; cancelling an active operation releases it. Retry uses the complete previous three-file selection. A new operation clears the previous field.

## Prepared data

Full trees remain in the Worker. The main thread receives technology, component and building catalogs, a shared RU/EN index, original technology links, separate object requirements and explicit object upgrades.

A node address is `{ database, pointer }`; object identity is `{ database, id }`. Identical IDs and pointers from different databases remain distinct. Localization origins, inheritance and shared-description references are also qualified by database role. Conditional building descriptions have separate string IDs; no active condition is evaluated.

`upgradeEvidence` groups witnesses of each technology pair. Evidence requires an explicit object upgrade, exactly one direct technology requirement at each end, and an existing original dependency between those technologies. Alternative or negative object requirements remain structural data rather than an inferred unique continuation.

## Errors and reports

Opening stops for wrong file count, duplicate roles, mixed set identities, old formats, invalid JSON, missing required enrichment, duplicate objects, conflicting translations or unresolved consumed references. No partial set is displayed.

**Save report** exports `sttv.frontend_diagnostics` version 2: all selected files, known roles and identities, object/link counts, warnings and the error reason. Details include qualified references to affected nodes. Missing translations remain warnings.

The frontend checks data needed for transformation; it does not duplicate the complete AST or game-command validator.

## Validation

Verified TypeScript, the production build, 26 unit scenarios and 12 browser scenarios, including the complete game set in the built frontend. The set contains 679 technologies, 1,506 components, 498 buildings and 21 conditional building descriptions.

The result contains 615 original technology links, 1,581 object-requirement links and 720 object upgrades. There are 138 technology pairs with 503 witnesses; all 16 cases and 60 witnesses from the earlier ambiguous-chain research are confirmed. The main-thread result is approximately 9.0 MB of JSON instead of the full trees.

Working reports: `data/stage11/frontend_catalog_report.json`, `data/frontend-tests/browser-report.json`, `data/frontend-tests/real-database.json`; interface screenshots: `data/frontend-tests/real-*.png`. The frontend reports 170 missing-description warnings: 85 components × two languages. Four unresolved localization references remain in string provenance; details are in the backend report. The complete set has no transformation errors.

## Stage boundaries

The existing technology-card layout remains in use. Building and component catalogs supply data for future chain identification; separate screens and a new sorting algorithm are outside this stage. Languages, themes, tooltips, manual variants and the absence of connection lines are preserved. Portable distribution and cross-session persistence remain separate tasks.

[Русская версия](FRONTEND_STAGE_2_RU.md).
