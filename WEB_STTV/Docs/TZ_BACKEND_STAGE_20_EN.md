# Stage 20 — tree combinations with DLC settings

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Verified inputs](#2-verified-inputs)
- [3. Settings and configuration](#3-settings-and-configuration)
- [4. Evaluating DLC restrictions](#4-evaluating-dlc-restrictions)
- [5. Parents and children](#5-parents-and-children)
- [6. Storing combinations](#6-storing-combinations)
- [7. Local browser invocation](#7-local-browser-invocation)
- [8. Snapshot coordination](#8-snapshot-coordination)
- [9. DLC images](#9-dlc-images)
- [10. Diagnostics and validation](#10-diagnostics-and-validation)
- [11. Deliverables and sequence](#11-deliverables-and-sequence)
- [12. Related documents](#12-related-documents)

## 1. Status and scope

**Approved by the user on 2026-11-19; implemented.** Results and startup: [guide](BACKEND_STAGE_20_EN.md).

Use the completed stage 19 database set. Add Python evaluation of DLC-dependent visibility and parent/child combinations, browser invocation and DLC image preparation. Switching DLC does not reparse game files. Application startup and section navigation do not run the database generator.

Do not introduce a specific empire profile, Steam ownership detection, save reading, event reachability, draw probability calculation or automatic `technology_swap` selection. Persistent user preferences remain a separate task. Stored calculation combinations and restoration of user settings are distinct mechanisms.

Full acceptance requires a completed stage 19 set. The approved `CLASS` repair belongs to stage 19 and must not be replaced by excluding traits from the database.

## 2. Verified inputs

List entries come from the nested `dlcs` catalog and its RU/EN enrichment. Store selections using stable catalog IDs such as `dlc036`; match game predicates against exact technical `name`, such as `BioGenesis`. Localized titles, filenames and Steam numbers do not participate in matching.

The accepted stage 17 technology snapshot contains 143 technologies with DLC predicates: 166 occurrences of `host_has_dlc`, including 143 in `potential` and 23 in `weight_modifier`, using 17 distinct technical names. These are expanded AST observations, not product constants. Research files relative to the repository: `TMP/WEB_STTV/analyze_dlc_stage20.py` and `TMP/WEB_STTV/dlc_stage20_analysis.json`. The previous technology source documents match prepared stage 19 documents; repeat the analysis on the finally published set.

Examples relevant to the algorithm:

- `tech_archeology_lab`: its negative Ancient Relics condition expands to negated `host_has_dlc = "Ancient Relics Story Pack"`. Disabling DLC can reveal rather than only hide a technology.
- `tech_arcane_deciphering`: a zero multiplier when Ancient Relics is missing OR a required resource is unavailable. An unknown resource does not prevent proving the first alternative with disabled DLC.
- `tech_cloaking_psi`: First Contact is required together with Shadows of the Shroud OR non-gestalt ethics. Unknown ethics are not false.

Verify against `common/technology/00_ancient_relics_tech.txt`, `common/technology/00_phys_tech.txt`, expanded `common/scripted_triggers/00_scripted_triggers.txt` and technology output documents. Expansion history is not evaluated again as conditions.

## 3. Settings and configuration

Extend combinations with an explicit normalized DLC profile: sorted known and enabled catalog IDs plus the catalog/name-mapping revision. Known IDs not selected are disabled; unknown selected IDs are request errors. A predicate naming DLC absent from the catalog remains unknown with diagnostics, rather than disabled.

Keep field names, supported predicates/wrappers, `potential`/`weight_modifier` boundaries, image sources and local service parameters in separate extensible configurations. Reuse existing source and storage settings. Do not maintain handwritten technology lists for each DLC.

For this first mode, the single user selection describes host availability (`host_has_dlc`). Do not equate `has_dlc`, `local_has_dlc` or other unsupported predicates with host checks without separately confirming their semantics.

## 4. Evaluating DLC restrictions

Create an independent evaluator returning `true`, `false`, `unknown` and evidence: condition address, technical name, DLC ID, selected state and intermediate results. An empty condition block uses ordinary AND semantics. Preserve AND/OR, negation, nesting and scope. Do not extract checks from arbitrary effects, descriptions or metadata.

Unknown empire, event, resource and game-object conditions remain unknown. False determines a conjunction; true determines a disjunction. A single-child NOT inverts a known result. NAND/NOR use verified negation of conjunction/disjunction. Do not guess the meaning of multi-entry NOT, scalar logical forms or unsupported wrappers: retain unknown and diagnostic addresses until separately verified. Negations in the inspected DLC subset wrap one child block.

Two independent exclusion grounds:

1. `potential` becomes provably false because of selected DLC states.
2. The condition of `weight_modifier/modifier` with numeric `factor = 0` becomes provably true because of DLC. Evaluate the whole condition, excluding only configured action fields. If other actions or complex structure prevent proving the final zero, retain an unknown result.

Distinguish DLC causes from pre-existing restrictions by comparing partial evaluation with known DLC states against the same DLC states treated as unknown, or recording equivalent dependency evidence. A DLC predicate beside `always = no` does not turn an unrelated prohibition into a DLC restriction.

Base `weight = 0`, nonzero weight changes and conditions without a proven DLC cause do not hide cards by themselves. Do not calculate numerical probabilities. Hiding due to a zero DLC modifier is a reference-mode policy, not a statement that events cannot grant that technology.

Retain technologies for unknown results. Reports distinguish “not excluded by this filter” from “all game conditions satisfied”; this stage does not assert the latter. Leave source AST unchanged.

## 5. Parents and children

Evaluate DLC visibility for all technologies first, then choose parents for visible objects using the existing criterion order. Disabling DLC does not alter reference-empire facts or introduce new functional heuristics.

A DLC-hidden candidate cannot become a visible parent. This is an eligibility restriction before the criterion chain: the existing “skip a criterion producing zero candidates” rule must not restore hidden parents. With no candidates, display an independent root and report `no_visible_parent` with original prerequisites. Preserve existing ambiguity diagnostics when multiple candidates remain.

Do not automatically remove descendants just because the previously selected parent is hidden. Preserve original AND/OR prerequisites: this stage filters DLC, rather than proving all prerequisite and event reachability. Report when no prerequisite is visible instead of inventing an alternative edge.

Attach children as parents are selected; final `parent_tech`/`children` are reciprocal within one combination. Excluded objects remain in the database with visibility results but occupy no field cells. Recompute placement, language sorting and lines for the visible tree; additional prerequisite edges remain undisplayed.

## 6. Storing combinations

Preserve database enrichment: store DLC visibility and parent relationships per combination, not over universal technology properties. Visibility has its own status/reason; do not overload `parent_tech = null`.

Calculation revisions include the source set, parent rules, DLC rules, empire profile, variants, DLC catalog, enabled IDs and implementation version. Toggle order does not affect the key. Language affects text/layout, not DLC visibility or parent selection. Identical requests reuse verified results.

Publish atomically through existing storage: new immutable documents, then a new manifest. A failed calculation does not delete source objects or replace the previous accepted snapshot. Preserve indented multiline JSON.

## 7. Local browser invocation

This draft proposes a small explicitly started Python loopback service. It calls the shared calculation module, without duplicating it in TypeScript or starting the game builder. For development, Vite proxies a configured relative API prefix. Configure address, port and registered set directory; no MongoDB or container is required.

Browser `File` objects do not expose the chosen directory's absolute path. The service therefore knows the allowed set from its own configuration. After explicit opening, the client sends manifest identity/revision and the service verifies an exact match. A different set requires explicitly changing service configuration, not submitting arbitrary filesystem paths.

Minimum operations: attach a matching set, start/poll a calculation, cancel, retrieve the published manifest and declared result documents by identifiers. A start request contains request ID, expected revision and full DLC profile. Responses bind operation ID, original/result revisions, combination, counts, diagnostics and changed documents.

Long calculations run outside HTTP handlers, with one writer per set. Requests cannot mix results. Cancellation before publication preserves the active snapshot; if publication already completed, return its completed result. Do not expose arbitrary disk reads or command execution. The initial service can use Python's standard HTTP facilities and a separate operation executor; a new web framework is not required.

## 8. Snapshot coordination

Browser-loaded Files belong to the previous directory selection. After publication, do not treat them as new files or merely replace the revision number. Obtain the new manifest and reread changed documents through the service; reuse unchanged verified documents by hashes. The reader accepts bytes from both selected files and the local API with identical checks.

A mismatching source revision, closed/replaced set, cancelled or stale response cannot attach results to another state. Switch the tree atomically after preparing/verifying the result. Errors preserve the previous applied profile and tree.

Explicit set opening prepares or reuses the all-DLC-enabled combination. This is a database operation responding to a user action, not database generation on page startup. Without the service, a matching prepared combination can be viewed; disable applying new selections with a clear reason rather than silently using a simplified frontend filter.

## 9. DLC images

Extend existing set asset preparation. For each matched descriptor, resolve `thumbnail` relative to its own directory under `dlc/`. The inspected installation contains 32 `thumbnail.png` files and four catalog entries without descriptors; do not hardcode these counts.

Copy/normalize images through existing asset handling; store DLC-ID links, hashes and provenance. Resolve paths within the configured DLC tree; do not open archives or arbitrary external paths. Reuse image conversion/validation. Missing thumbnails produce warnings and frontend placeholders without disabling the switch.

This stage does not need a general GFX parser: list images use thumbnails. Prepare them with assets, not when toggling DLC. Additional assets do not require reconverting the previous 791 technology images when their inputs are unchanged.

## 10. Diagnostics and validation

Reports contain the full DLC profile, revisions, per-technology visibility with reason/condition address, unknown predicates/names, removed candidates and parent decisions, read/reused document counts, durations, written bytes and reuse status. Unread documents are not reported as verified.

Verify:

1. Individual DLC, negation, AND/OR across DLC and unknown conditions; unknown must not become false.
2. Disabling DLC that reveals a negatively gated technology; zero modifier with OR; nonzero multiplier; base zero weight; unsupported action form.
3. Missing DLC names, duplicate technical names, invalid selected IDs and decision provenance. Catalog conflicts block calculation; unsupported predicates produce diagnostics.
4. Hidden-parent exclusion, alternative candidate selection, independent roots, reciprocal children and no restoration of forbidden candidates.
5. All-on/all-off/mixed profiles, ID order independence, rule changes invalidating revisions, reuse and unchanged source AST.
6. Set/revision mismatches, cancellation, publication errors, sequential requests, atomic adoption and absence of game-builder calls.
7. API reading of changed documents with hash verification; preserved localization/assets and reuse of unchanged documents.
8. Valid, missing, corrupt and unsafe thumbnail paths; repeated preparation without duplication.

Run three profiles on real data and retain reports/measurements. Browser acceptance is defined in the frontend specification. These checks validate reference mode, not game-engine condition execution.

## 11. Deliverables and sequence

Approve the specification and complete stage 19 acceptance first; then implement the independent evaluator, combination changes/tests, DLC assets, local invocation and frontend integration. Stage 20 code, schemas and configuration are implemented; see the linked guide. New source exceptions are outside this stage.

Preserve modularity, DRY, compact files and existing schema/report infrastructure. Provide a bilingual guide, update indexes/changelogs and report actual checks and remaining limitations.

## 12. Related documents

- [Reference import](TZ_BACKEND_STAGE_19_EN.md).
- [Parents and children](TZ_BACKEND_STAGE_16_EN.md), [storage](TZ_BACKEND_STAGE_17_EN.md), [assets](TZ_BACKEND_STAGE_18_EN.md).
- [Interface sections and DLC settings](frontend/TZ_FRONTEND_STAGE_10_EN.md).
- [Logic and context](semantics/LOGIC_AND_CONTEXT_EN.md).
