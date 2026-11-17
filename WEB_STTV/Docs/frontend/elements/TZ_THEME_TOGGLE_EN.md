# Stellaris Technological Tree View — Theme toggle specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and action](#composition-and-action)
- [Placement and visibility](#placement-and-visibility)
- [Initial value and persistence](#initial-value-and-persistence)
- [Styling](#styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the day/night theme toggle requirements agreed by the user on 2026-11-16. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md). The toggle changes styling throughout the interface.

## Composition and action

The element consists of a shared [Button](TZ_BUTTON_EN.md) with an [Icon](TZ_ICON_EN.md) and a bound [Tooltip](TZ_TOOLTIP_EN.md). There is no visible text label. Mouse and keyboard activation, button states, and hint visibility follow the basic element specifications.

The icon represents the action of the next activation:

| Active theme | Icon | Action |
| --- | --- | --- |
| Night | Sun | Enable day theme |
| Day | Moon | Enable night theme |

The tooltip and accessible action name explain the same action. The button receives their string identifiers using the default built-in source; separate localized files determine the text using the application language, following the [Text specification](TZ_TEXT_EN.md).

The current theme comes from application state. On activation, the component reports a switch to the other theme. The change applies immediately throughout the interface, including the menu, cards, and tooltips; the icon and hint update for the next action.

## Placement and visibility

- In the expanded menu panel, the button sits at the bottom, to the right of the collapse button.
- Collapsing the menu hides the theme button; the selected theme remains active.
- Expanding the menu shows a button reflecting the active theme and offering the opposite one.

Dimensions and spacing are determined when designing the bottom menu button group.

## Initial value and persistence

The first launch uses the night theme. The application supplies the initial state; a restored user selection takes precedence.

Persisting the theme between launches belongs to the [shared settings and state persistence mechanism](../CONCEPT_EN.md#settings-and-state-persistence), which requires separate design and a specification. The toggle receives the current value and reports changes; persistent storage is managed at the application layer.

## Styling

Button, border, and icon colors, together with tooltip styling, are defined by named variables in the [color and typography dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for the active theme and state. Shared Button, Icon, and Tooltip rules apply.

## Acceptance criteria

Checks are performed after implementation:

- The button displays an icon without a visible text label and uses the shared tooltip.
- In the night theme, the sun enables the day theme; in the day theme, the moon enables the night theme.
- One mouse or keyboard activation switches the theme once and immediately updates the whole interface.
- The icon, tooltip, and accessible name match the next action; strings resolve by identifiers and update when RU/EN changes.
- The expanded menu places the button at the bottom, to the right of collapse; the collapsed menu hides it. Collapsing and expanding retain the theme.
- The first launch without a restored value uses the night theme; a restored selection takes precedence.
- Button states and tooltip styling use dictionary variables for both themes.

Actual persistence and restoration across launches are checked after implementing the shared mechanism under its separate specification.

## Subsequent implementation details

API parameter names, icon and string identifiers, styling variables, dimensions, and application state integration are determined during implementation design.

[Русская версия](TZ_THEME_TOGGLE_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
