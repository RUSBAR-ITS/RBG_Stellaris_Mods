# Stellaris Technological Tree View — Technology tier column specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and input data](#composition-and-input-data)
- [Heading and localization](#heading-and-localization)
- [Dimensions and card placement](#dimensions-and-card-placement)
- [Empty column](#empty-column)
- [Scrolling and styling](#scrolling-and-styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the technology tier column requirements agreed by the user on 2026-11-16. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md), [UI element list](../UI_ELEMENTS_EN.md), [Technology field specification](TZ_TECHNOLOGY_FIELD_EN.md), and [Research area region specification](TZ_RESEARCH_AREA_EN.md). A column contains technologies of one `tier` within one research area.

## Composition and input data

The column is composed of the shared [Text](TZ_TEXT_EN.md) element for its heading and a vertical list of shared [Technology cards](TZ_TECHNOLOGY_CARD_EN.md).

| Data or setting | Purpose |
| --- | --- |
| `tier` value | Technology level of the column and number in its heading |
| Heading string ID | Obtaining the level label from built-in interface localization |
| Ordered cards | Membership and order already determined by the field for this tier and area |
| Shared field grid | Column horizontal position and gaps between columns |
| Shared width | Equal configured column width matching the card width |
| Vertical spacing and gaps | Heading placement, list start, and distances between cards |
| Styling roles | Dedicated column and heading variables for both themes |

The table describes the required information; final parameter names and the mechanism used to pass them are determined during implementation design. Language and theme come from application state. The column displays cards in the supplied order; technology assignment and sorting belong to the field.

## Heading and localization

A level label and number matching `tier` appear above the cards: “Уровень 0” / “Level 0”, “Уровень 1” / “Level 1”, and so on. The heading is repeated in each research area.

The heading uses shared Text and built-in interface localization. Text receives a string ID with the default source; the system supplies the language. Changing language updates the label while retaining the `tier` value, card membership, and card order.

The heading's left edge aligns with the cards' left edge. Column headings align vertically within one research area; card lists also start at the same height.

## Dimensions and card placement

All columns have the same configured width matching the card width. The shared field grid determines horizontal positions and gaps; the same `tier` retains its position across research areas.

Cards appear from top to bottom in the supplied order with an equal configurable vertical gap. Column height is determined by its heading, cards, and configured spacing and gaps. The research area region accounts for its tallest column when determining its own height.

Window or menu size changes affect the visible portion of the field under the viewport specification. Card dimensions and column positions assigned by the grid are retained.

## Empty column

If an area has no technologies of a given tier, the column retains its width, horizontal position, and heading. Neighboring columns remain in place, keeping tiers aligned across areas regardless of card presence.

This also applies when membership changes: if moving the last card makes a column empty, its heading and grid position remain. When cards appear, they are placed below the heading under the shared rules.

## Scrolling and styling

The heading and cards move with their research area during horizontal and vertical field scrolling. The [technology viewport](TZ_TECHNOLOGY_VIEWPORT_EN.md) provides the visible portion and scroll handling.

Column and heading colors and typography use dedicated named variables in the [styling dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for day and night themes. The heading uses its own styling role of shared Text. Cards retain styling under their own specification.

## Acceptance criteria

Checks are performed after implementation:

- The column displays cards of one tier and area in the order supplied by the field.
- The heading contains the correct `tier` number and “Уровень” / “Level” label in the system language from built-in localization through shared Text; it repeats in each research area.
- The heading aligns with the cards' left edge; headings and card list starts align vertically within the region.
- All columns have the same configured width matching the card; horizontal positions and gaps follow the shared field grid.
- Cards appear from top to bottom with an equal configured gap; column height accounts for its heading, cards, and spacing.
- An empty column retains its heading, width, and position; neighboring tiers do not shift. Checks cover an initially empty column and removal of its last card when a technology variant changes research area.
- When cards appear in an empty column, they occupy the regular positions below the heading while retaining alignment with other columns.
- The heading and cards scroll with the region on both axes; window and menu changes retain card dimensions and column positions.
- Changing language updates the heading while retaining `tier` and card order; both themes use dedicated column variables and child card styling under the card specification.

## Subsequent implementation details

Concrete width, spacing and gap values, parameter and styling variable names, string IDs, and the mechanism for forming a localized label with its level number are determined during implementation design. Input data format and the layout mechanism also remain to be defined. Loading and data-error states are considered separately.

[Русская версия](TZ_TIER_COLUMN_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
