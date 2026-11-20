# Stellaris Technological Tree View — stage 12 specification: extended database set

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Members and sources](#2-members-and-sources)
- [3. Configuration and format](#3-configuration-and-format)
- [4. Parsing and identity](#4-parsing-and-identity)
- [5. Localization](#5-localization)
- [6. Building and JSON output](#6-building-and-json-output)
- [7. Known obstacles](#7-known-obstacles)
- [8. Verification and acceptance](#8-verification-and-acceptance)
- [9. Related documents](#9-related-documents)

## 1. Status and scope

Approved by the user on 2026-11-18. Implementation and acceptance checks are complete. The full set was built and opened in the browser; results are recorded in the [stage guide](BACKEND_STAGE_12_EN.md). The user selected 12 additional databases, RU/EN localization, and frontend opening of the complete set. The user also requested multiline JSON output.

The deliverable is a set of 15 databases: existing technologies, components and planetary buildings plus the sources in section 2. Each retains universal parser output and enrichments. New technology chain selection rules, evaluation of game conditions and event execution are outside this stage. Detailed behavioral reference graph extraction will be designed separately; definitions and references are retained now.

Backend and frontend share the set contract; interface changes are specified in [frontend stage 3](frontend/TZ_FRONTEND_STAGE_3_EN.md). Backward compatibility with three-file sets is not required.

## 2. Members and sources

Keep existing `technologies`, `components`, `buildings` and their variables. Add one variable per new database to `global_variables.json`; values are relative to `STELLARIS_ROOT`.

| `dataset.kind` / JSON basename | Variable | Directory | TXT files in the inspected installation |
| --- | --- | --- | ---: |
| `megastructures` | `MEGASTRUCTURES_DIR` | `common/megastructures` | 30 |
| `ship_sizes` | `SHIP_SIZES_DIR` | `common/ship_sizes` | 40 |
| `starbase_levels` | `STARBASE_LEVELS_DIR` | `common/starbase_levels` | 8 |
| `starbase_modules` | `STARBASE_MODULES_DIR` | `common/starbase_modules` | 10 |
| `starbase_buildings` | `STARBASE_BUILDINGS_DIR` | `common/starbase_buildings` | 4 |
| `terraform` | `TERRAFORM_DIR` | `common/terraform` | 3 |
| `deposits` | `DEPOSITS_DIR` | `common/deposits` | 26 |
| `pop_jobs` | `POP_JOBS_DIR` | `common/pop_jobs` | 22 |
| `economic_categories` | `ECONOMIC_CATEGORIES_DIR` | `common/economic_categories` | 8 |
| `scripted_actions` | `SCRIPTED_ACTIONS_DIR` | `common/scripted_actions` | 6 |
| `on_actions` | `ON_ACTIONS_DIR` | `common/on_actions` | 4 |
| `events` | `EVENTS_DIR` | `events` | 171 |

332 physical TXT files were inspected, including empty and documentation files. This is neither an object count nor a program constant. Initial syntax research without call expansion: `data/stage12/specification_research/source_inventory.json`.

Defaults per kind: `*.txt`, recursive, `utf-8-sig`; all configurable. Outputs relative to `WORK_DIR`: `databases/<kind>.json`, `reports/<kind>_build.json`, `reports/<kind>_localization.json`; aggregate report: `reports/database_set.json`. The aggregate report is not a sixteenth database.

Game and Workshop inputs remain read-only. No game directory copies are required. Shared inline/script/variable libraries retain their existing role and do not become extra databases. Do not add `starbase_types` or other unlisted directories.

## 3. Configuration and format

Extend the existing set coordinator. Move supported roles to a small shared `config/datasets.json` used by the backend, schema generator and frontend instead of duplicating 15-item constants. Sources and destinations remain in `config/backend.json`; localization rules remain in `config/enrichment/localization.json`.

Separate configurable object selection, ID fields and localization key rules by kind. Do not create one builder per directory. Split large configuration sections into explicitly referenced files if necessary; do not introduce an arbitrary code execution language in JSON.

Use `sttv.parse_database`, new version `6`, reflecting expanded roles and localization targets. Each database retains `dataset = {kind, set_id}`. All 15 members share a `set_id` calculated from every member's content excluding root `dataset`, as in stage 11. Filenames do not determine roles. Regenerate schemas from their source code; validate the exact configured set membership.

The full `documents` tree remains the database foundation. Do not introduce a mandatory semantic game-command schema or discard unknown fields. Localization attaches to the relevant nodes separately from game content.

## 4. Parsing and identity

Reuse the existing order for inline expansion, scripted effects/triggers, script values and static variables. Preserve order, repeated constructs, conditions, scopes, provenance and metadata. Each document retains its own context.

| Definition kind | Identity |
| --- | --- |
| Named root blocks in new directories | Root key within the corresponding database namespace |
| Event | Direct `id` field; block type such as `country_event` is retained separately |
| `terraform_link` | Definition address in its database; `from` and `to` are properties, not a unique ID |
| `on_actions` | Handler name plus the address of every definition fragment |

The configured event root types exclude `namespace`, variables and nested event calls. Repeated event types are valid; actual duplicate event IDs receive diagnostics. Named singleton objects retain per-kind duplicate ID checks. Equal IDs in different databases do not conflict.

Keep every repeated `terraform_link`, including equal `from`/`to` pairs with different conditions. Do not invent game IDs or merge by planet-class pair. Preserve repeated `on_actions` fragments separately; do not select the first fragment or classify handlers as events. Never replace the source tree with a map that loses repetitions.

Root definitions must not be expanded as calls to identically named scripted effects/triggers. Where necessary, extend configured definition/body boundaries while still expanding actual calls inside definitions.

Action-to-handler and handler-to-event references remain references. Do not replace event calls with event bodies: this changes deferred execution, conditions and scope semantics. Retain these data for subsequent analysis.

## 5. Localization

Enrich after expansion. RU priority: `RU_LOC_TIER_1` → 2 → 3; EN: `EN_LOC_TIER_1`. Retain raw strings, statically resolved text, requested and actual keys, provenance and unresolved references. Keep dynamic substitutions and game markup. Empty strings differ from missing strings; do not substitute another language.

New target rules:

| Database | Name | Description and additional targets |
| --- | --- | --- |
| `megastructures` | `<id>` | `<id>_DESC` |
| `ship_sizes` | `<id>` | An explicitly declared description key if present; do not invent a mandatory suffix |
| `starbase_levels` | Direct `ship_size` value as the hull name key | Do not invent a level description |
| `starbase_modules`, `starbase_buildings` | `sm_<id>` | `sm_<id>_desc` |
| `deposits` | `<id>` | `<id>_desc` |
| `pop_jobs` | `job_<id>` | `job_<id>_desc` |
| `economic_categories` | `<id>` | An explicitly declared description if present; technical categories may have no text |
| `terraform` | Localize `from` and `to` values on their assignments | Endpoint class descriptions use `<class>_desc`; do not invent transition names/descriptions |
| `scripted_actions` | Direct `context_menu_name` | `tooltip` as description; localize `activity_key` separately on its assignment |
| `on_actions` | Only explicitly declared text fields under a rule | Technical handlers may have neither name nor description |
| `events` | Direct `title` | Direct `desc` and their textual variants; do not derive keys from event IDs |

Installed sources confirm these distinctions: `ring_world_1_DESC`, `sm_detection_array`, `job_foundry`, `starbase_level_outpost.ship_size = starbase_outpost`, and action `context_menu_name`/`tooltip`. Configure prefixes, suffixes and fields. Unsupported text-field shapes receive located diagnostics instead of arbitrary conversion.

Retain every event description: repeated scalar `desc`, blocks containing `text`, nested textual variants, their conditions and order. Localize only declared textual positions within descriptions, not arbitrary event-wide `text` fields. Do not pick the first variant as active or evaluate conditions. Hidden technical events may omit `title`/`desc`. Localizing event option buttons and every arbitrary effect message is outside this stage.

Enrichment schemas allow targets containing `name`, `description`, or both, without empty language objects. For each selected role retain both languages, including missing-key records. If a definition has no applicable text role, omit that field: this is not a missing translation. A technical database with zero localization targets succeeds and records a zero-target report.

Preserve existing technology, variant, component and building rules. Conditional strings attach to their own nodes; validate their addresses and key origins. Enrichment does not manually invent translations or fix game localization files.

## 6. Building and JSON output

One explicit `python -m sttv.database_sets` invocation prepares the whole set. Temporary outputs and reports reside in `WORK_DIR`. Process databases sequentially without retaining all 15 complete trees simultaneously. Immutable library and localization indexes may be reused without mixing contexts.

Validate all results, schemas, provenance and unchanged input hashes before publication. Failure while preparing any member leaves previously published databases untouched. Do not publish a partial database with omitted erroneous documents as complete. Individual file replacement is atomic; the entire set is not a single atomic operation. Failure between replacements records actual writes, while different `set_id` values prevent opening a mixed set.

All database and report JSON produced in this stage uses UTF-8 without BOM, two-space indentation, LF line endings, a final newline, and readable Unicode (`ensure_ascii=False`). The entire file, including `dataset`, remains formatted after adding membership metadata. Do not use the current compact-prefix insertion for final output.

Canonical compact serialization with sorted keys remains an internal hashing mechanism only. Output whitespace does not change `set_id` when data are unchanged. Fix final object-key order for reproducibility and preserve source array order. Do not reformat historical results or unrelated repository JSON.

## 7. Known obstacles

Initial syntax parsing of 332 TXT files succeeded in this research, but this was not a full expansion run. Historical `data/stage9/corpus_report.json` recorded seven problematic documents within the selected sources:

| Source | Recorded cause |
| --- | --- |
| `common/pop_jobs/06_event_jobs.txt` | `invalid_script_value_arguments` |
| `events/ancient_relics_arcsite_events_2.txt` | `unsupported_scripted_call` |
| `events/first_contact_dlc_operations_events.txt` | Missing `bonus` |
| `events/grand_archive_events.txt` | Missing `RELIC` |
| `events/leviathans_events_1.txt` | Missing `RELIC` |
| `events/nomads_origin_events.txt` | Missing `RANDOM` |
| `events/shroud_events.txt` | `ambiguous_static_environment` |

**Rechecked on 2026-11-18:** all seven files failed again with the same errors using the current parser. Six distinct causes were confirmed because two files share `RELIC`. Additional Shroud probes with three `TIER` values identified a limitation in our environment resolver despite the global variable being available. See the [recheck report](RESEARCH_STAGE_12_BLOCKERS_EN.md) for evidence and artifacts. Each document stopped at its first error; this run does not exclude later errors behind that point.

**User clarification after the recheck:** case-insensitive parameter names and conditional exceptions for `06_event_jobs.txt`, `grand_archive_events.txt`, `leviathans_events_1.txt`, `nomads_origin_events.txt` are agreed, including temporary `RANDOM = 0`. A separate [source_exceptions.json](../../Instruments/Stellaris_Parser/stellaris_parser/config/source_exceptions.json) is prepared; wiring, conditions and reporting are described in the [import addendum](SOURCE_IMPORT_EXCEPTIONS_EN.md). The implementation now loads this file through `parser.source_exceptions`. These transformations operate only in memory, preserving original data and provenance.

The addendum separately proposes removing the structural expansion restriction on `effect = no` while preserving the original invocation, and resolving a composed static variable when every environment finds the same declaration. Both changes were approved with this stage and implemented; structural expansion does not assert engine behavior for `no`.

Investigation and diagnostics are in scope; further arbitrary arguments, silently excluded files and installed-game changes are prohibited. Changes beyond the agreed rules require a separate decision. An unresolved complete-set blocker is an unfinished result, not successful acceptance. `VANILLA-002` already tracks the `RELIC` issue in the repository TO_DO; an import exception does not repair the installed game.

## 8. Verification and acceptance

1. Check 15 roles, variables and safe destinations; missing, duplicate and unknown roles. Roles agree across frontend and generated schemas.
2. Use small fixtures for new definition shapes, repeated event types with distinct IDs, real duplicate IDs, repeated transitions and handler fragments. Preserve all game nodes and ordering.
3. Check existing expansions inside new definitions and verify that events are not expanded as textual inserts. Run exception, case-policy and agreed-remedy checks from the [import addendum](SOURCE_IMPORT_EXCEPTIONS_EN.md#verification), then rerun the seven full problematic files.
4. Verify every key rule, RU/EN priorities, name-only/description-only targets, hidden events, zero targets, missing/empty strings and every conditional description without selecting an active one.
5. Check formatting of all 15 JSON files including `dataset`, and equivalent data after rereading. Repeated unchanged builds are byte-reproducible; a changed member changes the shared `set_id`.
6. Exercise late-member preparation failure, changed inputs and interrupted publication: no false complete success or lost diagnostics.
7. A successful full 15-database run records sizes, elapsed time, document/object/target counts, warnings and hashes of read inputs. Sources remain unchanged. Use formatted file sizes for frontend validation; do not assume the entire set fits browser memory before testing.
8. Building and opening the new complete set under the frontend specification are required for completion. If confirmed input errors or memory limits prevent this, record the concrete blocker and agree the required remedy.
9. Update invocation guides, README and RU/EN changelogs. Follow modularity, DRY and file-size rules from the general specification. Documentation changes are not implementation. Stellaris execution is unnecessary for JSON checks.

## 9. Related documents

- [Previous database-set stage](TZ_BACKEND_STAGE_11_EN.md).
- [Frontend stage 3](frontend/TZ_FRONTEND_STAGE_3_EN.md).
- [Technology chain rules](frontend/TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [General project principles](TZ_EN.md).
- [Repository TO_DO](../../TO_DO_EN.md).
- [Русская версия](TZ_BACKEND_STAGE_12_RU.md).
