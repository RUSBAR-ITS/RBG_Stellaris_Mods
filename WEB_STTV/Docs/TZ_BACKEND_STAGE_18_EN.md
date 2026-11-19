# Stage 18 — game images for technology cards

## Contents

- [1. Status and objective](#1-status-and-objective)
- [2. Preparation operation](#2-preparation-operation)
- [3. Configuration](#3-configuration)
- [4. Image selection and conversion](#4-image-selection-and-conversion)
- [5. Storage and publication](#5-storage-and-publication)
- [6. Research category names](#6-research-category-names)
- [7. Modules and diagnostics](#7-modules-and-diagnostics)
- [8. Validation and deliverables](#8-validation-and-deliverables)

## 1. Status and objective

**Approved by the user and implemented on 2026-11-19.** Startup and results: [stage 18 guide](BACKEND_STAGE_18_EN.md). Related document: [frontend stage 8](frontend/TZ_FRONTEND_STAGE_8_EN.md).

Prepare game images used by cards inside the database set, together with RU/EN research category names. Opening a prepared set must not require browser access to the installed game. The foundation is [stage 17 separate storage](TZ_BACKEND_STAGE_17_EN.md).

The stage covers base technologies, their `technology_swap` representations and three research resource icons. Images for other object kinds, empire state evaluation, interactive variant switching and browser-triggered generation are outside scope.

## 2. Preparation operation

1. Add an independent Python operation on an existing set with a manifest. Read technologies through the existing set reader, without parsing the game again or loading the other 14 database kinds.
2. Prepare images for every technology representation, including variants outside the current tree combination; this does not evaluate variant selection conditions.
3. Prepare used category names through the existing localization mechanism.
4. Validate and publish through the set storage facilities.
5. Allow the same operation to run during explicitly requested preparation of a new set. Order: source documents and localization → resource preparation; tree enrichment may already exist or follow afterwards.

A repeated run reuses unchanged prepared images after checking source contents and conversion settings. Changing an image does not require parsing technology files again. Starting the interface, opening a directory or refreshing a page does not launch this operation.

## 3. Configuration

Add `config/enrichment/assets.json` with a format version and references to the existing storage and localization configurations. Externalize:

- source root `STELLARIS_ROOT`, directory `gfx/interface/icons/technologies`, source extension `.dds`;
- area mapping to `gfx/interface/icons/resources/physics_research.dds`, `society_research.dds`, `engineering_research.dds`;
- field names `icon`, `technology_swap`, `name`, `inherit_icon`, `category` and inheritance rules;
- prepared resource directory relative to the set, PNG format, conversion and reuse settings;
- report location and category localization key extraction rules.

This config describes rules and locations, not a manually maintained list of technologies or images. Generate the actual registry automatically. Working locations follow `WORK_DIR` and storage configuration; do not hardcode this computer's absolute paths.

Game sources remain read-only. Write prepared files and reports into the project's working directory. Paths inside the set remain relative and follow stage 17 path constraints.

## 4. Image selection and conversion

| Representation | Selection rule |
| --- | --- |
| Base technology | Nonempty `icon` when specified, otherwise the technology ID; resolve in the configured technology directory with the source extension |
| Variant with `inherit_icon = yes` | The base technology image |
| Variant with `inherit_icon = no` | Its own image using variant `name`; handle an explicit own `icon`, if encountered, through configuration |
| Variant without `inherit_icon` | For the current corpus, use the configured own-image rule based on `name`; do not present this assumption as proven engine behavior across all versions |
| Cost icon | Research resource for the representation's effective area: physics, society or engineering |

The current set contains 679 technologies, 12 with explicit `icon`. The six variants without `inherit_icon` have image files matching their `name`. Verify resolution of all actual references during implementation, including explicit overrides.

Prepare PNG copies retaining aspect ratio, original resolution and transparency. The frontend controls display size; do not upscale source pixels during preparation. A second copy of the original DDS is unnecessary. Files with identical prepared content share one resource; retain the provenance of each reference in data/reports.

A missing source or individual decoding failure produces a diagnostic with technology, variant and attempted path. Record explicit image absence rather than substituting an unrelated image. The frontend uses a neutral placeholder. A publication failure must not leave a partial set.

## 5. Storage and publication

Suggested location: `assets/<content_hash>.png` inside the set directory. The manifest registry records each resource ID, relative path, MIME type, byte size, SHA-256 and image dimensions. Store the three research area resource mappings separately.

Add a resource reference under `enrichments.presentation` on the base technology and variant nodes without rewriting source AST fields. The reference holds a resource ID or explicit absence; do not embed repeated images or Base64 data into every JSON.

New presentation information and images have their own contract version and revision. They participate in the set snapshot revision and file verification, but do not change semantic inputs to `parent_tech` selection. Exclude this new enrichment from tree input hashing so that adding pictures does not invalidate prepared combinations. Do not revise existing treatment of earlier enrichments in this stage.

Preserve all combinations, `parent_tech`, `children`, technology localization, document IDs and node addresses. Rewrite only documents that actually change, updating their byte hashes. Use the existing publication mechanism: prepared files first, then a complete manifest. Interruption leaves the previous published set available.

Extend generated schemas and auditing with the new contract. Normal opening verifies images when read; a separate full audit covers every declared resource. Do not introduce repeated full AST validation just to add images.

## 6. Research category names

Collect unique IDs from base and variant `category` fields. A variant category list replaces the base list when present; otherwise inherit the base list. Preserve multiple categories instead of arbitrarily selecting one.

Add a shared RU/EN category name dictionary to the set's presentation metadata, accessible through the manifest. It is part of the database set; the frontend does not read game localization files. Build keys from category IDs using configuration; the existing localization mechanism retains raw strings, resolved static references and provenance.

Priorities remain unchanged: RU uses `RU_LOC_TIER_1`, then `RU_LOC_TIER_2`, then `RU_LOC_TIER_3`; EN uses `EN_LOC_TIER_1`. Reuse existing configuration instead of duplicating priority rules. Do not translate technology names and descriptions again.

Handle a missing category name through existing localization diagnostics and display its ID. Adding the category dictionary alone does not change parent selection.

## 7. Modules and diagnostics

Separate resource selection, reading/decoding, writing/reuse and publication. Reuse configuration, hashing, localization and reporting helpers. Follow the project's compact module rules; do not duplicate the database builder.

Report technology and variant counts, image reference counts, unique resources, converted and reused files, missing/corrupt sources, categories per language, written bytes and stage timings. Diagnostics link problems to technology ID, representation and source node. The prepared browser set does not require sensitive absolute user paths.

Document concrete CLI options and the entry module in the implementation guide. The operation must also be callable from Python without an interactive console dialogue.

## 8. Validation and deliverables

- Verify base naming, `icon`, inheritance, variant-specific images, reuse and missing sources.
- Check PNG dimensions/transparency, unique resources and references from all prepared representations.
- Verify RU/EN category names, priorities and variant list replacement/inheritance.
- Repeat preparation: unchanged files are neither converted nor rewritten. Changing an input image or settings updates the corresponding result.
- Test interrupted publication and detection of a damaged image on read/audit.
- On the current real set, confirm preservation of all 679 technologies and prepared tree combinations; do not reread the other 14 database kinds for image preparation.
- Record time, resource size and source problems. Separately verify opening the prepared set without access to the game.

Deliver the operation, config, extended schemas, prepared working set, report and bilingual guide. Update both changelogs. Stellaris testing is unnecessary; visual acceptance is performed together with frontend stage 8.
