# Stellaris Technological Tree View — stage 11 specification: three localized databases

## Contents

- [1. Status and goal](#1-status-and-goal)
- [2. Sources and scope](#2-sources-and-scope)
- [3. Configuration and outputs](#3-configuration-and-outputs)
- [4. Format and set membership](#4-format-and-set-membership)
- [5. Building and publication](#5-building-and-publication)
- [6. Localization target selection](#6-localization-target-selection)
- [7. Descriptions and string provenance](#7-descriptions-and-string-provenance)
- [8. Diagnostics and validation](#8-diagnostics-and-validation)
- [9. Code organization](#9-code-organization)
- [10. Acceptance criteria](#10-acceptance-criteria)
- [11. Related documents](#11-related-documents)

## 1. Status and goal

Approved by the user on 2026-11-17. Implementation and validation are described in the [stage-eleven guide](BACKEND_STAGE_11_EN.md).

The backend builds technology, component and building databases from one set of game sources. All three retain results of the existing general-purpose parser and localization enrichment. This prepares data for subsequent chain identification. A new sorting algorithm and selection of a primary predecessor are outside this stage.

## 2. Sources and scope

Add two variables to `global_variables.json`; resolve paths relative to `STELLARIS_ROOT`:

| Database / `dataset.kind` | Variable | Default value |
| --- | --- | --- |
| `technologies` | existing `TECH_PATH` | `common/technology` |
| `components` | new `COMPONENTS_DIR` | `common/component_templates` |
| `buildings` | new `BUILDINGS_DIR` | `common/buildings` |

Each database independently configures its directory variable, filename pattern, recursion and encoding. Defaults: `*.txt`, recursive traversal, `utf-8-sig`. Shared inline, scripted effect/trigger/value and static-variable libraries use existing settings and do not become independent objects in these databases.

Game and Workshop inputs remain read-only. `WORK_DIR` specifies the working directory. Do not copy source directories or resolve arbitrary paths outside permitted sources.

Weapon-stat CSV/ODS files in `component_templates` are outside this stage. The component database contains TXT definitions sufficient for IDs, technology requirements and upgrades; completeness of all combat statistics is not claimed. The `component_sets` directory is not added as another source: shared descriptions are looked up using the explicit `component_set` field value in a component.

Pre-implementation research: `data/stage11/specification_research/object_inventory.json`. Direct parsing of 83 component/building files identified three component template types, 498 building definitions and 9 buildings with `desc` blocks. Some component IDs are supplied by inline calls. These counts are not a baseline for fully expanded output and must not be hardcoded.

## 3. Configuration and outputs

Extend `config/backend.json`: declare shared parser settings once; a `datasets` section contains named source and output sets. Do not copy parser configurations for each database type. A set coordinator passes per-run parameters to the shared builder.

Recommended outputs relative to `WORK_DIR`, configurable:

| Kind | Database | Parsing report | Localization report |
| --- | --- | --- | --- |
| `technologies` | `databases/technologies.json` | `reports/technologies_build.json` | `reports/technologies_localization.json` |
| `components` | `databases/components.json` | `reports/components_build.json` | `reports/components_localization.json` |
| `buildings` | `databases/buildings.json` | `reports/buildings_build.json` | `reports/buildings_localization.json` |

The aggregate report is `reports/database_set.json`, also configurable. Paths must be distinct, remain inside the permitted working directory and not overlap inputs, configuration or code.

Keep shared languages, priorities, reading and reference expansion in `config/enrichment/localization.json`. Separate target selectors and key rules by object kind; the coordinator provides database and report paths. Root construct types, ID fields, description suffixes and allowed `component_set` use belong in configuration.

## 4. Format and set membership

Proposed format: `sttv.parse_database`, version 5. Game nodes and entry order are preserved. Add a root marker:

```json
{
  "format": "sttv.parse_database",
  "format_version": 5,
  "dataset": {
    "kind": "technologies",
    "set_id": "<sha256>"
  },
  "documents": []
}
```

The three files have different `kind` values and the same `set_id`. Filenames do not determine roles. `set_id` identifies specific set contents, not a Stellaris version or validation of game semantics.

For determinism, after enrichment compute SHA-256 for each database document without its root `dataset`, then SHA-256 of the `kind -> hash` dictionary. Canonical serialization for both steps is UTF-8 JSON with sorted keys, no separator whitespace, no ASCII escaping of Unicode and no NaN/Infinity. Exclude timestamps, absolute environment paths and reports. Identical results yield identical `set_id` values and database files.

The general-purpose low-level builder may produce standalone trees without `dataset`; it is not coupled to three game directories. The new frontend accepts only a complete marked set. Automatic migration of the previous single database is unnecessary: rebuild the set for the new interface.

## 5. Building and publication

One explicit Python command builds the complete set. Proposed entry point: `python -m sttv.database_sets`, accepting variable and configuration paths; document the exact invocation in the implementation guide. Parsing and enrichment remain separate functions usable in independent checks.

1. Validate configuration, sources and outputs for all three databases.
2. Run the existing complete pipeline for each dataset: nested inline expansion, scripted effects/triggers, script values and static-variable substitution in the established order. Preserve provenance and service metadata according to existing stages.
3. Enrich every selected target in RU/EN. The localization index and immutable shared data may be reused; document-local variables and expansion contexts must not leak between documents.
4. Validate schemas, enrichment integrity and unchanged inputs across the entire run, including shared files read by different builds. Different hashes for one source block publication.
5. Prepare all three outputs in temporary working-directory files, compute `set_id`, and validate final files.
6. Publish prepared databases and write the aggregate report with actually written outputs.

Existing databases are not replaced until the entire set is prepared and validated. Replacement of one file is atomic using the existing mechanism; replacement of three files is not described as a single atomic operation. If publication fails between replacements, the report records partial publication and mismatched `set_id` values prevent the frontend from opening a mixed set. Do not introduce a separate rollback mechanism.

Avoid holding three unnecessary copies of full trees simultaneously; sequential preparation through temporary outputs is acceptable. Rewriting an aggregate report must not conceal completed writes after a failure.

The existing separate single-file enrichment operation must not silently modify a member of a finished set while preserving its previous `set_id`. For these files, report that the set must be rebuilt. Standalone databases without `dataset` remain accessible to low-level operations; refreshing only localization of a finished set without reparsing may be designed separately.

## 6. Localization target selection

Select targets after expansion; the original tree is not restricted to the listed fields.

| Target | Identifier / name key | Primary description key |
| --- | --- | --- |
| Technology | root definition key | `<id>_desc` |
| `technology_swap` | direct `name` field | `<name>_desc`, then base description under stage 10 rules |
| Component | direct `key` field | `<key>_DESC`, then `<component_set>_DESC` under section 7 |
| Building | root definition key | `<id>_desc`; explicit `desc` entries follow section 7 |

Select components from root `weapon_component_template`, `utility_component_template` and `strike_craft_component_template` assignments; configure this list. These construct names repeat and are not component IDs. Do not use a nested aura's `name` as the component name.

Select root building definitions in their configured directory. Comment documents, scalar directives and variables are not localization objects. Main technology selection preserves the existing exclusion of category/tier subdirectories from localization targets, although their trees remain in the database.

A primary object requires one nonempty scalar ID and unambiguous fields used to select keys. Selection errors carry locations. Do not merge duplicate object IDs within a kind: report an error for manual investigation. IDs in different kinds occupy separate namespaces.

## 7. Descriptions and string provenance

Priorities remain unchanged: RU uses `RU_LOC_TIER_1`, then 2 and 3; EN uses `EN_LOC_TIER_1`. Each key lookup traverses all priorities for that language. Missing Russian text does not trigger English substitution. A found empty string differs from an absent entry.

Preserve `requested_key`, selected `key`, `raw`, expanded `text`, `source`, `inherited_from` and `unresolved_references`. Expand static `$key$` references; retain game runtime substitutions and formatting. Missing entries, conflicts, cycles and expansion limits follow stage 10.

**Components.** If `<key>_DESC` is absent from every language tier and direct `component_set` is one nonempty scalar, look up `<component_set>_DESC`. This is a shared-description rule, not technology-family inference. For example, `SMALL_RED_LASER` references `RED_LASER`, which has `RED_LASER_DESC`. Do not strip size prefixes or numeric suffixes from IDs. Names use the component's own `key`.

For this case, add an optional string-record field `fallback`: `{ "kind": "component_set", "source_ref": "<JSON Pointer to component_set assignment>" }`. `requested_key` retains the first requested key, `key` identifies the actual match, and `inherited_from` stays `null`. Validation checks that the reference addresses this component's field and matches the selected key. Omit `fallback` for direct selection and inherited technology descriptions. A found empty description is not replaced with a shared description.

**Buildings.** The main description uses `<id>_desc`. A single direct scalar `desc`, if present, explicitly replaces this key. For repeated `desc = { trigger = ... text = ... }` blocks, localize every direct scalar `text`, preserving order and conditions in the original tree. Do not evaluate `trigger` or designate the first conditional variant as active.

Attach conditional description translations to the `desc` assignment itself at `enrichments.localization.<language>.description`. Such targets have no localized name field. The schema permits description-only targets; both fields in each language remain required for primary objects and technology variants. Preserve the main `<id>_desc` independently of conditional descriptions; record a missing key as missing. Incompatible mixed `desc` forms, ambiguous `text`, or an unsupported selection construct produce diagnostics without invented descriptions.

## 8. Diagnostics and validation

The aggregate report contains status, `set_id` when computed, input configuration and source hashes, three output paths, separate parsing/localization/publication statuses, object/string counts by kind/language, errors and warnings. Timing and memory measurements belong only in reports. Diagnostic references include database kind and node path.

Parsing errors, ambiguous IDs or keys, conflicts in selected localization and input changes block set publication. Missing text and retained dynamic references remain reported warnings under stage 10 rules. Code error messages are English; frontend-facing messages use interface localization.

The backend validates saved trees and enrichment. It does not evaluate chain rules, primary-predecessor suitability or country state. Preparing object references for the frontend is specified separately.

## 9. Code organization

Add a compact set coordinator; reuse `builder`, `database`, `sources` and `enrichment/localization`. Extract shared publication/report helpers only where logic actually repeats. Do not create copies of the parser or localizer for each database kind.

Update schema generators for the database, build configuration, localization and affected reports; provide a separate generated aggregate-report schema. Do not edit generated schemas independently of their source. Follow existing file-size and DRY rules.

## 10. Acceptance criteria

1. A configurable command creates three valid localized JSON files with correct roles and a shared deterministic `set_id`.
2. Standard nested expansion and static substitution work in all three; preserve fields, ordering, unknown game constructs and provenance.
3. Check component IDs supplied by inline calls, repeated root template names, separate ID namespaces and diagnostics for actual duplicate IDs.
4. Verify RU/EN and source priorities for every kind, `_desc` versus `_DESC`, shared component descriptions, empty/missing strings and conditional building descriptions without condition selection.
5. Enrichment changes only service fields; technology variants and inherited descriptions preserve their behavior.
6. Repeating unchanged inputs yields byte-identical databases. Changing any member's contents changes the shared `set_id`.
7. Test unavailable sources, failure in the third database after preparing the first two, changes to shared inputs, and publication failure between files. Reports reflect actual outcomes, and the frontend detects mixed sets.
8. A real run over the three directories records sizes, time, object counts, warnings and unchanged source hashes. Pre-expansion research counts are not expected final totals.
9. Update the invocation guide, RU/EN changelog and document links. Report only executed checks; launching the game is not required to validate these database formats.

## 11. Related documents

- [Stage 10: technology localization](TZ_BACKEND_STAGE_10_EN.md).
- [Frontend stage 2: three-database opening and links](frontend/TZ_FRONTEND_STAGE_2_EN.md).
- [Ambiguous chain research](frontend/RESEARCH_AMBIGUOUS_CHAINS_EN.md).
- [Chain and sorting rules](frontend/TECHNOLOGY_CHAINS_AND_SORTING_EN.md).

[Русская версия](TZ_BACKEND_STAGE_11_RU.md).
