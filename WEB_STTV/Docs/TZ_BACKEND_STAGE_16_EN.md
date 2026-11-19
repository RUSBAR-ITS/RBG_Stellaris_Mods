# Stage 16 — technology parent and child enrichment

## Contents

- [1. Status and objective](#1-status-and-objective)
- [2. Scope](#2-scope)
- [3. Inputs and operation configuration](#3-inputs-and-operation-configuration)
- [4. Extensible rules](#4-extensible-rules)
- [5. Combination and selected variants](#5-combination-and-selected-variants)
- [6. Analytical technology representation](#6-analytical-technology-representation)
- [7. Parent and child calculation](#7-parent-and-child-calculation)
- [8. Per-object result](#8-per-object-result)
- [9. Shared combination metadata](#9-shared-combination-metadata)
- [10. Identity and freshness](#10-identity-and-freshness)
- [11. Reading and publication](#11-reading-and-publication)
- [12. Operation interface](#12-operation-interface)
- [13. Diagnostics and report](#13-diagnostics-and-report)
- [14. Modules and schemas](#14-modules-and-schemas)
- [15. Tests and acceptance](#15-tests-and-acceptance)
- [16. Deliverables](#16-deliverables)

## 1. Status and objective

**Approved by the user and implemented on 2026-11-19.** This document specifies the [agreed approach](TECHNOLOGY_TREE_ENRICHMENT_EN.md). Running, result format and verification results are described in the [stage 16 guide](BACKEND_STAGE_16_EN.md).

Using an existing database set, calculate each technology's parent and immediately extend the parent's child list. Store results inside the technology database as object enrichment for named combinations. The initial supplied combination is the reference view with base representations and the agreed conventional empire profile.

Criteria are grounded in the [complete analytical pass](frontend/CHAIN_RULES_FULL_REVIEW_EN.md). Research scripts and reports provide porting material and verification data; the product must not import code from `data` or substitute recorded research decisions for calculation.

## 2. Scope

Includes a standalone Python operation, separate rule configuration, combination parameters, evidence extraction from prepared databases, manual variant selection support, persistence, freshness checks, a diagnostic report and a noninteractive CLI.

Excludes the grid, `location`, visual child ordering, HTTP API, frontend changes, generation on startup, MongoDB and storage migration. Event-based acquisition remains deferred; previously agreed weapon function analysis through actions and events remains included.

The operation does not change game files, the parser, insertion libraries or original technology requirements. No new game-command allowlist, arbitrary empire-state interpreter or manual parent overrides are introduced.

## 3. Inputs and operation configuration

Input is the current set of 15 `sttv.parse_database` databases with `format_version = 6`. Files must have distinct expected `dataset.kind` values and the same `dataset.set_id`. Missing files, mismatched sets or unsupported formats fail before publication.

Separate configuration `config/enrichment/technology_tree.json` contains:

| Field | Purpose |
| --- | --- |
| `format`, `format_version` | `sttv.technology_tree_config`, version 1 |
| `backend_config` | Reference to `config/backend.json`; use database output paths without invoking a build |
| `dataset_registry` | Reference to `config/datasets.json` for object kinds and ID extraction |
| `technology_targets` | Reference to `config/enrichment/targets/technologies.json` to select technology documents |
| `rules` | Reference to `config/enrichment/technology_tree/rules.json` |
| `combination` | Reference to `config/enrichment/technology_tree/combinations/reference_default.json` |
| `report` | `reports/technology_tree.json` relative to `WORK_DIR` |
| `staging_directory` | `staging/technology_tree` relative to `WORK_DIR` |

Configuration references use the existing `base`/`path` format. Working paths are configurable through `WORK_DIR`; machine-specific absolute addresses are absent from code. Loading settings does not check game directories, invoke the builder or localizer, or prepare libraries.

Provide a separate profile at `config/enrichment/technology_tree/profiles/reference_empire.json`. Mapping values, functional groups, object traversal directions and profile facts reside in configuration rather than Python lists of specific technologies.

## 4. Extensible rules

`rules.json` has `format = sttv.technology_tree_rules`, `format_version = 1`, a `rules` array and a `definitions` dictionary of reusable blocks. Array entries contain a unique `id`, `enabled` and `parameters`; array order defines execution order. `parameters` contains handler parameters directly or a single `definition_ref` field naming a `definitions` block. The reference replaces the entire parameter object without overrides or reference chains; validate the block against the consuming handler's schema. Arbitrary expressions and executable text are forbidden.

Supplied order and content:

| ID | Criterion and configurable information |
| --- | --- |
| `normalized_id` | Equal IDs after removing digits `0–9`; do not discard other ID parts |
| `same_area` | Matching effective research area |
| `same_category` | Nonempty intersection of effective research categories |
| `mandatory` | Mandatory technology requirements before alternatives |
| `direct_upgrades` | Direct object upgrades; configure kinds, fields and direction |
| `same_potential` | Complete structural equality of nonempty base `potential`, ignoring node provenance |
| `functional_groups` | Mobile combat ship, planet class change, anti-ship weaponry |
| `direct_relations` | Agreed direct functional object relations |
| `indirect_affinity` | Affinity through candidate prerequisites; initial depth 1 and configured effect fields |
| `production_affinity` | Own production bonus → economic category → job → provider building |
| `capacity_affinity` | Own capacity bonus → capacity-consuming object → linked hull → required technology |
| `standard_empire` | Exclude candidates contradicting known profile facts |
| `highest_tier` | Highest game `tier` among remaining candidates |

Retain exact evidence boundaries from the [complete pass](frontend/CHAIN_RULES_FULL_REVIEW_EN.md), [direct upgrades](frontend/CHAIN_DIRECT_UPGRADES_EN.md), [conditions](frontend/CHAIN_AVAILABILITY_EN.md), [functional groups](frontend/CHAIN_FUNCTIONAL_GROUPS_EN.md), [direct relations](frontend/CHAIN_DIRECT_RELATIONS_EN.md), [indirect affinity](frontend/CHAIN_INDIRECT_AFFINITY_EN.md), [production](frontend/CHAIN_PRODUCTION_AFFINITY_EN.md), [capacity](frontend/CHAIN_CAPACITY_AFFINITY_EN.md) and [weaponry](frontend/CHAIN_WEAPONRY_EN.md). Do not silently expand traversal depth or mapping semantics while porting.

The engine dispatches handlers by known ID. Each handler receives current candidates and returns a matching subset, evidence references and applicability state. A new mapping of a supported type is configurable; a fundamentally new calculation requires a handler and parameter definitions in the schema generator. Unknown IDs, duplicates, unresolved block references and invalid parameters are configuration errors, including for disabled rules.

Evidence counts are not votes. Conditional bonuses and relations retain conditions and scope rather than becoming unconditional. If applicability is unknown for some current candidates and prevents a valid comparison, the criterion does not reduce the set and records diagnostics. The exception is the defined `standard_empire` semantics: remove only confirmed incompatibilities and retain unknowns. This interprets used fields, not validates every game command.

## 5. Combination and selected variants

A combination file has `format = sttv.technology_tree_combination`, `format_version = 1`, and fields `id`, `mode`, `profile`, `variants`. `id` follows `^[a-z][a-z0-9_]*$`; initial values are `reference_default` and `reference`. This stage supports only `reference` mode.

`profile` references a facts file. The supplied profile is non-nomadic, non-gestalt, with biological founders and conventional ships. Other ethics, origins, DLC and development paths remain unknown. Use the agreed three-valued condition interpretation and `country`/`founder_species` scopes; unfamiliar predicates and scope transitions do not become false.

A profile file has `format = sttv.technology_tree_profile`, `format_version = 1`, `id` and `facts`. Fact structure is scope → predicate → string argument value → boolean result. Missing facts mean unknown. Port initial facts from the verified research profile; do not port historical criterion lists or manual technology pairs from research materials.

`variants` maps base technology IDs to `base` or `swap:N`, where N starts at 1 and follows `technology_swap` order, matching the current frontend. Omitted technologies use `base`; normalize the selection for every technology before hashing and saving. Unknown technologies or variants are request errors. Manual selection does not require the variant's game `trigger` to pass and does not automatically select variants from empire state.

The combination ID is a named result slot. Changing its parameters replaces that result after successful calculation; a different combination uses another ID. Store only requested combinations. A matching mode name without matching inputs and parameters does not permit reuse.

## 6. Analytical technology representation

Select technologies from target top-level definitions containing a game `tier`; research category and tier definitions are not technologies. The definition key supplies the ID. Duplicate technology IDs are forbidden. Related object references use database kind and ID; provenance uses database kind and JSON Pointer. Ambiguous resolution of a used reference is an error, without first-match selection.

Base ID, game `tier`, `prerequisites` and base `potential` remain unchanged under variant selection. Variant `area` and `category` replace those values when present and otherwise inherit them. Preserve `technology_swap.trigger` as a representation condition without automatically adding it to base `potential`.

Own-effect criteria account for `inherit_effects`: `yes` permits base effects together with variant effects; `no` excludes base effects from this comparison. Related object game requirements continue to reference the base ID. Do not extend effect inheritance to every technology field automatically.

**Approved missing `inherit_effects` policy:** the inspected projection has 23 of 206 variants without it. Without a confirmed default, treat inheritance as unknown; a dependent criterion does not narrow candidates and emits `variant_effects_unknown`. Likewise, do not guess the final numeric result of conflicting entries for one modifier. ID, area, category and other independent criteria continue to work. Do not infer defaults from technology names. This policy was approved with the specification.

Preserve original AND/OR requirements. Candidate IDs are the union of all referenced IDs; mandatory requirements are the ID for a leaf, union for AND/implicit lists, and intersection for OR. An empty prerequisite list means a root. Unknown IDs, empty OR or unsupported constructs produce errors; retain the previously agreed stop on NOT/NAND/NOR technology requirements. Logical `potential` conditions are handled separately.

## 7. Parent and child calculation

Before selection, all objects are available by ID with effective representations and empty child lists for this calculation. Process deterministically by base ID:

1. No candidates means `root`; one means `resolved` without running criteria.
2. For multiple candidates, apply enabled criteria to the current set. Nonempty matches replace it; empty matches are skipped; eliminated candidates never return.
3. Stop once a single candidate remains. Multiple candidates after exhausting criteria mean `ambiguous`, without assigning a parent.
4. Immediately store a selected `parent_tech` and append the technology ID to that parent's `children`, excluding duplicates. Processing the parent later preserves accumulated children.

No separate reverse-link construction pass is needed. Final checks and canonical list ordering are allowed. JSON `children` are ordered by ID for reproducibility; this is not alphabetical card ordering or a placement rule.

A selected parent must be an original direct prerequisite. All other game links remain intact. Parents from another area or a higher game tier are allowed; record this in the report rather than modifying tiers. Check relationship reciprocity and absence of cycles. Cycles or reciprocity violations fail publication; ambiguity is a valid result with a warning.

## 8. Per-object result

Use `enrichments.technology_tree[combination_id]` on the base technology node. A variant creates neither a new technology nor a separate tree node. The record contains only:

| Field | Value |
| --- | --- |
| `parent_tech` | Immediate parent ID or `null` |
| `children` | Unique IDs of technologies selecting this object as parent |
| `status` | `root`, `resolved` or `ambiguous` |

For `root` and `ambiguous`, the parent is `null`; absence of requirements and unresolved selection remain distinct. Technologies in any state may have children. Traces and evidence belong to the report, and combination parameters are not duplicated per technology. `location` is absent at this stage.

Illustrative node fragment omitting its existing localization:

```json
{
  "enrichments": {
    "technology_tree": {
      "reference_default": {
        "parent_tech": "tech_a",
        "children": ["tech_c"],
        "status": "resolved"
      }
    }
  }
}
```

## 9. Shared combination metadata

Add optional root `technology_tree` to the technology database, with `format_version = 1` and a `combinations` dictionary. Each combination stores:

- `mode`, full normalized `parameters` containing profile facts and variant selections;
- `source_set_id`, `inputs` listing database kind, hash algorithm and hash, and `input_revision`;
- full applied `rules_snapshot`, `rules_revision`, `parameters_revision`, `implementation_revision`;
- `calculation_revision`, `result_revision`.

Source object JSON Pointers do not change. Publish combination metadata and node records together in one file. Parameters and revisions exclude execution times, absolute paths and random identifiers; times and working paths belong to the report. Database format remains 6: this is optional enrichment version 1, not an AST replacement. Other database kinds do not receive technology tree records.

Per-object results follow the future rule of one technology, building or other object per MongoDB document. References contain IDs without embedded object copies. No new storage abstraction or MongoDB preparation is required now.

## 10. Identity and freshness

Retain `dataset.set_id` as the identity of the original published set. Do not recompute it from enriched files. Actual inputs and results have separate revisions; matching headers alone cannot establish reuse eligibility.

For the technology database, compute the source digest using the existing `sttv.document_hashes.v1` algorithm, excluding only root service metadata `technology_tree` and node `enrichments.technology_tree`. Also exclude an empty `enrichments` container created solely by this enrichment. Do not remove a game field with the same name: exclusions target structural service paths rather than script strings. Localization, original AST, provenance and document order remain in the input digest.

For the other 14 databases use streaming SHA-256 over actual bytes, algorithm `sha256.file.v1`. `input_revision` is the canonical SHA-256 of this kind-sorted input inventory and `source_set_id`. Formatting another input file may conservatively cause recalculation; changing only tree enrichment must not change the input revision.

`rules_revision` hashes the fully resolved rule and mapping configuration. `parameters_revision` hashes mode, profile facts and the complete variant selection. `implementation_revision` is an explicit code version for calculation semantics, changed when handlers or evidence extraction change results. Configuration paths do not replace content hashes.

`calculation_revision` hashes the input, rule, parameter and implementation revisions. `result_revision` hashes this revision and the sorted technology ID-to-result mapping. Canonical JSON uses existing sorted-key, UTF-8 and compact separator settings and rejects NaN/Infinity.

A matching `calculation_revision` plus successful result checks permits reuse. Otherwise calculate a new result for the requested combination. Preserve other combinations, whose freshness depends on their own revisions. Changed source data must not leave an older combination declared current merely because its record remains present.

The builder continues producing source sets without automatically calculating relationships. Historical build reports describe the original publication; the new report records actual file hashes before and after enrichment. Do not rewrite historical reports to claim the file was unchanged.

## 11. Reading and publication

Read existing JSON directly. Do not load the events database in full with `json.load`: it exceeds 9 GB. Extract needed objects sequentially, release unnecessary ASTs and retain compact evidence indexes. For weaponry, follow only the agreed explicit action and event routes. JSON reading must handle strings and escaping correctly; an arbitrary ID text match is not evidence of a relationship.

For an unchanged combination, input hash and stored result checks suffice; rebuilding all functional evidence is unnecessary. During calculation, prepare indexes once per operation and share them across criteria. New persistent projection caches and new parallelism are out of scope.

Prepare results in memory or the working directory while preserving the current database until checks finish. Publish only the changed technology database through a temporary file beside its destination and atomic replacement. JSON remains formatted with two-space indentation, UTF-8 and actual line breaks.

When replacing a combination, remove its old records, including those on objects no longer selected, and attach a complete new result. Preserve other combinations and localization. Metadata and objects must not mix old and new versions of the same combination.

Before replacement, ensure input files and configurations still match the operation snapshot. Prevent concurrent publication to one database using a destination lock and snapshot freshness check. Preparation, reading, validation or write errors preserve the old database; clean up temporary files. Combine checks and hashing with reading where possible and account for additional passes in metrics.

## 12. Operation interface

Expose `enrich_technology_tree(variables_path=None, config_path=None, combination_path=None, *, recalculate=False)` from `sttv.enrichment.technology_tree`. Defaults use product global variables, the operation configuration and its referenced combination. Explicit `combination_path` overrides only combination request selection.

`recalculate=False` permits reuse of a current result, otherwise calculation proceeds. `recalculate=True` forces calculation of the selected combination. Even forced calculation need not rewrite the file when the complete canonical result matches and has been checked.

The function returns a report rather than the full AST. CLI `python -m sttv.enrichment.technology_tree` supports `--variables`, `--config`, `--combination`, `--recalculate`, without interactive questions. Exit code 0 means success including warnings; errors use a nonzero exit code.

Transport is outside the function. HTTP API, mapping browser-selected files to a server set, a recalculation button and UI refresh belong to a separate stage.

## 13. Diagnostics and report

The report has `format = sttv.technology_tree_report`, `format_version = 1`, `status` (`success`, `success_with_warnings`, `failed`), `action` (`reused`, `computed` or `null` for incomplete calculation), `database_written`, working paths, combination and rule snapshots, input and output revisions, counts and stage timings.

For each technology retain original candidates, mandatory IDs, selected variant, state, parent and the actual criterion trace: before, matches, after, skip reason and evidence references. Do not fabricate steps after finding a unique candidate. Unknown effect inheritance, ambiguity and conditional evidence must remain distinguishable.

For ambiguities apply the [agreed log contents](frontend/CHAIN_AMBIGUITIES_EN.md): complete calculation context, remaining candidates, settings and sources. Since UI integration is absent, do not invent window dimensions or scrolling; mark them as not supplied. An ambiguous result may be published with `success_with_warnings`.

Errors include invalid settings or variants, incomplete sets, conflicting IDs or reference resolution, missing technology prerequisites, unsupported requirements, cycles, reciprocity violations, changed inputs and write failures. Publication errors cannot report `database_written = true`. Report-write failure after successful database replacement is recorded separately while retaining the true completed-publication flag.

## 14. Modules and schemas

Add `src/backend/sttv/enrichment/technology_tree/` separating settings, reading/indexes, representations, evidence, criterion handlers, selection, attachment, revisions, reporting and orchestration. Share repetitive logic through helpers. Aim for files below 200 lines; files above 300 require splitting except justified indivisible blocks.

Add generators for `technology_tree.schema.json`, `technology_tree_rules.schema.json`, `technology_tree_combination.schema.json`, `technology_tree_profile.schema.json`, `technology_tree_report.schema.json`. Extend `database.schema.json` generation with optional metadata and object enrichment, and structural checks with relationship and revision integrity. Do not hand-edit schemas.

Check prepared input set format and structures needed by analysis; repeated full AST JSON Schema validation and reparsing game files are unnecessary. Strictly check new configurations, enrichment and its references. Retain stage 13–15 optimizations and one source for structural validation rules. Do not add frontend dependencies to the calculation module.

## 15. Tests and acceptance

Synthetic checks:

1. Roots, unique and multiple parents; AND/OR and mandatory intersections; empty-result skipping, stopping at one candidate, disabled and reordered rules.
2. Parents processed after children; multiple children; no duplicates; reverse traversal produces the same links; structural list order is independent of RU/EN.
3. Ambiguity logging, missing prerequisites, conflicting IDs, cycles, unsupported requirements and unknown rules. Errors preserve previous results.
4. Area/category changes in child and candidate variants, preserved base IDs and requirements; yes/no/missing `inherit_effects`; conditional and unknown evidence.
5. Enrichment-only changes leave input revision intact; AST, other input files, rules, profiles, variants or implementation changes invalidate reuse. Corrupted results are not reused.
6. Repeated execution, forced recalculation, preserving a second combination and localization, removing obsolete children after parent changes, no partial result under errors or concurrent invocations.
7. Streaming large JSON, braces and escapes inside strings; unchanged other 14 files; schema generation and existing backend tests relevant to the change.

Run actual-data checks using a working technology database copy under `WORK_DIR/stage16`, preserving the reference until verification. A separate acceptance configuration points to this copy and the other 14 source databases as read-only inputs; copying every large file is unnecessary. Do not regenerate game data.

For the base combination on the researched set, expect **679 technologies: 178 roots, 501 selected parents (412 with one original requirement and 89 with multiple), 0 ambiguities and 0 cycles**. Compare all decisions and 12 control examples with the [reference report](../data/chain_analysis/final_review/report.json). Verification reads the reference after calculation; selection cannot access expected pairs. Investigate mismatches instead of masking them with manual corrections.

Using indexes prepared once, check all 206 variants individually and several combinations, including the seven changing area/category. Variant checks cover invariants, unknown-state diagnostics and reproducibility; zero ambiguity is not promised for them. Separately verify saving and reopening at least the base combination and one changed combination.

Record reading/hashing, index preparation, criterion, validation, writing and reuse timings, plus bytes read and written. No speedup factor is promised in advance. Tests do not evaluate actual empire availability and do not replace in-game verification.

## 16. Deliverables

Deliver the Python module and CLI, rule/profile/base-combination configurations, generated schemas, tests, an enriched working database, report and bilingual implementation guide. Update README, specification index, approach and changelog for actual changes. The frontend keeps its existing behavior until a separate integration stage.

[Agreed approach](TECHNOLOGY_TREE_ENRICHMENT_EN.md) · [Specification index](TZ_EN.md) · [Русская версия](TZ_BACKEND_STAGE_16_RU.md).
