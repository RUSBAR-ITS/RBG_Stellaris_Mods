# Stellaris Technological Tree View — Tooltip element specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and input settings](#composition-and-input-settings)
- [Showing and hiding](#showing-and-hiding)
- [Placement and styling](#placement-and-styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the current requirements agreed by the user on 2026-11-16. Future extensions will be discussed separately. The element has not been implemented yet.

Tooltip is a shared reusable element for button hints and technology names with descriptions. The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md).

## Composition and input settings

Content consists of body text and an optional heading above it. Both parts use the basic [Text](TZ_TEXT_EN.md) element with their own styling roles. The consuming component supplies a source, a body string ID, a heading string ID when a heading is present, and an anchor element. The source defaults to built-in; technology cards use the database. The source and corresponding ID are passed to each Text instance, while the system provides the language.

| Data or setting | Purpose |
| --- | --- |
| Optional source | Built-in strings by default, or the application database |
| Body string identifier | Tooltip body text key for the Text element |
| Optional heading identifier | Key of a separate string above the body text |
| Anchor element | Interface element relative to which the tooltip is placed |
| Visibility condition | Determines whether the tooltip should currently be shown |
| Styling role | Dictionary variables for the tooltip and its text |

The table describes the required information, rather than final API parameter names or the mechanism used to pass it.

Without a heading, only body text is displayed. For a technology card, the heading contains the full name and the body contains the description; the card's two-line name limit does not apply to the tooltip.

## Showing and hiding

The tooltip has hidden and visible states. Its consuming component determines the visibility condition; shared placement and styling rules belong to the tooltip.

- Button conditions for pointer hover, keyboard focus, and an absent hint are defined in the [Button specification](TZ_BUTTON_EN.md#tooltip-binding).
- A [technology card](TZ_TECHNOLOGY_CARD_EN.md) shows its name and description when any part is hovered, including padding; moving the pointer away hides the tooltip.

Tooltip is one shared UI element type; its rules are not copied into separate implementations for each consumer.

## Placement and styling

- The tooltip is placed beside its anchor element over interface content.
- Showing and hiding it does not move cards, buttons, or other elements.
- Placement respects visible boundaries: positioning beyond an edge must not clip the tooltip.
- For [bottom menu group](TZ_MENU_BUTTON_GROUP_EN.md) buttons, the tooltip may extend beyond group and panel boundaries without clipping while staying within visible window bounds, including when the panel is collapsed.
- In the [technology viewport](TZ_TECHNOLOGY_VIEWPORT_EN.md), scroll container boundaries likewise do not clip the tooltip; it remains within visible window bounds and does not affect field dimensions, scroll ranges, or scrollbar visibility.
- Background, border, and text colors, together with typography properties, come from the [styling dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for the active day or night theme.
- Placement and styling rules are shared across tooltip uses; the consumer supplies the particular content and anchor element.

## Acceptance criteria

Checks are performed after implementation:

- Body text and a supplied heading resolve through their source and respective IDs using shared Text and update when RU/EN changes; checks cover a built-in hint by default and database strings.
- Without a heading, only body text is displayed; when provided, the heading appears above the body and uses its own styling role.
- Transitions between hidden and visible states follow the consumer's visibility condition.
- The same shared element is used for a button hint and a technology name with its description; a name shortened in the card remains fully available in the tooltip.
- Showing and hiding it does not change the size or position of other elements.
- Placement is checked near every visible edge; the tooltip remains within the visible area.
- Bottom menu button hints are not clipped by group or panel boundaries in expanded or collapsed states.
- Card tooltips near viewport edges are not clipped by the scroll container and do not change field dimensions, scroll ranges, or scrollbar visibility.
- Both themes apply colors and typography from the dictionary.
- Button visibility scenarios from its specification are verified, including the absence of a configured hint.

## Subsequent implementation details

Specific parameter and variable names, anchoring mechanism, preferred placement side, spacing, and allowed dimensions are determined during implementation design. Handling text that exceeds the available area must also be determined at that stage.

[Русская версия](TZ_TOOLTIP_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
