# Stellaris Technological Tree View — Scrollbar specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and input data](#composition-and-input-data)
- [Position and visibility](#position-and-visibility)
- [Thumb dimensions and position](#thumb-dimensions-and-position)
- [Mouse interaction](#mouse-interaction)
- [Keyboard interaction](#keyboard-interaction)
- [State and container responsibility](#state-and-container-responsibility)
- [States and styling](#states-and-styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the horizontal and vertical scrollbar requirements agreed by the user on 2026-11-16. Both share common behavior with a choice of orientation. The elements have not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md), [UI element list](../UI_ELEMENTS_EN.md), and [Technology viewport specification](TZ_TECHNOLOGY_VIEWPORT_EN.md). A scrollbar displays the current viewing position on one axis and allows changing it.

## Composition and input data

A scrollbar consists of a track and a thumb.

| Data or setting | Purpose |
| --- | --- |
| Orientation | Horizontal or vertical axis |
| Content extent | Full width or height of the scrollable field on the selected axis |
| Viewport extent | Width or height available for viewing on the same axis |
| Current offset | Viewing position supplied by the container |
| Change handling | Reporting a new offset to the container after user interaction |
| Scrollbar thickness | Configurable cross-axis scrollbar size |
| Minimum thumb size | Lower bound for thumb length to keep it easy to grab |
| Small scroll step | Configurable offset change for arrow key interaction |
| Styling roles | Named track and thumb variables by state and theme |

The table describes the required information; final parameter names and the mechanism used to pass them are determined during implementation design.

## Position and visibility

In the technology viewport, the vertical scrollbar sits on the right and the horizontal scrollbar at the bottom. Each appears only when its axis overflows and remains visible for as long as that overflow exists.

Overflow checks are independent: one scrollbar, both, or neither may be visible. When both are needed, they occupy their respective viewport sides without overlapping each other.

## Thumb dimensions and position

Scrollbar thickness is configurable. Thumb length reflects the visible proportion of the full field extent on its axis, subject to the configured minimum size and available track length.

Thumb position corresponds to the current offset. At the start of the range it is at the beginning of the track; at the end it reaches the track's end. Changes to content or viewport dimensions update thumb length and position from container data.

## Mouse interaction

- Dragging the thumb moves the visible portion of the field along the corresponding axis.
- Clicking the track before or after the thumb scrolls in that direction by approximately one viewport extent on that axis, bounded by the scroll range.
- The mouse wheel over the viewport scrolls the field vertically.
- `Shift` + mouse wheel over the viewport scrolls the field horizontally.

Handling the wheel over content belongs to the viewport. It updates the offset displayed by the corresponding scrollbar, keeping thumb position synchronized with the field.

## Keyboard interaction

A visible scrollbar is reachable with `Tab`. While it has focus:

- For the vertical scrollbar, up and down arrows scroll vertically in small steps.
- For the horizontal scrollbar, left and right arrows scroll horizontally in small steps.
- `Home` moves to the start of the corresponding axis's range.
- `End` moves to the end of the corresponding axis's range.

Interaction on one axis retains the other axis's valid current position. Offsets remain within the range determined by the container.

## State and container responsibility

The scrollbar receives content dimensions, viewport dimensions, and the current offset from its consuming container. User interaction reports a new offset to that container; the scrollbar displays the current value supplied by the container.

The viewport owns the overall field position, clamps offsets when the range changes, and retains the current position under its specification. Changes from the wheel, keyboard, dragging, or container are reflected in thumb position.

Persistence across launches belongs to the shared application mechanism. A scrollbar introduces no state storage of its own.

## States and styling

The track and thumb use named variables in the separate [styling dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for day and night themes.

The thumb distinguishes default, hover, dragging, and scrollbar keyboard focus states. A state change updates styling while preserving geometry: scrollbar thickness and calculated thumb length. Thumb movement itself reflects changes in viewing position.

## Acceptance criteria

Checks are performed after implementation:

- Scrollbars consist of a track and thumb; the vertical scrollbar is on the right and the horizontal scrollbar at the bottom.
- Checks cover no overflow, overflow on one axis only, and overflow on both axes; required scrollbars remain visible during overflow and do not overlap each other.
- Thickness follows settings; thumb length reflects the visible proportion subject to the minimum size and available track.
- At the start and end of the range, the thumb reaches the corresponding track edge; resizing updates its geometry and position from container data.
- Dragging scrolls the field on the selected axis; clicking before or after the thumb moves approximately one viewport extent in the correct direction, bounded by the range.
- The wheel over the viewport scrolls vertically, and `Shift` + wheel scrolls horizontally; corresponding thumbs update.
- A visible scrollbar receives focus through `Tab`; arrows on its axis scroll by a small step, and `Home` and `End` move to that axis's start and end.
- Interaction on one axis retains the valid offset of the other; external container position changes are reflected in the thumb.
- Language, theme, and viewport size changes retain position under the container rules; the scrollbar displays the current offset.
- Default, hover, dragging, and keyboard focus states are distinguishable in both themes through dictionary variables; state changes do not alter scrollbar thickness or thumb length.

## Subsequent implementation details

Concrete thickness, minimum thumb length and small-step values, parameter and variable names, and scrollbar and input handling implementation are determined during implementation design. The exact focus order among window elements and behavior when resizing during dragging also remain to be defined.

[Русская версия](TZ_SCROLLBAR_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
