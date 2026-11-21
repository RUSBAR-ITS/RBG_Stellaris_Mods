# Tabs

## Contents

- [Purpose](#purpose)
- [Interaction](#interaction)

## Purpose

The UI kit element shows one of several panels in the main view. Its parent supplies stable IDs, localized label keys, content, the selected ID and the selection callback. A single tab retains its visible label. The settings screen owns DLC draft and mode state. [Usage](../TZ_FRONTEND_STAGE_11_EN.md)

## Interaction

Clicking a tab selects its panel. In a horizontal tab list, Left and Right move focus and selection to the adjacent tab and wrap at the ends. Home and End select the first and last tab. Tab advances from the selected tab to the available controls in the panel. Hidden panels are excluded from keyboard navigation.

Connect tabs and panels with `tablist`, `tab`, `tabpanel`, `aria-selected`, `aria-controls` and `aria-labelledby`. In both themes the selected tab has a visible marker and keyboard focus has a separate indicator. Colors and fonts use styling dictionary tokens.
