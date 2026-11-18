# Stellaris Technological Tree View — Localization index record specification

## Contents

- [Status and scope](#status-and-scope)
- [Index address and record](#index-address-and-record)
- [String provenance](#string-provenance)
- [Merging and missing text](#merging-and-missing-text)
- [Contradictory texts](#contradictory-texts)
- [Inheritance and built-in strings](#inheritance-and-built-in-strings)
- [Transfer and use](#transfer-and-use)
- [Acceptance criteria](#acceptance-criteria)
- [Further design](#further-design)

## Status and scope

As of 2026-11-17, this document's single-file and unqualified-reference provisions are superseded by the approved [stage-two specification](TZ_FRONTEND_STAGE_2_EN.md). The current implementation opens three version-five databases as one set and uses `{ database, pointer }` references; other applicable requirements remain in effect.

This document records the localization index record format agreed by the user on 2026-11-17. It refines the [shared localization mechanism](TZ_LOCALIZATION_EN.md) and [Worker result](TZ_WORKER_RESULT_EN.md). Contradictory texts are data errors requiring manual investigation; this decision replaces the previous rule of displaying a marker for a conflict.

This iteration produces documentation. It does not implement the frontend, modify the backend, or rebuild the database.

## Index address and record

The shared string address is source → language → ID. Components supply the source and ID; application state supplies the language. The `database` source uses `data.localization.ru` and `data.localization.en` in the `ready` response; each entry key comes from the original localization `requested_key`.

The source, language, and requested ID follow from the record's position in the index and are not duplicated inside it. The record has three required fields:

| Field | Type and purpose |
| --- | --- |
| `status` | `resolved` — text found; `missing` — text absent |
| `text` | A string for `resolved`, including `""`; `null` for `missing` |
| `origins` | An array of information about original records |

Example `data.localization.ru.tech_titans` entry from the current database:

```json
{
  "status": "resolved",
  "text": "Титаны",
  "origins": [
    {
      "recordRef": "/documents/7/items/5/enrichments/localization/ru/name",
      "key": "tech_titans",
      "raw": "Титаны",
      "source": {
        "tier": "RU_LOC_TIER_2",
        "file": "technology_l_russian.yml",
        "line": 51
      },
      "inheritedFrom": null,
      "unresolvedReferences": []
    }
  ]
}
```

`resolved` means display text is available. Preserved game substitutions and unresolved references do not by themselves make a string missing; this stage does not introduce game markup processing.

## String provenance

Each database `origins` entry has the following required fields:

| Field | Type and source |
| --- | --- |
| `recordRef` | String path to the original localization record inside the opened database |
| `key` | Actual selected translation key; a string or `null` when the translation is absent |
| `raw` | Original string before backend static reference expansion; a string or `null` |
| `source` | Translation provenance object or `null`: `tier` and `file` are strings, `line` is a positive integer |
| `inheritedFrom` | Original `inherited_from` value: a path to the base technology or `null` |
| `unresolvedReferences` | Array of strings from the original `unresolved_references` |

`recordRef` addresses a `name` or `description` record, while `inheritedFrom` addresses the base technology node. Both paths refer to the current database JSON, not disk files; replacing the database removes old references together with its index.

`source` describes translation provenance and differs from the lookup source `database`. Metadata is copied from the backend result; localization files are not read again.

The resulting `text` is stored once per index record. It is not duplicated in `origins`; `raw` remains a separate original value even if it matches the resulting text. All original records of a merged string remain represented in `origins`.

## Merging and missing text

Matching is scoped to source/language/ID. IDs and texts are compared as stored without changing case, whitespace, or markup. `null` denotes missing text and is not a separate text alternative.

| Input records for one ID | Result |
| --- | --- |
| One found text | `resolved`, with that `text` |
| Multiple identical found texts | `resolved`, one resulting text, all original records in `origins` |
| All texts are `null` | `missing`, `text: null`, preserved provenance |
| One unambiguous text together with missing `null` values | `resolved`, the found text, provenance for found and missing translations |
| Found empty string `""` | `resolved`, `text: ""` |
| Two or more differing found texts, including empty and nonempty strings | Data preparation error |

Lookup of an absent ID or a `missing` entry displays `⟦ID⟧`. Creating an entry for every arbitrary absent ID is unnecessary. A found empty string displays as empty. The selected language is not replaced with another.

## Contradictory texts

Different resulting texts for the same source, language, and ID are data errors requiring manual investigation. Index preparation fails. Diagnostics contain:

- The lookup source, language, and string ID.
- The differing resulting texts.
- References to original objects and localization records.
- Translation source and inheritance information.

During database opening, the failure is returned as an `error` response under the [Worker protocol](TZ_WORKER_PROTOCOL_EN.md). The catalog, links, and index are not published partially or as a successful empty result. Further correction and reopening follow the user's decision under the [database opening specification](TZ_DATABASE_OPENING_EN.md#errors-and-retry).

The prepared index has no `conflict` state. A missing-translation marker does not bypass contradictory text errors. This error uses `localization_conflict` with `severity: "error"` under the [diagnostics specification](TZ_DIAGNOSTICS_EN.md). In `details`, each differing text is associated with its provenance using the existing `origins` structure; `params` is `{}`. Exact program types for nested fields are refined separately.

## Inheritance and built-in strings

The backend has already applied inheritance. `requested_key` remains the index key; the actual `key` and parent are preserved in `origins`. For example, `tech_biogenesis_titans_desc` remains the lookup ID even when its description comes from `tech_titans_desc`. The actual key does not create an additional index alias; if it occurs independently, it is indexed normally.

If inheritance from different parents produces differing texts under one ID, the general error rule applies. The frontend does not select a parent itself or repeat translation resolution.

Built-in `locales/ru.json` and `locales/en.json` files retain the simple `ID → string` format. Their reader converts a found entry to the same structure, for example:

```json
{
  "status": "resolved",
  "text": "Язык",
  "origins": []
}
```

For built-in strings, `origins` is empty at this stage. Shared lookup is identical for both sources; interface template parameter substitution remains a separate operation under the localization specification.

## Transfer and use

The Worker prepares both database language indexes and transfers them with the catalog and links only after all preparation succeeds. The main thread registers the result as the `database` source. The built-in source is prepared separately from frontend resources.

Lookup and display use prepared records without tree traversal or Worker messages for each string. Changing the language selects the other index branch; replacing a data source replaces its index. The complete tree stays in the Worker, and database and game files remain unchanged.

## Acceptance criteria

Checks are performed after implementation:

1. A record contains `status`, `text`, and `origins`; only the agreed states and corresponding text types are allowed.
2. Identical texts merge while preserving every record's provenance; the resulting `text` is not duplicated in `origins`.
3. All `null` values produce `missing`; missing values together with one unambiguous text produce `resolved` with full provenance.
4. An absent ID and `missing` produce a marker; `""` remains a found empty string. There is no language substitution.
5. Differing texts, including empty and nonempty strings, produce an error with the required information; neither `ready` nor partial data is published.
6. Inherited descriptions resolve by `requested_key` and retain the actual key and parent; ambiguous inheritance is also an error.
7. `recordRef` addresses the original localization record in the current database; metadata is transferred without rereading game files.
8. Built-in strings use the shared structure with empty `origins`; RU/EN use one lookup mechanism without rebuilding the index on language changes.

## Further design

Program types for nested `details` fields, module APIs and types, and the complete source configuration schema remain to be designed. The diagnostics specification defines detail contents and empty `params` for current codes. This document defines index records and their preparation rules; handling invalid interface template parameters is refined separately.

[Русская версия](TZ_LOCALIZATION_INDEX_RU.md) · [Shared localization mechanism](TZ_LOCALIZATION_EN.md) · [Worker result](TZ_WORKER_RESULT_EN.md).
