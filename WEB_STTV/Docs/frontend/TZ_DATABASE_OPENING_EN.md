# Stellaris Technological Tree View — startup and existing database opening specification

## Contents

- [Status and scope](#status-and-scope)
- [Startup and page refresh](#startup-and-page-refresh)
- [Explicit database opening](#explicit-database-opening)
- [File reading and Web Worker](#file-reading-and-web-worker)
- [In-memory data preparation](#in-memory-data-preparation)
- [Interface states](#interface-states)
- [Cancellation and database replacement](#cancellation-and-database-replacement)
- [Validation responsibilities](#validation-responsibilities)
- [Errors and retry](#errors-and-retry)
- [Separation from database generation](#separation-from-database-generation)
- [First-stage execution mode](#first-stage-execution-mode)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and scope

**Current opening behavior is specified in [stage 4](TZ_FRONTEND_STAGE_4_EN.md):** the user selects a directory containing a manifest; documents load selectively. See the [guide](FRONTEND_STAGE_4_EN.md) for launch instructions. Single or multiple monolithic file selection below refers to earlier stages.

As of 2026-11-17, this document's single-file and unqualified-reference provisions are superseded by the approved [stage-two specification](TZ_FRONTEND_STAGE_2_EN.md). The current implementation opens three version-five databases as one set and uses `{ database, pointer }` references; other applicable requirements remain in effect.

This document records the agreed interface startup and existing database opening behavior. The frontend uses a prepared JSON file containing parsed results and localization. Database creation and updates remain separate backend processes.

The first stage uses browser File API access to the selected file and a TypeScript adapter running in a Web Worker. Python is used by separate database creation and enrichment processes; viewing a prepared file does not require a Python service. React, TypeScript, and Vite are established by the [technology stack specification](TZ_TECH_STACK_EN.md); exact program interfaces remain to be defined.

## Startup and page refresh

Application startup and page refresh load the interface and its own resources. They do not automatically open a database, read game sources, or start database generation or enrichment.

Before a file is explicitly opened, the [Status panel](elements/TZ_STATUS_PANEL_EN.md) invites the user to open a database through the menu; the workspace stays clear. Initial language, theme, and menu state follow the [Main window specification](elements/TZ_MAIN_WINDOW_EN.md). The presence of a database file on disk does not itself trigger loading.

During the first stage, the user explicitly opens the prepared database again after refreshing the page. Automatic restoration of the opened file is not introduced; shared state persistence is designed separately.

## Explicit database opening

An **Open database** action is provided:

1. The user invokes the opening action.
2. The user selects an existing database JSON file.
3. The application reads the selected file and prepares display data.
4. After successful preparation, the technology field appears in the workspace.

File contents are not loaded before file selection. Opening reads the prepared database without changing the selected file.

The action uses the shared [Button element](elements/TZ_BUTTON_EN.md) and resides in the [Menu panel](elements/TZ_MENU_PANEL_EN.md) main content, in the database action group above language selection. Its label and the status-panel prompt to open a database come from built-in localization. The button invokes the browser's standard file selection dialog. Exact dimensions, spacing, and interface string identifiers are defined during implementation design.

## File reading and Web Worker

The browser obtains the user-selected `File` object through the File API. The main thread sends it to a Web Worker in a message; content reading and JSON parsing run in the Worker. Access to selected files is described in the [File API documentation](https://developer.mozilla.org/en-US/docs/Web/API/File_API/Using_files_from_web_applications); separate-thread processing and messaging are described in the [Web Workers documentation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers).

Processing sequence:

1. The main thread receives the selected file and sends it to the Worker.
2. The Worker reads the contents, parses JSON, and checks the supported database format and version.
3. The Worker prepares the technology and variant catalog, technology requirements and links, and the RU/EN localization index.
4. The Worker sends the prepared data to the main thread for interface construction.

| Part | Responsibility |
| --- | --- |
| Browser main thread | File selection, receiving prepared data, element placement and rendering, user interaction |
| Web Worker | File reading, JSON parsing, format and version checking, invoking data preparation modules, retaining the complete database tree |
| TypeScript modules | Technology extraction, requirement processing, and reading stored localization under their separate specifications |

File reading and messaging form the outer integration layer. Data extraction and transformation functions are separated from the DOM, file dialog, and Worker protocol so that they can be checked independently. Card coordinates and user selections remain interface responsibilities.

JSON parsing reads the prepared database. It does not run the game-file parser or database generator. Data exchange for viewing takes place within the browser; the file is not sent to a Python service or an external server.

## In-memory data preparation

Opening the database includes preparing derived data in memory:

- The technology and representation catalog under the [adapter specification](TZ_DATABASE_ADAPTER_EN.md).
- The requirement tree and its derived results for technology placement and links.
- The RU/EN name and description index under the [localization specification](TZ_LOCALIZATION_EN.md).

This processing uses only the selected database. It does not repeat game parsing, localization collection from source directories, or database file enrichment. Text comes from the stored localization records.

Prepared data is used for display during the current session. Its preparation does not write a new database or overwrite the original.

The complete parsed database tree stays in Worker memory while that database is in use. Catalog `sourceRef` references identify its original nodes; resolving those references belongs to the tree owner in the Worker. The main thread receives the catalog, requirements and links, and the localization index with its specified metadata. The complete database tree and complete source JSON are not copied into interface state or result messages. Message types follow the [Worker protocol specification](TZ_WORKER_PROTOCOL_EN.md); the `ready` container, catalog, and string references follow the [result specification](TZ_WORKER_RESULT_EN.md); the tree and links follow the [technology requirements specification](TZ_TECHNOLOGY_REQUIREMENTS_EN.md). Localization records are described in the [index specification](TZ_LOCALIZATION_INDEX_EN.md); the shared diagnostic record and `error` response are defined in the [diagnostics specification](TZ_DIAGNOSTICS_EN.md).

The database index is prepared for both languages and connected to the shared localization mechanism in the main thread. Language changes and tooltip display use prepared data without rereading the file or traversing the complete tree.

The current stage-ten database file occupies 140,937,166 bytes, approximately 141 MB. This is a verification reference, not a size limit in code. The Worker moves processing off the main thread but does not itself reduce memory usage. Implementation must verify opening time, interface responsiveness, and memory usage with the actual database; results are not available yet.

## Interface states

| State | Workspace | Status panel | Menu actions |
| --- | --- | --- | --- |
| No database open | Clear | Prompt to open a database through the menu | Open database |
| Loading | Clear | Message identifying the current processing stage | Cancel |
| Ready | Technology field | Database opened message and technology count | Open database to choose another file, Save report |
| Empty catalog | Clear | Message: No technologies found in the selected database | Open database, Save report |
| Error | Clear | Understandable problem description | Retry, Open database, Save report |

All database actions reside in the group above language selection. Only actions for the current state are shown; the bottom menu group retains collapse and theme buttons. Collapsing the menu hides database actions with its main content; the user expands the menu to open a file, cancel, retry, or save a report. Under the [report saving specification](TZ_DIAGNOSTIC_REPORT_EN.md), export is available after an attempt finishes, including success without warnings; it is unavailable before opening and during loading.

The status panel remains visible at the bottom across the entire window width, below the menu and workspace. It occupies its own space, does not scroll with content, and does not overlap scrollbars. The workspace does not duplicate panel messages. Detailed requirements reside in the [Status panel specification](elements/TZ_STATUS_PANEL_EN.md).

During loading, the status panel shows the current stage: file reading, JSON parsing, or data preparation. Completion percentages are not used in the first stage. Language, theme, and menu collapse remain operational. The button for opening another file is hidden during processing; the user can first cancel the current load.

The field appears only after successful preparation of the complete set: catalog, requirements and links, and localization index. Partially prepared data is not published to the interface. All displayed data belongs to the same opened database.

An empty catalog means that a valid database was successfully read and prepared but contains no technologies to display. Reading, structural, or preparation errors must not become an empty catalog.

State messages and action labels come from built-in RU/EN localization. Actions use the shared Button element; no separate styling or UI element set is introduced for them.

## Cancellation and database replacement

Cancelling the standard file dialog changes nothing. The opened database, its display, and user selections remain intact; its Worker keeps running.

Cancelling an active load terminates that operation's Worker and discards intermediate results. The application returns to No database open with a prompt to open a file. Messages and results from cancelled or replaced operations must not change the interface, including after another load has started.

Opening another database follows this sequence:

1. The current database and its display remain intact until a new file is selected.
2. After selection, the old Worker terminates, and the interface drops the previous catalog, links, database localization index, and references to old data. Built-in interface localization is retained.
3. A new Worker starts reading the selected file; the interface enters the loading state.
4. After successful preparation, the new data is published. Base technology representations are displayed, and the viewing position resets to the upper left corner. Language, theme, and menu state are retained.

The application does not retain two complete database trees for switching or rollback: the old Worker terminates before processing the new file. An error or cancellation of the new load does not automatically restore the previous database. To return to it, the user explicitly opens its file again.

In Ready or Empty catalog, the Worker retains the current database. Cancellation or a blocking load error terminates that operation's Worker and discards intermediate data and references to it. Under the protocol specification, each new attempt or retry receives a new `operationId`; only responses for the current operation from the current Worker are accepted. Cancellation first invalidates the operation, then calls `worker.terminate()` without a `cancel` command or acknowledgement wait.

## Validation responsibilities

The backend is responsible for the correctness of the database it produces: it checks the schema, source document uniqueness, expansion history, and localization consistency before publication. The frontend consumes this contract without porting the backend validator or its schemas, or traversing the complete tree to repeat validation.

During opening, the frontend handles file-reading and JSON parsing errors and checks the format and version. The adapter then performs its own transformations for cards, links, and the localization index. Ambiguities discovered during these transformations become preparation errors; there is no separate preliminary pass checking every database field.

For example, merging object localizations into a shared index requires a single text for each language and ID pair. Different texts produce the agreed `localization_conflict`: this is a condition of the new interface index, not a repeated check of the original tree structure. A failed transformation is not replaced with an empty catalog or an arbitrarily selected value.

## Errors and retry

An unreadable file, invalid JSON, an unsupported database format or version, or inability to prepare display data stops opening and puts the interface in the error state. The Validation responsibilities section defines the processing boundaries; repeated database validation is not required.

Missing localization strings do not block viewing. They use markers and diagnostics under the [localization specification](TZ_LOCALIZATION_EN.md). Differing texts under one ID and language block preparation under the [index specification](TZ_LOCALIZATION_INDEX_EN.md): opening enters the error state, data is not published, and the cause requires manual investigation.

Retry starts a new processing attempt for the same selected file. The selected `File` reference is therefore retained in the current session after an error; the complete tree is not retained. Another attempt begins only through user action. Open database allows selection of another file; automatic retries and switching to the generator do not occur.

The status panel shows an understandable localized message. Technical error details remain in diagnostics under a [separate specification](TZ_DIAGNOSTICS_EN.md). The received error cause and warnings remain in the main thread after Worker termination; initially, details are viewed in an external editor after explicit JSON saving under the [report specification](TZ_DIAGNOSTIC_REPORT_EN.md). Language changes update the message through built-in localization.

## Separation from database generation

Viewing a prepared database and creating or updating it are independent. Opening a prepared file does not require access to the original game and localization directories.

The first stage has no Update database button. Generator execution is not tied to opening a file, refreshing the page, or starting the application. A missing or unusable database must not automatically trigger a build either.

Future database updates through the interface require separate design and explicit user action.

## First-stage execution mode

The initial interface is developed and tested from the project's development environment. Portable packaging and launch through a packaged `.exe` are not requirements or acceptance criteria for this stage.

Portable Windows distribution remains a later stage of the overall project. Vite is selected for starting the development environment and building the frontend. Viewing the prepared database uses the browser and Worker; no Python service is started for this stage.

## Acceptance criteria

Checks are performed after implementation:

1. On startup and page refresh, the status panel prompts the user to open a database through the menu and the workspace stays clear; the database file is not loaded automatically.
2. Loading the selected JSON starts only after explicit user action and file selection.
3. Successfully opening a prepared database produces the technology field using stored RU/EN names and descriptions.
4. Opening works while the original game and localization directories are unavailable; source data is not read again.
5. The catalog, requirements, and localization index are prepared in memory, and the selected database file remains unchanged.
6. Startup, page refresh, database opening, and opening errors do not invoke the database generator or enrichment.
7. Page refresh requires another explicit file opening. There is no database update button; portable packaging is not required for checks.
8. File selection uses the browser's standard dialog. Content reading, JSON parsing, and data preparation run in the Worker; viewing works without a Python service.
9. The main thread receives display data without a complete copy of the database tree or source JSON. `sourceRef` resolves to the corresponding node of the tree retained in the Worker.
10. Technology extraction, requirement processing, and localization reading modules are checked independently of the file dialog, DOM, and Worker protocol.
11. Opening time, memory usage, and interface responsiveness results are recorded using the actual database. Checks identify their environment and browser; Worker architecture alone is not considered evidence of performance.
12. All five states are checked: No database open, Loading, Ready, Empty catalog, and Error. A valid empty catalog is distinguished from a failed opening.
13. Processing shows the current stage without percentages; language, theme, and menu collapse remain operational. The field receives the complete agreed data set only after success.
14. Cancelling the file dialog preserves the current database and user selections. Cancelling an active load terminates the Worker and returns to the initial screen; stale messages are not applied, including messages received after a new operation starts.
15. Selecting another database terminates the old Worker before processing the new file. Previous data and the database index are dropped; successful opening resets base representations and the upper left position while retaining language, theme, and menu state.
16. Failed or cancelled replacement does not automatically restore the previous database. Checks confirm that two complete trees are not retained for rollback.
17. Retry starts new processing of the same selected file only through user action. File-reading and JSON errors, unsupported formats and versions, adapter transformation errors, blocking contradictory localization texts, and nonblocking missing translations are checked.
18. Current-state actions appear in the menu above language selection; others are hidden. Collapsing hides database actions while retaining the expand button; expanding exposes actions for the current state.
19. Messages for all five states reside in the always-visible bottom panel across the entire window width. The workspace does not duplicate messages and shows the field only in Ready; the menu and field sit above the panel without overlapping content or scrollbars.

## Subsequent implementation details

The `open_database`, `progress`, `ready`, and `error` messages, operation identification, and stale response filtering are defined by the [Worker protocol specification](TZ_WORKER_PROTOCOL_EN.md). The diagnostics specification defines `details` contents and `params: {}` for current codes. Program types for opening and transformation error details, module interfaces, tool configuration, element dimensions and spacing, and interface string identifiers remain to be refined. State behavior, cancellation, retry, database replacement, menu action placement, and status-panel messages are established by this document.

Persistent state, automatic file restoration, database generation through the interface, and portable distribution are not implemented under this document.

[Русская версия](TZ_DATABASE_OPENING_RU.md) · [Interface concept](CONCEPT_EN.md).
