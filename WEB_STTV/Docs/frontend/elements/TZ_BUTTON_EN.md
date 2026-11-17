# Stellaris Technological Tree View — Button element specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and input settings](#composition-and-input-settings)
- [Layout and border](#layout-and-border)
- [States and styling](#states-and-styling)
- [Activation and accessibility](#activation-and-accessibility)
- [Tooltip binding](#tooltip-binding)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the current requirements agreed by the user on 2026-11-16, including optional text and icon, border configuration, and shared tooltip binding. Future extensions will be discussed separately. The element has not been implemented yet.

Button is a shared element for interface actions. Menu items, panel collapse, and theme switching can use this element. The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md).

## Composition and input settings

The button uses [Text](TZ_TEXT_EN.md), [Icon](TZ_ICON_EN.md), and, when a hint is provided, [Tooltip](TZ_TOOLTIP_EN.md).

Each text label, action name, and hint may receive a source alongside its identifier under the Text specification. Built-in interface strings are the default; an explicitly selected database source is searched instead. The button passes the source and identifier together to the shared localization mechanism.

| Data or setting | Purpose |
| --- | --- |
| Optional string identifier | Visible label key for the Text element |
| Optional icon | Symbol from the shared set |
| Action | Action assigned by the consuming component |
| Dimensions, spacing, and content placement | Button layout |
| Styling role | Dictionary variables by purpose and state |
| Border visibility by state | Visible or hidden decorative border |
| Accessible action name identifier | Localized name key; may match the visible label key |
| Optional tooltip binding | Hint string identifier for the shared Tooltip element |

The table describes the required information, rather than final API parameter names or the mechanism used to pass it. Text-only, icon-only, and combined uses are supported.

## Layout and border

The consuming component specifies dimensions, spacing, and content placement. The active area covers the entire button, including its padding.

The border can be visible or hidden depending on state. For example, a menu item may show it only on hover. Changing border visibility does not resize the button or shift its content.

## States and styling

Default, hover, focus, and pressed states are supported. Background, border, text, and icon colors, together with label typography, are assigned through the [styling dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) according to theme and state.

Text and Icon use styling for the state of their containing button. Keyboard focus remains distinguishable when the decorative border is hidden; border visibility does not replace the focus indication.

## Activation and accessibility

Mouse and keyboard activation are supported. One activation invokes the assigned action once, including when the text, icon, or padding is clicked. The consuming component determines the action's meaning.

The visible label may serve as the accessible action name. A button without text receives a localized name identifier separately. All strings, including the accessible name, are resolved through the shared localization mechanism using the current application language.

## Tooltip binding

The button uses the shared [Tooltip](TZ_TOOLTIP_EN.md) element; its placement and styling rules are defined in the separate specification.

- If no hint is provided, no tooltip appears.
- If a hint is provided, the tooltip appears when the button is hovered **or** has keyboard focus.
- The tooltip hides when both conditions are absent. Moving the pointer away while keyboard focus remains does not hide it; losing focus while hover remains also does not hide it.
- The button itself is the anchor. The hint string identifier is supplied by the consuming component.

## Acceptance criteria

Checks are performed after implementation:

- Text-only, icon-only, and combined variants are displayed through the respective basic elements.
- Dimensions, spacing, and content placement match consumer settings.
- Visible and hidden borders, including hover transitions, preserve button size and content placement.
- Default, hover, focus, and pressed states apply the assigned variables in both themes.
- Keyboard focus remains distinguishable with a hidden border.
- Mouse activation over content and padding, as well as keyboard activation, invokes the action once.
- The label, accessible action name, and hint are resolved by identifiers and update when the language changes.
- No configured hint means no tooltip. With a hint, hover, focus, their combination, and the absence of both conditions are checked.

## Subsequent implementation details

Specific parameter and variable names, dimensions, text/icon layout rules, and focus styling are determined during implementation design. The button's role in menus and particular actions are specified by its consuming components.

[Русская версия](TZ_BUTTON_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
