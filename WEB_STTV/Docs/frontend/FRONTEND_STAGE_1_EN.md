# Stellaris Technological Tree View — first frontend

## Contents

- [Result](#result)
- [Running](#running)
- [Usage](#usage)
- [Implementation](#implementation)
- [Configuration and styling](#configuration-and-styling)
- [Display details](#display-details)
- [Checks](#checks)
- [Limitations](#limitations)

## Result

The first frontend implements the agreed documents in the [element index](UI_ELEMENTS_EN.md) and the specifications for [database opening](TZ_DATABASE_OPENING_EN.md), the [adapter](TZ_DATABASE_ADAPTER_EN.md), [Worker results](TZ_WORKER_RESULT_EN.md), [localization](TZ_LOCALIZATION_EN.md), and [styling](TZ_STYLING_DICTIONARY_EN.md). The frontend package version is `0.0.1`.

It displays name cards with title-and-description tooltips, RU/EN, day/night themes, manual variants, research areas, and tier columns. As requested, connecting lines are not drawn yet; the prepared catalog retains the requirement tree and links. It includes a collapsible menu, separate status panel, cancellation, retry after failure, and diagnostic report saving.

Historical first-stage guide. The current frontend opens three version-five databases as one set; current paths and commands are in the [stage-two guide](FRONTEND_STAGE_2_EN.md).

## Running

Run commands from `WEB_STTV`. A regular development environment needs Node.js 24 and the dependencies in `package-lock.json`:

```powershell
npm ci
npm run dev
```

Open `http://127.0.0.1:5173/`. Stop the server with `Ctrl+C` in its terminal. The port is fixed: an occupied port causes a startup error. Viewing requires no Python service.

The current workspace already contains the dependencies and a local Node.js installation without system changes. It can run immediately:

```powershell
Set-Location D:\Repos\RBG_Stellaris_Mods\WEB_STTV
& .\data\frontend-tools\node-v24.22.3-win-x64\node.exe .\node_modules\vite\bin\vite.js --host 127.0.0.1
```

This Node.js copy is a working tool in ignored `data/`, not a portable product distribution. Use the regular method above for another checkout.

Build with `npm run build`. Output goes to `data/frontend-build/`; use `npm run preview` to inspect the build. Opening `index.html` through `file://` is not supported: modules and the Worker load through Vite's local server. Fonts and icons are local in the build; the interface uses no external CDNs.

## Usage

1. Click **Open database** and select a prepared JSON file. The current verified database is `data/stage10/database.json`.
2. Wait for the loaded technology count. Canceling the file picker retains the previous catalog; canceling active processing returns to the initial empty state.
3. Hover over a card for its description. For a description taller than the window, scroll the wheel over the card to scroll its tooltip. Leaving the card hides it.
4. Click a card that has variants. Arrow keys move the active option, `Enter` confirms, and `Escape` cancels. Variants sharing a title receive a localized suffix using the original variant number.
5. Change language and theme in the menu. A collapsed menu retains only its bottom expand button. The wheel scrolls vertically, `Shift` + wheel horizontally; scrollbars support dragging, track clicks, and keyboard control.
6. Click **Save report** when needed. The browser downloads the current completed attempt as JSON with its operation number, file name/size, error, and warnings. It does not include the full database.

Startup and refresh neither open a file nor invoke the generator. Database rebuilding and enrichment remain separate backend operations. Settings and selected variants exist only in the current session; refresh restores RU, the night theme, and the expanded menu.

## Implementation

| Directory | Purpose |
| --- | --- |
| `src/frontend/app/` | Application state, Worker integration, messages, and report export |
| `src/frontend/workers/` | JSON reading, protocol, and attempt lifecycle |
| `src/frontend/data/` | Technology extraction, requirements, links, and layout |
| `src/frontend/localization/` | String index, provenance, and shared source/language/ID lookup |
| `src/frontend/locales/` | Built-in RU/EN dictionaries |
| `src/frontend/ui/` | Base/composite elements, layout containers, and scrollbars |
| `src/frontend/views/` | Main window assembly from UI elements |
| `src/frontend/styles/`, `assets/` | Styling dictionaries, shared styles, local Inter and SVG icons |
| `tests/frontend/` | Unit and browser checks |

File reading, `JSON.parse`, and adaptation run in a Worker. It retains the complete tree until replacement, cancellation, error, or page closure. Only `technologies`, `links`, `localization`, and `diagnostics` cross to the main thread. A new attempt terminates the previous Worker; only one terminal response from the current Worker with the current `operationId` is accepted.

The adapter consumes direct `common/technology/*.txt` documents, excluding auxiliary definitions in subdirectories. It checks format/version and handles failures of its own transformations. It does not repeat the backend's full JSON Schema traversal.

String addressing is `source → language → id`. Database IDs use `requested_key`, and values use stored `text`. Matching texts merge provenance; different non-null values under one address block preparation. `null` means missing, while an empty string is valid. Missing translations produce `⟦ID⟧` and a warning without substituting another language.

## Configuration and styling

| File | Configuration |
| --- | --- |
| `config/frontend/adapter.json` | Database format/version, technology directory, fields, and area order |
| `config/frontend/interface.json` | Initial settings and card/menu/spacing/scrollbar/overlay dimensions |
| `config/frontend/localization.json` | Languages, default source, source readers and paths |
| `config/frontend/diagnostics.json` | Diagnostic codes mapped to built-in message IDs |
| `src/frontend/styles/dictionary.css` | Shared palettes, typography, and local font |
| `src/frontend/styles/elements.css` | Component variable assignments |

Configuration is bundled. Vite handles edits during development; a distributed build requires another `npm run build`. Components use their own CSS variables with colors and fonts assigned in dictionaries. Interface strings reside in separate JSON files; technical report details are in English.

## Display details

Cards are `208 × 64` CSS px, column gaps `24`, card gaps `12`, and field padding `12`. Level 0 has only the normal padding, without an extra empty column. The menu is `244` px wide, or `53` when collapsed, including its `36` px button, padding, and border. These values reside in configuration.

Each column uses stable topological ordering: currently placeable cards are compared by requirement count, sorted immediate predecessor set, then ID. Sets are compared lexicographically by their JSON representation. Dependencies within the same column and area take precedence. There is no separate family alignment between neighboring columns yet.

Language and theme do not affect geometry. A variant may move a card to another research area while retaining base `tier` and requirements. Focus returns to the same technology after a move without forcing scrolling. Tooltips and lists use window-level portals, remain within window bounds, and do not expand the field.

## Checks

```powershell
npm run build
npm test
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD/data/frontend-tools/browsers"
npx playwright install chromium
npm run test:browser
```

Integration checks need an existing `data/stage10/database.json`; tests do not generate it. Chromium is already installed in the current workspace. Without a system Node.js installation, add the local Node.js directory to the terminal's `PATH` before these commands.

Checks cover types, production build, 16 unit scenarios, and 10 Chromium browser scenarios: real data, requirements and ordering, variants, translation provenance/conflicts, stale Worker replies, cancellation/retry, report export, RU/EN, both themes, long literal text, keyboard controls, scrolling, and refresh reset.

The real result contains 679 technologies, 206 variants, 615 links, and 3,400 unique string addresses across both languages, without errors or warnings. The serialized prepared catalog is 2,308,044 bytes; the input database is 140,937,166 bytes. These are serialized sizes, not browser memory measurements. A control run opened and displayed the data in roughly one second; timing depends on the environment and is not guaranteed.

The browser report is `data/frontend-tests/browser-report.json`, with timing in `real-database.json` beside it. Screenshots `real-night.png`, `real-day.png`, `real-tooltip.png`, and `real-variants.png` are also saved there and were visually reviewed. Game sources and database files were not modified.

## Limitations

- Lines, technology images, search, game-condition evaluation, automatic variants, UI database generation, cross-session persistence, and portable packaging belong to later stages.
- Game markup and dynamic substitutions remain literal text; HTML is not executed.
- Under additional user approval, `NOT`, `NAND`, and `NOR` in technology requirements stop opening with `invalid_database` and an explanation in the report. Their counting/layout semantics are still undefined.
- Chromium on Windows was tested. Other browsers were not tested separately. Testing this reference interface does not require launching Stellaris.

[Русская версия](FRONTEND_STAGE_1_RU.md) · [README](../../README_EN.md).
