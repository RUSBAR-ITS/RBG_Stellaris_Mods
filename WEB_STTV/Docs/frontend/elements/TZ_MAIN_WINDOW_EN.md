# Stellaris Technological Tree View — Main window specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and responsibility](#composition-and-responsibility)
- [Layout and dimensions](#layout-and-dimensions)
- [Resizing and scrolling](#resizing-and-scrolling)
- [Shared state and initial values](#shared-state-and-initial-values)
- [Overlays](#overlays)
- [Styling and interface updates](#styling-and-interface-updates)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the main window requirements agreed by the user on 2026-11-16. Interface implementation has not started yet.

The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md). The main window assembles UI kit elements into a single view and occupies the entire available application area.

## Composition and responsibility

The main window combines:

- On the left, the [Menu panel](TZ_MENU_PANEL_EN.md) with database actions above language selection and the bottom group of menu collapse and theme buttons.
- On the right, the [Technology viewport](TZ_TECHNOLOGY_VIEWPORT_EN.md), containing the [Technology field](TZ_TECHNOLOGY_FIELD_EN.md) and scrollbars when content overflows.
- At the bottom across the full width, the [Status panel](TZ_STATUS_PANEL_EN.md) with the current database message.
- Overlays belonging to child components: [Tooltips](TZ_TOOLTIP_EN.md) and [Selection lists](TZ_SELECT_EN.md).

The window connects child elements to shared application state: language, theme, menu state, selected technology representations, and viewing position. Element changes pass through this connection; current values are supplied back to the consuming components.

The field determines card placement, the viewport manages the visible portion and offsets, and individual controls follow their own specifications. Input data formats and programming interfaces for these connections are determined during implementation design.

## Layout and dimensions

The bottom of the window reserves its own space for the status panel across the full width. The menu panel and viewport sit side by side above it and occupy the remaining window height. The expanded menu uses its configured width; the viewport receives the remaining width on the right. The status panel remains visible, does not scroll with content, and does not overlap content or scrollbars.

Collapsing the menu leaves a narrow strip sized to the expand button with minimal padding. The button remains at the bottom of the menu, above the status panel; main menu content, including database actions, and the theme button are hidden under the panel specification. The viewport occupies the released space. The status panel retains its width and visibility.

## Resizing and scrolling

Resizing the window or collapsing and expanding the menu changes the visible portion of the field. Card and column dimensions and assigned positions within the field are retained.

The field is left-aligned. When viewing its left edge, only the small configured gap precedes `Level-0`; expanding the viewport does not add empty space before it.

The technology field and main menu content scroll independently. The panel stays in place when technologies scroll. The [Bottom menu button group](TZ_MENU_BUTTON_GROUP_EN.md) sits outside the scrollable main content and remains accessible at the bottom of the panel.

Valid current viewing offsets are retained under the viewport specification. If resizing puts an offset outside the range, it is clamped to the nearest valid boundary on that axis; when the axis has no overflow, its valid offset is zero.

## Shared state and initial values

Initial values when no restored state is supplied:

| Setting | Value |
| --- | --- |
| Language | Russian, `ru` |
| Theme | Night |
| Menu panel | Expanded |
| Technology representations | Base version of each technology |
| Field viewing position | Upper left corner: zero offsets on both axes |

Restored state takes precedence over initial values. A restored viewing position respects the viewport's valid bounds.

Storage, writing, and restoration across launches are designed separately within the [shared state mechanism](../CONCEPT_EN.md#settings-and-state-persistence). This document defines initial values and use of supplied state; the persistence mechanism has not been determined yet.

Under the [startup and existing database opening specification](../TZ_DATABASE_OPENING_EN.md), the initial screen prompts the user to open a database. Startup and page refresh do not load it automatically or invoke the generator. The technology field appears after explicit selection of a prepared JSON and successful data preparation. Representation and field-position values apply after opening; they do not trigger automatic file loading.

Messages for No database open, Loading, Ready, Empty catalog, and Error appear in the status panel under the [database opening specification](../TZ_DATABASE_OPENING_EN.md#interface-states). The workspace shows the field only in Ready and stays clear in other states. Available database actions reside in the menu above language selection. Language, theme, and menu collapse remain available during processing. Successful database replacement resets representation selections to base versions and the field position to the upper left corner while retaining language, theme, and menu state. Cancelling file selection preserves the previous screen; cancelling an active load returns to the status-panel prompt to open a database.

## Overlays

Tooltips and selection lists appear over content and respect the main window's visible bounds. Showing them does not change the main layout, card dimensions, or field scroll ranges.

Nested panel and scroll container boundaries do not clip overlays. Opening, closing, and interaction follow the respective element specifications. In particular, opening a technology variant list hides that card's tooltip under the card specification.

Specific side selection, placement, and handling of content exceeding the available window dimensions are refined in the relevant specifications during implementation design.

## Styling and interface updates

The first stage uses a simple design. The window's own colors use named variables in the [styling dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for day and night themes. Child elements use their own styling roles and specifications.

Changing language updates localized strings throughout the interface, including labels, technology names, descriptions, and open overlays. Changing theme updates styling throughout the interface. Both actions retain the current menu state, selected technology representations, and valid scroll position.

## Acceptance criteria

Checks are performed after implementation:

- The window occupies the entire available application area; the menu is on the left and the viewport on the right, both occupying the remaining height above the status panel.
- The status panel remains visible at the bottom across the full width, does not overlap content or scrollbars, and retains its width when the menu collapses. Messages reside in it, and database actions in the menu; the workspace does not duplicate messages.
- The expanded panel has its configured width; collapsing it leaves the expand button with minimal padding, and the viewport receives the released space.
- Window and menu state changes retain card and column dimensions and positions within the field; the visible portion changes.
- When viewing the left edge, only the configured gap precedes `Level-0`, including when the field is narrower than the viewport.
- Technology and main menu content scrolling are independent; bottom menu buttons remain in place and accessible.
- Without restored state, defaults are Russian, the night theme, an expanded menu, base technology versions, and the upper left field position.
- Supplied restored state takes precedence over initial values; offsets respect viewport bounds. Actual writing and restoration across launches are checked under the separate persistence specification after its implementation.
- Tooltips and lists near edges respect window bounds, appear over content without clipping by nested containers, and do not change the main layout or field scroll ranges.
- Language and theme changes update the entire interface, including open overlays, while retaining representation selections, menu state, and valid offsets.
- The window's own colors and child element styling use the corresponding dictionary variables in both themes.

## Subsequent implementation details

Component structure and state connections, integration of Worker results, specific parameter and variable names, dimensions and spacing, overall keyboard focus order, and the technical overlay placement mechanism remain to be defined. The initial screen, explicit File API opening, Web Worker processing, and loading, empty-catalog, error, cancellation, and replacement behavior are established in the startup specification. Actions reside in the menu and messages in the status panel; the technical implementation of transitions is refined separately.

Cross-launch persistence and the first frontend implementation stage specification will be prepared separately. Specifications for all current UI elements do not imply that these shared mechanisms have already been designed or implemented.

[Русская версия](TZ_MAIN_WINDOW_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
