# Stellaris Technological Tree View — Color and typography dictionary specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Two variable levels](#two-variable-levels)
- [Usage and naming](#usage-and-naming)
- [Day and night themes](#day-and-night-themes)
- [Agreed palette](#agreed-palette)
- [Element states](#element-states)
- [Typography and text roles](#typography-and-text-roles)
- [File organization](#file-organization)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the styling dictionary structure, palettes, and typography agreed by the user on 2026-11-16. The dictionary resides in separate CSS files with named variables used directly by the interface. Implementation of the product's dictionary and interface has not started.

The basis is the [interface concept](CONCEPT_EN.md#color-and-typography-dictionary) and element specifications in the [UI reference](UI_ELEMENTS_EN.md). The dictionary defines colors and typography properties for all current elements and their agreed states.

## Two variable levels

Two levels are defined:

| Level | Purpose | Examples |
| --- | --- | --- |
| Shared variables | Reusable styling values, including surface background, primary text, border, and interface font | `--sttv-surface-background`, `--sttv-text-primary`, `--sttv-font-family` |
| Element variables | A specific property of an element or its part, accounting for state | `--sttv-tech-card-background-default`, `--sttv-tech-card-title-color` |

An element variable may reference a shared variable. Concrete values and links between variables are assigned in the dictionary. Values unique to an element are also assigned there.

Example assignments inside the dictionary:

```css
--sttv-tech-card-background-default: var(--sttv-surface-background);
--sttv-tech-card-title-color: var(--sttv-text-primary);
--sttv-tech-card-title-font-family: var(--sttv-font-family);
```

The example illustrates the connection between the two levels; it is not a complete variable inventory or a ready-to-use CSS file.

## Usage and naming

An element references its own styling variables. When several elements share an appearance, their separate variables reference shared definitions. Changing one element variable's assignment allows changing that element independently of others.

Component and view styles do not duplicate color literals or typography values. Shared values are consumed through element variable assignments in the dictionary.

Names are written in English with the `--sttv-` prefix and identify the element, property role, and state where applicable. For example, `--sttv-tech-card-background-hover` describes the card background on hover, while `--sttv-tooltip-text-color` describes tooltip text color. The final name inventory is determined during implementation design.

Shared Text and Icon elements receive a styling role from their consuming component under their specifications. A card title, button label, and tooltip text therefore use their own variables while reusing the basic element.

## Day and night themes

Each theme supplies the complete set of values in use, directly or through shared definitions. Every used variable must have a defined chain of assignments leading to a concrete value in both themes.

Switching themes changes assignments throughout the interface. Components and views continue using the same variable names; they do not introduce their own color values for theme switching.

Identical values may reference shared definitions. Repeating the same values in both theme files is unnecessary when the shared dictionary portion makes them available in each theme.

## Agreed palette

The styling uses neutral gray backgrounds and a muted green accent for hover, selection, and focus. Research areas are distinguished by headings in the first stage; separate area palettes are not introduced.

| Role | Day theme | Night theme |
| --- | --- | --- |
| Technology field background | `#F3F5F7` | `#151B20` |
| Menu panel background | `#E8EDF0` | `#1C252C` |
| Card, tooltip, and default control background | `#FFFFFF` | `#263139` |
| Hover background | `#E6F2EE` | `#303F47` |
| Pressed background | `#D3E8DF` | `#374C52` |
| Primary text | `#202A32` | `#E6EDF2` |
| Secondary text | `#53616D` | `#ADBCC6` |
| Default border | `#73828E` | `#6F828E` |
| Selection and focus accent | `#176B50` | `#79CEAA` |

Values are assigned to shared dictionary definitions. Element-owned variables reference them according to role and state. On hover, a card or control uses the hover background and accent border; a pressed control uses the corresponding background. Focus uses the accent. States apply only where defined by the element specification.

Contrast was calculated for primary, secondary, and accent text on five backgrounds: field, menu, default surface, hover, and pressed. The minimum across these combinations is **4.97:1** in the day theme and **4.65:1** in the night theme. These calculations cover the listed colors; actual interface rendering is checked after implementation. The accent is intended for emphasis and focus; using it as a fill with text on top requires a separate text-color assignment.

## Element states

Variables are created only for states specified for that element. For example, buttons account for hover and pressed states, while scrollbar thumbs account for dragging. A state supported by one element does not need to be added to other elements.

When values match across elements or states, their respective variables explicitly reference a shared definition. This keeps assignments unambiguous and allows changing one state independently.

The component selects a variable for its state; the dictionary determines its value. Child text and icon styling follows the consuming component's state under their specifications. State changes retain geometry where required by the element specification.

## Typography and text roles

The dictionary defines the following for each text role:

- Font family.
- Font size.
- Font weight.
- Line height.

Text color uses a separate color variable for that role. Technology names, descriptions, setting labels, and other uses have their own assignments under the [Text specification](elements/TZ_TEXT_EN.md#styling-and-roles).

In the first stage, typography is identical in day and night themes: a role's family, size, weight, and line height remain unchanged when switching themes. Shared definitions allow these values to be reused.

**Inter** is selected for both languages. Cyrillic and Latin coverage is confirmed by the [Google Fonts family metadata](https://github.com/google/fonts/blob/main/ofl/inter/METADATA.pb).

| Text role | Size, CSS px | Line height, CSS px | Weight |
| --- | --- | --- | --- |
| Technology name in a card | 15 | 20 | 500 |
| Tooltip description | 15 | 22 | 400 |
| Technology name in a tooltip | 16 | 22 | 600 |
| Research area heading | 18 | 24 | 600 |
| Tier heading | 13 | 18 | 500 |
| Button and select text | 14 | 20 | 500 |

Sizes are given in CSS pixels at normal interface scale. Values reside in the dictionary and are reused through text-role variables. Typography for other roles is assigned when defining the complete variable inventory.

Inter files are bundled with the portable application and loaded locally: installing the font in Windows and internet access during application use are unnecessary. The font is distributed with its copyright notice and [SIL Open Font License 1.1](https://github.com/rsms/inter/blob/master/LICENSE.txt). Specific font files, their version, and loading paths are determined during implementation design.

## File organization

The dictionary is divided into small CSS files by responsibility:

| Part | Contents |
| --- | --- |
| Shared definitions | Reusable values, including typography shared by both themes |
| Theme values | Assignments for day and night themes |
| Element assignments | Variables for specific elements and states, their shared references or dedicated values |

Element assignments are distributed across separate small files. Composite components and views use their elements' variables, preserving the separation between the dictionary and interface layout.

Exact paths, filenames, loading method, and the active-theme selection mechanism are determined during implementation design. This stage defines the CSS format and responsibility split between dictionary parts.

## Acceptance criteria

Checks are performed after implementation:

- The dictionary resides in separate CSS files; shared definitions, theme values, and element assignments are separated.
- Components and views use element-owned variables for colors and typography without repeating concrete values in their styles.
- Names use the `--sttv-` prefix and unambiguously identify the element, property, and applicable state.
- Every used variable resolves to a concrete value in both themes; missing references and cyclic assignments are not allowed.
- Changing a shared variable affects all assignments referencing it. Changing one element's assignment does not change other elements' independent assignments.
- All agreed states of used elements have the required assignments; identical values are reused through explicit shared-definition references.
- Theme switching updates the entire interface, including open lists and tooltips, while preserving variable names used by components.
- Each text role defines color, family, size, weight, and line height; its typography is identical across both themes.
- Palette values and the listed text roles match the agreed tables in this document.
- Inter loads from the application distribution without system installation or an external service; Cyrillic and Latin characters render in interface strings, technology names, and descriptions. The distribution includes the font copyright notice and license.
- Element state changes retain geometry under the respective specification.

## Subsequent implementation details

The [Status panel](elements/TZ_STATUS_PANEL_EN.md) also receives its own background, border, message color, and typography variables. The shared Text element receives the panel role. Assignments for both themes and whether states need distinct values belong to subsequent design; this addition does not assign new concrete colors or font sizes.

Under the [frontend structure specification](TZ_STRUCTURE_EN.md), the dictionary and shared styles reside in `src/frontend/styles/`, component styles beside their components, and local fonts in `src/frontend/assets/`. The complete variable inventory and assignments for current elements remain to be defined using the agreed palettes and typography. Exact CSS files and loading order, Inter files and version, active-theme representation, and precedence among simultaneous states also require design.

Card dimensions, panel widths, spacing, and other layout parameters are defined in their respective specifications and implementation settings. This document covers the color and typography dictionary.

[Русская версия](TZ_STYLING_DICTIONARY_RU.md) · [Interface concept](CONCEPT_EN.md).
