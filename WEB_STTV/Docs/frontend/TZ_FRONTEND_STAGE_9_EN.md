# Frontend stage 9 — technology field zoom

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Controls and configuration](#2-controls-and-configuration)
- [3. Geometry and scrolling](#3-geometry-and-scrolling)
- [4. State and interaction](#4-state-and-interaction)
- [5. Validation and acceptance](#5-validation-and-acceptance)

## 1. Status and scope

**Approved by the user and implemented on 2026-11-19.** Startup and results: [0.0.10 guide](FRONTEND_STAGE_9_EN.md). Based on the user's request to reduce cards to 50%, including fonts, and add a zoom setting.

This stage extends the [expanded card](TZ_FRONTEND_STAGE_8_EN.md). Frame and excessive minimum height corrections were completed separately within stage 8 and are described in the [0.0.9 guide](FRONTEND_STAGE_8_EN.md).

Zoom applies to the entire technology field: cards, text, images, inner spacing, frames, glow, area/tier headings, gaps and connection lines including bridges, dots and arrows. The menu, status bar, scrollbars, dropdowns and tooltips retain their normal size. Browser page zoom remains independent.

## 2. Controls and configuration

Add a “Zoom” / «Масштаб» setting below the language selector in the expanded menu, using the existing UI-kit select element. Collapsing the menu hides the setting with its contents.

The initial value is **50%**. Available choices: **50%, 75%, 100%, 125%, 150%**. 100% corresponds to the stage 8 base card geometry. At 50%, linear dimensions and fonts are halved; a 520 px card occupies 260 screen pixels.

Store the initial value and allowed percentages in a separate `config/frontend/zoom.json`. Labels and accessible names come from the embedded RU/EN dictionaries. Generate choices from configuration; the initial value must be included. Do not add a custom range selector, slider or zoom shortcuts.

## 3. Geometry and scrolling

Text measurement, shared card height and connection routing use base coordinates at 100%. Render the resulting field with a single zoom factor. Changing zoom alone does not change text wrapping, parent relationships, logical rows/columns or the selected combination.

Calculate scrollable bounds from the scaled field width and height. Scrollbars must reach its right and bottom edges without empty space from the original 100% bounds. Scale cards and SVG together: connection endpoints remain on card outer boundaries, and bridges/corner dots retain their positions relative to lines.

When zoom changes, preserve the field point previously at the viewport centre. If this is impossible near an edge, clamp offsets to available scroll limits. Account for viewport changes when scrollbars appear or disappear. Initial set opening retains the existing initial field position.

## 4. State and interaction

Zoom is session state, retained across language/theme changes, menu collapse and opening another database set. Page reload uses the configured initial value. Persistent settings remain a separate task.

Hover, focus and connection highlighting use the actual on-screen card positions. Tooltips anchor to scaled cards, remain inside the window and retain their normal text size. Changing zoom closes the current tooltip to avoid leaving it at an outdated position. Keyboard navigation to a card scrolls the field correctly.

The setting is available before opening a database. Changing zoom does not read set files, invoke the backend or calculate parents again. Language changes retain the existing measurement/layout process, followed by the selected zoom factor.

## 5. Validation and acceptance

- Check initial 50% and every proposed percentage, mouse/keyboard selection and RU/EN labels.
- Check proportional card, text, icon and connection dimensions, with no truncated names or detached line endpoints.
- Check both scroll edges, centre preservation, edge clamping and scrollbar appearance/disappearance.
- Check parent/child highlighting, tooltips and keyboard focus scrolling at 50%, 100% and 150%.
- Check retained zoom across language/theme/menu/set changes and reset on page reload.
- Check the real prepared set and a synthetic long-name example. Production build and TypeScript checks must pass.

The result requires user visual review in the application; no game launch is needed.
