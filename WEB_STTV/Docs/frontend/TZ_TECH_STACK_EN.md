# Stellaris Technological Tree View — frontend technology stack specification

## Contents

- [Status and scope](#status-and-scope)
- [Selected tools](#selected-tools)
- [Interface components](#interface-components)
- [Application state](#application-state)
- [Data processing and Worker](#data-processing-and-worker)
- [Development and build](#development-and-build)
- [Acceptance criteria](#acceptance-criteria)
- [Further design](#further-design)
- [Sources](#sources)

## Status and scope

This document records the agreed choice of React, TypeScript, Vite, and plain CSS for the initial interface. It complements UI element requirements and the [existing database opening specification](TZ_DATABASE_OPENING_EN.md). Interface implementation and dependency installation are not performed during this documentation iteration.

The previously agreed boundaries remain: Python creates and enriches the database separately; the user explicitly opens a prepared JSON file in the browser. The initial interface is tested from the development environment; portable distribution belongs to subsequent stages.

## Selected tools

| Tool | Responsibility |
| --- | --- |
| TypeScript | Types, database processing, localization, Worker communication, and interface logic |
| React | UI kit components, screen composition, and view updates following state changes |
| HTML and plain CSS | Markup, layout, dimensions, styling, and themes |
| Vite | Local development environment and frontend file builds |
| Web Worker | Reading and preparing the selected database outside the main interface thread |

The initial interface uses React's built-in state facilities. The agreed scope does not require an additional state management library.

## Interface components

The UI kit consists of independent React components following the [element list](UI_ELEMENTS_EN.md) and their individual specifications. Composite components use basic elements; the screen is assembled from these components.

A component receives explicitly described inputs and reports actions through handlers. For example, a card receives a technology representation and reports selection of another variant; language selection receives the current value and reports changes.

Styling uses plain CSS and variables from the [color and typography dictionary](TZ_STYLING_DICTIONARY_EN.md). Localized text is obtained through shared [string lookup](TZ_LOCALIZATION_EN.md).

## Application state

React's built-in facilities manage language, theme, menu expansion, database opening state, and selected technology representations. State ownership between the application and individual components is refined during module design; shared state is not independently duplicated across components.

Opening, cancellation, retry, and database replacement transitions are defined by their separate specification. Language or theme changes update the view through application state.

This choice concerns state during the current session. Persistence and restoration across launches require separate design.

## Data processing and Worker

The [database adapter](TZ_DATABASE_ADAPTER_EN.md), requirement and link preparation, and localization index construction are independent TypeScript modules. They do not depend on React, the DOM, or a particular component and can be checked separately from the interface.

The Worker invokes processing modules and returns prepared results to the main thread under the [protocol specification](TZ_WORKER_PROTOCOL_EN.md). The full database tree stays in the Worker. React displays the received data and operation state; full JSON parsing is not moved to the main thread.

Viewing a prepared file requires no Python service. Starting the development environment or page, or refreshing it, does not start database creation or enrichment.

## Development and build

Vite starts the local development environment, serves interface files, and updates them in the browser when sources change. Its build prepares application files for subsequent distribution. Specific portable packaging is designed separately.

TypeScript type checking runs as a separate command and is included in project checks: Vite's TypeScript transformation does not itself check types. This check uses the TypeScript compiler, for example `tsc --noEmit`.

Exact tool versions, configurations, and project commands are recorded when preparing implementation. Building the interface must not depend on the user's selected game database.

## Acceptance criteria

Checks are performed after implementation:

1. The Vite environment starts the interface and updates modified components in the browser.
2. A separate TypeScript check passes for interface code, data processing, and Worker communication.
3. The Vite build successfully prepares the frontend and its Worker.
4. UI elements are assembled from React components with typed inputs and action handlers.
5. Data processing modules can be checked without starting React or accessing the DOM.
6. Prepared database opening and language and theme changes follow their specifications; startup and page refresh do not invoke database generation.

## Further design

- Refinement of module files and interfaces within the agreed [frontend structure](TZ_STRUCTURE_EN.md); code, configuration, localization, and asset directories are already defined.
- Component and data module interfaces and detailed result types for the agreed Worker protocol.
- Exact versions, development and build commands, TypeScript configuration, and checking tools.
- Shared persistent state storage and restoration.

## Sources

- [React: components and data flow](https://react.dev/learn/thinking-in-react).
- [React: creating an application with a build tool, including Vite and TypeScript](https://react.dev/learn/build-a-react-app-from-scratch).
- [Vite: TypeScript support and separate type checking](https://vite.dev/guide/features.html#typescript).

[Русская версия](TZ_TECH_STACK_RU.md) · [Interface concept](CONCEPT_EN.md).
