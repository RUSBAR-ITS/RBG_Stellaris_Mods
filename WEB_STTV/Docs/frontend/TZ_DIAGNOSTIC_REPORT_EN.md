# Stellaris Technological Tree View — Diagnostic report saving specification

## Contents

- [Status and scope](#status-and-scope)
- [Menu action](#menu-action)
- [Availability by state](#availability-by-state)
- [Report structure](#report-structure)
- [Outcome and diagnostics](#outcome-and-diagnostics)
- [Creation and viewing](#creation-and-viewing)
- [Acceptance criteria](#acceptance-criteria)
- [Further design](#further-design)

## Status and scope

As of 2026-11-17, this document's single-file and unqualified-reference provisions are superseded by the approved [stage-two specification](TZ_FRONTEND_STAGE_2_EN.md). The current implementation opens three version-five databases as one set and uses `{ database, pointer }` references; other applicable requirements remain in effect.

This document records saving a JSON report for the current database opening attempt, agreed by the user on 2026-11-17. At the initial stage, details are viewed in an external editor such as VS Code; an integrated diagnostic viewer is deferred.

The basis is the [diagnostics specification](TZ_DIAGNOSTICS_EN.md), [database opening](TZ_DATABASE_OPENING_EN.md), and [menu panel](elements/TZ_MENU_PANEL_EN.md). This is a user-requested export of information already available in the main thread. This iteration produces documentation; code, the database, and backend reports are unchanged.

## Menu action

The main database action group above language selection gains “Сохранить отчёт” / “Save report”. It uses the shared [Button element](elements/TZ_BUTTON_EN.md), built-in RU/EN strings, and UI kit styling.

The button sits next to database opening actions in the existing group. Like the other group actions, it is hidden when the menu collapses. The status panel continues to show one short database status message; neither the saving button nor technical details are added to it.

This stage does not create a separate UI element for the action or an integrated viewer.

## Availability by state

| Application state | Save report |
| --- | --- |
| No database open | Unavailable |
| Loading | Unavailable |
| Ready | Available |
| Empty catalog | Available |
| Error | Available |

Following the existing menu rule, only current-state actions are shown: the save button is hidden before opening and during loading. It appears after the attempt finishes, even when there are no warnings. Worker startup failure also completes an attempt with an error outcome and allows saving.

The report belongs to the current attempt and its `operationId`. Starting a new attempt returns the application to Loading and makes saving unavailable. Cancelling loading returns to No database open; no cancellation report is introduced. Cancelling the new-file selection dialog preserves the current result and report availability under the database opening specification.

## Report structure

The report is a separate JSON object with eight required fields:

| Field | Type and purpose |
| --- | --- |
| `format` | String identifier `sttv.frontend_diagnostics` |
| `formatVersion` | Integer `1` for the first report structure version |
| `exportedAt` | UTC export date and time string, ISO 8601 with a `Z` suffix |
| `operationId` | Positive integer: the current completed attempt number |
| `file` | Object with the selected database file's name and size |
| `result` | `ready`, `empty`, or `error` |
| `error` | Blocking diagnostic record or `null` |
| `diagnostics` | Array of warnings |

`file` has two fields: `name`, the selected file's string name, and `size`, its nonnegative integer size in bytes. This information is available from the selected file and retained with the attempt; retrieving it does not require rereading the content.

`formatVersion` versions this report structure, not the database or application. `exportedAt` identifies when the export is created, not when database processing finished.

Illustrative successful attempt with an empty catalog:

```json
{
  "format": "sttv.frontend_diagnostics",
  "formatVersion": 1,
  "exportedAt": "2026-11-17T10:30:00Z",
  "operationId": 7,
  "file": {
    "name": "database.json",
    "size": 1024
  },
  "result": "empty",
  "error": null,
  "diagnostics": []
}
```

## Outcome and diagnostics

| `result` | Outcome source | `error` | `diagnostics` |
| --- | --- | --- | --- |
| `ready` | Successful preparation of a nonempty catalog | `null` | Warnings from `ready.data.diagnostics` |
| `empty` | Successful preparation of an empty catalog | `null` | Warnings from `ready.data.diagnostics` |
| `error` | Opening error or Worker failure | Stopping cause record with `severity: "error"` | Accumulated warnings |

In the Worker protocol, an empty catalog still returns a `ready` message; the report's `empty` value reflects the final application state and does not add a Worker message type.

Each `error` or `diagnostics` record preserves the agreed `severity`, `code`, `phase`, `params`, and `details`. The array contains only warnings and does not duplicate the blocking cause. When there are no warnings, it is saved as `[]`.

Codes, parameters, and technical details are exported in their original diagnostic structure without replacement by localized panel messages. Interface language does not change their contents. Saving the same attempt again uses the same outcome and a new `exportedAt` time.

## Creation and viewing

Saving occurs only through explicit user action. The report is assembled from information about the current completed attempt already available in the main thread. It does not require a new opening attempt, database rereading, tree traversal, or a Worker request for diagnostic records.

The complete database, source JSON, technology catalog, links, and localization index are not included in the report. Technical information required by `details` is preserved under the diagnostics specification.

The user receives a separate JSON file and opens it in a suitable editor for manual investigation. Saving does not change the selected database, its opening outcome, or technology viewing state. The `WORK_DIR` working directory does not imply automatically writing this report into the product directory.

Automatic file logging, attempt history, and persistent state storage are not introduced. An integrated diagnostic viewer belongs to a later stage.

## Acceptance criteria

Checks are performed after implementation:

1. Save report uses a shared button in the menu action group, obtains its label from RU/EN, and hides with the menu.
2. The action is available in Ready, Empty catalog, and Error; it is unavailable and hidden before opening and during loading.
3. A successful attempt without warnings can also be saved with `error: null` and `diagnostics: []`.
4. JSON contains all eight fields, selected file and current attempt information; `exportedAt` identifies export time in UTC.
5. A successful empty catalog receives `result: "empty"` without changing the Worker protocol; an error contains the blocking record separately from warnings.
6. Diagnostics retained after failure can be exported after Worker termination, including startup failure.
7. Switching RU/EN does not change codes, parameters, or technical details; repeated export preserves the same attempt's outcome.
8. Saving uses prepared main-thread information without reading the database or requesting the Worker; the complete database is neither included nor modified.
9. Starting a new attempt and cancelling loading make saving unavailable; cancelling the file dialog preserves the current report. There is no automatic log or history.

## Further design

The concrete file export mechanism, filename rule, interface string identifiers, and handling of export failures are refined during implementation design. The diagnostics specification defines `details` contents, reuse of `origins` for conflicts, and empty `params` for current codes; program types for details are refined within its scope. Integrated viewing, history, and automatic saving require separate decisions.

[Русская версия](TZ_DIAGNOSTIC_REPORT_RU.md) · [Diagnostics](TZ_DIAGNOSTICS_EN.md) · [Menu panel](elements/TZ_MENU_PANEL_EN.md).
