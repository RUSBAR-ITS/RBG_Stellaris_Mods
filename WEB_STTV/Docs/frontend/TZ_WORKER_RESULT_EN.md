# Stellaris Technological Tree View — Worker result and technology catalog specification

## Contents

- [Status and scope](#status-and-scope)
- [Result container](#result-container)
- [Technology entry](#technology-entry)
- [Technology representations](#technology-representations)
- [Original-node references](#original-node-references)
- [Localization and diagnostics](#localization-and-diagnostics)
- [Acceptance criteria](#acceptance-criteria)
- [Further design](#further-design)

## Status and scope

As of 2026-11-17, this document's single-file and unqualified-reference provisions are superseded by the approved [stage-two specification](TZ_FRONTEND_STAGE_2_EN.md). The current implementation opens three version-five databases as one set and uses `{ database, pointer }` references; other applicable requirements remain in effect.

This document records the agreed `ready` container, technology entry fields, representation identifiers, and string references to original nodes. It refines the [adapter specification](TZ_DATABASE_ADAPTER_EN.md) and [Worker protocol](TZ_WORKER_PROTOCOL_EN.md). Implementation is not performed in this iteration.

The shared diagnostic record and `error` response container are defined in the [diagnostics specification](TZ_DIAGNOSTICS_EN.md); exact per-code detail schemas are still being refined. The localization format is defined in the [index record specification](TZ_LOCALIZATION_INDEX_EN.md). The [technology requirements specification](TZ_TECHNOLOGY_REQUIREMENTS_EN.md) defines `prerequisites` nodes, `links` entries, and counting for `AND`/`OR`; using negation in counting and layout is not agreed yet. Including sections in the container does not approve their internal structure before it is described.

## Result container

A successful response contains `type: "ready"`, the current `operationId`, and a `data` object. The general form is shown with an empty result:

```json
{
  "type": "ready",
  "operationId": 7,
  "data": {
    "technologies": {},
    "links": [],
    "localization": {
      "ru": {},
      "en": {}
    },
    "diagnostics": []
  }
}
```

All four `data` sections are also present in an empty result.

| Field | Type and purpose |
| --- | --- |
| `technologies` | Dictionary: base ID → technology entry |
| `links` | Array of `from`, `to`, and `requirementPaths` entries under the technology requirements specification |
| `localization` | Object with `ru` and `en` indexes; each index maps string IDs to localization records |
| `diagnostics` | Array of non-blocking data preparation issues |

The catalog, requirements, links, and localization belong to one opened database and are published together. The complete tree and original JSON string are excluded from `data` and are not copied into interface state. A valid empty catalog remains a successful result under the database opening specification.

## Technology entry

Each `data.technologies` entry represents one base technology. Its dictionary key matches the entry's `id` field.

| Field | Type and purpose |
| --- | --- |
| `id` | String: base game technology ID |
| `tier` | Integer: level used for column assignment |
| `prerequisites` | Tree of `technology` and `group` nodes with an `AND` root under the technology requirements specification |
| `prerequisiteIds` | Array of unique string IDs of directly mentioned technologies, including alternatives |
| `requirementCount` | Non-negative integer: requirement count computed under the agreed sorting rules |
| `representations` | Ordered array: base representation, then variants in original order |
| `sourceRef` | String path to the original base technology node in the loaded database |

`prerequisites` is extracted only from the base technology field of that name. Empire, species, DLC, building checks, and other eligibility conditions are excluded. The shared requirement processor computes `prerequisiteIds` and `requirementCount`; consumers use the prepared values.

Transitive predecessors are not added to `prerequisiteIds`. ID ordering does not change set membership. The array does not replace the tree: mentioning a technology among alternatives does not make it individually mandatory.

In the current database, `tech_titans` directly names `tech_battleships` and `tech_stinger_growth_2` inside `OR`. Its `prerequisiteIds` therefore contains two IDs, while `requirementCount` equals `1`. This is an example from actual data, not a technology-specific rule.

Under the technology requirements specification, a technology node contributes `1`, `AND` sums child values, an `OR` group contributes `1`, and an empty root `AND` contributes `0`. The tree format accommodates all five known operators; counting and layout for `NOT`, `NAND`, and `NOR` require separate agreement. Until then, under additional user approval, opening such data stops with `invalid_database` and does not return `ready`.

## Technology representations

Research area and text IDs belong to the representation. Base `id`, `tier`, and technology requirements remain unchanged when switching variants.

| Field | Type and purpose |
| --- | --- |
| `id` | String: `base` for the base representation, `swap:1`, `swap:2`, and so on for variants |
| `variantNumber` | Positive integer variant number; absent for `base` |
| `area` | Effective area: `physics`, `society`, or `engineering` |
| `nameId` | Name string ID from `requested_key` |
| `descriptionId` | Description string ID from `requested_key` |
| `sourceRef` | String path to the original technology node or corresponding `technology_swap` block |

`base` is always first in the array. Variants follow in original `technology_swap` block order; the number in `swap:N` matches `variantNumber`. Different variants with matching names or localization keys retain separate identifiers.

A representation identifier is unique within its base technology. Full identity is the pair of base technology ID and representation ID. Variant numbering and locations are not considered stable between database builds.

The effective `area` already incorporates inheritance from the base technology when a variant does not specify its own area. Names and descriptions are not duplicated as text inside representations: they are resolved through the shared localization index.

## Original-node references

`sourceRef` is a string path within the loaded JSON tree retained by the Worker. It is not a filesystem path. The actual path to the `tech_titans` node in the current database is:

```text
/documents/7/items/5
```

A reference belongs only to the opened database from which the entry was produced. Database replacement discards previous references together with the catalog. Matching paths in two different files do not establish identical technologies or variants.

The Worker owning the original tree resolves the reference. This stage does not add a separate node retrieval command; the first screen uses prepared data. Reference stability after a database rebuild is not promised.

## Localization and diagnostics

`data.localization.ru` and `data.localization.en` contain only the opened database's localization. The application connects this index as the `database` source of shared lookup. Built-in interface strings are loaded separately and are not sent back in the Worker result.

Lookup using source `database`, the selected language, and a string ID reaches the corresponding index record. The lookup key remains `requested_key`, and the text remains saved `text`, under the [localization specification](TZ_LOCALIZATION_EN.md). A record contains `status` (`resolved` or `missing`), `text`, and `origins` under the [index record specification](TZ_LOCALIZATION_INDEX_EN.md). Identical texts merge while preserving provenance; differing texts under one ID and language are a blocking preparation error, and no `ready` response is returned. The index has no `conflict` state.

`diagnostics` contains only warnings with `severity: "warning"` under the [diagnostics specification](TZ_DIAGNOSTICS_EN.md). Shared record fields are `severity`, `code`, `phase`, `params`, and `details`. An empty array is sent when there are no warnings. A blocking opening failure is returned in a separate `error` record within an `error` response together with accumulated warnings; it does not belong in `ready` or become a successful empty result.

## Acceptance criteria

Checks are performed after implementation:

1. The `ready` response includes all four `data` sections, including results with an empty catalog.
2. Catalog keys match technology `id` values; derived requirement values are prepared by the shared processor.
3. The `tech_titans` alternative requirement example produces two direct IDs and a requirement count of `1`.
4. Every technology starts with `base`; variants receive sequential `swap:N` identifiers and matching `variantNumber` values.
5. Matching names do not merge different variants, and language changes do not change identifiers.
6. `sourceRef` identifies the corresponding original node in the current database; previous references are not used after replacement.
7. The RU/EN index is connected as `database`; texts are not copied into each representation.

## Further design

- Counting and layout for `NOT`, `NAND`, and `NOR`; tree structure, links with paths, and `AND`/`OR` rules are already defined.
- Program types for nested `details` fields following the contents agreed in the diagnostics specification; current codes use `params: {}`.
- Program types and module interfaces for the derived result; transformation errors follow the [division of responsibilities](TZ_DATABASE_OPENING_EN.md#validation-responsibilities), without repeating validation of the original database.

[Русская версия](TZ_WORKER_RESULT_RU.md) · [Worker protocol](TZ_WORKER_PROTOCOL_EN.md) · [Interface concept](CONCEPT_EN.md).
