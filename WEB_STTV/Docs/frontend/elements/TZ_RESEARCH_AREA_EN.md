# Stellaris Technological Tree View — Research area region specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and input data](#composition-and-input-data)
- [Heading and localization](#heading-and-localization)
- [Columns and dimensions](#columns-and-dimensions)
- [Region separation and scrolling](#region-separation-and-scrolling)
- [Styling](#styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the research area region requirements agreed by the user on 2026-11-16. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md), [UI element list](../UI_ELEMENTS_EN.md), and [Technology field specification](TZ_TECHNOLOGY_FIELD_EN.md). A research area region is a container with a heading and technology columns for one area: Physics, Society, or Engineering.

## Composition and input data

The region is composed of the shared [Text](TZ_TEXT_EN.md) element for its heading and [Tier columns](TZ_TIER_COLUMN_EN.md) containing shared [Technology cards](TZ_TECHNOLOGY_CARD_EN.md).

| Data or setting | Purpose |
| --- | --- |
| Research area ID | `physics`, `society`, or `engineering` |
| Heading string ID | Looking up the title in built-in interface localization |
| Columns with cards | Technologies assigned to tiers and ordered by the field |
| Shared field grid | Field width and horizontal positions of tier columns |
| Padding and gaps | Heading spacing, distance to columns, and gap between regions |
| Styling roles | Named variables for the region and its heading in both themes |

The table describes the required information; final parameter names and the format used to pass them are determined during implementation design. Language and theme come from application state.

The field determines technology area assignments, grouping, and order. The region receives cards that are already assigned and ordered, and arranges the corresponding columns using the shared grid.

## Heading and localization

The heading is placed on the left above the columns. Its left edge aligns with the left edge of `Level-0`.

Built-in interface strings are used:

| Area ID | Russian | English |
| --- | --- | --- |
| `physics` | Физика | Physics |
| `society` | Социология | Society |
| `engineering` | Инженерия | Engineering |

The shared Text element receives the corresponding string ID with the default built-in source. The system supplies the language; the shared localization mechanism selects the translation. Changing language updates the heading while preserving the area ID, card membership, and card order. Texts reside in separate interface localization files.

## Columns and dimensions

Columns use the shared field grid: the same `tier` occupies the same horizontal position in all three regions. An individual region's contents do not change the column positions assigned by the field. Cards within columns appear one below another under the field rules.

Level headings repeat in each region. Column headings and card list starts align vertically within the region; empty columns retain their width, position, and heading under the column specification.

The region width equals the technology field width. Its height is determined by its tallest column together with heading height and configured vertical spacing. The next region starts below the completed previous region with the configured gap between regions.

Card dimensions follow their specification. When column contents change, for example when selecting a variant moves a card, the region height is determined from the updated contents; the field continues to determine card assignments and order.

## Region separation and scrolling

In the simple first-stage design, headings and configurable vertical gaps distinguish regions. Heading spacing and the gap between the heading and cards are also configurable. Horizontal alignment retains the small gap before `Level-0` defined for the field.

The region and its heading participate in horizontal and vertical scrolling of the shared field. The [technology viewport](TZ_TECHNOLOGY_VIEWPORT_EN.md) provides the visible portion and scroll handling.

## Styling

Region and heading colors and typography use their own named variables in the [styling dictionary](../CONCEPT_EN.md#color-and-typography-dictionary). Values are defined for day and night themes and may reference shared theme variables.

The heading uses its own styling role of the shared Text element. Child columns, cards, and their elements follow their respective specifications. Changing theme updates styling while retaining technology membership and order.

## Acceptance criteria

Checks are performed after implementation:

- The region displays supplied columns and cards while preserving membership, grouping, and order assigned by the field.
- Each area ID has the agreed RU/EN heading from built-in localization; the heading uses the shared Text element.
- The heading appears above the columns and aligns with the left edge of `Level-0`.
- Columns of the same `tier` share horizontal positions across regions, including when card counts differ.
- Region width equals field width; with columns of different heights, region height accounts for the tallest column, heading, and spacing.
- The next region starts after the previous one ends with the configured gap; after membership changes, height reflects the updated columns.
- Heading spacing, distance to cards, and gaps between regions come from settings.
- During horizontal and vertical scrolling, the heading moves with its region inside the shared viewport.
- Changing language updates the heading while preserving region identity and card order; changing theme applies dictionary variables without altering technology membership.

## Subsequent implementation details

Concrete spacing values, parameter and styling variable names, interface string IDs, and the layout mechanism are determined during implementation design. Technology tier column requirements are recorded in that element's specification. Entirely empty-region behavior and loading or data-error states are considered separately.

[Русская версия](TZ_RESEARCH_AREA_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
