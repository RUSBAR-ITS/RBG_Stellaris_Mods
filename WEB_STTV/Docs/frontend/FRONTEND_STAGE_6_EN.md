# Stellaris Technological Tree View — frontend 0.0.6

## Contents

- [Result](#result)
- [Starting and combination](#starting-and-combination)
- [Routing and rendering](#routing-and-rendering)
- [Configuration and styling](#configuration-and-styling)
- [Diagnostics](#diagnostics)
- [Checks and measurements](#checks-and-measurements)
- [Limitations and user review](#limitations-and-user-review)

## Result

Implemented the approved [stage 6 specification](TZ_FRONTEND_STAGE_6_EN.md): connections from the selected `parent_tech` to children within a research area, arrows, shared trunks and junction dots. Hovering over a card highlights its parent path in blue and its immediate child paths in orange. Sibling branches retain their normal color; leaving the card clears highlighting.

Stage 5 logical rows, tiers and tree order remain intact. Gaps expand when needed for noncrossing routes. Colors follow the theme. Hovering changes the styling of prepared segments without running layout or reading databases.

## Starting and combination

From `WEB_STTV` with Node.js 24: run `npm run dev`, then open `http://127.0.0.1:5173/`. Install dependencies with `npm ci` during initial setup.

Using the Node.js installation prepared inside this repository:

```powershell
$env:PATH="$PWD/data/frontend-tools/node-v24.22.3-win-x64;$env:PATH"
npm run dev
```

Use “Open database set” to select **`data/stage17/database_set`**, containing `manifest.json`. The existing database is sufficient; no rebuild is required. Starting or refreshing the page does not run the generator.

`config/frontend/tree_layout.json` selects `reference_default` or `reference_variants`. Reopen the set after changing `combination_id`. Manual variant selection and Python calls remain deferred.

## Routing and rendering

Pure functions in `src/frontend/data/connections/` perform these steps:

1. Receive local trees and logical card positions from stage 5.
2. Choose attachment sides while accounting for the parent's incoming line. Use a bottom exit if the side port is occupied.
3. Find orthogonal paths through gaps using A*. Cards and foreign-parent routes block the path; an existing own trunk is preferred. Grid refinements and visited search states are bounded.
4. Convert routes and cards to pixels. Each gap has its own width; columns align across research areas. Independent trees reuse horizontal lanes instead of accumulating their widths.
5. Split shared paths into unique segments carrying their child route IDs. Draw each segment once.
6. Validate parent-pair coverage, endpoints, orthogonality, absence of card penetration and intersections between different parents.

| Modules | Responsibility |
| --- | --- |
| `routing.ts`, `grid.ts`, `search.ts`, `heap.ts` | Attachments, free gaps and search |
| `axis.ts`, `layout.ts` | Gap dimensions, shared columns and final geometry |
| `segments.ts`, `points.ts`, `validation.ts` | Shared trunks, geometry operations and validation |
| `ui/base/Connection.tsx` | UI kit segment and arrow |
| `ui/layout/Connections.tsx` | SVG layer, junctions and highlighting roles |
| `ui/layout/TechnologyField.tsx` | Shared coordinates for cards, headings and connections |

SVG does not intercept pointer events and is hidden from the accessibility tree. Card DOM order and keyboard traversal are preserved. Keyboard focus alone does not highlight connections.

## Configuration and styling

`config/frontend/connections.json` defines routing and geometry parameters:

| Parameter | Value | Purpose |
| --- | --- | --- |
| `cardClearance` | 6 | Minimum routing lane clearance from a card, px |
| `laneSpacing` | 6 | Distance between lanes, px |
| `exitLength` | 6 | Minimum exit space, px |
| `strokeWidth` | 1.5 | Line thickness, px |
| `arrowSize` | 6 | Arrow length, px |
| `junctionRadius` | 2 | Junction dot radius, px |
| `bendPenalty` | 0.4 | Search turn penalty |
| `sharedPathCost` | 0.1 | Own-trunk cost multiplier |
| `maxRefinements` | 2 | Additional attempts with refined gaps |
| `maxSearchStates` | 1000000 | Processed-state limit per attempt |

Baseline gaps and card sizes remain in `config/frontend/interface.json`. The configured numeric stroke width is supplied to CSS through `--sttv-connection-stroke-width`.

`styles/elements.css` maps `--sttv-connection-color-default`, `--sttv-connection-color-parent` and `--sttv-connection-color-children` to `styles/dictionary.css`.

| Theme | Normal line | Parent | Children |
| --- | --- | --- | --- |
| Night | `--sttv-border` | `#73BFFF` | `#F2B366` |
| Day | `--sttv-border` | `#1768A6` | `#9B4F0B` |

## Diagnostics

Exported reports include `tree.connections`: settings, logical connection, segment and junction counts, final gaps and preparation time. Logical connections and shared-trunk drawing segments are counted separately.

The `tree_connections_failed` error prevents publication of a partially successful field. Its message is localized; report details contain the reason, combination, language and settings, plus parent, child, attachments and card positions when no path is found. Search attempts are bounded; an error does not mathematically prove that another routing is impossible.

## Checks and measurements

All four language/variant combinations were checked against the existing `data/stage17/database_set`:

| Combination | Language | Cards | Connections | Omitted cross-area links | Connection preparation, s |
| --- | --- | --- | --- | --- | --- |
| `reference_default` | RU | 679 | 464 | 37 | 0.159 |
| `reference_default` | EN | 679 | 464 | 37 | 0.176 |
| `reference_variants` | RU | 679 | 463 | 38 | 0.152 |
| `reference_variants` | EN | 679 | 463 | 38 | 0.174 |

Measured on 2026-11-19 on the current computer using Node.js 24.22.3 after database reading. Includes routing, coordinate conversion and geometric validation, excluding browser rendering. This is one reference run, not a performance guarantee for other datasets.

Automatic checks confirmed no prohibited intersections, complete connections and unchanged input data. Every logical card position matched the saved stage 5 result. Only 35 technology documents are read; the other 14 kinds stay unloaded, and changing language does not reread documents.

Synthetic checks cover agreed forks, occupied incoming ports, the reverse `3 → 4 → 3` transition, skipped tiers, nested trunks, local expansion, deterministic geometry, shared-path highlighting, damaged geometry and bounded search. An additional 20 reproducible trees with mixed transitions were processed.

`npm run test` with `STTV_DATABASE_DIR` passed all 59 tests without skips or failures, including real-set checks. `npm run build` passed TypeScript checking and the Vite production build. Test output is saved in `data/frontend-stage6/unit-tests.log`.

Twenty browser checks passed; one optional giant-file scenario was skipped. Checks cover RU/EN, both themes, highlighting and tooltips, scrolling, window size, menu collapse, arrow attachment and error export. Screenshots and reports reside in `data/frontend-stage6/`; the shared browser report is `data/frontend-stage6/browser-full-report.json`.

## Limitations and user review

Additional prerequisites and cross-area relationships remain in the data without lines. Parents and variants are not recalculated, databases are not modified and geometry is not persisted between launches.

Stellaris does not need to run. User review should assess dense-branch readability, expanded-gap usability and distinguishability of the two highlight colors on their display.
