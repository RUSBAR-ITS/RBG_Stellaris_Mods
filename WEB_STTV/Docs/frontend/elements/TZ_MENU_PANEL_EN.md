# Stellaris Technological Tree View — Menu panel specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Panel composition](#panel-composition)
- [Database actions](#database-actions)
- [Position and dimensions](#position-and-dimensions)
- [Scrolling](#scrolling)
- [State and collapsing](#state-and-collapsing)
- [Styling](#styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the menu panel requirements agreed by the user on 2026-11-16. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md). The panel combines database actions, initial interface settings, and controls for its own expanded state.

## Panel composition

The panel is assembled from agreed elements and consists of two regions:

- **Main content at the top:** the database action group, with the [Language selector](TZ_LANGUAGE_SELECTOR_EN.md) below it.
- **Bottom button group:** contains the [Menu collapse/expand button](TZ_MENU_TOGGLE_EN.md) and the [Theme toggle](TZ_THEME_TOGGLE_EN.md) to its right.

Child element behavior, localized string retrieval, and their tooltips follow the respective specifications. Bottom button group layout is defined in its [separate specification](TZ_MENU_BUTTON_GROUP_EN.md): right alignment, identical button dimensions, and no reserved space for the hidden theme button.

## Database actions

The group above language selection uses shared [Button elements](TZ_BUTTON_EN.md). The application determines available actions under the [database opening specification](../TZ_DATABASE_OPENING_EN.md#interface-states):

| State | Visible buttons |
| --- | --- |
| No database open | Open database |
| Loading | Cancel |
| Ready | Open database, Save report |
| Empty catalog | Open database, Save report |
| Error | Retry, Open database, Save report |

Only current-state actions are shown. Save report exports JSON for the current completed attempt under a [separate specification](../TZ_DIAGNOSTIC_REPORT_EN.md), including success without warnings. This button is hidden before opening and during loading. Labels use built-in localization. The panel sends action requests to the application; it does not read the database or manage the Worker itself.

Collapsing hides actions with the main content. The user expands the menu to open, cancel, retry, or save a report; actions for the current state are shown. Messages remain visible in the separate [Status panel](TZ_STATUS_PANEL_EN.md), which is not part of the menu.

## Position and dimensions

The panel sits on the left and occupies the available height above the main window's bottom status panel. It remains in place when technologies scroll. The bottom button group stays at the bottom of the menu, above the status panel.

Expanded panel width and padding are defined in settings. Collapsed panel width is determined by the expand button size plus minimal padding. The button itself retains its size when collapsing and expanding under its specification.

The workspace occupies the space to the right of the panel and expands into the released space when the panel collapses. At the leftmost scroll position, `Level-0` retains only a small gap from the panel, without additional empty space.

## Scrolling

When main content exceeds the available height, it scrolls vertically within its region. Menu scrolling is independent of technology field scrolling.

The bottom button group sits outside the scrollable main content. It remains at the bottom of the panel and available during scrolling; main content does not push it beyond the bottom edge.

## State and collapsing

The panel receives its current expanded state from the application and reports change requests back. The initial state on first launch is expanded; a restored state takes precedence.

When collapsed:

- Main content and the theme button are hidden.
- The expand button remains available at the bottom of the narrow panel.
- The selected language and theme are retained in application state.

Expanding shows main content and the theme button with their active values. Expansion controls follow the corresponding button specification.

Persistence between launches belongs to the [shared settings and state persistence mechanism](../CONCEPT_EN.md#settings-and-state-persistence). Storage format, writing, and restoration are designed separately at the application layer.

## Styling

The panel background and border with the workspace use named variables in the [color and typography dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for day and night themes. Child elements use their own agreed styling rules.

## Acceptance criteria

Checks are performed after implementation:

- The panel sits on the left, occupies the available height above the status panel, and remains in place when technologies scroll.
- When expanded, database actions appear above language selection; the bottom group contains the collapse button and theme button to its right.
- Each database state shows only its corresponding buttons; collapsing hides them, and expanding shows current-state actions. Messages in the bottom status panel remain visible.
- Expanded panel width and padding match settings; the collapsed panel is as wide as the expand button plus minimal padding.
- On overflow, main content scrolls vertically and independently of technologies; bottom buttons remain at the bottom and available.
- Collapsing hides main content and the theme button while retaining the available expand button and active language and theme; expanding restores elements with those values.
- The workspace occupies the released space without additional empty space before `Level-0` at the leftmost scroll position.
- The panel reflects application state and reports toggles; without a restored state, first launch shows an expanded menu.
- Background and border use dictionary variables in both themes; child elements follow their specifications.

Actual persistence and restoration across launches are checked after implementing the shared mechanism under its separate specification.

## Subsequent implementation details

Concrete dimensions, spacing, parameter and styling variable names, region separation, and application state integration are determined during implementation design. Detailed requirements for the bottom button group are described in its separate specification.

[Русская версия](TZ_MENU_PANEL_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
