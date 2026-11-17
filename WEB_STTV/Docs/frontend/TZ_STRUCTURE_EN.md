# Stellaris Technological Tree View — frontend structure specification

## Contents

- [Status and scope](#status-and-scope)
- [Code directories](#code-directories)
- [UI kit categories](#ui-kit-categories)
- [Components and styles](#components-and-styles)
- [Data processing and messaging](#data-processing-and-messaging)
- [Localization and assets](#localization-and-assets)
- [Configuration and working data](#configuration-and-working-data)
- [Acceptance criteria](#acceptance-criteria)
- [Further design](#further-design)

## Status and scope

This document records the agreed frontend directory division and responsibilities. Technologies are defined by the [technology stack specification](TZ_TECH_STACK_EN.md), and element behavior by the [UI element list](UI_ELEMENTS_EN.md) and linked specifications.

This is structure design. The current iteration produces documentation; implementation directories, code, and dependencies are not added yet. Exact filenames and program interfaces are defined separately; messages and operation management are described in the [Worker protocol specification](TZ_WORKER_PROTOCOL_EN.md).

## Code directories

All paths in the table are relative to `WEB_STTV/src/frontend/`.

| Directory | Responsibility |
| --- | --- |
| `app/` | Application startup, shared state, and user action management |
| `ui/` | UI kit divided into the agreed element categories |
| `views/` | Screen composition from UI components; initially the main window |
| `data/` | Database adapter and preparation of technologies, requirements, and links |
| `workers/` | Worker startup and message handling between it and the application |
| `localization/` | String lookup, source readers, index construction, and language selection during lookup |
| `locales/` | Built-in RU/EN interface strings |
| `styles/` | Styling dictionary and shared styles |
| `assets/` | Local fonts and icons |

`app/` connects application state and actions to the view. `views/` composes the screen, while individual UI components receive data and handlers under their specifications. Independent database processing resides in data modules rather than components.

## UI kit categories

Directories follow the existing catalog categories. The Views category resides in `views/` alongside `ui/`.

| Path relative to `src/frontend/` | Initial-stage elements |
| --- | --- |
| `ui/base/` | Text, icon, button, selection control |
| `ui/composite/` | Language selector, theme toggle, menu toggle, technology card, tooltip, status panel |
| `ui/layout/` | Menu panel, bottom button group, viewport, technology field, research area, tier column |
| `ui/scroll/` | Horizontal and vertical scrolling under their shared specification |
| `views/` | Main window |

Categories define component locations without repeating their requirements. The UI element catalog remains a linked list; requirements are maintained in separate documents.

## Components and styles

A component's files and its own styles reside together within the corresponding category. Shared styles and the variable dictionary reside in `styles/`.

Component styles use variables from the [styling dictionary](TZ_STYLING_DICTIONARY_EN.md). Theme and state color and typography values are assigned in the dictionary rather than independently in each component. Keeping CSS beside a component does not change this rule.

Modules remain compact. Repeated logic is extracted into small helper modules beside the functionality that owns it, following the project's general modularity and file size rules.

## Data processing and messaging

`data/` contains independent TypeScript modules for [database adaptation](TZ_DATABASE_ADAPTER_EN.md), technologies, requirements, and links. They do not depend on React, the DOM, or a particular screen.

`workers/` handles communication with the background processor and invokes data preparation modules. Worker startup code executes on the application side, while message handling and processing calls execute in the Worker; sharing a directory does not merge these execution contexts.

The full database tree stays in the Worker. The application receives prepared results under the [database opening rules](TZ_DATABASE_OPENING_EN.md). Preparation algorithms are not duplicated in message handlers or components.

String index construction belongs to `localization/`; its independent modules are invoked during Worker data preparation. The interface uses lookup over the prepared index. One directory can contain modules for both contexts; React does not become a dependency of localization processing in the Worker.

## Localization and assets

`localization/` contains the string handling mechanism; `locales/` contains built-in translations. The `locales/ru.json` and `locales/en.json` files from the [localization specification](TZ_LOCALIZATION_EN.md) are relative to `src/frontend/`. Technology names and descriptions come from the opened database under the same specification.

`assets/` stores local interface resources: fonts and icons. Inter is distributed with the required license materials under the styling specification. Specific font files and their loading method are defined separately.

Language selection resides in application state; the localization mechanism receives it for string lookup and does not create an independent copy of the shared setting.

## Configuration and working data

Frontend configurations reside in `WEB_STTV/config/frontend/`, separate from source code. This is also the root directory for the future localization source configuration. Specific files, schemas, and configuration loading are defined when designing the relevant modules and build.

Diagnostic configuration in this directory defines the code-to-built-in-string-ID mapping under the [diagnostics specification](TZ_DIAGNOSTICS_EN.md#interface-message). Texts reside in `src/frontend/locales/ru.json` and `src/frontend/locales/en.json`; configuration contains identifier mappings without duplicating translations. The exact filename and loading mechanism remain to be defined.

The color and typography dictionary remains CSS in `src/frontend/styles/`, as specified. Built-in translations and resources reside in their own frontend directories and are not moved into the configuration directory.

`src/frontend/data/` contains processing code only. The project working directory `WEB_STTV/data/`, configurable through `WORK_DIR`, holds databases, reports, and checks. The frontend opens a prepared file selected by the user; the existence of the working directory does not imply automatic database loading or generation. The [frontend diagnostic report](TZ_DIAGNOSTIC_REPORT_EN.md) is saved through an explicit user menu action; `WORK_DIR` does not automatically route this export into the working directory.

## Acceptance criteria

Checks are performed after implementation:

1. Code, configuration, and resources are placed according to the responsibilities in the tables.
2. The screen is composed from the UI kit; elements follow the catalog categories.
3. Component styles reside beside their components and use the shared color and typography dictionary.
4. Data processing is checked independently of React and the DOM; the Worker uses these modules without duplicating algorithms.
5. The localization mechanism is separate from built-in translations and the shared language setting.
6. Working databases and reports are not placed in the `src/frontend/data/` code directory.

## Further design

- The adapter result representation and nested message data for the agreed Worker protocol.
- Component input types and application state organization.
- Specific configurations, style and resource files, loading order, and build settings.
- Implementation verification scenarios and tools.

[Русская версия](TZ_STRUCTURE_RU.md) · [Interface concept](CONCEPT_EN.md).
