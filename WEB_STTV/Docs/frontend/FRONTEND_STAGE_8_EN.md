# Stellaris Technological Tree View — frontend 0.0.9

## Contents

- [Result and startup](#result-and-startup)
- [Card and geometry](#card-and-geometry)
- [Modules and settings](#modules-and-settings)
- [Images and diagnostics](#images-and-diagnostics)
- [Validation](#validation)
- [User review](#user-review)

## Result and startup

Implemented the approved [stage 8 specification](TZ_FRONTEND_STAGE_8_EN.md). Cards show the game image, full name, categories, game tier, starting flag, base cost/weight and finite repeat count. Background follows the research area; rare frames are purple and dangerous frames red, with danger taking precedence.

From `WEB_STTV`, run `npm run dev` and open `http://127.0.0.1:5173/`. On this computer:

```powershell
$env:PATH="$PWD/data/frontend-tools/node-v24.22.3-win-x64;$env:PATH"
npm run dev
```

Click “Open database set” and select **`data/stage17/database_set`**. Images have already been added. For another set, run [resource preparation](../BACKEND_STAGE_18_EN.md#running) first. Without it, the interface requests image preparation; generation is never started automatically.

The prepared combination is still selected by `combination_id` in `config/frontend/tree_layout.json`. `reference_default` and `reference_variants` are supported; interactive switching remains deferred.

## Card and geometry

- Missing cost/weight hides the whole row; explicit zero is shown.
- Block `cost` displays its base `factor`. Empire modifiers and repeat research costs are not evaluated.
- “Level N” uses game `tier`, even in display column 6. “Levels: N” appears only for finite `levels > 1`.
- The selected representation determines name, description, icon, area and categories. Base numbers and flags come from the base technology.
- Names and categories wrap without truncation. Tooltips retain the name and description; game formatting codes remain literal text.

Card width is 520 px; minimum height is 158 px. The previous 188 px minimum created excessive empty space. The new minimum fits the 112 px image, 14 px inner padding on each side, 1 px inner borders, 6 px frame bands and 2 px outer borders. A hidden measuring composition uses the same UI elements and actual fonts. The maximum required height applies to every card, followed by geometry and SVG preparation. Changing language repeats measurement. Image loading does not change dimensions. Shorter cards retain space up to the common height required by the tallest cards.

The rarity/danger colour fills the entire frame between the inner surface and the card's outer boundary. The inner surface keeps its research-area colour; ordinary cards use that colour for their frame as well. This corrects the previous outer-outline-only colouring.

Stage 8 used 100% zoom. The subsequent [stage 9, version 0.0.10](FRONTEND_STAGE_9_EN.md) implements a zoom setting initially at 50%.

Logical positions, parent connections, bridges, corner dots and parent/child highlighting are preserved. Font metrics match between themes, so changing theme does not require relayout.

## Modules and settings

| Path | Purpose |
| --- | --- |
| `config/frontend/card.json` | 112 px image, 20 px cost icon, spacing, frame and glow |
| `config/frontend/interface.json` | Shared width, minimum height and gaps |
| `config/frontend/adapter.json` | Source attribute fields |
| `data/presentation.ts` | Numbers, flags, categories and image reference extraction |
| `storage/assets.ts` | Registry, verification on read, cache and categories |
| `ui/base/ResourceImage.tsx` | Shared image element, decoding, URLs and placeholder |
| `ui/composite/CardContent.tsx` | Shared attribute row and card contents |
| `ui/composite/CardMeasurement.tsx` | Complete text height measurement |
| `styles/dictionary.css`, `styles/elements.css` | Palettes and color/font roles |

Code paths in this table are relative to `src/frontend/`, except explicit `config/` paths. Heading: Inter 17/23 px, 600; details: 13/20 px, 400. Color literals live only in the dictionary. Card dimensions are supplied from configuration through CSS variables.

## Images and diagnostics

The Worker reads only selected representation images and necessary cost icons. It checks size, SHA-256, PNG header and dimensions; subsequent requests use the cache. The UI creates one object URL and pre-decodes each unique resource once per open set. Cards share that URL; replacing the set releases the URLs.

Missing/damaged images show a neutral placeholder and produce `image_unavailable` in the exported report, including browser decoding errors. Invalid optional numbers are hidden with `card_value_invalid`; absent numbers are not warnings. Contradictory required flags or unusable layout data stop opening. Repeated identical `is_dangerous = yes` entries present in vanilla data are accepted.

Missing resource preparation produces `assets_not_prepared`. Use the existing “Save report” button to inspect reasons. The browser does not access absolute game installation paths.

## Validation

TypeScript and the production build passed. Passed 65 unit checks; 3 more require an explicitly selected real database and are skipped in the ordinary run. A separate real test of both combinations in RU/EN passed: 679 technologies, 464/463 local connections, unchanged logical order and source data.

Passed 24 browser checks: 23 general checks and 1 separate image cache/decoding check. One existing large monolithic-file test was skipped because its separate input was not provided. Covered real and synthetic cards, both themes, long names, zero/missing values, tooltips, keyboard, scrolling, menu collapse, window resize, highlighting and bridges. All 679 selected real icons loaded.

Results: `data/stage18/`. Screenshots: `data/frontend-stage8/`, including `real-ru-night.png`, `real-en-night.png`, `synthetic-night.png`, `synthetic-day.png`. The synthetic screenshots also cover a long artificial title and red-frame precedence.

After the 0.0.9 corrections, the production build with TypeScript and 10 browser checks of cards, connections, tooltips and the grid passed; 2 development-configuration interception scenarios were skipped for the production build. The real 679-technology set was checked in RU/EN. Screenshots in `data/frontend-stage8/` were updated. Reload the page and open the same set to view the changes; no database rebuild is needed.

## User review

Review readability of card/image sizes, both palettes and navigation through the expanded field. Images preserve original game pixels; enlargement does not invent detail. No game launch is needed. Variant switching, additional connections and empire condition evaluation remain subsequent stages.
