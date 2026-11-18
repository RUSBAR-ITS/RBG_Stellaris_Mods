# Stellaris Technological Tree View — frontend stage 2 specification: three-database set

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Opening a set](#2-opening-a-set)
- [3. Worker and states](#3-worker-and-states)
- [4. Addressing and catalogs](#4-addressing-and-catalogs)
- [5. Localization](#5-localization)
- [6. Requirement and upgrade links](#6-requirement-and-upgrade-links)
- [7. Diagnostics](#7-diagnostics)
- [8. Configuration and modules](#8-configuration-and-modules)
- [9. Validation and acceptance](#9-validation-and-acceptance)
- [10. Related documents](#10-related-documents)

## 1. Status and scope

Approved by the user on 2026-11-17. Implementation and validation are described in the [frontend-stage-two guide](FRONTEND_STAGE_2_EN.md).

This stage adds joint opening of technologies, components and buildings, their catalogs, localization and explicit object links. The technology field retains its current display behavior. A new chain algorithm and sorting, field connection lines, building/component cards or screens, images and country-condition evaluation are outside scope. Rules L-01–L-08 remain requirements for future layout work.

This document replaces first-stage provisions for a single file and unqualified node references. Other UI kit, text, theme, language, tooltip, manual-variant and backend-responsibility requirements remain in effect.

## 2. Opening a set

Replace “Open database” with “Открыть набор БД” / “Open database set” in the menu. One UI-kit button invokes the standard multiple-file picker. The user selects exactly three JSON files: technologies, components and buildings. Selection order and filenames are arbitrary; each role comes from the file's `dataset.kind`.

A ready set requires:

- Every file uses `sttv.parse_database`, supported version 5.
- Each kind, `technologies`, `components` and `buildings`, occurs exactly once.
- All three share a nonempty `dataset.set_id` in the expected SHA-256 format.
- Adapter-required data can be prepared.

Missing files, repeated roles, unsupported format and mismatched sets are opening errors; do not enter partial mode or reuse an old member. The frontend does not automatically search adjacent files or open game directories. The set marker checks membership in one build result, not a cryptographic revalidation of all browser-side contents.

Application startup and page reload do not read databases or invoke Python, generation or localization. Opening reads only explicitly selected files. Dismissing the picker without selection preserves current state.

## 3. Worker and states

The opening command carries `operationId` and a `files` array instead of one `file`. One Worker reads and parses the selected files sequentially, releasing text after JSON parsing, identifies roles and invokes the set adapter. Full trees remain in the Worker; the main thread receives only prepared catalogs, indexes, links and diagnostics.

Keep phases `reading`, `parsing` and `preparing`; extend progress with file index, total count and role when known. The role can be unknown before reading. Link preparation starts after all three trees are read. Status-panel progress must be understandable, using localized phase names rather than internal technical identifiers.

Display the field only after one `ready` for the entire set. Do not publish partial catalogs on failure. Beginning a new operation after file selection releases the previous Worker and clears the old field under the existing replacement model. Do not automatically restore the previous set after failure.

“Retry” reuses the same three selected `File` objects. “Cancel” terminates the Worker, clears the operation and restores the initial state. Ignore stale `operationId` replies. Valid empty catalogs are not errors; no technologies produce the existing empty state regardless of component/building counts.

## 4. Addressing and catalogs

Separate game identity from node addresses:

```typescript
type SttvDatasetKind = 'technologies' | 'components' | 'buildings';
type SttvNodeRef = { database: SttvDatasetKind; pointer: string };
type SttvObjectRef = { database: SttvDatasetKind; id: string };
```

`pointer` is a JSON Pointer inside the relevant database. Identical IDs in different kinds and identical paths in different files do not conflict. Carry one `setId` in the result rather than copying it into every reference. Qualify backend-internal file references with the file's role during adaptation.

The ready result contains existing `technologies`, `links`, `localization`, `diagnostics` and new `setId`, `datasets`, `components`, `buildings`, `objectRequirements`, `objectUpgrades`, `upgradeEvidence`. `datasets` contains roles and selected-file information for messages and reports. Full ASTs are excluded.

| Catalog | ID | Minimum record |
| --- | --- | --- |
| Technologies | definition key | Existing technology/variant record with qualified `sourceRef` values |
| Components | direct template `key` | `id`, template type, `sourceRef`, `nameId`, `descriptionId`, `prerequisites` tree and its reference |
| Buildings | definition key | `id`, `sourceRef`, `nameId`, `descriptionId`, `prerequisites` tree and its reference, conditional descriptions |

A conditional building description contains its original `desc` reference, `descriptionId` and a `trigger` reference when present. Conditions remain in the Worker's tree and are not evaluated in the main thread. Do not introduce an active building description without separate agreement.

Identify primary objects using explicit directory/type settings and post-expansion fields. Repeated root `utility_component_template` assignments are valid; duplicate component `key` values are errors. Technology category/tier service definitions are not cards. Do not traverse expansion/localization metadata as independent game objects.

## 5. Localization

Build a shared RU/EN index using stored `requested_key` values across all three databases, including conditional building descriptions. The text contract remains source `database`, string ID and system language. Game object kinds do not become three new UI text sources.

In each record's `origins`, qualify `recordRef`, `inheritedFrom` and `fallback.source_ref` with the database role. Preserve the actual key, original text and translation source. Identical texts for one ID merge their origins; different found texts for the same ID/language produce an error with both origins, without choosing the first entry.

Handle description-only targets explicitly: do not require `name` for a conditional `desc`, but require both localization fields for a primary technology, variant, building and component. A correctly recorded missing translation is a warning; absent required enrichment is a preparation error.

The frontend does not reread game localization, expand `$key$` again, guess shared descriptions from IDs or interpret game formatting. Display names/descriptions as stored text under current requirements. Language switching uses the two already prepared indexes.

## 6. Requirement and upgrade links

Preserve three distinct data groups:

1. `links`: original technology prerequisites, as in stage one.
2. `objectRequirements`: technology requirements of components/buildings, including occurrence paths in logical trees. Direction: technology → requiring object.
3. `objectUpgrades`: explicit component → component upgrades through `upgrades_to`, or building → building upgrades through `upgrades`. Each entry retains qualified endpoints and references to source fields. Keep every listed building upgrade.

Absent or empty `prerequisites` mean no technology requirements. Preserve groups, order and operators of nonempty trees; collecting IDs does not make `OR` alternatives mandatory. Object requirements can be stored structurally without layout counting. For technologies, retain the previously agreed negative-requirement restriction until a separate sorting specification changes it.

`upgradeEvidence` contains separate evidence of possible technology continuations. At this stage, produce it only when both endpoints of an explicit upgrade have a simple list with exactly one scalar technology prerequisite, the technologies differ, and the source technology already occurs in the target technology's original `prerequisites`. Preserve the technology pair and object/field references supporting each witness.

For multiple requirements, logical alternatives or absent technology requirements, preserve the object upgrade without guessing a unique technology pair. Multiple witnesses for one pair form an evidence list, not multiple technology dependencies. Do not add `links` from evidence; area/category matching and primary-continuation selection belong to subsequent sorting work.

Acceptance example: `AFTERBURNER_1` → `AFTERBURNER_2` supports `tech_afterburners_1` → `tech_afterburners_2`; the `tech_thrusters_3` requirement remains an original additional link. Evidence alone does not reposition cards.

## 7. Diagnostics

Do not port JSON Schema, a full AST validator or the game parser into the frontend. Check the three file envelopes and data needed directly to construct catalogs and links. Do not conceal errors encountered during transformation.

Opening is blocked by incorrect set composition/version/markers, an unusable required-field shape, duplicate IDs within a kind, conflicting text, or a missing target of a used technology reference or `upgrades_to`/`upgrades`. Diagnostics identify database role, file, ID and problematic field path. Do not validate `potential`, external resources or other unused fields as cross-database references.

Lack of continuation evidence for multiple requirements is not an error. Missing localization produces warnings. Map new codes to short RU/EN messages through interface configuration; technical details remain in the diagnostic report.

Update report export to include all three files, `setId`, roles, failure phase and qualified references. Export remains a separate menu action and does not automatically write into the working directory.

## 8. Configuration and modules

Update `config/frontend/adapter.json`: supported format, required roles, object selectors and ID/requirement/upgrade fields. Do not introduce a large game-command registry. Update localization and diagnostic configurations according to their responsibilities.

Separate the set adapter, object adapters and cross-object linking in `data/`. Reuse AST, requirement and reference helpers. `workers/` handles lifecycle/messages; localization indexing stays in `localization/`; compose menu/status changes from the UI kit. Follow file-size limits, English code and separate styling dictionaries.

## 9. Validation and acceptance

1. A synthetic three-file set opens in one action regardless of selection order or renamed files. Prepared data contains all three roles and localizations.
2. Test one/two/four files, repeated roles, mismatched `set_id`, old format, malformed JSON and absent enrichment: no field is built and the report identifies the cause.
3. Test picker dismissal, operation cancellation, retry, set replacement and stale Worker replies. Page reload neither opens nor creates databases.
4. Identical IDs across kinds and identical JSON Pointers stay separate; within-kind duplicates and conflicting texts report both locations.
5. Test RU/EN names/descriptions for all three kinds, shared component descriptions and all conditional building descriptions without evaluating conditions. Existing technology variants and tooltips work.
6. Test direct/alternative/empty requirements, multiple upgrades, missing reference targets and aggregation of witnesses for one pair. Ambiguous requirements do not become a unique technology pair.
7. Open the real stage-11 set successfully. Preserve supporting pairs for the 16 known upgrade cases from research, including afterburners and combat computers; separately investigate completeness of new results after expansion.
8. Run TypeScript checks, production build and relevant unit/browser scenarios. Measure set reading/preparation and interface responsiveness; do not copy full trees to the main thread.
9. Preserve current card placement and absence of connection lines. Update the user guide, Worker response model, addressing documentation and RU/EN changelog with actual results.

## 10. Related documents

- [Backend stage 11: three localized databases](../TZ_BACKEND_STAGE_11_EN.md).
- [Stage-one database opening](TZ_DATABASE_OPENING_EN.md).
- [Stage-one Worker result](TZ_WORKER_RESULT_EN.md).
- [Frontend structure](TZ_STRUCTURE_EN.md).
- [Chain and sorting rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).

[Русская версия](TZ_FRONTEND_STAGE_2_RU.md).
