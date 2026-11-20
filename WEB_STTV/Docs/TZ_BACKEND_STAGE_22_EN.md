# Stage 22 — importing game localization into MongoDB

## Contents

- [Scope and sources](#scope-and-sources)
- [Localization document](#localization-document)
- [Selecting a translation](#selecting-a-translation)
- [Preparation and loading](#preparation-and-loading)
- [Acceptance](#acceptance)

## Scope and sources

**Approved and implemented on 2026-11-20.** The first import into the test server populates the `localization` collection in the `wiki` database. Its contents cover every game string from the configured RU and EN sources, including keys the viewer does not yet use. The frontend manages its own interface translations. [Usage and verification](BACKEND_STAGE_22_EN.md)

Source order and parser settings come from the [localization configuration](../config/enrichment/localization.json). Directory locations come from the [global project variables](../global_variables.json). For each language, recursively read `*.yml` files and collect definitions from sections with the corresponding language header using the [existing reader](../src/backend/sttv/enrichment/localization/reader.py).

| Language | Sources in descending priority |
| --- | --- |
| `ru` | `RU_LOC_TIER_1` — Russian Localization Fix RE `replace` directory → `RU_LOC_TIER_2` — main mod translation → `RU_LOC_TIER_3` — vanilla Russian |
| `en` | `EN_LOC_TIER_1` — vanilla English |

## Localization document

One document represents one key in one language. Both writers and readers construct the composite `_id` with `language` first and `key` second. Keys retain their original case. A description ending in `_desc` has its own document. A key available in just one language produces a single document.

```json
{
  "_id": { "language": "ru", "key": "tech_titans" },
  "selected": 0,
  "definitions": [
    { "tier": "RU_LOC_TIER_2", "file": "technology_l_russian.yml", "line": 51, "raw": "Титаны" },
    { "tier": "RU_LOC_TIER_3", "file": "technology_l_russian.yml", "line": 47, "raw": "Титаны" }
  ]
}
```

`definitions` holds every occurrence. `file` is a path relative to the corresponding tier directory, using `/` as its separator. Line numbers start at 1. The `raw` field stores the contents of the original outer quotes, preserving empty strings, literal escape sequences, `$KEY$` references, dynamic substitutions and game markup. Reference expansion belongs to a subsequent enrichment stage.

## Selecting a translation

1. Collect all definitions for each `(language, key)`. Sort them by configured tier priority, then by relative path and line number within a tier. Preserve occurrences with identical text.
2. Select the highest-priority tier containing the key. If all its definitions have the same `raw` value, set `selected` to the zero-based index of the first one. Consumers read the text through `definitions[selected].raw`.
3. Different `raw` values in the selected tier are a conflict. Report the language, key, tier and source locations, and stop publication of that dataset. Preserve conflicts in overridden tiers and include them in the report. This follows the existing [translation selection rules](../src/backend/sttv/enrichment/localization/index.py).

## Preparation and loading

Preparation runs on the Windows machine hosting the game. It writes formatted JSON to the working directory and reports file, definition, document and conflict counts by language and tier. The prepared data can be loaded again without opening the game files.

An explicit command on that workstation connects directly to MongoDB over TLS as `wiki`. Configuration specifies the address, database, collection and Vault references for the password and public CA certificate. Connection secrets are handled in memory.

The loader writes documents in batches and publishes the complete dictionary after verification. Loading identical input again yields identical documents. Loading updated input removes keys that have disappeared from all sources. A preparation or write failure leaves the previous complete dictionary available. The import operates only on localization. Resetting the entire database is a separate administrative operation.

## Acceptance

The following baseline was measured from the configured sources on 2026-11-20. Recalculate the expected counts when those sources change.

| Source | Files | Definitions |
| --- | ---: | ---: |
| `RU_LOC_TIER_1` | 9 | 2,167 |
| `RU_LOC_TIER_2` | 233 | 149,404 |
| `RU_LOC_TIER_3` | 232 | 151,952 |
| `EN_LOC_TIER_1` | 232 | 150,258 |
| **Total** | **706** | **453,781** |

- Compare the published documents with the prepared JSON by composite key, definitions and `selected`. The baseline contains 303,500 documents, including 153,242 RU and 150,258 EN. There are 2,984 Russian-only keys.
- Read `tech_titans` in both languages. RU selects `Титаны` from `RU_LOC_TIER_2`, and EN selects `Titans` from `EN_LOC_TIER_1`. Also check a description key, a string containing a substitution and a Russian-only key.
- The RU baseline has 13 keys with competing definitions within the vanilla tier. Higher tiers override all 13. Use fixtures for identical duplicates, a conflict in the selected tier and an empty string.
- Check reloading identical input, removing an obsolete key after a source update and interrupting a load midway. Compare the readable collection with the expected complete dictionary in each case.
