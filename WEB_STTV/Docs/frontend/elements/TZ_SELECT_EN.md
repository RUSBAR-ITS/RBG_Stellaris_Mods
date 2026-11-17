# Stellaris Technological Tree View — Selection control specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Content and input settings](#content-and-input-settings)
- [Display and selection](#display-and-selection)
- [States and styling](#states-and-styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the current requirements agreed by the user on 2026-11-16. In the first stage, the element is a dropdown with a single selected option. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md). The consuming component determines the particular option set and the meaning of the selected value. The first use is described in the separate [Language selector specification](TZ_LANGUAGE_SELECTOR_EN.md).

## Content and input settings

| Data or setting | Purpose |
| --- | --- |
| Option set | Values and label string identifiers of available options |
| Current value | One selected option from the supplied set |
| Selection handling | The consuming component receives the user's selection |
| Styling role | Named variables for the control and its options by state |

The table describes the required information, rather than final API parameter names or the mechanism used to pass it.

Label identifiers and the current value come from the consuming component. Labels are resolved through the shared localization mechanism using the application language. The element reports the selected value to the consumer, which determines the subsequent action. An option value and its label identifier are separate data; changing the language updates the label while retaining the value.

A label identifier may be accompanied by a source under the [Text specification](TZ_TEXT_EN.md). The source defaults to built-in, and the database is also supported; the source is passed to the shared localization mechanism together with the identifier.

## Display and selection

- The closed control displays the label of the currently selected option.
- Opening the dropdown displays the supplied option set.
- One option is selected at a time.
- Mouse and keyboard interaction and selection are supported.
- When the user selects an option, its value is passed to the consuming component.
- The displayed selection matches the current value provided by the consumer.

Displaying labels by identifier follows the shared requirements for the [Text element](TZ_TEXT_EN.md). The composite component using the dropdown determines the selection's functional purpose.

The open list appears over content under the [Main window specification](TZ_MAIN_WINDOW_EN.md#overlays), respects its visible bounds, and is not clipped by nested containers. Showing it does not change main layout dimensions or field scroll ranges.

When used in a [Technology card](TZ_TECHNOLOGY_CARD_EN.md#variant-list-interaction), the card itself serves as the closed control and list trigger. Its name follows the card specification; list option labels include the agreed variant suffixes. Option order, confirmation and cancellation, keyboard commands, and tooltip suppression for this use are defined in the card specification and implemented through the shared Selection control.

## States and styling

Styling covers the default state, hover, focus, and the selected option. The selected value and focus position are separate properties; styling must make them distinguishable.

Background, border, and text colors, together with typography properties, are assigned through named variables in the [styling dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for the active theme and corresponding state. This applies to the closed control and options in the open dropdown.

## Acceptance criteria

Checks are performed after implementation:

- The supplied option set is displayed with labels resolved by identifiers; the closed control shows the current value's label.
- Selecting an option with the mouse or keyboard passes its value to the consuming component.
- One option is selected at a time, matching the consumer's current value.
- An external change to the current value is reflected in the element.
- Changing the language updates labels through the shared localization mechanism while retaining option values and the current selection.
- Default, hover, focus, and selected option styling use the corresponding dictionary variables in both themes.
- The selected option and focus remain distinguishable during interaction.
- The open list near window boundaries appears over content without clipping by nested containers or changing the main layout or field scroll ranges.

## Subsequent implementation details

Specific parameter and variable names, dimensions, the dropdown implementation mechanism, and keyboard commands not yet defined in the consuming component's specification are determined during implementation design. Behavior for an empty option set or a current value missing from that set must also be determined at that stage.

[Русская версия](TZ_SELECT_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
