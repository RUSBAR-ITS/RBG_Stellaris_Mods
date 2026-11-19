# Frontend 0.0.5 — technology tree grid

## Contents

- [Starting and combination](#starting-and-combination)
- [Placement](#placement)
- [Modules and report](#modules-and-report)
- [Checks and measurements](#checks-and-measurements)
- [Limitations and user review](#limitations-and-user-review)

## Starting and combination

Implemented the [stage 5 specification](TZ_FRONTEND_STAGE_5_EN.md). Run `npm run dev` from `WEB_STTV`, then open `http://127.0.0.1:5173/`. On this computer:

```powershell
$env:PATH="$PWD/data/frontend-tools/node-v24.22.3-win-x64;$env:PATH"
$env:npm_config_cache="$PWD/data/npm-cache"
npm run dev
```

Use “Open database set” to select **`data/stage17/database_set`**, the directory containing `manifest.json`. The existing set is sufficient; rebuilding is unnecessary. Startup and refresh neither open data nor run the generator.

`config/frontend/tree_layout.json` sets `combination_id`, defaulting to `reference_default`. The other prepared combination in the control set is `reference_variants`. Reopen the set after changing the configuration; rebuild a production bundle with `npm run build` first. There is no manual variant or combination picker at this stage. Cards use the complete saved `parameters.variants` selection.

## Placement

The field contains physics, society and engineering. Each area places whole trees: starting roots first, followed by other roots, sorted by their displayed name in the current language. Starting descendants remain in their branches. Equal names are ordered by base ID.

A child whose ID matches its parent after stripping digits goes first; remaining children follow by name. A parent and its first child at different tiers share a row when the cell is free. Same-tier children move down. On backward tier transitions, an occupied cell shifts only the affected descendant branch. Branches and whole trees do not fill gaps left by earlier branches.

Columns preserve game tiers. The display exception is `levels = -1`, `tier = 5`, with at least one technology prerequisite: display column 6. The stored game tier is unchanged. Cross-area parents remain in the data, while their children become local roots for placement. Additional prerequisites do not impose vertical constraints.

Changing language recalculates order and coordinates from loaded data. Theme, menu and tooltips do not change coordinates. Scrolling is clamped to the new field bounds. Cards are keyboard-focusable in tree traversal order; focus also shows the tooltip. Names and descriptions come from the selected representation. Duplicate variant names use the localized “Variant N” suffix.

## Modules and report

| Module | Purpose |
| --- | --- |
| `data/tree/metadata.ts`, `extraction.ts` | Selecting combination metadata and extracting technology records |
| `data/tree/validation.ts` | Variants, reciprocal references and cycles, including cross-area links |
| `data/tree/forest.ts`, `comparison.ts` | Local trees, display tiers and ordering |
| `data/tree/placement.ts`, `layout.ts` | Iterative traversal, rows, geometry and diagnostics |
| `localization/sources.ts` | Shared string lookup for cards and sorting |
| `app/field.ts`, `ui/layout/TechnologyField.tsx` | Field preparation, error handling and CSS Grid |

The independent `sttvOrderColumn` implementation is removed. The frontend does not recalculate parents. It places compact objects; full AST is not passed to the main thread. Opening reads only 35 technology documents; the other 14 kinds remain unloaded. Combination metadata is compared with manifest `set_id` and `source_revision` without reading those kinds.

Frontend report version 4 includes `tree`: the combination, complete variant selection, input/result revisions, language, settings, dimensions, per-area card/tree/row counts, hidden cross-area link count and geometry timing. `treeCombination` retains selected metadata even if field preparation fails. Input revision comparison is not claimed as a repeated full database audit.

Missing/unsupported combinations, stale inputs, incomplete enrichment and placement failures have distinct RU/EN messages. `ambiguous` retains the card as a separate tree and adds a report warning with its `NodeRef`, parameters and field settings. Detailed parent-selection traces remain on the backend.

## Checks and measurements

TypeScript, the production build and 49 synthetic tests passed. A separate real-set test passed for `reference_default` and `reference_variants` in RU/EN: 679 cards exactly once without overlap, preserving parents, children and game tiers. Checked lasers, five mutations, the arkship jump, dark matter mining and physics encryption/decryption with a society parent. Identical repeated `start_tech = yes` entries in three technologies are accepted; conflicting values have a separate negative check.

| Combination | Physics: cards / trees | Society | Engineering | Cross-area links |
| --- | --- | --- | --- | --- |
| `reference_default` | 168 / 62 | 312 / 98 | 199 / 55 | 37 |
| `reference_variants` | 168 / 62 | 319 / 97 | 192 / 57 | 38 |

Both combinations retain 178 roots and 501 selected parents. Local tree counts differ from stored root counts. Language changes do not reread documents; documents and manifest remain unchanged.

Chromium 159.0.8154.6 passed 16 browser scenarios, including both combinations, invalid inputs, report export, cancellation, menu, language, themes, scrolling, tooltips, coordinates and focus order. One independent large non-technology document streaming test was skipped because the reader is unchanged in this stage. Loading all 15 databases was not repeated. The second combination was tested by substituting the loaded configuration module's value, without database changes.

Visually checked RU/EN in day and night themes. On this computer, browser opening took **5.786 s**, technology document reading **4.782 s**; **129,571,596 bytes** read, 35 of 450 documents verified, 415 unread. Initial RU geometry took **21.1 ms**, subsequent EN geometry **4.2 ms**. Separate Node.js loader measurements: 3.711 s and 4.347 s for the two combinations, with geometry taking 4–6 ms. These are individual measurements without clearing the OS cache; total browser/Worker memory and full-audit timing were not measured here. Menu, cancellation and language interaction were exercised by browser scenarios.

Working results: `data/frontend-stage5/real-layout.json`, `browser-real-set.json`, `real-ru-night.png`, `real-ru-day.png`, `real-en-day.png`, `real-en-night.png`, `real-tooltip.png`. Browser scenario log: `data/frontend-tests/browser-report.json`.

## Limitations and user review

Connection lines, interactive variant changes with backend recalculation, event/zero-weight markers and persistent coordinates are excluded. Database files and parent-selection rules are unchanged. The field deliberately preserves branch gaps, making it taller than the previous independent column lists.

The user should assess branch readability and scrolling on the real field. Running Stellaris is not required for acceptance of this stage.

[Specification](TZ_FRONTEND_STAGE_5_EN.md) · [Русская версия](FRONTEND_STAGE_5_RU.md).
