# Frontend stage 10 — tree and DLC settings sections

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Navigation](#2-navigation)
- [3. DLC list](#3-dlc-list)
- [4. Draft and application](#4-draft-and-application)
- [5. Tree and loading states](#5-tree-and-loading-states)
- [6. UI kit and styling](#6-ui-kit-and-styling)
- [7. Data and local API](#7-data-and-local-api)
- [8. Validation and deliverables](#8-validation-and-deliverables)

## 1. Status and scope

**Approved by the user on 2026-11-19; implemented.** Results and startup: [guide](FRONTEND_STAGE_10_EN.md).

Calculations run in Python under [backend stage 20](../TZ_BACKEND_STAGE_20_EN.md). This document covers navigation, list, selection state, UI kit and integration. Implementation follows the approved specification.

## 2. Navigation

Add two entries to the expanded menu:

| RU | EN | Main content |
| --- | --- | --- |
| Древо технологий | Technology tree | Existing technology field |
| Настройка DLC | DLC settings | DLC list and selection actions |

Start in the tree section. Distinguish the active entry visually and programmatically. Reuse the existing button with a menu-item style; visible borders are optional. Entries disappear with the collapsed menu; the bottom expansion button keeps existing behavior. Do not introduce another concealed navigation panel.

Open set and export report remain shared menu actions. Language, theme and menu collapse work in both sections. Show zoom in the tree section and retain its value across navigation. Theme/language apply to both views; the bottom status panel is shared.

Navigation neither reopens the set nor recalculates parents nor clears draft selections. Preserve the tree viewport until application and restore it when returning without profile changes. The list has independent vertical scrolling and does not use field zoom.

## 3. DLC list

On the first visit, selectively load `dlcs` and required assets from the opened set, then reuse them within the session. Do not load all other catalogs. Include all imported catalog entries, including those without descriptors/thumbnails. `show`, `hide_if_unowned` and local file presence do not determine user choices.

Each row contains a small image on the left, full localized name, two-state switch on the right and Enabled/Disabled text. “Slider” means an on/off switch, not a continuous range. Support mouse and keyboard, with an accessible name tied to the DLC title.

Sort by the current language's display name, with stable ID as the final tie-breaker. Use the existing technical fallback if translation is missing. Missing images use a neutral placeholder of the same size. Wrap full names instead of truncating them. Decorative images do not duplicate spoken titles.

Read images from prepared set assets by DLC ID, without accessing game directories. Missing images do not disable DLC or its switch. Cosmetic entries may be toggled; the tree can remain unchanged when they do not affect inspected conditions.

## 4. Draft and application

Distinguish `draft` switch values from the `applied` profile matching the displayed tree. Explicitly opening a new set initializes both with all catalog DLC enabled; IDs/counts come from the catalog.

Switching changes only draft. Place Apply and Discard changes below the list; the former prepares a combination, the latter restores the applied profile. Disable both when unchanged. Do not add enable-all/disable-all, search or grouping without a separate need.

Apply submits a full draft snapshot and original revision. Freeze that submitted draft during the operation: disable switches/repeated application and provide cancellation. Navigation remains available. The status panel shows tree preparation.

Only after successfully receiving/preparing a consistent result replace applied profile, combination, cards and lines atomically. Stay in the current section; the user chooses when to return to the tree. On error/cancellation retain the previous tree/applied profile and keep the draft for editing/retry.

While unapplied changes exist, the status panel explains that the tree uses previous settings, including when viewing the tree. An operation error takes precedence over this notice.

Keep selections across navigation, language, theme and zoom changes within the session. Page reload does not restore the profile or automatically open the database. Cross-launch persistence belongs to the future shared state mechanism; do not add an isolated DLC store.

## 5. Tree and loading states

After application, rebuild the grid and lines using the new parent/child combination. Hidden technologies reserve no card cells. Preserve research area order, actual tiers, approved repeatable tier promotion, language sorting, zoom, bridges and connection highlighting.

The previous complete tree may remain visible during calculation with a clear preparation status. Do not present old edges as results of the new profile. On success retain the previous viewport center where possible, clamping scrolling to the new geometry.

Without an opened set, show a request to open one; opening remains in the menu. Handle catalog loading, read failure/retry, empty catalog, unavailable local service, mismatching set and calculation failure separately. A result excluding every technology is an explained empty tree, not a JSON error.

Visibility comes from the backend. Do not implement a second frontend evaluator of potential, zero weights or parent selection. Unknown conditions retain technologies under backend policy; reports preserve analytical limitations.

## 6. UI kit and styling

Extend the atomic UI kit with:

- a base on/off switch with label, focus and on/off/disabled states;
- a composite DLC row containing resource image, text and switch;
- a DLC settings view composed of rows, action block and loading state;
- a navigation variant of the existing button without duplicated behavior.

Define colors/fonts for every state through named day/night styling variables. Configure image geometry, spacing, row width and menu order. Research-area colors do not indicate DLC state. All UI strings, accessible labels and messages use RU/EN localization through the common text component.

Keep UI_ELEMENTS as a linked list. Switch/row requirements may be split into separate documents during implementation without changing approved behavior. Do not introduce a component library just for an on/off control.

## 7. Data and local API

Development adds the explicitly started service described by the backend specification. Opening a directory remains explicit. Verify that its manifest matches the configured service set; the browser sends no absolute paths.

Initial opening requests or calculates the all-enabled combination over existing databases. If the service is unavailable, an already prepared matching combination may open, but new selections cannot be applied. Do not substitute visual card hiding without parent recalculation.

After publication obtain the current manifest and changed documents through the API. Existing Files are not automatically updated. Extend the common byte reader and Worker protocol while preserving hashes, selective loading and unchanged-document reuse. Do not send full database trees to React.

Bind every response to set identity, original/result revisions, request ID and combination. Opening another set cancels prior requests; late responses cannot alter the new screen. Language changes during calculation do not cancel DLC selections: render the returned result in the current language.

## 8. Validation and deliverables

Verify navigation, viewport/zoom retention, menu collapse, both themes/languages, long names, absent translations/images, keyboard switching and accessible labels.

Verify all-enabled initialization, draft changes without recalculation, discard, one request applying several changes, cancellation, errors/retry, preservation of prior results and rejection of stale replies. Language changes must not alter selected DLC.

On a real set cover positive/negative DLC conditions, zero modifiers and unknown OR branches; replacement of a hidden parent and empty trees. Compare cards/lines against the Python report and ensure no forbidden visible parent remains.

Confirm selective reads for the list, cached revisits, no game parsing on Apply and no unnecessary reads of all 25 kinds. Test adopting the new manifest and changed files, and absence of automatic generation on reload.

After approval/implementation provide FRONTEND_STAGE_10_RU/EN guides and update UI inventory, README, concept and changelog. Record actual unit/browser checks and latency measurements. Implementation and acceptance are recorded in the linked guide.
