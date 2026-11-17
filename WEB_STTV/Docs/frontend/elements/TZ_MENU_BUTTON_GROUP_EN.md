# Stellaris Technological Tree View — Bottom menu button group specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Group composition](#group-composition)
- [Position and dimensions](#position-and-dimensions)
- [Collapsed menu](#collapsed-menu)
- [State and responsibility](#state-and-responsibility)
- [Styling and tooltips](#styling-and-tooltips)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the bottom menu button group requirements agreed by the user on 2026-11-16. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md), [UI element list](../UI_ELEMENTS_EN.md), and [Menu panel specification](TZ_MENU_PANEL_EN.md). The group handles control button placement at the bottom of the panel and their visibility when collapsing.

## Group composition

The group consists of two agreed elements in a single horizontal row:

- On the left, the [Menu collapse/expand button](TZ_MENU_TOGGLE_EN.md).
- Immediately to its right, the [Theme toggle](TZ_THEME_TOGGLE_EN.md).

Actions, icons, localized hints, accessible names, and mouse and keyboard operation are defined by these elements' specifications.

## Position and dimensions

The group sits at the bottom of the panel, outside its scrollable main content. It remains available while the menu and technology field scroll. Its buttons align to the right edge of the panel with a small amount of padding.

Both buttons have the same width and height. Their dimensions do not stretch with panel width. Button dimensions, the gap between them, and group padding are defined in settings; concrete values are determined during implementation design.

Group height is determined by button height and vertical padding. Expanding and collapsing the menu do not change that height.

## Collapsed menu

When collapsed, only the expand button remains. The theme button is hidden; neither its space nor the gap between buttons is reserved.

The remaining button retains its size. The narrow panel is as wide as this button plus minimal padding under the [Menu panel specification](TZ_MENU_PANEL_EN.md). Expanding restores both buttons in the defined order.

## State and responsibility

The group receives expanded state from the panel or shared application state and uses it for element placement and visibility. The corresponding components handle theme and expansion changes through application state under their own specifications.

Hiding the theme button does not change the active theme. Settings storage and restoration between launches belong to the [shared application mechanism](../CONCEPT_EN.md#settings-and-state-persistence); the group introduces no separate storage.

## Styling and tooltips

The group shares the menu panel background and uses its variable from the [color and typography dictionary](../CONCEPT_EN.md#color-and-typography-dictionary). Child buttons use their own styling variables for the current theme and state.

Hints use the shared [Tooltip](TZ_TOOLTIP_EN.md). It may extend beyond group and panel boundaries so that the narrow collapsed menu does not clip its content. The tooltip must still remain within the visible window bounds. Showing and hiding conditions are defined by the button specifications.

## Acceptance criteria

Checks are performed after implementation:

- In the expanded menu, buttons form a single row at the bottom right: collapse on the left and theme immediately to its right.
- The group remains available when main menu content and the technology field scroll.
- Buttons have identical configured dimensions and do not stretch when panel width changes; the gap and padding match settings.
- In the collapsed menu, only the expand button remains, with no space or gap reserved for the hidden theme button.
- Collapsing and expanding preserve menu button size and group height; expanding restores the defined button order.
- The group reflects panel state; button actions follow their specifications, and hiding the theme button retains the active theme.
- The background matches the panel; buttons use their own dictionary variables for both themes and states.
- Tooltips are available in expanded and collapsed menus, are not clipped by group or panel boundaries, and remain within the visible window bounds; built-in strings update when RU/EN changes.

## Subsequent implementation details

Concrete dimensions and spacing, setting and API parameter names, layout technique, and tooltip placement mechanism are determined during implementation design. This document defines group behavior and responsibility without selecting a particular implementation mechanism.

[Русская версия](TZ_MENU_BUTTON_GROUP_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
