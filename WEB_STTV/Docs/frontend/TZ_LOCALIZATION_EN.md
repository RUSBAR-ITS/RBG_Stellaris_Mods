# Stellaris Technological Tree View — Shared localization specification

## Contents

- [Status and scope](#status-and-scope)
- [Lookup contract](#lookup-contract)
- [Built-in strings](#built-in-strings)
- [Database source](#database-source)
- [Source configuration](#source-configuration)
- [In-memory index](#in-memory-index)
- [Duplicates and missing text](#duplicates-and-missing-text)
- [Interface string parameters](#interface-string-parameters)
- [Display without markup processing](#display-without-markup-processing)
- [Language changes and data updates](#language-changes-and-data-updates)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and scope

This document records string lookup agreed by the user on 2026-11-16 and the decision to display text without processing game markup at this stage. The index format and contradictory text handling were refined by the 2026-11-17 decision in the [index record specification](TZ_LOCALIZATION_INDEX_EN.md). The mechanism has not been implemented yet.

The basis is the [Text specification](elements/TZ_TEXT_EN.md), [language selector](elements/TZ_LANGUAGE_SELECTOR_EN.md), [technology card](elements/TZ_TECHNOLOGY_CARD_EN.md), and [localization storage in the database](../BACKEND_STAGE_10_EN.md#database-storage-and-reading).

The mechanism serves built-in interface strings and prepared technology and variant names and descriptions in the database. The backend has already applied game source priorities, static reference expansion, and description inheritance. The frontend uses that result.

## Lookup contract

Lookup requires three values:

| Value | Provider | Purpose |
| --- | --- | --- |
| Source | Consuming component; built-in by default | Select the localized string collection |
| String ID | Consuming component; required | Locate a record within the source |
| Language | Application state | Select `ru` or `en` |

The component supplies an ID and, when needed, a source. The system provides the language. An interface template may additionally receive named parameters; they do not change the string address.

Example card request:

```text
source: database
id: tech_titans
```

With system language `ru`, the result is Титаны; with `en`, it is Titans. Descriptions use their own string ID, such as `tech_titans_desc`. Lookup does not require additional `name`, `description`, technology ID, or specific variant-block ID parameters.

The card's selected variant identity remains separate from its text ID. Matching names or string IDs do not merge variants in the interface.

## Built-in strings

Built-in localization resides in two separate JSON files: `locales/ru.json` and `locales/en.json`. These are relative names within frontend resources; their full paths and loading are determined during build design.

Each file is an `ID → string` dictionary. Both languages have the same key set. New interface keys use the `sttv_` prefix; original game string keys are retained.

Example Russian dictionary:

```json
{
  "sttv_language_label": "Язык",
  "sttv_variant_suffix": " (Вариант {number})"
}
```

Example English dictionary:

```json
{
  "sttv_language_label": "Language",
  "sttv_variant_suffix": " (Variant {number})"
}
```

Labels, hints, and accessible action names retrieve text from this source through the shared mechanism. Game translations are not copied into built-in files.

## Database source

The reader collects records from `enrichments.localization` on technologies and their `technology_swap` nodes. For each language, it includes both `name` and `description`, using:

| Record field | Use |
| --- | --- |
| `requested_key` | String ID in the index |
| `text` | Text for display |
| `key` | Actual selected translation key; metadata |
| `source` | Translation provenance; metadata |
| `inherited_from` | Inherited description provenance; metadata |
| `raw`, `unresolved_references` | Preserved backend information; resolution is not repeated |

When a description is inherited, the variant retains its own `requested_key`, while `key` and `text` refer to the selected base technology description. Lookup therefore uses `requested_key`; `key` does not become an additional lookup ID.

The request source and a record's `source` field are distinct: the former selects storage, while the latter describes translation provenance.

Inspection of the current stage-ten database found 3,540 localization records, 3,400 unique language/ID pairs, and 124 repeated pairs. All repeated texts match; this sample contains no missing or empty texts. These figures describe the inspected database and do not constrain implementation.

## Source configuration

A separate configuration describes built-in storage and the database. Each source specifies:

- Reader type: string dictionary or enriched database nodes.
- Data and localization record locations.
- Language-based file or branch selection.
- The field or key matched against the string ID.
- The resulting text field.

Two small readers support the two agreed formats and prepare the shared index. Configuration describes source structure; the appropriate reader performs traversal and reading. Internal path knowledge is not duplicated in UI elements.

Under the [frontend structure specification](TZ_STRUCTURE_EN.md), configuration resides in `WEB_STTV/config/frontend/`, the localization mechanism in `src/frontend/localization/`, and built-in strings in `src/frontend/locales/ru.json` and `src/frontend/locales/en.json`. The complete configuration schema, filename, and reader API names are determined during implementation design.

## In-memory index

The shared index has this logical structure:

```text
source → language → string ID → text record
```

It is built for both languages when a source loads. Text display uses the index; each card or tooltip does not need to traverse the database tree again.

The index is derived in-memory data. Its record contains `status` (`resolved` or `missing`), `text`, and `origins` under the [index record specification](TZ_LOCALIZATION_INDEX_EN.md). Original database record information is retained in `origins`; the built-in string reader uses the same structure with empty `origins`. Localization in the database file remains attached to objects; this stage does not introduce saving the index into the database or a separate persistent file.

Under the [database opening specification](TZ_DATABASE_OPENING_EN.md#file-reading-and-web-worker), the database localization reader runs in a Web Worker. It prepares the RU/EN index with its specified metadata and sends it to the main thread for registration as the database source. Built-in interface strings load separately from frontend resources. Shared lookup by source, language, and ID runs in the main thread; displaying each string does not require Worker messaging. The complete database tree stays in the Worker.

## Duplicates and missing text

Matching is scoped to source/language/ID. Identical IDs in different sources or languages do not conflict. IDs and texts are compared as stored, without changing case, whitespace, or markup.

| Situation | Behavior |
| --- | --- |
| One found text | `resolved`, return its text |
| Multiple records with identical text | `resolved`, merge while retaining all original records in `origins` |
| Multiple records with differing found texts | Data preparation error with diagnostics for manual investigation; the prepared result is not published |
| Missing ID or all texts are `null` | Treat the string as missing; existing records with `null` produce `missing` |
| One unambiguous text together with missing `null` values | `resolved`, use the found text and preserve every record's provenance |
| Found text is `""` | `resolved`, display empty text; combining it with nonempty text under the same ID is an error |

A missing string displays `⟦string ID⟧`, for example `⟦tech_titans⟧`. The selected language is not automatically replaced with another. Contradictory texts are a blocking database opening error: diagnostics include the lookup source, language, ID, differing texts, references to original objects and records, and translation source and inheritance information. The prepared index has no `conflict` state; after manual investigation and correction, the user opens the database again.

## Interface string parameters

Named parameters support built-in templates, such as `{number}` in a variant suffix. The component supplies values separately from the string ID; the mechanism substitutes them into the resolved interface template.

For `sttv_variant_suffix` and number `2`, the result is ` (Вариант 2)` or ` (Variant 2)`, depending on language. The number follows variant-block order under the card specification. The name comes from the database and the suffix from built-in storage; combining them does not change either source string.

Interface parameter substitution does not apply to game text from the database. The parameter API and diagnostics for invalid calls are refined during implementation design.

## Display without markup processing

At this stage, database `text` is displayed as plain text. It is not replaced with the `raw` field.

Game color codes `§…`, icon notation `£…`, preserved `$…$` tokens, square-bracket expressions, and other fragments remain as stored. They are not removed, expanded, or converted into styling or images. A literal backslash followed by `n` is likewise not converted into a line break by an additional processor. Normal JSON decoding remains part of data reading.

The string is not interpreted as HTML or Markdown. The shared Text element's styling role, width-based wrapping, and agreed line restriction still apply; they do not alter the source string. Numeric substitution in a built-in variant suffix follows the previous section.

The [Text specification](elements/TZ_TEXT_EN.md#placement-and-overflow) defines how the subsequent stage renders colored spans. Lookup returns the original string with its markup.

## Language changes and data updates

Changing the language updates all visible strings, including open tooltips and variant lists, using the same sources and IDs. The already prepared index for the other language is used. Switching does not require database rebuilding, retrieving translations from game files, or rebuilding the index each time.

Replacing or updating a source rebuilds its portion of the index. Old entries from the replaced source are no longer used. Changing the language preserves the selected technology variant and other interface settings.

Persisting language across launches remains the responsibility of the [shared state mechanism](CONCEPT_EN.md#settings-and-state-persistence).

## Acceptance criteria

Checks are performed after implementation:

1. The same built-in string ID resolves to RU/EN from the respective JSON file; omitting the source selects built-in storage.
2. Technology and variant names and descriptions resolve by `requested_key`; inherited descriptions return prepared `text` even when `key` differs.
3. Cards and tooltips pass string IDs without selecting internal `name` / `description` fields or supplying an extra object ID.
4. Duplicate records with matching text merge while preserving provenance; differing texts produce a blocking error with diagnostics, and the prepared result is not published.
5. Missing IDs and exclusively `null` values produce a marker; missing values with unambiguous text produce `resolved`, and a found empty string remains empty. No automatic language substitution occurs.
6. Matching IDs across sources or languages do not mix their records.
7. A built-in `{number}` template receives the supplied number; game text does not pass through that parameter processor.
8. Game color, icon, and substitution codes, HTML-like text, and literal escape sequences remain plain text. Display uses `text`, not `raw`.
9. Switching RU/EN updates visible text and open overlays without traversing the database again, reading game localizations, or resetting selected variants.
10. Replacing a source updates its index and removes obsolete entries from lookup; the database file is unchanged.

## Subsequent implementation details

The index record structure is defined in a [separate specification](TZ_LOCALIZATION_INDEX_EN.md). The shared record, `missing_localization` warning, and `localization_conflict` error are defined in the [diagnostics specification](TZ_DIAGNOSTICS_EN.md). The API, complete configuration schema and paths, resource loading, and program types for per-code details remain to be defined. The diagnostics specification already defines `details` contents and empty `params` for current codes. Database opening, cancellation, retry, and replacement follow the [database opening specification](TZ_DATABASE_OPENING_EN.md#errors-and-retry): the index is published with the catalog after success, individual missing strings do not block viewing, and contradictory texts block preparation. Detailed handling of other whole-localization-source failures and invalid template parameters requires further design.

Frontend-to-local-service transport, persistent state storage, and game markup processing are designed separately. This document establishes shared lookup, merging rules, and text display.

[Русская версия](TZ_LOCALIZATION_RU.md) · [Interface concept](CONCEPT_EN.md).
