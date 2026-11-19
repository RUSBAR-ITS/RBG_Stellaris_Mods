# Technology chains — ambiguity log

## Contents

- [Status and decision](#status-and-decision)
- [Behavior on ambiguity](#behavior-on-ambiguity)
- [Record contents](#record-contents)
- [Field state and settings snapshot](#field-state-and-settings-snapshot)
- [Capture time and recalculations](#capture-time-and-recalculations)
- [Stage boundaries](#stage-boundaries)
- [Related documents](#related-documents)

## Status and decision

User clarification dated 2026-11-18: **manual predecessor selection is deferred**. Ambiguous technologies must be logged with field state and settings so cases can be investigated across different reference application modes.

This document records a decision for a future specification. This iteration changes documentation only; the logging mechanism is not implemented yet.

## Behavior on ambiguity

If multiple candidates remain after all criteria:

1. Leave `parent_tech = null` and explicitly record an ambiguous selection state, distinct from having no prerequisites.
2. Retain the remaining candidates and rule application results. Neither alphabetical order nor source record order selects the parent.
3. Continue opening and displaying the reference application. Temporarily place the card as an independent branch at its own tier; retain all game dependencies.
4. Automatically add a diagnostic log record. Ambiguous anchor selection alone is not a database format error.

Neither manual parent assignment configuration nor a selection interface is created at this stage. Selected technology representations remain part of field state and are included in diagnostics.

## Record contents

| Information | Purpose |
| --- | --- |
| Detection time and calculation identifier | Associate the issue with a particular field calculation. |
| Database set and its identification | Identify the input data and versions. |
| Base technology ID and selected representation | Unambiguously identify the affected card independently of its localized name. |
| Selection state and `parent_tech` | Explicitly indicate unresolved ambiguity. |
| Initial and remaining candidates | Show the starting set and the candidates that could not be distinguished. |
| Rule application trace | Criterion order, sets before and after each step, and supporting reasons, including skipped empty results. |
| References to supporting data | Locate source technologies, objects, conditions and effects. |
| Field state and settings snapshot | Reproduce the calculation context. |

The record and snapshot must be available in a saved diagnostic log/report, not only as a console message. This defines required information, not the final JSON schema.

## Field state and settings snapshot

Capture the values actually used:

- field mode and its parameters;
- language and selected representations across the entire field, including effective defaults;
- the active empire profile and known parameters if used by that mode;
- order, enabled state and parameters of anchor selection and layout rules, including indirect search depth and functional group definitions in use;
- applied filters and other mode settings when introduced;
- display state: layout parameters, field/viewport dimensions, scroll position, effective styling settings and panel states affecting the field's appearance.

This requirement creates no new modes or filters: the snapshot records the actual active state. As modes and filters are added, the snapshot must include new parameters needed to investigate the result.

Configuration identifiers or file paths do not replace effective values: configuration may change after calculation. The full database need not be copied into the log; its identification and references to the data used are sufficient.

## Capture time and recalculations

Capture the snapshot for the calculation in which the ambiguity is detected. Later changes to language, representations, mode or settings must not alter an existing issue's context. Report export uses the captured snapshot rather than substituting the current interface state.

Multiple ambiguities from one calculation may reference a shared snapshot; export must include it alongside the records. Detection after recalculation belongs to a new context rather than being mixed with an earlier case without identifying its state.

## Stage boundaries

This decision concerns the planned chain anchor selector. It neither changes current database reading error rules nor adds manual selection.

Exact fields, the diagnostic code and integration of field recalculation records into the existing report mechanism must be defined in the implementation specification. The current frontend report contains database opening information; it does not yet include the field snapshot described here.

## Related documents

- [General chain and sorting rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [Diagnostic records](TZ_DIAGNOSTICS_EN.md).
- [Saving the diagnostic report](TZ_DIAGNOSTIC_REPORT_EN.md).
- [Русская версия](CHAIN_AMBIGUITIES_RU.md).
