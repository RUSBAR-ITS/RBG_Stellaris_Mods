# Stellaris Technological Tree View — Language selector specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and options](#composition-and-options)
- [Applying the selected language](#applying-the-selected-language)
- [Initial value and persistence](#initial-value-and-persistence)
- [Styling](#styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the language selection requirements agreed by the user on 2026-11-16. The element has not been implemented yet.

The element controls the language of the interface, technology names, and tooltip descriptions. The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md).

## Composition and options

The composite element includes a label using the basic [Text](TZ_TEXT_EN.md) element and a dropdown [Selection control](TZ_SELECT_EN.md). Mouse and keyboard interaction follow the base dropdown specification.

Setting label:

| Current language | Label |
| --- | --- |
| `ru` | Язык |
| `en` | Language |

Available options:

| Value | Option label |
| --- | --- |
| `ru` | Русский |
| `en` | English |

The setting and option labels are passed to basic elements as string identifiers using the default built-in source. The strings listed in the tables reside in separate RU and EN localization files. The setting label uses the same identifier in both languages, with Язык and Language as its values. Option labels remain as listed regardless of the selected language: their identifiers map to Русский and English in both files.

Option values `ru` and `en` are separate from their label identifiers. The current value comes from application state. When a new option is selected, the component reports the corresponding `ru` or `en` value to the application.

## Applying the selected language

Selection immediately changes the language of:

- Interface elements, including the setting's own label.
- Technology names in cards.
- Technology descriptions in tooltips.

The language setting determines which built-in localized string file and database localization language branch are used. Display elements resolve text by source/identifier pairs through the shared mechanism described in the [Text specification](TZ_TEXT_EN.md).

Technology names and descriptions specify the database source, using prepared RU/EN localization described in the [stage-ten guide](../../BACKEND_STAGE_10_EN.md). The system supplies the current language to the shared lookup mechanism; source configuration defines record locations and ID matching under the [Text specification](TZ_TEXT_EN.md#shared-lookup-and-source-configuration). Switching languages does not rebuild the database or retrieve localization from game files.

Collapsing the menu retains the selected language in application state. Reopening the menu displays the active selection.

## Initial value and persistence

Russian (`ru`) is the initial language on the first launch. The application supplies the initial state; when a restored selection is available, that selection is used.

The selected language is intended to persist between launches through the [shared settings and state persistence mechanism](../CONCEPT_EN.md#settings-and-state-persistence). Its format, storage location, write timing, and restoration order require separate design work and a separate specification.

The element receives the current language and reports changes to the application layer. Independent access to persistent storage is outside the element's responsibilities.

## Styling

The label and dropdown use the styling roles of the basic Text and Selection control elements. Colors and typography come from the [styling dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for the active theme and state.

The menu panel specification determines the composite element's dimensions and position within the panel.

## Acceptance criteria

Checks are performed after implementation:

- The element consists of a label and dropdown with `ru` / Русский and `en` / English options.
- The setting label resolves through one identifier in the selected file: Язык or Language; option labels also resolve by identifiers and retain their specified wording in both localizations.
- Mouse and keyboard selection report the new value to the application and immediately update the language of the interface, technology names, and descriptions.
- Switching uses prepared database localization without collecting game data again.
- The first launch without a restored selection uses `ru`; a restored value supplied by the application is displayed correctly.
- Collapsing and expanding the menu preserves the active language.
- Both themes use dictionary styling for the label and dropdown.

Actual persistence and restoration across launches are verified after implementing the shared mechanism and integrating it with application state; that check belongs to its separate specification.

## Subsequent implementation details

Specific API parameter names, styling variables, interface localization keys, and application state integration are determined during implementation design. Behavior when required text is missing from the data remains a shared localization display concern.

[Русская версия](TZ_LANGUAGE_SELECTOR_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
