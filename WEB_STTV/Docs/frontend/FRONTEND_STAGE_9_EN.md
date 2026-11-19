# Stellaris Technological Tree View — frontend 0.0.10

## Contents

- [Result and startup](#result-and-startup)
- [Zoom controls](#zoom-controls)
- [Geometry and state](#geometry-and-state)
- [Modules and configuration](#modules-and-configuration)
- [Validation](#validation)
- [User review](#user-review)

## Result and startup

Implemented the approved [stage 9 specification](TZ_FRONTEND_STAGE_9_EN.md). The technology field opens at 50%; the menu setting offers 50%, 75%, 100%, 125% and 150%. Cards, fonts, images, headings, spacing and connections scale together.

Run from `WEB_STTV`:

```powershell
$env:PATH="$PWD/data/frontend-tools/node-v24.22.3-win-x64;$env:PATH"
npm run dev
```

Open `http://127.0.0.1:5173/`, click “Open database set” and select **`data/stage17/database_set`**. If the application is already running, reload the page and open the same directory. No database or image rebuild is required; data preparation remains a separate explicit operation.

## Zoom controls

The shared “Zoom” selection control appears below the language selector. It is available before opening a database, supports mouse and keyboard input, and is hidden when the menu collapses. Its label is localized in RU/EN.

100% corresponds to the 520 px base card width; at 50% it occupies 260 px, and at 150% it occupies 780 px. The menu, status bar, scrollbars, dropdowns and tooltips retain their normal size. Browser page zoom is independent of this setting.

## Geometry and state

Text is measured at 100%; shared card height and connection routes also use base coordinates. A CSS transformation applies to the entire field, while an outer region sets its actual scaled width and height. The original large block does not extend scroll limits after zooming out.

Zoom changes preserve the field point at the viewport centre. Offsets are clamped at field edges. Viewport changes caused by scrollbar appearance/disappearance are included. Hover, focus and tooltip anchoring use screen coordinates; changing zoom clears the previous tooltip and highlighting.

Zoom persists within the session across language, theme, menu and database-set changes. Page reload applies the configured initial value. Zoom changes do not reread data, invoke the backend or change parents/tree order. Persistent settings remain a separate task.

## Modules and configuration

| Path from the project root | Purpose |
| --- | --- |
| `config/frontend/zoom.json` | `initialPercent` and `percentages`; the initial value must belong to the unique positive percentage list |
| `src/frontend/ui/composite/ZoomSelector.tsx` | Setting composed from existing UI-kit select/text elements; configuration checks |
| `src/frontend/app/App.tsx` | Session zoom state |
| `src/frontend/ui/layout/TechnologyViewport.tsx` | Scaled bounds, scroll limits and centre preservation |
| `src/frontend/ui/layout/viewport.css` | Shared field transformation and original-bounds containment |
| `src/frontend/ui/layout/TechnologyField.tsx` | Scale propagation and previous-highlight reset |
| `src/frontend/ui/composite/TechnologyCard.tsx` | Tooltip dismissal on zoom changes |
| `src/frontend/locales/ru.json`, `en.json` | Setting label and value template |

No new colours or fonts were introduced; the setting uses existing UI-kit variables. Implementation files remain compact.

## Validation

Production build and TypeScript checks passed. 65 unit checks passed; 3 checks requiring separate real inputs were skipped in the standard unit run. 27 browser checks passed against the production build, including all 5 new zoom scenarios. 3 earlier scenarios were skipped: 2 require development-server configuration interception, and 1 needs a separate large monolithic JSON input. The real set of 679 technologies and 464 local connections was checked in the browser.

The complete browser report is saved as `data/frontend-stage9/browser-report.json`. No additional database rebuild was performed for these checks.

Stage checks cover initial 50%, all five values, text/geometry proportions, centre preservation, both scroll limits, scrollbar appearance, keyboard input, tooltips, relationship highlighting, language/theme/set changes and reset on page reload. The real database is checked in RU/EN at 50%, 100% and 150%; a synthetic example includes a long title. Screenshots are in `data/frontend-stage9/`.

## User review

Review 50% readability on your display, the zoom selector and navigation through the tree. Select 75% or 100% if preferred. No game validation is required.
