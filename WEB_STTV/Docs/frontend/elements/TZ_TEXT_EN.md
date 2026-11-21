# Stellaris Technological Tree View — Text element specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Content and input settings](#content-and-input-settings)
- [Shared lookup and source configuration](#shared-lookup-and-source-configuration)
- [Styling and roles](#styling-and-roles)
- [States and interaction](#states-and-interaction)
- [Placement and overflow](#placement-and-overflow)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

This document records the requirements agreed by the user on 2026-11-16 during discussion of the basic Text element. The element has not been implemented yet.

The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md). The element is intended for reuse in technology names, descriptions, and setting labels.

## Content and input settings

Text lookup needs three values: a source, a string identifier within that source, and a language. The consuming component supplies the source and identifier; the system provides the current language from application state. The identifier is required; when no source is explicitly supplied, built-in interface localization is used.

Two sources are supported:

- **Built-in:** separate localized interface string files; the language setting determines which file is used.
- **Application database:** object localization already stored in `enrichments.localization`. For the selected language, the relevant field's (`name` or `description`) `text` is used; the storage structure is described in the [stage-ten guide](../../BACKEND_STAGE_10_EN.md#database-storage-and-reading).

Text uses a shared localization mechanism to retrieve the string. Consuming components pass a source and identifier without duplicating translation lookup. Identifiers resolve within the selected source. Changing the language updates text for the same source/identifier pair; the element does not choose a language independently of the application. The database source does not require moving game strings into built-in interface files.

The source parameter selects storage for display. The `source` field within a database localization record has a different purpose: translation provenance, including tier, file, and line.

Required input data and settings:

| Data or setting | Purpose |
| --- | --- |
| Optional source | Built-in interface localization by default, or the application database |
| String identifier | Required text identifier within the selected source |
| System-provided language | Current `ru` or `en` localization from application state |
| Optional built-in template parameters | Named values, such as `number` for a variant label; do not change the string ID |
| Styling role | Named variable set for this text purpose |
| Parent component state | Selects the corresponding variables when styling depends on state |
| Alignment and size constraints | Placement within the consuming component |
| Overflow mode | Full wrapping text or a limited number of lines |
| Maximum line count | Limit for the line restriction mode |

The table describes the required information, rather than final API parameter names or the mechanism used to pass it.

## Shared lookup and source configuration

Lookup follows the [Shared localization specification](../TZ_LOCALIZATION_EN.md). Built-in files and the database may have different structures; the shared lookup mechanism receives a source, string ID, and language and applies the selected source description. Text does not construct paths based on a particular storage structure.

Each source configuration must describe:

- Where data and localization records reside.
- How the system language selects a file or language branch.
- How the supplied string ID matches a key or record field.
- Where the resulting text is retrieved from.

Example request: database source, string ID `tech_titans`, and system language `ru`. The shared mechanism uses database configuration, finds the corresponding record, and returns its `text`: Титаны. The consuming component does not additionally supply `name` or `description`: it supplies a string ID, and source configuration describes internal addressing.

The current database nests strings within objects and their variants. On loading, the reader builds an in-memory index by `requested_key` for each language; display uses `text`. The `key` field describes the actual selected translation and does not replace the lookup ID. Under the [index record specification](../TZ_LOCALIZATION_INDEX_EN.md), duplicates with matching text merge while preserving provenance; differing texts under one ID and language produce a blocking preparation error requiring manual investigation. Missing strings display `⟦string ID⟧`; empty strings remain empty. No automatic language substitution occurs.

The built-in source reads separate RU/EN JSON dictionaries. Its templates may receive named parameters such as `{number}`. Database strings do not pass through the interface parameter processor. Language changes use the already prepared index; replacing a source rebuilds its index.

## Styling and roles

Named variables in a separate dictionary define:

- Text color.
- Font family.
- Font size.
- Font weight.
- Line height.

Variable assignments and their day/night values follow the [Styling dictionary specification](../TZ_STYLING_DICTIONARY_EN.md). Role-owned CSS variables reference shared definitions in the dictionary. Concrete color and typography values are not duplicated in the element or its consuming components.

A technology name, description, and setting label may use different variable sets while sharing the same basic Text element. References to shared definitions are assigned in the dictionary. In the first stage, a role's family, size, weight, and line height are identical in day and night themes; the font supports Cyrillic and Latin characters.

## States and interaction

When text styling changes on hover or another parent component state, variables for that state are used. The element introduces neither an independent action set nor its own click action.

States affecting a particular text instance are defined by the consuming component's requirements.

## Placement and overflow

The consuming component specifies alignment and size constraints. Two modes are supported:

1. **Full display:** text wraps at word boundaries and remains fully visible.
2. **Line restriction:** text occupies no more than the specified number of lines; if that limit is exceeded, an ellipsis appears at the end of the visible portion. Text that fits does not receive an ellipsis.

The mode and maximum line count are chosen when specifying the card, tooltip, and other composite elements. Display restrictions apply to the resolved text without modifying its identifier or content in the selected source.

The database retains the source string. When rendering it, Text applies the game palette to colored spans. Other notation, including icons and unresolved substitutions, is displayed literally. [Game name colors](../TZ_TECHNOLOGY_TOOLTIP_CONTENT_EN.md#game-name-colors)

## Acceptance criteria

Checks are performed after implementation:

- With no explicit source, the identifier resolves to a string from the built-in file for the selected language; explicitly choosing the built-in source gives the same result.
- Choosing the database displays the corresponding object's name or description `text` in the selected language.
- The identifier resolves within the selected source, including when the same identifier exists in another source; consuming components do not contain text literals.
- Switching RU/EN resolves the same source/identifier pair to the corresponding translation through the shared localization mechanism.
- The language comes from application state; the consuming component supplies a string ID and, when needed, a source and named built-in template parameters.
- Built-in storage and the database use the shared mechanism with separate configurations; knowledge of paths and field locations is not duplicated in the element or its consumers.
- The same element is used for names, descriptions, and labels with different styling roles.
- All five styling properties listed above are defined through the dictionary; changes to assigned variables affect the display in both themes.
- Parent state changes apply the corresponding text styling without introducing an independent click action.
- Full display mode wraps long text containing spaces at word boundaries and retains all content.
- Line restriction mode is checked with short text that fits without an ellipsis and long text that ends with an ellipsis when it exceeds the limit.
- Changing available width preserves the selected overflow mode and specified alignment.
- Duplicates, conflicts, missing strings and built-in template parameters follow the localization specification. For a colored name, verify that the name has the game color and the following text returns to its ordinary color.

## Subsequent implementation details

Specific parameter and variable names, dictionary integration, and the interface library are determined during implementation design. Modes and dimensions for individual uses are specified in the corresponding composite element specifications.

Built-in JSON dictionaries, the in-memory index, lookup by `requested_key`, duplicates, and missing text are described in the [Localization specification](../TZ_LOCALIZATION_EN.md). The complete configuration schema, resource loading, API, and diagnostics require implementation design. Configured lookup handles internal name/description fields and conditional variants; they do not become additional element parameters. Existing localization storage within database objects is retained; no index is added to the database file.

[Русская версия](TZ_TEXT_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
