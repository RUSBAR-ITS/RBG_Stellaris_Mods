# Stellaris Technological Tree View — Technology field specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and input data](#composition-and-input-data)
- [Research areas and columns](#research-areas-and-columns)
- [Technology requirements](#technology-requirements)
- [Vertical order and grouping](#vertical-order-and-grouping)
- [Geometry and viewport](#geometry-and-viewport)
- [Variant selection and display updates](#variant-selection-and-display-updates)
- [Styling](#styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the technology field requirements agreed by the user as of 2026-11-16, including grouping when technology requirement counts are equal. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md). The field determines card placement. A separate [technology viewport](TZ_TECHNOLOGY_VIEWPORT_EN.md) provides its visible portion and scrolling.

## Composition and input data

The field is composed of [Research area regions](TZ_RESEARCH_AREA_EN.md), [Tier columns](TZ_TIER_COLUMN_EN.md), and shared [Technology cards](TZ_TECHNOLOGY_CARD_EN.md).

| Data or setting | Purpose |
| --- | --- |
| Base technology IDs | Stable card identity, requirement matching, and order within groups |
| Current representations | Base version or selected `technology_swap` block for each technology |
| Research area | Placement in Physics, Society, or Engineering according to the selected representation |
| `tier` level | Column assignment |
| `prerequisites` structure | Technology dependencies, requirement count, and immediate predecessor set |
| Card localization data | References to prepared names and descriptions of current representations in the database |
| Geometry settings | Shared card dimensions, padding, and gaps between layout elements |
| Application state | Language, theme, and representation selection for each technology |

The table describes the required information. The logical catalog and representation structure is established in the [Database adapter specification](../TZ_DATABASE_ADAPTER_EN.md); the final program representation is determined during implementation design. The prepared database supplies the data. The field displays one card per base technology using its current representation.

## Research areas and columns

Research areas have a fixed top-to-bottom order:

- Physics — `physics`.
- Society — `society`.
- Engineering — `engineering`.

Columns correspond to `tier` values in ascending order from left to right: `Level-0`, `Level-1`, …, `Level-5` for the current game data. Columns of the same tier align across research areas.

“Уровень N” / “Level N” headings repeat in each area. Columns share a configured width matching the card width; an empty column retains its width, position, and heading without shifting neighboring tiers. Heading and card placement follow the column specification.

Each region contains a localized heading above its columns and spans the field width. Its height is determined by its tallest column together with the heading and spacing. The next region starts below it with a configured gap; the heading scrolls with its region under that element's specification.

Cards within a column of one area are placed one below another. Dependencies across areas remain in the relationship data without changing area order. A requirement for a technology in another column does not move a card out of its own `tier` column.

The field supports placing related cards close together without requiring a single horizontal row for every chain. The agreed first grouping step is described below; manual family definitions belong to later stages.

## Technology requirements

The [technology requirements specification](../TZ_TECHNOLOGY_REQUIREMENTS_EN.md) defines the `AND` root, `technology`/`group` nodes, and links with `requirementPaths`. Paths retain each occurrence's logical context. The rules below concern mandatory requirements and `AND`/`OR` alternatives; using `NOT`, `NAND`, and `NOR` in counting and vertical ordering still requires agreement.

Only technology requirements from `prerequisites` are used for layout. Conditions from `potential`, empire, species, DLC, building checks, and other eligibility restrictions are excluded from the count.

The adapter supplies the requirement tree, and a separate shared processor derives requirement counts, immediate predecessors, and links under the [Adapter specification](../TZ_DATABASE_ADAPTER_EN.md#technology-requirements). The field uses these results for grouping and layout; calculation rules are not duplicated in cards.

Counting rules:

- A single mandatory technology contributes one requirement.
- Simultaneously required technologies are added together.
- An `OR` alternative group counts as one requirement.
- Without technology requirements, the count is zero.

Requirement count and the immediate predecessor set are different properties. The set contains technology IDs mentioned directly in `prerequisites`, including alternative members. ID order does not change the set; predecessors of those technologies are not additionally included.

For example, mandatory technologies `A` and `B` contribute two requirements, while an `OR` group containing `A` and `B` contributes one. Both have the same immediate predecessor set but different requirement counts. Display grouping preserves the original logical requirement structure.

## Vertical order and grouping

Rules apply within one column of one research area with the following precedence:

1. A predecessor appears above its dependent technology when both cards belong to that column and area. This applies throughout the dependency sequence.
2. Subject to the first rule, technologies with fewer technology requirements appear higher.
3. For equal requirement counts, technologies with identical immediate predecessor sets are placed consecutively.
4. Within such a group, ordering is stable by base technology ID.

If rules conflict, technology dependencies take precedence, followed by requirement count. Grouping and ID ordering cannot place a dependent technology above its predecessor. Having no predecessors corresponds to an empty set and zero requirements.

Grouping does not depend on localized titles or merge distinct technologies into one object. With unchanged data and selected representations, changing the language preserves card order. Predecessor sets use base IDs; “(Variant N)” labels do not affect grouping.

Ordering between distinct groups with equal requirement counts and aligning their vertical positions across columns require further design.

## Geometry and viewport

All cards use the same configured dimensions under their own specification. Padding and gaps are defined in layout settings.

The field is left-aligned. Only a small configured gap precedes `Level-0`; no additional empty space is inserted even when the field is narrower than the viewport.

Resizing the window or expanding and collapsing the menu changes the visible portion of the field while preserving card dimensions and assigned positions. Scrollbars, initial view position, and retention of valid offsets belong to the viewport specification.

## Variant selection and display updates

The field uses manual representation selection for each technology under the card specification. If the selected variant specifies a research area, that area is used; otherwise, the base technology's area applies.

When the area changes, the card moves to the corresponding region. Its base ID, `tier`, and technology dependencies are retained; the same vertical ordering and grouping rules apply to the updated layout. Returning to the base version restores its research area. Other technologies retain their own selected representations.

Changing the language updates text, while changing the theme updates styling; neither changes card order. Persistence across launches is considered separately within the shared application mechanism.

## Styling

The first stage uses the simplest practical design. Colors and typography use named variables in a separate [styling dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for both themes. Child cards, selection lists, and tooltips follow their own specifications and styling roles.

## Acceptance criteria

Checks are performed after implementation:

- Areas appear in Physics, Society, Engineering order; columns correspond to `tier` and align across areas.
- Cards appear one below another in each column; each base technology has one card.
- Only `prerequisites` contributes to the count; eligibility conditions do not change the technology requirement count.
- Checks cover no requirements, one mandatory technology, multiple simultaneously required technologies, and an `OR` group.
- A predecessor and its sequence of dependent technologies in one column and area retain their vertical order even when other rules suggest the opposite order.
- Subject to dependencies, technologies with fewer requirements appear higher.
- For equal requirement counts, identical immediate predecessor sets form consecutive groups; ordering within groups is stable by ID while preserving dependency precedence.
- A different listing order of identical predecessors does not create distinct groups; identical sets with different requirement counts do not override requirement-count ordering.
- Dependencies across research areas do not reorder areas, and requirements in other columns do not change a card's `tier`.
- No additional empty space precedes `Level-0`; window and menu size changes retain card dimensions and positions within the field.
- Language and theme changes retain ordering and selected representations; text and styling update under their respective specifications.
- Selecting a variant with another research area moves the technology's single card while retaining its base ID, `tier`, and dependencies; returning to the base version restores its area.

## Subsequent implementation details

As requested on 2026-11-17, the first frontend displays cards without connecting lines. Link data is retained. Implemented ordering and geometry are described in the [first frontend guide](../FRONTEND_STAGE_1_EN.md#display-details). Manual technology family grouping and alignment of related groups across columns will be considered separately.

Research area region and column requirements are recorded in their specifications, and the logical input structure in the Database adapter specification. Exact spacing values, program data representation, and a layout algorithm satisfying the agreed priorities require separate design. Loading, missing-data, and invalid-data behavior are also determined separately. These remaining details are not considered approved by this document.

[Русская версия](TZ_TECHNOLOGY_FIELD_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
