# Stage 19 — empire and DLC reference data import

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Sources and set contents](#2-sources-and-set-contents)
- [3. Configuration](#3-configuration)
- [4. Parsing and object identities](#4-parsing-and-object-identities)
- [5. DLC catalog](#5-dlc-catalog)
- [Main entries](#main-entries)
- [Package descriptors](#package-descriptors)
- [6. Localization](#6-localization)
- [7. DLC source exception](#7-dlc-source-exception)
- [8. Storage and frontend reading](#8-storage-and-frontend-reading)
- [9. Diagnostics](#9-diagnostics)
- [10. Verification and acceptance](#10-verification-and-acceptance)
- [11. Implementation deliverables](#11-implementation-deliverables)
- [12. References](#12-references)

## 1. Status and scope

**Approved by the user on 2026-11-19. Implementation and acceptance checks are complete; results are recorded in the [stage guide](BACKEND_STAGE_19_EN.md).**

Prepare data for future settings covering archetype, Gestalt status, biological ships, origin, nomadic status, ethics, species traits, civics and the DLC selection. Add sources to the existing builder and support reading the expanded set in the current frontend.

Scope includes complete AST import, existing expansion and variable substitution, object indexing, RU/EN localization, linking DLC package descriptors to the catalog, schemas, reports and checks. Preserve separate documents, reusable libraries, file parallelism and selective reading from stages 14–18.

Empire/DLC controls, user-profile persistence, evaluating setting compatibility and technology availability, new parent-selection rules, Steam/launcher integration and automatic detection of purchased DLCs belong to a separate stage. Import does not select active object variants or evaluate game conditions. Images for the new catalogs remain source references; copying them is outside this stage. Preparation of existing technology images remains supported.

## 2. Sources and set contents

Add **10 database kinds** to the existing 15, producing a registry of **25 kinds**. Origins and civics share the `civics` source; there is no additional copy of an origins database.

All paths are relative to `STELLARIS_ROOT`. Read `*.txt` recursively for the first nine sources. Counts below come from the initial structural pass of the installed game on 2026-11-19; they are neither format limits nor evidence that full expansion succeeds.

| Database kind | Source | Files / objects in the initial pass |
| --- | --- | --- |
| `species_archetypes` | `common/species_archetypes/` | 1 / 6 |
| `species_classes` | `common/species_classes/` | 2 / 42 |
| `ethics` | `common/ethics/` | 2 / 17 |
| `ethic_categories` | `common/ethic_categories/` | 1 / 5 |
| `authorities` | `common/governments/authorities/` | 1 / 8 |
| `civics` | `common/governments/civics/` | 6 / 358, including 77 origins |
| `traits` | `common/traits/` | 44 / 1127, including leader traits |
| `graphical_culture` | `common/graphical_culture/` | 2 / 52 |
| `ship_categories` | `common/ship_categories/` | 1 / 7 |
| `dlcs` | `dlc_metadata/dlc_info.txt` and `dlc/**/*.dlc` | 36 catalog entries and 32 package descriptors |

The nine TXT directories contain 60 checked files; basic syntax parsing without expansion found no errors or duplicate root-object IDs. Comment-only files count as read documents containing zero objects.

For DLCs, select exactly `dlc_info.txt` from the metadata directory and recursively select `*.dlc` from the package directory. `dlc_recommendations/`, ZIP files, thumbnails and other package contents are not inputs to this import. A catalog entry may lack a separate descriptor. A missing DLC catalog or another configured mandatory source is a preparation error.

## 3. Configuration

Add the following addresses to `global_variables.json`; relative values resolve against `STELLARIS_ROOT`:

| Variable | Initial value |
| --- | --- |
| `SPECIES_ARCHETYPES_DIR` | `common/species_archetypes` |
| `SPECIES_CLASSES_DIR` | `common/species_classes` |
| `ETHICS_DIR` | `common/ethics` |
| `ETHIC_CATEGORIES_DIR` | `common/ethic_categories` |
| `AUTHORITIES_DIR` | `common/governments/authorities` |
| `CIVICS_DIR` | `common/governments/civics` |
| `TRAITS_DIR` | `common/traits` |
| `GRAPHICAL_CULTURE_DIR` | `common/graphical_culture` |
| `SHIP_CATEGORIES_DIR` | `common/ship_categories` |
| `DLC_METADATA_DIR` | `dlc_metadata` |
| `DLC_DIR` | `dlc` |

Extend `config/datasets.json`, sources and reports in `config/backend.json`, rules under `config/enrichment/targets/`, and the target registry in `config/enrichment/localization.json`. Do not introduce a manually maintained inventory of every game object or DLC.

Configure source selection, extensions, the `dlcs` container, and identity/matching/localization fields. For `dlcs`, distinguish the main catalog role from auxiliary descriptor sources. A kind's settings must specify the permitted object location within a document; ordinary kinds continue selecting root blocks. Indexing and localization use consistent object selection rather than independent exception lists.

Working paths come from `WORK_DIR` and `config/storage.json`; parallelism comes from `config/parallel.json` (currently 10). Preserve explicit library rebuild/reuse modes. Changed import rules participate in the relevant configuration revisions; stale results must not be declared current.

## 4. Parsing and object identities

Preserve complete parsing results: unknown game fields, ordering, repeated entries, nested blocks, operators, conditions, dynamic expressions and expansion history. Do not add a semantic command allowlist. Enrichment metadata does not become a game condition.

For the nine ordinary kinds, the object ID is its root block name. Variables, comments and scalar service entries do not become objects. A repeated ID within a kind is an error identifying both addresses. Identical IDs across kinds are allowed: for example, archetype and species-class `MACHINE` are distinguished by `database`.

- `is_origin = yes` distinguishes an origin from a civic regardless of file name. Store the object and its nested `swap_type` blocks once; conditional representations are not independent origins.
- Preserve every definition in `traits`, including leader traits. This stage does not produce a final list of selectable species traits; neither file names nor missing `allowed_archetypes` justify removing an object.
- Preserve `playable`, `initial`, `pickable_at_start`, `potential`, `possible`, `allowed_*`, `forbidden_*`, `opposites`, `modification`, archetype inheritance and related fields. Do not filter objects for an assumed starting empire.
- Preserve `advanced_authority_swap`, `swap_type` and other nested variants with conditions and source order. Do not evaluate their activation.
- Authorities, civics and species classes may use special requirements such as `ethics = { value = ... }`. Preserve their structure without converting them into ordinary technology triggers. Random selection weight does not become a manual-selection prohibition.

Do not create separate `gestalt`, `bioships` or `nomadic` databases. Gestalt status relates to `ethic_gestalt_consciousness`, biological ships to `ship_kinds`/`bio_ship`, and `is_nomadic` is a separate empire property referenced by conditions. `trait_nomadic` does not substitute for that property. These relations explain the data's purpose but do not introduce a profile evaluator in this stage.

## 5. DLC catalog

### Main entries

Store `dlc_info.txt` as one source document, preserving its `dlcs` container. Index its immediate blocks such as `dlc001` and `dlc036`; the container itself is not a DLC object. Use each nested block name as its ID, retaining `name` separately as the identifier used by `host_has_dlc`.

An object address has the form `/items/i/value/items/j`. Do not move blocks to the AST root to accommodate the existing indexer restriction. Preserve `recommendations`, `icon`, `show`, `affects_gameplay` and other fields; `show = no` or `affects_gameplay = no` must not remove a DLC from the catalog. Recommendations are not enablement dependencies.

### Package descriptors

Store each `.dlc` as a separate `dlcs` document with its original root fields. Keep `name`, `archive`, `localizable_name`, `steam_id`, `pops_id`, `category`, `thumbnail` and all other fields in the AST. A descriptor does not create a second DLC object in the index; source configuration determines its role.

Match a descriptor to a catalog entry by the exact `name` value, not by translated text, a Steam number or file-name similarity. Duplicate catalog IDs, ambiguous `name` values and multiple descriptors for one DLC are errors identifying every participant. Preserve unmatched descriptors and report a warning; do not automatically invent a new ID from the file name.

Add `enrichments.dlc.descriptors` to the catalog entry: an array of document references `{database, document_id}`, empty when no descriptor exists. This is a whole-document reference without an artificial root-assignment pointer. Descriptor fields do not overwrite catalog fields. Form links after document preparation and before final publication; verify them during audit.

In the current installation, four catalog entries (`dlc001`, `dlc003`, `dlc010`, `dlc011`) lack separate `.dlc` files. Record this observation in the report rather than in exceptions or a hardcoded required-package list.

Document/archive presence, Steam IDs and the `show`/`affects_gameplay` flags do not establish `owned` or `enabled`. Import does not add these values. Enabled DLC selection will belong to a future user profile. Expand conditions such as `has_shroud_dlc_and_machine_age` through the existing mechanism, preserving their complete logic; do not reduce every function to a single DLC name.

## 6. Localization

Use the existing `enrichments.localization` mechanism: independent RU/EN handling, existing `RU_LOC_TIER_1` → `RU_LOC_TIER_2` → `RU_LOC_TIER_3` and `EN_LOC_TIER_1` priorities, and preservation of keys, raw strings, resolved text, provenance and unresolved references. Do not duplicate translation-source definitions in new configs.

| Objects | Text target rules |
| --- | --- |
| Archetypes, classes, ethics, authorities, civics/origins, traits | Name by ID; description by `<id>_desc` when that key exists |
| Ethic categories | Name by ID when available; technical categories without translations remain identified by ID |
| Graphical cultures | Configured name-key candidates using the ID and uppercase ID; description by `<id>_shipset_desc`. Other verified mappings belong in localization rules, not guesses based on similar text |
| Ship categories | Name by ID; explicit `desc`, otherwise `<id>_desc` when available |
| DLCs | Main catalog `localizable_name`; if absent or untranslated, use the matched descriptor's key. Record the selected key's source; the display fallback when no translation exists is technical `name` |

Evaluate localization candidates independently per language. Do not record a technical fallback as a successfully found translation. Missing optional descriptions do not block publication; distinguish missing keys from objects without a text target in reports. Do not invent DLC descriptions using a suffix on `dlc036` or a store name.

Process explicit `description`/`desc` fields and named `swap_type`/`advanced_authority_swap` blocks through separate configured targets on their corresponding nodes. For example, `origin_default_desc` and `description = origin_tooltip_default_effects` are different texts; preserve both without replacing narrative text with effects. Preserve conditional texts alongside their conditions without selecting a branch. Do not invent a localization ID for a variant lacking its own `name`.

Resolve ordinary static `$key$` references. Preserve dynamic substitutions, game formatting commands and concept references as written. Retain existing base-technology description inheritance for technology variants; do not automatically extend that rule to every new nested block.

## 7. DLC source exception

The installed `dlc_metadata/dlc_info.txt` contains `paradoxplaza_store_url ""` without `=` inside `dlcs/dlc002` (line 35 during research). This is an observed source irregularity; no claim is made about engine behavior for it.

Add a scoped `sttv_dlc_metadata_store_separator` rule to `config/parser/source_exceptions.json`: only for that file, container, DLC entry and exact field/empty-string sequence, insert `=` in memory before ordinary parsing. Extending the exception mechanism must preserve references to original positions and use the original, uncorrected file when hashing input. Configure rule conditions and its action.

The line number must not be the sole condition. Comments and occurrences inside string literals do not match. If the field is already valid, the rule is not applied; multiple ambiguous matches are an error. Matching text in another file or object is not corrected. Keep the game source unchanged; the report records the rule ID, address, original and accepted constructs. Do not globally permit arbitrary assignments without an operator.

User-approved amendment: missing `CLASS` in vanilla trait icon calls may be corrected by a targeted exception using the enclosing object. In the configured list of `common/traits` files and exact templates, use the sole class from the root trait's immediate `leader_class` field; use `leader` for multiple distinct allowed classes. Configure the field, allowed classes, neutral value, files and templates. Preserve explicitly supplied arguments. Missing fields, unknown values, ambiguous objects or invalid field shapes remain errors. Nested calls retain the original trait context through the call chain; adjacent traits and filenames do not determine the class. Report the rule, object/field, derived value and call chain. This corrects presentation import without changing trait eligibility or game files.

Preserving explicit arguments includes forwarding through an intermediate template that dropped CLASS: within the same targeted exception, prefer the nearest explicitly supplied value in the call chain before deriving a class from the object. This does not introduce general argument inheritance between inline invocations.

Investigate and report other full-expansion problems separately. The amendment does not authorize automatically adding further exceptions or excluding problematic objects.

## 8. Storage and frontend reading

Each source file produces one persistent JSON in the existing separate-document storage format. Use common set publication: prepare documents first, then publish a consistent manifest. Preserve UTF-8, two-space indentation and line breaks. Do not reintroduce monolithic merging.

Extend indexing, the shared reader, reference checks, localization and generated schemas for permitted nested objects. Address validity follows the kind's selector and actual AST rather than removing all JSON Pointer restrictions. On reading, verify that an address exists, targets the expected entry and matches its ID. Separately validate DLC references to declared descriptor documents of the same kind.

Changed contract/configuration versions and the registry revision reflect the new format. Compatible reading of old sets is not required. Prepare the new set in a separate working directory; do not delete or overwrite the existing acceptance reference.

The expanded contents change the set revision. Do not mark an old set's prepared tree combinations current merely by replacing `source_set_id`. For browser acceptance, prepare a combination through the standard operation on the new set with the previous rules and profile. New catalogs do not become parent-selection evidence without a separately agreed stage. With unchanged previous inputs, verify preserved `parent_tech`/`children` decisions.

In the frontend, update the shared registry, types, localized kind labels, manifest checks, nested-address resolution and reference-data adapter. Explicit directory opening must accept a 25-kind set. Initial loading remains technology-only: additional documents are read on request and then reused within the session. Preserve hash verification on read, explicit coverage tracking and a separate full-audit command.

Verify targeted reading of a new object and its localization, including `dlcs/dlc036`. Adding catalogs does not create additional cards on the technology field. Opening, page refresh and application startup do not trigger database generation. New empire/DLC selection panels are not created in this stage.

## 9. Diagnostics

Existing reports must include, per kind, discovered/read files, documents and objects, successful/failed expansions, RU/EN localization targets, missing translations, applied exceptions, written bytes and stage timings. Report the origin count within `civics` and the count of all `traits` definitions separately, without presenting the latter as the count of selectable species traits.

For DLCs, add catalog-entry, descriptor, matched-pair, entry-without-descriptor, unmatched-descriptor and conflict counts. Problems retain the kind, source file, ID, node address and reason. A missing DLC descriptor does not imply a missing license.

Mandatory-structure errors, duplicate IDs, ambiguous matches or expansion failures must not leave a partially published set. Do not introduce a repeated full AST JSON Schema walk: extend stage 13's current checks and use the shared storage audit.

## 10. Verification and acceptance

1. Use synthetic sources to verify root objects of nine kinds, identical IDs across kinds, duplicate IDs within a kind and a comment-only file.
2. Verify an origin outside `00_origins.txt`, an ordinary civic in the same file, nested variants and preservation without duplicate objects.
3. Verify preservation of species and leader traits, unknown fields and conditions without filtering for starting availability.
4. Verify existing inline/scripted expansion, static-variable substitution and preservation of `AND`/`OR`/`NOT`, special requirement lists and invocation history.
5. Verify a nested DLC object, a flat descriptor, a missing descriptor, an extra descriptor, ambiguous names, duplicate IDs and a `name` differing from the file name. Keep catalog IDs, technical names and translation keys distinct.
6. Verify that `show = no`, `affects_gameplay = no` and local-file presence neither hide objects nor establish ownership/enablement.
7. Verify RU/EN localization, priorities, a descriptor fallback key, missing translations, a variant's own text, separate narrative/effect descriptions, cyclic/dynamic references and shipset descriptions.
8. Verify the exact DLC exception, an already corrected entry, a different file/object, a comment and ambiguous matches. Check original positions, the original-input hash and the diagnostic record.
9. Verify nested addresses and rejection of a missing node, wrong ID or mismatched selector; descriptor references remain within declared documents.
10. Verify publication and interruption, selective reading and detection of a corrupted file when read. Unread data must not be marked verified.
11. Generate schemas from the codebase, validate configs, run relevant backend and affected frontend unit/browser tests, and build TypeScript.
12. Build a real new 25-kind set, perform RU/EN enrichment, prepare existing resources and a ready combination, then run a full audit. Record actual counts and differences from the initial inventory; do not present full-expansion errors as passed checks.
13. Compare the previous 15 kinds and tree decisions against the reference with unchanged sources, excluding expected service revisions/format changes. Check browser opening, RU/EN, cards, zoom and connections; measure initial reading and confirm that the new catalogs are not all loaded upfront.

The reference counts of 36 DLCs and 32 descriptors apply to the researched installation. Do not hardcode counts into the product or substitute them for content checks. Synthetic tests and source reading do not establish game-engine availability evaluation; this stage does not implement that evaluator.

## 11. Implementation deliverables

Prepare modular changes to the existing importer, index, localization and readers; source/target configs; schemas through the standard generator; tests; real-build/audit reports; and a bilingual stage guide. Update the README, general specification index, exception documentation and changelog after implementation. The guide must list the vanilla sources actually read and remaining limitations.

Move repeated operations into shared helpers. Normal code files should remain within 200 lines; consider splitting above 200 and extract functional parts above 300, except for genuinely indivisible blocks. Do not create a separate DLC parser or duplicate the builder per new kind.

Changes outside this scope and additional vanilla-data corrections require separate agreement. Preparing this specification changes documentation only; configurations and executable code remain unchanged.

## 12. References

- [Stage 17 storage and addressing](TZ_BACKEND_STAGE_17_EN.md), [stage 18 assets](TZ_BACKEND_STAGE_18_EN.md), [existing exceptions](SOURCE_IMPORT_EXCEPTIONS_EN.md).
- [Kind registry](../config/datasets.json), [localization config](../config/enrichment/localization.json), [source variables](../global_variables.json).
- Game files `common/governments/99_README_GOVERNMENT.txt`, `common/governments/civics/00_civics.txt` and `common/traits/000_documentation_species_traits.txt` were compared with actual definitions. Code takes priority over comments.
- Game files `dlc_metadata/dlc_info.txt`, `dlc/dlc036_biogenesis/dlc036.dlc` and `common/scripted_triggers/00_scripted_triggers.txt` confirm the mapping `dlc036` → `name = "BioGenesis"` → `host_has_dlc = "BioGenesis"`.
