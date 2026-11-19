# Stellaris Technological Tree View — frontend 0.0.7

## Contents

- [Result](#result)
- [Starting and combination](#starting-and-combination)
- [Implementation](#implementation)
- [Configuration and styling](#configuration-and-styling)
- [Diagnostics](#diagnostics)
- [Checks and comparison](#checks-and-comparison)
- [Limitations and user review](#limitations-and-user-review)

## Result

Implemented the approved [stage 7 specification](TZ_FRONTEND_STAGE_7_EN.md). Simple orthogonal routes replace detours around foreign lines. At a crossing, the horizontal line smoothly bridges upward over the vertical line. Actual forks retain junction dots and shared trunks.

Bridges highlight with their horizontal connection. Vertical lines highlight independently and remain below the bridge. Hover changes neither geometry nor layering. Logical card positions, order and dimensions are preserved; gaps account for arc dimensions and clearance.

Branch corner dots are not displaced along the line. Children sharing an exit side use one exit corner even when their entry sides differ.

## Starting and combination

From `WEB_STTV` with Node.js 24, run `npm run dev`, then open `http://127.0.0.1:5173/`. Install dependencies with `npm ci` on first setup.

On the current computer:

```powershell
$env:PATH="$PWD/data/frontend-tools/node-v24.22.3-win-x64;$env:PATH"
npm run dev
```

Use “Open database set” to select **`data/stage17/database_set`**, containing `manifest.json`. No database rebuild is required. Starting or refreshing the page does not run the generator.

Select a prepared combination through `combination_id` in `config/frontend/tree_layout.json`: `reference_default` or `reference_variants`. Reopen the set after changing it. Interactive variant selection remains a separate stage.

## Implementation

1. Select attachment sides from prepared card positions, accounting for occupied incoming ports.
2. Allocate shared-trunk lanes for child groups. Try a straight path, side trunk and bottom exit; prefer fewer bends, then shorter length and fewer crossings. Foreign perpendicular lines are permitted; cards, merged lines and corner contacts require another lane.
3. Joining an own trunk reuses its existing prefix, preventing extra cycles. Shared sections retain child path membership.
4. Convert gaps to pixels, accounting for arcs, underlays and clearance. Independent trees reuse lanes; columns align between areas.
5. Merge shared sections before computing crossings and one bridge per crossing. Validate final geometry.
6. SVG draws continuous paths containing arcs, then underlays and arcs above vertical lines, junctions and arrows. There is no straight horizontal stroke beneath its own arc.

| Modules | Responsibility |
| --- | --- |
| `data/connections/routing.ts`, `templates.ts`, `candidates.ts` | Attachments, shapes, lanes and route selection |
| `axis.ts`, `layout.ts` | Gaps, shared columns and pixel coordinates |
| `segments.ts`, `contact.ts`, `crossings.ts` | Shared sections, contacts and crossings |
| `validation.ts`, `bridgeValidation.ts` | Connection coverage, geometry and bridge clearance |
| `paths.ts`, `ui/base/Connection.tsx` | Continuous SVG path, arc, underlay and arrow |
| `ui/layout/Connections.tsx` | Connection layer, dots and highlight roles |

Old `grid.ts`, `search.ts`, `heap.ts` files were removed. There is no A* fallback. SVG does not intercept the pointer and is hidden from the accessibility tree; card keyboard order is preserved.

## Configuration and styling

`config/frontend/connections.json`:

| Parameter | Value | Purpose |
| --- | --- | --- |
| `cardClearance`, `exitLength` | 6, 6 | Minimum space near a card, px |
| `laneSpacing` | 6 | Baseline lane distance, px |
| `strokeWidth`, `arrowSize`, `junctionRadius` | 1.5, 6, 2 | Line thickness, arrow size and dot radius, px |
| `bridgeWidth`, `bridgeHeight` | 14, 7 | Arc dimensions, px |
| `bridgeClearance` | 6 | Clearance from cards, corners, arrows, dots and other lines, px |
| `bridgeSpacing` | 6 | Additional spacing between neighboring arc clearance regions, px |
| `bridgeUnderlayWidth` | 5 | Arc underlay stroke width, px |
| `maxLaneAttempts` | 16 | Maximum lane sets per logical route |

Old A* settings were removed. Baseline card dimensions and gaps remain in `interface.json`. Gaps containing bridges may exceed baseline values.

Colors remain in the styling dictionary: parent `#73BFFF` at night / `#1768A6` by day; children `#F2B366` / `#9B4F0B`. `--sttv-connection-bridge-background` refers to `--sttv-field-background`. The underlay follows the theme; SVG does not hardcode black or white.

## Diagnostics

`tree.connections` adds `crossings`, `bridges`, `bends`, `maxBends`, `logicalPathLength`. Bends count orthogonal backbone turns, excluding bridge curves. Length sums logical paths in pixels; shared trunks may be counted multiple times. Settings, gaps, connection/segment/junction counts and preparation time remain available.

`tree_connections_failed` prevents publishing a partially prepared field. Reports include the combination, language and settings, plus route or bridge conflict details. Attempts are bounded; failure does not mathematically prove that another routing is impossible.

## Checks and comparison

Both prepared combinations were checked in RU and EN: 679 cards each, 464/463 local connections. Every card's logical `(area, column, row)` matches stage 6. Database files were unchanged; only 35 technology documents were read, leaving 14 other kinds unloaded. Changing language does not reread data.

| Combination / language | Bridges | Bends: stage 6 → 7 | Maximum per path: 6 → 7 | Total length: 6 → 7, px |
| --- | --- | --- | --- | --- |
| `reference_default` / RU | 19 | 989 → 453 | 24 → 3 | 291492 → 134299 |
| `reference_default` / EN | 24 | 1125 → 459 | 34 → 4 | 435962 → 158163 |
| `reference_variants` / RU | 19 | 980 → 438 | 24 → 3 | 299618 → 131551 |
| `reference_variants` / EN | 24 | 1110 → 442 | 34 → 4 | 438726 → 153761 |

For example, `tech_energy_torpedoes_1 → tech_energy_torpedoes_2` crosses the `tech_lasers_4` trunk horizontally with a bridge. The old vertical-line detour is gone. Comparison is saved in `data/frontend-stage7/comparison.json`; original geometry and screenshots are under `baseline/`, with new routes and screenshots alongside.

On the current computer using Node.js 24.22.3, connection preparation after database reading took approximately 0.02–0.06 s; this excludes file opening and browser rendering. A separate opening, preservation and layout test is recorded in `real-layout.json`.

Passed 61 synthetic tests, a separate four-real-layout test, TypeScript checking and the production build. Passed 21 browser tests; one optional giant-JSON test was skipped. Checks cover themes, languages, independent horizontal/vertical highlights, stable layering, tooltips, scrolling, resize, menu collapse and error export. Working results are under `data/frontend-stage7/`.

## Limitations and user review

Additional and cross-area prerequisites remain undrawn. Parent selection, databases and storage format are unchanged. Geometry is not persisted between launches.

Stellaris testing is unnecessary. The user reviews bridge, fork and highlight readability in the browser at their window size and zoom.
