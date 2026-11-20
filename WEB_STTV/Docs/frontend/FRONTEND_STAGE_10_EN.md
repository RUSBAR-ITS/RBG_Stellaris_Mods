# Frontend 0.0.12 — DLC settings

## Contents

- [Startup and opening](#startup-and-opening)
- [Using settings](#using-settings)
- [Implementation](#implementation)
- [Validation](#validation)
- [Limitations](#limitations)

## Startup and opening

Implemented [stage 10](TZ_FRONTEND_STAGE_10_EN.md), with calculations provided by [backend stage 20](../BACKEND_STAGE_20_EN.md). From the repository root, start the service in a separate terminal:

```powershell
$env:PYTHONPATH = (Resolve-Path WEB_STTV/src/backend).Path
WEB_STTV/data/.venv/Scripts/python.exe -X utf8 -B -m sttv.service
```

In another terminal:

```powershell
$env:PATH = (Resolve-Path WEB_STTV/data/frontend-tools/node-v24.22.3-win-x64).Path + ';' + $env:PATH
npm.cmd --prefix WEB_STTV run dev
```

Open `http://127.0.0.1:5173/`, click “Open database set” and select **`WEB_STTV/data/stage20/database_set`**. This directory is registered in the current `config/service.json`. Preparation is complete; no builder invocation is required.

Explicit opening selects an all-enabled DLC combination. With the service unavailable, a matching prepared combination remains viewable, but Apply is disabled. A set/configuration mismatch has a separate message. Reopen the directory after starting the service.

## Using settings

The menu now includes Technology tree and DLC settings. Navigation retains the set, field position, zoom and draft. The collapsed menu keeps its existing narrow strip; expand it to choose a section.

DLC rows sort by the current language's name. Each row has a thumbnail/placeholder on the left and a switch with state text on the right. Mouse, Space and Enter operate switches. The accessible name is the DLC name. Names wrap without ellipsis.

Switches edit a draft. Apply sends the entire selection in one request; Discard changes restores the active profile. During calculation navigation and cancellation remain available, while switches are disabled. The previous tree stays visible until success. Errors/cancellation preserve that tree and the draft; the saved report contains details.

Success atomically adopts visibility, parents, children, layout and connections. Viewport position is clamped to the new geometry. Language/theme/zoom changes retain DLC selection. Reloading the page neither opens data, builds databases nor restores preferences automatically.

## Implementation

| Area | Files |
| --- | --- |
| View and draft | `views/DlcSettings.tsx`, `app/useDlc.ts` |
| UI kit | `ui/base/Switch.tsx`, `ui/composite/DlcRow.tsx`, navigation state in `Button` |
| Settings and styling | `config/frontend/dlc.json`, `styles/elements.css`, `views/dlc-settings.css`, `locales/ru.json`, `locales/en.json` |
| Service and bytes | `storage/api.ts`, `storage/bytes.ts`, `storage/reader.ts` |
| Snapshot and adapter | `storage/session.ts`, `data/setAdapter.ts`, `workers/dlc.ts`, Worker protocol |

List/switch geometry comes from configuration; colors/fonts use named variables for both themes. Full AST and DLC evidence remain in the backend; the interface consumes compact results and reports. It does not duplicate game-condition evaluation.

Snapshot updates reread only changed technology documents. Unchanged catalogs/images are reused. API bytes stream through hash verification; adoption waits for the complete new catalog. Late replies from another operation/revision cannot replace the current screen.

## Validation

Type checking and the production build passed. Unit checks: 69 passed, 3 environment-dependent checks skipped. Browser checks: 32 scenarios passed including reruns of corrected scenarios; the separate 512 MiB file stress check was skipped. The real set was checked in both themes, including thumbnails, connections and the all-DLC → no-DLC → all-DLC transition.

Checks cover draft changes without calculation, discard, one request for multiple changes, cancellation, failure, preservation of the old tree, API document refresh and no automatic opening after page reload. Separate tests verify reading only changed files, retaining the DLC catalog and rejecting corrupt new bytes.

Real reference profiles: 678 visible technologies with all DLC, 543 without DLC, 544 with `dlc002` and `dlc036`. Disabling DLC can also reveal a negatively gated technology. All original 679 objects remain stored.

Logs are under `data/stage20/`; interface captures under `data/stage20/screenshots/`. Browser scenarios use Chromium and the local Python service. Condition tests do not replace execution in the game engine.

## Limitations

Indirect DLC restrictions through other object definitions are not evaluated yet. For example, the biological-ship requirement leaves weaver weapons visible without BioGenesis. This confirmed coverage gap is addressed by the proposed [stage 21 draft](../TZ_BACKEND_STAGE_21_EN.md). Visible-technology counts above describe the stage-20 filter.

These are reference settings, not purchased-DLC detection. Unknown game conditions do not exclude technologies. Base zero weight alone does not hide a card. Variants come from the prepared combination; automatic empire-based selection and interactive variant switching were not added. Preferences are not yet persisted between launches.
