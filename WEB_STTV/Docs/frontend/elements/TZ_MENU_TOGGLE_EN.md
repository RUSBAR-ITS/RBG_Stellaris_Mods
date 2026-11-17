# Stellaris Technological Tree View — Menu collapse/expand button specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and action](#composition-and-action)
- [Placement and panel behavior](#placement-and-panel-behavior)
- [Initial value and persistence](#initial-value-and-persistence)
- [Styling](#styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the menu collapse/expand button requirements agreed by the user on 2026-11-16. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md). The button controls the expanded and collapsed states of the menu panel.

## Composition and action

The element consists of a shared [Button](TZ_BUTTON_EN.md) with an [Icon](TZ_ICON_EN.md) and a bound [Tooltip](TZ_TOOLTIP_EN.md). There is no visible text label. Mouse and keyboard activation, button states, and tooltip visibility follow the basic element specifications.

The icon and hint represent the action of the next activation:

| Menu state | Icon | RU hint | EN hint |
| --- | --- | --- | --- |
| Expanded | Left arrow | Свернуть меню | Collapse menu |
| Collapsed | Right arrow | Раскрыть меню | Expand menu |

The tooltip and accessible action name use string identifiers from the built-in source. The system provides the language; strings are retrieved through the shared mechanism under the [Text specification](TZ_TEXT_EN.md). The localized strings listed in the table reside in the corresponding interface files.

The button receives the current menu state and reports a toggle. State changes and showing or hiding content are handled at the panel level. After switching, the icon and hint reflect the next action.

## Placement and panel behavior

- The button remains at the bottom of the panel and is available in both menu states.
- In the expanded menu, the [Theme toggle](TZ_THEME_TOGGLE_EN.md) sits to its right.
- When collapsed, the panel remains a strip as wide as the expand button plus minimal padding. The button itself retains its size when switching.
- Collapsing the panel hides language selection and the theme button; expanding shows them with their active values. The selected language and theme are retained.
- The workspace occupies the space released by collapsing. At the leftmost scroll position, `Level-0` retains only a small gap from the panel, without additional empty space.

Specific dimensions and spacing are determined when designing the panel and bottom menu button group.

## Initial value and persistence

The menu is expanded on the first launch. The application supplies the initial state; a restored menu state takes precedence.

Persisting this state between launches is included in the [shared settings and state persistence mechanism](../CONCEPT_EN.md#settings-and-state-persistence), which requires separate design and a specification. The button receives the current state and reports changes; persistent storage is managed at the application layer.

## Styling

Button, border, and icon colors, together with tooltip styling, are defined by named variables in the [color and typography dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for the active theme and state. Shared Button, Icon, and Tooltip rules apply.

## Acceptance criteria

Checks are performed after implementation:

- The button displays an icon without a visible text label and uses the shared tooltip.
- In the expanded menu, the left arrow collapses the panel; in the collapsed menu, the right arrow expands it. The hint and accessible name match the next action.
- One mouse or keyboard activation switches the state once.
- The button is available at the bottom in both states and retains its size; the collapsed panel width matches the button plus minimal padding.
- Collapsing hides language selection and the theme button; expanding shows them with their previous values.
- The workspace occupies the released space; at the leftmost scroll position, no additional empty space appears before `Level-0`.
- The first launch without a restored state shows an expanded menu; a restored state takes precedence.
- The hint and accessible name resolve through identifiers from the built-in source and update when RU/EN changes; styling follows the dictionary in both themes.

Actual persistence and restoration across launches are checked after implementing the shared mechanism under its separate specification.

## Subsequent implementation details

API parameter names, icon and string identifiers, styling variables, dimensions, and panel state integration are determined during implementation design.

[Русская версия](TZ_MENU_TOGGLE_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
