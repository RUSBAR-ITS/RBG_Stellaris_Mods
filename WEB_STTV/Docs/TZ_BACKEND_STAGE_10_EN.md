# Stellaris Technological Tree View — stage ten specification: localization in the database

## Contents

- [1. Status and goal](#1-status-and-goal)
- [2. Research baseline](#2-research-baseline)
- [3. Stage boundaries](#3-stage-boundaries)
- [4. Configuration and sources](#4-configuration-and-sources)
- [5. Object and key selection](#5-object-and-key-selection)
- [6. Localization reading and priorities](#6-localization-reading-and-priorities)
- [7. References and description inheritance](#7-references-and-description-inheritance)
- [8. Database storage](#8-database-storage)
- [9. Refresh and publication](#9-refresh-and-publication)
- [10. Diagnostics](#10-diagnostics)
- [11. Modules and schemas](#11-modules-and-schemas)
- [12. Verification and acceptance](#12-verification-and-acceptance)
- [13. Deliverables](#13-deliverables)

## 1. Status and goal

**Approved by the user; stage ten is implemented.** Date: 2026-11-16. Operation, results, and limitations are in the [stage-ten guide](BACKEND_STAGE_10_EN.md).

The foundation is [stage nine](BACKEND_STAGE_9_EN.md), the [concept](CONCEPT_EN.md), and [shared coding principles](TZ_EN.md#2-project-structure-and-coding-principles). Agreed decisions cover technologies and conditional variants, RU/EN names and descriptions, static reference expansion while retaining original text, inheritance of missing variant descriptions, and storing results **inside the database itself**.

The goal is a separate operation enriching completed trees with localization without reparsing game definitions. Text is attached to the corresponding objects in a service section. The parser remains general purpose. Possible removal of game mechanics unnecessary for the reference application belongs to future database processing and is outside this stage.

## 2. Research baseline

Research used the verified format-3 database `data/stage9/database.json` and configured localization sources. The file is 138,156,360 bytes: technology-directory processing results with expansions and provenance, without localization or images.

| Observation | Result |
|---|---|
| Database documents | 35 files from `common/technology`, including subdirectories |
| Target objects | 679 technologies and 206 `technology_swap` blocks |
| Other definitions | 13 categories and 6 research `tier` definitions; outside this stage's localization scope |
| Names found per language | All 679 base names and 206 variant names |
| Descriptions found per language | All 679 base descriptions and 125 variant-specific descriptions |
| Variants missing their own descriptions | 81 per language; use the agreed inheritance |
| Localization files inspected | 706: 9 in RU tier 1, 233 in RU tier 2, 232 in RU tier 3, 232 in EN tier 1 |
| Static references in selected text | Reach 371 additional RU keys and 388 additional EN keys |
| Conflicts in selected keys, cycles, and missing static references | None found during research |

The inventory is under `data/stage10/specification_research/`: `localization_inventory.json`, `reference_inventory.json`, and `localization_line_inventory.json`. This is preimplementation research, not verification of the new processor. Counts describe the inspected sources and must not be hardcoded. All currently selected Russian text comes from tier 2; tiers 1 and 3 remain supported.

## 3. Stage boundaries

Includes selecting objects from a completed database, reading RU/EN, prioritized text lookup, ordinary static reference expansion, variant description inheritance, saving results in the database, reporting, a programmatic operation and noninteractive invocation, schemas, and verification.

Excludes localization of other objects, automatic translation, glossary population, icons, HTML or visual execution of game markup, dynamic value evaluation, country eligibility evaluation, UI, HTTP service, database compression/splitting, and removal of game mechanics. The old command whitelist profile is not restored. Translations are extracted from files rather than authored.

## 4. Configuration and sources

A separate `config/enrichment/localization.json` with `format_version: 1` defines the following settings groups. It does not become a ninth parser configuration and is not required for ordinary tree builds.

| Group | Requirements and initial values |
|---|---|
| Input and output | `database: "database.json"`, `report: "reports/localization_report.json"`, relative to `WORK_DIR`; read and update the database at the same path |
| Technology selection | Variable `TECH_PATH`, `pattern: "*.txt"`, `recursive: false`; match against database document paths |
| Keys | Base name from the object key; variant name from the direct `name` field in a direct `technology_swap` block; description suffix `_desc` |
| Languages | `ru` / `l_russian`, `en` / `l_english`; independent ordered source lists |
| Reading | `pattern: "*.yml"`, `recursive: true`, `encoding: "utf-8-sig"` |
| References | Delimiter `$`, ordinary key matching `[A-Za-z0-9_.:-]+`; depth limit 64, final field text limit 1,000,000 characters |
| Inheritance | Use the base technology's description when the variant-specific key is absent |

Obtain paths from `global_variables.json`, expanding `${...}` through the existing mechanism. Resolve relative localization directories against `STELLARIS_ROOT`:

| Language | Priority, highest to lowest |
|---|---|
| RU | `RU_LOC_TIER_1` → `RU_LOC_TIER_2` → `RU_LOC_TIER_3` |
| EN | `EN_LOC_TIER_1` |

Source lists are configurable; a particular mod is not a mandatory product dependency. Every explicitly configured source must be readable; do not silently skip missing directories. Users can remove a source from configuration. An existing empty directory is valid, with missing text diagnosed separately.

Reading a completed enriched database requires no sources. The operation itself requires the database and selected localization directories; technology, inline, effect, trigger, variable, and script value directories are not reread. `TECH_PATH` is an addressing setting without checking whether its directory exists on disk.

## 5. Object and key selection

In selected documents, a technology is a root assignment `name = { ... }`. Do not identify it by the `tech_` prefix: `null_void_beam`, for example, exists. Scalar declarations and other forms are not technologies. The default nonrecursive selector excludes `category/` and `tier/` documents while preserving their data in the database.

Process each technology's direct `technology_swap = { ... }` assignments, taking the single direct scalar `name` field from each. Do not search the whole tree for arbitrary `name` or `desc` fields. `prereqfor_desc.desc` describes unlocks and is not the general technology description. An absent, repeated, or nonscalar variant name is an object-selection error with coordinates.

| Object | Name key | Description key |
|---|---|---|
| Base technology | Root assignment key | That key + `_desc` |
| Conditional variant | Its `name` field value | That value + `_desc` |

An object's identity is its database location: a JSON Pointer from the root, such as `/documents/0/items/2`. A variant pointer addresses the `technology_swap` assignment itself, not its `name` field. Repeated names remain separate nodes rather than being merged. A variant's parent is its enclosing technology.

Keep selection rules separate from text reading and reference resolution. This stage implements one rule type for technologies and variants; a general query language or registry of every game object type is unnecessary. If the database has no matching technologies, fail selection rather than presenting empty processing as success.

## 6. Localization reading and priorities

Read game entries `key:0 "text"` and `key: "text"`, language headers, blank lines, and comments; support UTF-8 with and without BOM. The number after the colon is not source priority. Do not use a general YAML parser with automatic type coercion.

Preserve the content between outer quotes, including case, internal whitespace, escaping, game icons, color codes, and grammatical markup. `#` within text is not a comment; a comment after the closing outer quote is excluded. Account for escaped quotes and observed internal quotes. A game-file `\n` sequence remains two characters after JSON reading rather than automatically becoming a newline. Use the standard serializer for JSON escaping.

Index exact case-sensitive keys separately for each language. In mixed sources, consider only sections of the required language. Unreadable files, encoding errors, and ambiguous/unsupported localization lines produce diagnostics with file and line; do not silently discard them.

Apply priority independently to each key, including nested references. Continue to a lower source only if the key is absent. An empty string `""` is a found value. Do not replace missing RU with English, a technology identifier, or an invented translation.

Identical duplicates within a tier are allowed: select a source deterministically by relative path and line number. Different values for one key in the selected tier are an error; do not pick arbitrarily or fall through to a lower tier. Conflicts in unreachable keys or overridden lower tiers are reported but do not block selected text. Compare original text before reference expansion.

## 7. References and description inheritance

Recursively expand an ordinary `$key$` reference when its exact key exists in the same-language index. Each lookup uses the ordered sources independently. For example, `$tech_archeology_lab_desc$` becomes the selected description with its reachable static references expanded. Preserve the field's original string separately from the result.

Recognize token boundaries: dynamic `[...]`, formatted `$KEY|...$`, and icons `£...£` are preserved as whole tokens; their contents are not interpreted as ordinary references. Color codes and other game markup are preserved but do not prevent ordinary reference expansion in the text they surround. Game-code parameter substitution and defaults do not apply here. An exact `$NAME$` form with no indexed key does not by itself prove an error: it may be a dynamic substitution. Preserve it, record the unresolved token, and warn rather than guessing its value.

A static reference cycle or configured limit violation is an error carrying the key chain. Shared dependencies may be cached by language and key, but caching must not hide cycles or violate depth/size limits. Results must not depend on object processing order.

For a variant description, search its own key across **all tiers of the requested language** first. Only if absent, use the base technology's description in that language and mark inheritance. Do not replace an existing empty description; do not bypass an error or unresolved reference in an existing description through inheritance. Variant names do not inherit base names.

If the base description is also missing, preserve missing text and issue a warning. Successfully inheriting a parent description is an expected result tracked by a separate counter. The same variant may have its own description in one language and an inherited description in the other.

## 8. Database storage

The target format is `sttv.parse_database`, `format_version: 4`. Structural fields of the nine node kinds remain unchanged. An `assignment` node may have an optional service field `enrichments`, with a declared `localization` subsection in this stage. Enrichment may be absent: the ordinary builder emits format 4 without localization and does not read its sources.

Attach results directly to the base technology or variant assignment. Access structure:

```text
node.enrichments.localization.ru.name
node.enrichments.localization.ru.description
node.enrichments.localization.en.name
node.enrichments.localization.en.description
```

Each of the four fields uses the same declared structure:

| Field | Type and meaning |
|---|---|
| `requested_key` | String: the object's own name/description key |
| `key` | String: the actually selected key, or `null` when text is missing |
| `raw` | Original selected string content, or `null` |
| `text` | Text after ordinary static reference expansion, or `null` |
| `source` | `{tier, file, line}` or `null`; `tier` is the source variable name, `file` is relative to that source using `/`, `line` starts at 1 |
| `inherited_from` | JSON Pointer to the base technology when a description is successfully inherited; otherwise `null` |
| `unresolved_references` | Unique unresolved ordinary `$...$` tokens, including those reached through nested references, in stable order |

With inheritance, `requested_key` remains the variant key, while `key`, `raw`, `text`, and `source` describe the base technology's description. A separate boolean flag is unnecessary: nonnull `inherited_from` unambiguously marks inheritance. When text is missing, all selection/inheritance fields are `null`, references are empty, and the requested key remains. For found empty text, `raw` and `text` are `""`, with source and key present.

Do not insert localization into game `items`, `key`, or `value`; do not change order, repetitions, `span`, `origin`, or `expansions` history. Analytics traverses only syntax children; enrichment adds no game nodes or text-frequency occurrences. The service-section structure is schema-validated, while game-field names remain unrestricted by a registry.

Do not copy entire language dictionaries or temporary indexes into the database. Reached-reference sources and verification hashes are listed in the report. The database alone is sufficient for reading saved names and descriptions; no separate localization file needs joining to it.

## 9. Refresh and publication

The operation reads and validates the database, selects objects, loads localization, prepares all four fields for each object, and replaces only `enrichments.localization`. When selection changes, remove old localization subsections created by this operation from objects no longer selected. Preserve other supported service data and the entire game tree. Repeating unchanged inputs produces a byte-identical database; execution time belongs only in the report.

A complete parser rebuild creates a new database without previous enrichment. Run localization again explicitly; do not automatically transfer it from the old tree by matching names. The operation does not support older formats: rebuild is required. Verification for this stage uses a new database under `data/stage10/`, preserving previous results.

The database read/write path deliberately matches. This is a local exception to input/output collision checks, not permission to overwrite sources, configurations, schemas, or the report with the same file. All writes stay in permitted `WORK_DIR` inside the repository. Validate allowed physical paths using existing safeguards.

Publish through a temporary file beside the database: serialize, validate schema and references, reread, then atomically replace. Preparation failure leaves the previous database intact. Before replacement, check that the input database and read sources/settings have not changed during the operation. Concurrent writers to one database are unsupported in this stage.

Save the report separately using existing safe persistence. Do not claim a shared transaction across two files: if the database was replaced but report writing failed, the operation must disclose this and preserve an accurate `database_written`. Do not claim the old database survived when replacement occurred.

## 10. Diagnostics

Report format `sttv.localization_report`, version 1, contains status, `database_written`, before/after database hashes, settings and their hashes, read-file inventory with hashes, counters by language/field, and diagnostics. Include selected sources for transitive references, duplicates, missing text, inheritance, and unresolved tokens. Environment-specific absolute paths are allowed in the working report but are unnecessary in enriched nodes.

Object diagnostics include JSON Pointer, language, field, requested key, and available source coordinates; reference diagnostics include the chain. Missing text and unresolved ordinary tokens produce warnings, allowing publication with explicitly incomplete fields. Dynamic markup preserved according to the rules does not itself require a warning.

Configuration, reading, database-format, object-selection, selected-text ambiguity, cycle, limit, and writing errors prevent a successful result. Do not publish a partially processed database when errors occur. Research counts are not success requirements for another game installation.

## 11. Modules and schemas

Add `sttv/enrichment/localization/`: settings, target selection, line reading, priority indexing, reference resolution, result attachment, and operation coordination are separate compact responsibilities. Reuse existing JSON, path, error, and safe-publication utilities. If configuration variable expansion is needed independently of parser loading, extract only that shared code without unrelated refactoring.

Provide a Python operation and noninteractive command accepting configuration/global-variable paths. Do not create a setup dialogue or web UI. The programmatic result returns status and paths suitable for later UI integration; document the concrete invocation in the implementation guide.

Update the `database.schema.json` generator for format 4; add generated `localization.schema.json` and `localization_report.schema.json`, bringing the expected total to 13 schemas. Edit schemas through generator code; no game-command profile is required. Inheritance validation requires an existing parent node and matching text; provenance validation does not open the game. Existing readers and analytics must accept enriched databases without traversing service sections as code.

## 12. Verification and acceptance

Synthetic checks must cover:

1. Independent RU/EN, priority per key and nested reference, empty/missing values, identical/conflicting duplicates, and no cross-language substitution.
2. BOM, quotes, comments, `#` inside strings, escaping, literal `\n`, game markup, and reading errors.
3. A technology without `tech_`, category/tier exclusion, repeated variant names, direct `name` selection, malformed variant names, and no matching targets.
4. Multilevel references, shared dependencies, unknown tokens, dynamic/formatted substitutions, cycles, both limits, and retained `raw`.
5. Searching every tier for a variant-specific description before inheritance, independent language inheritance, empty own descriptions, missing parent descriptions, and valid `inherited_from`.
6. Unchanged original tree/history fields, unchanged node counts/frequencies after enrichment, repeatability, stale-result removal when selection changes, and localization-only refresh.
7. Enrichment without game-definition directories, reading completed data without localization or game sources, safe paths, failures before replacement, changing inputs during processing, and report-writing failure after replacement.
8. Schema generation, enriched/unenriched format-4 validation, and existing backend regression checks.

Real-data verification: build an unenriched format-4 database from the previous 35 files separately under `data/stage10/`, enrich it, and compare source trees and history before/after. With unchanged sources, expect 679 technologies and 206 variants, 885 RU/EN names each, and per language 679 base descriptions plus 125 own and 81 inherited variant descriptions. Independently verify actual reference chains and sources rather than relying on the processor; repeat the operation and compare bytes.

Record before/after database sizes, timing, and source immutability. Research inventories do not replace independent output verification. A full `common/` and `events/` traversal is unnecessary for this stage. In-game and visual checks have not been performed and are outside text-extraction acceptance; presentation remains a separate stage.

## 13. Deliverables

After approval and implementation: enrichment module, configuration, updated database contract, two new schemas, tests, verified enriched database and report in the working folder, bilingual `BACKEND_STAGE_10_RU.md` / `BACKEND_STAGE_10_EN.md` guide, and updated README/changelog. Existing game sources, previous outputs, working frequency lists, and general-purpose parser behavior are preserved.

[ТЗ на русском](TZ_BACKEND_STAGE_10_RU.md) · [Project overview](../README_EN.md).
