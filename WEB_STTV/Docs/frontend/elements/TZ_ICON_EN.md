# Stellaris Technological Tree View — Icon element specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Content and input settings](#content-and-input-settings)
- [Size and placement](#size-and-placement)
- [Styling and states](#styling-and-states)
- [Interaction](#interaction)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the requirements agreed by the user on 2026-11-16 during discussion of the basic Icon element. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md). The element is intended for reuse in buttons and other interface components.

## Content and input settings

The element displays a symbol selected by its consuming component from a shared icon set. The consuming component decides which symbol represents an interface action or state.

| Data or setting | Purpose |
| --- | --- |
| Selected icon | Symbol from the shared icon set |
| Size and position | Placement within the consuming component |
| Styling role | Named color variable for this icon purpose |
| Parent state | Selects the color variable when styling depends on state |

The table describes the required information, rather than final API parameter names or the mechanism used to pass it.

## Size and placement

The consuming component specifies size and placement. Resizing preserves the original image proportions: width and height are not independently stretched in a way that distorts the symbol.

Specific dimensions and spacing for buttons and other uses are defined in the corresponding component specifications.

## Styling and states

A named variable in the separate styling dictionary defines the color according to the active theme and parent state. The [color and typography dictionary rules](../CONCEPT_EN.md#color-and-typography-dictionary) apply; concrete color values are not duplicated in the element or consuming components.

If color changes on hover, press, or another parent state, variables for that state are used. The supported states are determined by the consuming component's requirements. Shared color values can be referenced through an additional dictionary variable layer when needed.

## Interaction

The icon has no click action of its own. A button or another containing element provides interaction.

Symbol changes, for example when the containing component changes state, are determined by that component; the icon displays the supplied selection.

## Acceptance criteria

Checks are performed after implementation:

- The selected symbol from the shared set is displayed; changing the supplied selection changes the displayed icon.
- Size and placement match the consuming component's settings.
- Different sizes preserve the original image proportions.
- Color comes from the assigned dictionary variable and matches the active day or night theme.
- Parent state changes apply the corresponding color variable when that styling change is defined.
- The icon does not trigger an independent click action; interaction remains the containing element's responsibility.

## Subsequent implementation details

The shared icon set format and source, symbol identifiers, API parameter and variable names, and rendering mechanism are determined during implementation design. Behavior for a missing requested icon must also be determined at that stage.

[Русская версия](TZ_ICON_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
