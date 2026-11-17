# Stellaris Technological Tree View — Diagnostics and error response specification

## Contents

- [Status and scope](#status-and-scope)
- [Shared diagnostic record](#shared-diagnostic-record)
- [Initial code inventory](#initial-code-inventory)
- [Blocking error response](#blocking-error-response)
- [Successful preparation warnings](#successful-preparation-warnings)
- [Technical details](#technical-details)
- [Interface message](#interface-message)
- [Current session storage](#current-session-storage)
- [Acceptance criteria](#acceptance-criteria)
- [Further design](#further-design)

## Status and scope

This document records the frontend data preparation diagnostics and `error` response format agreed by the user on 2026-11-17. It refines the [Worker protocol](TZ_WORKER_PROTOCOL_EN.md), [result container](TZ_WORKER_RESULT_EN.md), [database opening](TZ_DATABASE_OPENING_EN.md), and [localization index](TZ_LOCALIZATION_INDEX_EN.md).

It defines the shared record, initial codes, separation of warnings from a blocking error, and transfer and retention of received diagnostics in the main thread. Under the [report saving specification](TZ_DIAGNOSTIC_REPORT_EN.md), initial-stage details are exported as JSON for viewing in an external editor. This iteration changes documentation; it does not implement the frontend or modify backend reports.

## Shared diagnostic record

Warnings and errors use one structure with five required fields:

| Field | Type and purpose |
| --- | --- |
| `severity` | `warning` — processing continues; `error` — preparation fails |
| `code` | String: stable problem identifier |
| `phase` | `reading`, `parsing`, or `preparing`; `null` if processing has not started |
| `params` | `{}` for every current code; the field is retained for future messages with named substitutions |
| `details` | Object of technical information for investigating the cause; its contents depend on the code |

Phases follow the Worker protocol. The record does not contain a prepared localized user message: the main thread selects a string by `code` through the shared localization mechanism. Initial-stage diagnostic messages use no substitutions, so `params` is always `{}`. Specific paths, IDs, and technical causes belong in `details`.

The message's `operationId` and application state establish the operation; the number is not duplicated in every record. The contents of `details` for current codes are defined below; exact nested field names and types are refined when designing program types. Nonempty `params` will require separate agreement on new messages.

## Initial code inventory

| Code | `severity` | Meaning |
| --- | --- | --- |
| `file_read_failed` | `error` | The selected file could not be read |
| `invalid_json` | `error` | The content cannot be parsed as JSON |
| `unsupported_database` | `error` | The database format or version is unsupported |
| `invalid_database` | `error` | The adapter cannot transform the database data it uses into the display model |
| `missing_localization` | `warning` | A translation is missing |
| `localization_conflict` | `error` | Different texts were obtained for one language and ID |
| `worker_failed` | `error` | The Worker could not start or encountered an unhandled execution failure |

This is the initial agreed set. Under the [division of responsibilities](TZ_DATABASE_OPENING_EN.md#validation-responsibilities), database validation remains in the backend. The frontend handles opening errors, unsupported formats and versions, and problems in the adapter's own transformations. `invalid_database` denotes an inability to prepare data discovered during transformation, not the result of a separate repeated traversal against the database schema. This document defines detail contents, empty `params`, and built-in string IDs and texts for current codes; program types are refined separately.

## Blocking error response

The response has required `type: "error"`, `operationId`, `error`, and `diagnostics` fields. Illustrative example:

```json
{
  "type": "error",
  "operationId": 7,
  "error": {
    "severity": "error",
    "code": "invalid_json",
    "phase": "parsing",
    "params": {},
    "details": {
      "message": "Unexpected token at position 120."
    }
  },
  "diagnostics": []
}
```

`error` is one diagnostic record with the stopping cause and `severity: "error"`. `diagnostics` is an array of records with `severity: "warning"` accumulated before the failure; it is `[]` when there are none. The stopping cause is not duplicated in the array.

The example technical message does not prescribe what a JSON parser must return and is not a user-facing interface string.

A blocking error ends preparation: the catalog, links, and localization are not published partially, and no `ready` response is returned. The application accepts the response only from the current Worker with the current `operationId`, following the protocol.

If startup or an unhandled execution failure prevents the Worker from sending a response, the main-thread handler creates a `worker_failed` record using the shared structure and associates it with the current attempt. This does not require a separate message from the failed Worker.

## Successful preparation warnings

On success, warnings are transferred in `ready.data.diagnostics`. The array contains only records with `severity: "warning"`; it is empty when there are no issues. Records with `severity: "error"` do not belong in a successful result.

Missing translations follow the index specification: viewing is allowed, and missing text displays a marker. Warnings do not turn a valid result into Error or change the base technology count in the status-panel message.

## Technical details

The contents of `details` are agreed for each current code:

| Code | Technical detail contents |
| --- | --- |
| `file_read_failed` | The file-reading error name and technical message |
| `invalid_json` | The JSON parser message |
| `unsupported_database` | Received and supported database format and version |
| `invalid_database` | The data path and the reason the adapter cannot transform it |
| `missing_localization` | Lookup source, language, string ID, and references to records using it |
| `localization_conflict` | Lookup source, language, string ID, differing texts, and provenance of each text |
| `worker_failed` | Available information about the Worker startup or execution error |

The file-reading error name means the runtime error name, not the selected filename. Exception information is retained to the extent available; missing technical information is not invented.

The provenance of each conflicting text reuses the agreed `origins` structure from the [localization index specification](TZ_LOCALIZATION_INDEX_EN.md#string-provenance). It retains `recordRef`, `key`, `raw`, `source`, `inheritedFrom`, and `unresolvedReferences`. Provenance is associated with its corresponding differing text; a combined list without this association is insufficient to investigate the conflict. The lookup source, such as `database`, differs from `source` inside a provenance record, which describes the translation file.

The complete database tree and complete source JSON are not copied into diagnostics. Record references address the current database and do not retain its tree after the Worker terminates. Information about contradictory texts is transferred in diagnostics so it can be investigated after the tree is released.

This section defines detail contents for the seven current codes and reuse of `origins`. It introduces neither a universal field set for every error nor additional database validation. Exact nested field names and types are specified in the program contract based on these contents.

## Interface message

The following strings from the `builtin` source are agreed for current codes. Identifiers use the `sttv_diagnostic_` prefix:

| Code | String ID | Russian text | English text |
| --- | --- | --- | --- |
| `file_read_failed` | `sttv_diagnostic_file_read_failed` | Не удалось прочитать файл БД. | Could not read the database file. |
| `invalid_json` | `sttv_diagnostic_invalid_json` | Не удалось открыть БД: некорректный JSON. | Could not open database: invalid JSON. |
| `unsupported_database` | `sttv_diagnostic_unsupported_database` | Формат или версия БД не поддерживается. | Unsupported database format or version. |
| `invalid_database` | `sttv_diagnostic_invalid_database` | Не удалось подготовить данные для отображения. | Could not prepare data for display. |
| `missing_localization` | `sttv_diagnostic_missing_localization` | Для некоторых строк отсутствует перевод. | Some translations are missing. |
| `localization_conflict` | `sttv_diagnostic_localization_conflict` | В БД найдены противоречивые переводы. | Conflicting translations found in the database. |
| `worker_failed` | `sttv_diagnostic_worker_failed` | Не удалось завершить обработку БД. | Could not complete database processing. |

Texts reside in `src/frontend/locales/ru.json` and `src/frontend/locales/en.json`, relative to `WEB_STTV`. Both files contain the same IDs; the code-to-string-ID mapping is defined by diagnostic configuration under `WEB_STTV/config/frontend/`, following the [structure specification](TZ_STRUCTURE_EN.md#configuration-and-working-data). Texts remain in localization rather than being duplicated in configuration or the panel component. The exact configuration filename and loading mechanism are defined during implementation design.

On a blocking error, the [status panel](elements/TZ_STATUS_PANEL_EN.md) shows the corresponding message. The `missing_localization` warning remains in diagnostics and does not replace the agreed successful-load message with the technology count. Having the warning string in the dictionary does not itself add an interface state or notification.

The Worker supplies the code and empty `params`, and the main thread selects the language. Changing the language updates the message without reopening the database. Technical `details.message`, when present, does not replace the user-facing explanation.

The initial code inventory does not add interface elements or status-panel actions. The explicit Save report action resides in the menu under its separate specification; details are viewed in an external editor. An integrated diagnostic viewer is deferred.

## Current session storage

Received diagnostics are stored in the main thread with the current attempt's result: warnings accompany success, while the stopping cause and accumulated warnings accompany Error. Terminating the Worker after a failure preserves this information; intermediate catalog data and the complete tree are discarded under the database opening specification.

A Worker failure is also retained by the application using the shared structure. Stale responses and results from cancelled or replaced operations do not change the current attempt's diagnostics. Diagnostics remain associated with their `operationId`.

This document establishes in-memory retention of received information during the current session. Explicit export of the current completed attempt is defined by the [report specification](TZ_DIAGNOSTIC_REPORT_EN.md). Persistent state storage, attempt history, automatic file logging, and an integrated viewer require separate design.

## Acceptance criteria

Checks are performed after implementation:

1. Errors and warnings use the shared `severity`, `code`, `phase`, `params`, and `details` fields; phases follow the protocol, with `null` allowed before processing starts.
2. `error` contains one blocking record, while the adjacent `diagnostics` contains only accumulated warnings; the error is not duplicated in the array.
3. `ready.data.diagnostics` contains only warnings; a blocking failure does not become a successful or partial result.
4. A missing translation allows viewing with a warning; contradictory texts produce `localization_conflict` and the required information for manual investigation.
5. All seven current codes use `params: {}`, and configuration maps `code` to the agreed ID in the `builtin` source. RU/EN texts match the table, use identical IDs, and contain no substitutions; changing the language updates the message without restarting processing, and technical text does not replace the user-facing message.
6. The received error cause and warnings remain available in the main thread after Worker termination; diagnostics do not contain the complete tree.
7. Worker startup or unhandled execution failure becomes `worker_failed` for the current attempt even when no Worker response is received.
8. Stale responses and duplicate outcomes do not change current diagnostics; cancellation, replacement, and explicit retry rules remain in force.
9. `details` follows the agreed contents for its code. Each conflicting text retains its associated `origins`; references, metadata, and causes remain in the report after Worker termination.
10. `missing_localization` remains a diagnostic warning and does not replace the successful-load message with the technology count.

## Further design

- Program names and types for nested `details` fields based on the agreed contents; `params: {}` is already defined for current codes, and duplicating backend validation is not planned.
- The exact diagnostic configuration filename, program schema, and loading; code-to-ID mapping, RU/EN texts, and the configuration root directory are already defined.
- An integrated diagnostic viewer, persistent state storage, and attempt history; initial viewing through a saved JSON file is already defined.
- Program types, module interfaces, and message structure checks.

[Русская версия](TZ_DIAGNOSTICS_RU.md) · [Worker protocol](TZ_WORKER_PROTOCOL_EN.md) · [Worker result](TZ_WORKER_RESULT_EN.md).
