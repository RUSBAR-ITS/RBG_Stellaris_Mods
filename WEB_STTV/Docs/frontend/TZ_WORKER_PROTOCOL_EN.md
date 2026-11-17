# Stellaris Technological Tree View — Worker protocol specification

## Contents

- [Status and scope](#status-and-scope)
- [Shared fields and current operation](#shared-fields-and-current-operation)
- [Messages](#messages)
- [Processing stages](#processing-stages)
- [Successful result](#successful-result)
- [Errors and diagnostics](#errors-and-diagnostics)
- [Cancellation, replacement, and retry](#cancellation-replacement-and-retry)
- [Placement and responsibilities](#placement-and-responsibilities)
- [Acceptance criteria](#acceptance-criteria)
- [Further design](#further-design)
- [Sources](#sources)

## Status and scope

This document records the agreed protocol for opening a prepared database between the application and a Web Worker. It refines the [database opening specification](TZ_DATABASE_OPENING_EN.md): messages, operation identification, stale response filtering, and cancellation. Code is not implemented in this iteration.

There is one command, `open_database`, and three response types: `progress`, `ready`, and `error`. The [Worker result specification](TZ_WORKER_RESULT_EN.md) establishes the `ready` container, technology fields, representation IDs, and string `sourceRef` values; the [technology requirements specification](TZ_TECHNOLOGY_REQUIREMENTS_EN.md) defines the tree and links. Localization records are defined in the [index specification](TZ_LOCALIZATION_INDEX_EN.md); diagnostic records and the nested `error` response are defined in a [separate specification](TZ_DIAGNOSTICS_EN.md). The complete database tree stays in the Worker.

## Shared fields and current operation

Every message contains:

| Field | Purpose |
| --- | --- |
| `type` | String message type from the list below |
| `operationId` | Positive integer opening-attempt number assigned by the application |

The application assigns a new number whenever a selected file is opened or retried. Numbers are not reused within the current session. The Worker returns the received operation number in all responses for that operation.

The application accepts a response only when its `operationId` matches the current operation and it comes from the corresponding current Worker. Responses from cancelled or replaced operations do not change the current database state, data, or diagnostics.

An opening attempt has one outcome: `ready` or `error`. After accepting the outcome, `progress` messages and duplicate outcomes for that attempt do not change state. A Worker that successfully completes preparation continues to retain the opened database.

## Messages

| Direction | `type` | Contents besides shared fields |
| --- | --- | --- |
| Application → Worker | `open_database` | `file`: the user-selected `File` object |
| Worker → application | `progress` | `phase`: the current stage identifier |
| Worker → application | `ready` | `data`: the complete prepared result and non-blocking diagnostics |
| Worker → application | `error` | `error`: the blocking diagnostic record; `diagnostics`: accumulated warnings |

The selected file object is sent. The main thread does not read the entire JSON string to send it to the Worker. Reading, parsing, and preparation execute in the Worker.

The `ready` response's `data` container includes `technologies`, `links`, `localization`, and `diagnostics` under the result specification. Diagnostic records contain `severity`, `code`, `phase`, `params`, and `details` under the [diagnostics specification](TZ_DIAGNOSTICS_EN.md). An `error` response carries the stopping cause in a separate `error` record and accumulated warnings in the `diagnostics` array; the diagnostics specification defines `details` contents, and every current code uses `params: {}`. Program types for nested fields are refined separately.

## Processing stages

| `phase` | Work performed |
| --- | --- |
| `reading` | Reading file contents |
| `parsing` | Parsing JSON |
| `preparing` | Checking the required structure and preparing the catalog, requirements, links, and localization |

The Worker reports entry into a stage before performing its work. Completion percentages are not sent. Example message:

```json
{
  "type": "progress",
  "operationId": 7,
  "phase": "parsing"
}
```

The main thread maps `phase` to a built-in interface string and displays it in the [Status panel](elements/TZ_STATUS_PANEL_EN.md). The Worker does not select the message language. Changing language updates the current stage text without restarting processing.

## Successful result

`ready` contains the prepared technology and representation catalog, technology requirements and links, RU/EN localization index, and non-blocking diagnostics together. The application publishes this complete set after successful preparation; intermediate parts do not become screen data.

A valid database without technologies also returns `ready` with an empty catalog. The application selects Empty catalog instead of Ready. Reading, structure, and preparation failures do not become successful empty results.

The complete database tree and original JSON string are excluded from the result. The main thread receives a derived display model. The Worker is retained after success, including an empty catalog; original nodes remain with the tree owner.

## Errors and diagnostics

`error` reports a blocking failure during the current opening attempt. A stable code, such as `invalid_json`, lets the application select a localized interface string. Parameters are substituted by the shared localization mechanism. Technical details are intended for diagnostics and do not replace the user-facing explanation in the status panel.

Failure to start or execute the Worker also places the application in Error, even if the Worker could not send `error`. The application-side handler associates this failure with the current attempt and applies the same termination and retry rules. Such a failure uses `worker_failed` from the initial code inventory in the diagnostics specification. Exact technical detail schemas are refined separately.

A blocking failure terminates the Worker and discards intermediate data. The received error cause and warnings remain in the main thread and are not deleted with the Worker. The selected `File` reference remains available in the current session for explicit retry. Non-blocking issues, including missing localization strings, accompany the successful result and follow the [localization specification](TZ_LOCALIZATION_EN.md). Contradictory texts under one ID and language are a blocking preparation error under the [index specification](TZ_LOCALIZATION_INDEX_EN.md); an `error` with information for manual investigation is returned instead of `ready`.

## Cancellation, replacement, and retry

The application cancels loading by first invalidating the operation, then calling `worker.terminate()`, discarding intermediate data, and returning to No database open. There is no separate `cancel` command or acknowledgement wait. The `terminate()` method stops the Worker without waiting for its work to finish; see the source below.

Replacing the database invalidates the old operation, terminates its Worker, and removes previous interface data. A new Worker with a new `operationId` is created after a new file is selected. The current database remains while the standard file dialog is open; cancelling that dialog is not a loading cancellation.

Retry creates a new Worker and a new `operationId` for the retained `File` object. There are no automatic retries. Late messages from the previous Worker are discarded under the shared rules, whether or not another attempt has started.

## Placement and responsibilities

Under the [structure specification](TZ_STRUCTURE_EN.md), Worker startup, messages, and their handling belong to `src/frontend/workers/`; application state and user actions belong to `app/`. Independent algorithms from `data/` and `localization/` are invoked by the Worker handler and do not depend on the protocol or React.

Changing language, theme, or the selected technology representation uses already prepared main-thread data. These actions do not send database opening messages.

## Acceptance criteria

Checks are performed after implementation:

1. Opening sends a `File` with a new `operationId`; responses contain that same number.
2. The `reading`, `parsing`, and `preparing` stages use built-in localization without percentages.
3. `ready` publishes the complete prepared set; a valid empty catalog differs from a failure.
4. Old Worker messages, responses with obsolete numbers, and duplicate outcomes do not change current data or state.
5. Cancellation during reading, parsing, or preparation terminates the Worker without awaiting a response and clears loading state.
6. Retry uses the retained `File`, a new Worker, and a new number; replacement does not retain two complete database trees.
7. Opening errors and Worker failures end in Error with a localized explanation and diagnostics.
8. Language changes update stage or error messages without reprocessing the database.

## Further design

- Program types for nested `details` fields based on the agreed contents; the shared record, empty `params` for current codes, and `error` container are defined. Rules for using negation in requirements remain open.
- Interface message IDs and texts, and an integrated diagnostic viewer; explicit JSON saving for the current attempt is defined in the [report specification](TZ_DIAGNOSTIC_REPORT_EN.md) and adds no Worker messages.
- Shared message types and required structural checks, exact files, and handler interfaces.

## Sources

- [MDN: Worker.terminate()](https://developer.mozilla.org/en-US/docs/Web/API/Worker/terminate).
- [MDN: Web Worker messaging and operation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers).

[Русская версия](TZ_WORKER_PROTOCOL_RU.md) · [Interface concept](CONCEPT_EN.md).
