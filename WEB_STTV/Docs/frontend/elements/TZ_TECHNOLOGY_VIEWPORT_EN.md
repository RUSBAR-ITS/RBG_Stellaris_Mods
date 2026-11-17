# Stellaris Technological Tree View — Technology viewport specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and responsibility](#composition-and-responsibility)
- [Position and dimensions](#position-and-dimensions)
- [Scrolling and initial position](#scrolling-and-initial-position)
- [Retaining the current position](#retaining-the-current-position)
- [Tooltips and styling](#tooltips-and-styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the technology viewport requirements agreed by the user on 2026-11-16. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md). The viewport is the container to the right of the menu through which a portion of the overall technology field is visible.

## Composition and responsibility

The viewport contains the technology field and scrollbars when content overflows. It determines the visible portion of the field and manages the current viewing position.

The field is shown in Ready under the [database opening specification](../TZ_DATABASE_OPENING_EN.md#interface-states). In other states, the viewport stays clear. Messages reside in the separate [Status panel](TZ_STATUS_PANEL_EN.md), and database actions in the menu.

The [Technology field](TZ_TECHNOLOGY_FIELD_EN.md) determines card placement in rows and columns. Cards follow [their own specification](TZ_TECHNOLOGY_CARD_EN.md); horizontal and vertical scrollbars follow the shared [Scrollbar specification](TZ_SCROLLBAR_EN.md).

## Position and dimensions

The viewport sits to the right of the [Menu panel](TZ_MENU_PANEL_EN.md) and occupies all remaining width and height above the bottom status panel. Scrollbars belong to this region and do not overlap the status panel. Collapsing the menu expands the viewport into the released space; expanding the menu makes it occupy the remaining space again.

Resizing the window or panel changes the dimensions of the visible portion of the field. Card dimensions and their assigned positions within the field remain unchanged.

The field is left-aligned, including when it is narrower than the viewport. At the leftmost scroll position, only a small configurable gap from the panel precedes `Level-0`. Expanding the viewport does not create additional empty space before it.

## Scrolling and initial position

The default initial viewing position is the upper left corner of the field. A supplied restored position takes precedence and is clamped to the valid range under the [Main window specification](TZ_MAIN_WINDOW_EN.md#shared-state-and-initial-values); cross-launch restoration is designed separately.

- The vertical scrollbar sits on the right and appears when content overflows vertically.
- The horizontal scrollbar sits at the bottom and appears when content overflows horizontally.
- Each direction is checked separately; both scrollbars are available when content overflows in both directions.
- Technology scrolling is independent of menu content scrolling; the menu panel remains in place.

Required scrollbars remain visible throughout overflow and do not overlap each other. The viewport supplies each scrollbar with content and viewport extents on its axis, the current offset, and change handling. Thumb properties, dragging, track clicks, and scrollbar keyboard interaction follow the shared scrollbar specification.

The mouse wheel over the viewport scrolls the field vertically; `Shift` + wheel scrolls horizontally. The viewport updates the corresponding offset and thumb position. Interaction on one axis retains the other's valid offset.

## Retaining the current position

Changing language or theme, resizing the window, or collapsing and expanding the menu does not reset current scrolling. Horizontal and vertical offsets are retained while they remain valid.

If resizing puts a previous offset outside the valid range, it is clamped to the nearest valid value on that axis. A direction without overflow has a valid offset of zero. A range change on one axis does not reset a valid position on the other.

These requirements apply within the current session. Persistence across launches will be discussed with the [shared application state mechanism](../CONCEPT_EN.md#settings-and-state-persistence); no separate viewport storage is defined.

## Tooltips and styling

The shared [Tooltip](TZ_TOOLTIP_EN.md) appears over content and does not affect field dimensions, scroll ranges, or scrollbar visibility. Scroll container boundaries do not clip the hint; placement respects visible window bounds.

The viewport background uses its own named variable in the [color and typography dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for day and night themes. Scrollbars are styled under their shared specification; child cards and tooltips follow their own styling rules.

## Acceptance criteria

Checks are performed after implementation:

- The viewport occupies all space to the right of the menu and the available height above the status panel, changing width when the menu collapses and expands; scrollbars do not overlap the status panel.
- Resizing the viewport preserves card dimensions and assigned positions within the field.
- Without restored state, the initial position is the upper left corner; a supplied restored position takes precedence subject to valid bounds. At the leftmost scroll position, only the configured small gap precedes `Level-0`, including when the field is narrower than the viewport.
- Checks cover no overflow, vertical-only overflow, horizontal-only overflow, and overflow on both axes; the respective scrollbars appear on the right and at the bottom.
- Required scrollbars remain visible during overflow without overlapping; the extents and offsets supplied to them match the field and visible portion.
- Dragging, track clicks, wheel, `Shift` + wheel, and keyboard interaction synchronize field and thumb positions under the scrollbar specification; the other axis's valid offset is retained.
- Technology and main menu content scrolling are independent; the menu panel does not move with the field.
- Switching RU/EN and day/night themes retains valid current scroll offsets.
- Window resizing and menu collapse/expansion retain valid offsets; invalid offsets are clamped to the nearest limit on their own axis, including zero when overflow disappears.
- Tooltips near viewport edges are not clipped by the container, remain within visible window bounds, and do not change field dimensions or scrollbars.
- The background in both themes comes from its own dictionary variable; child elements follow their styling specifications.

## Subsequent implementation details

Concrete spacing values, parameter and styling variable names, layout technique, scrolling management, and tooltip placement are determined during implementation design. Technology chain formation and card placement rules belong to the technology field. Loading, missing data, and data error behavior are considered separately.

[Русская версия](TZ_TECHNOLOGY_VIEWPORT_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
