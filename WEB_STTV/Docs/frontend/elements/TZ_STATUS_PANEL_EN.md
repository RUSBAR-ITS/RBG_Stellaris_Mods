# Stellaris Technological Tree View — Status panel specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and responsibility](#composition-and-responsibility)
- [Position and dimensions](#position-and-dimensions)
- [Messages and localization](#messages-and-localization)
- [Styling](#styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the agreed status panel requirements for the initial interface. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md), [UI element list](../UI_ELEMENTS_EN.md), and [database opening specification](../TZ_DATABASE_OPENING_EN.md#interface-states). The panel continuously displays the current database state at the bottom of the main window.

## Composition and responsibility

The panel is a composite UI kit element using the shared [Text element](TZ_TEXT_EN.md). In the first stage, it contains one short message about the current state.

The application supplies a built-in message identifier and any required parameters. Language comes from shared application state. The panel displays the supplied data; database reading, requirement processing, technology counting, and Worker management take place outside it.

Open database, Cancel, Retry, and [Save report](../TZ_DIAGNOSTIC_REPORT_EN.md) actions reside in the [Menu panel](TZ_MENU_PANEL_EN.md). The status panel does not contain those buttons. The workspace does not duplicate its messages: it shows the technology field in Ready and stays clear in the other states.

## Position and dimensions

The panel sits at the bottom of the [Main window](TZ_MAIN_WINDOW_EN.md) across its entire width, below the menu and technology viewport.

- It remains visible and occupies its own space in the layout.
- The menu and viewport sit above it and use the remaining window height.
- The panel does not participate in menu or technology scrolling and does not overlap their content or scrollbars.
- Collapsing the menu neither changes the status panel width nor hides it.
- The bottom menu button group stays at the bottom of the menu itself, above the status panel.

Height, padding, and exact text behavior when width is insufficient are refined during implementation design. The first stage uses short messages and simple styling.

## Messages and localization

The panel reflects the five states from the database opening specification: No database open, Loading, Ready, Empty catalog, and Error. During loading, the message identifies the current stage without completion percentages. Cancellation, retry, and file replacement change the message according to application state; the panel does not determine those transitions itself.

| State or stage | RU message example | EN message example |
| --- | --- | --- |
| No database open | БД не открыта. Откройте файл через меню. | No database open. Open a file through the menu. |
| File reading | Загрузка: чтение файла… | Loading: reading file… |
| JSON parsing | Загрузка: разбор JSON… | Loading: parsing JSON… |
| Data preparation | Загрузка: подготовка данных… | Loading: preparing data… |
| Ready | БД открыта. Технологий: {count}. | Database opened. Technologies: {count}. |
| Empty catalog | В выбранной БД нет технологий. | No technologies found in the selected database. |
| JSON error | Не удалось открыть БД: некорректный JSON. | Could not open database: invalid JSON. |

The Ready message receives the actual number of base technologies from the prepared catalog. Variants are not added to this count. The value is not hardcoded into the string; it is supplied as a built-in template parameter under the [localization specification](../TZ_LOCALIZATION_EN.md).

Blocking errors use the agreed [diagnostic strings](../TZ_DIAGNOSTICS_EN.md#interface-message). The main thread maps `code` to the `sttv_diagnostic_<code>` identifier through diagnostic configuration, uses the `builtin` source, and supplies `params: {}`. RU/EN texts reside in the built-in localization files. Technical `details` are retained separately and do not replace the panel message. The `missing_localization` warning remains in diagnostics and does not replace the successful-load message with the technology count.

Changing language updates the current message without reopening the database. The panel stays visible and continues reflecting state when the menu is collapsed; the user expands the menu to access database actions.

## Styling

Background, border, message color, and typography use the panel's own named variables in the [styling dictionary](../TZ_STYLING_DICTIONARY_EN.md). The shared Text element uses the supplied panel role.

Day and night themes define every used assignment. Variables may reference shared dictionary values; color and font literals are not duplicated in the component. Specific assignments and whether states need distinct values are refined during implementation design.

## Acceptance criteria

Checks are performed after implementation:

1. The panel sits at the bottom of the window across its full width and stays visible, including when the menu is collapsed.
2. The menu and viewport sit above the panel; it occupies its own space without overlapping content or scrollbars.
3. Technology and menu scrolling do not move the status panel; bottom menu buttons remain above it.
4. The panel shows one short message for each of the five states; loading identifies the current stage without percentages.
5. The Ready message uses the technology count from the catalog. Variants are not counted as separate base technologies.
6. Messages use built-in RU/EN strings and the shared Text element; changing language updates the message without reloading the database.
7. Database actions reside in the menu. The workspace does not duplicate messages and shows the field only in Ready.
8. Both themes use the panel's own variables for colors and typography; the component does not repeat concrete values.

## Subsequent implementation details

The element API, identifiers for the remaining state messages, height, padding, long-text behavior, and exact styling variable names and assignments remain to be defined. IDs and texts for current diagnostic messages are already established in their specification. The panel uses the agreed application states; this document does not introduce new transitions or actions.

[Русская версия](TZ_STATUS_PANEL_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
