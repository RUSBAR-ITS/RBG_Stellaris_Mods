# Stellaris Technological Tree View — changelog

## Contents

- [2026-11-20 — reference data preparation profile](#2026-11-20--reference-data-preparation-profile)

- [2026-11-20 — separate parser, loader and server](#2026-11-20--separate-parser-loader-and-server)

- [2026-11-20 — research tools and fixture migration](#2026-11-20--research-tools-and-fixture-migration)

- [2026-11-20 — backend separation draft](#2026-11-20--backend-separation-draft)

- [2026-11-20 — loading the dictionary into MongoDB](#2026-11-20--loading-the-dictionary-into-mongodb)

- [2026-11-20 — MongoDB localization import draft](#2026-11-20--mongodb-localization-import-draft)

- [2026-11-19 — technology acquisition analysis and version 0.0.13](#2026-11-19--technology-acquisition-analysis-and-version-0013)

- [2026-11-19 — stage 21 progress and technology acquisition research](#2026-11-19--stage-21-progress-and-technology-acquisition-research)

- [2026-11-19 — recursive DLC dependency draft](#2026-11-19--recursive-dlc-dependency-draft)

- [2026-11-19 — DLC settings and frontend 0.0.12](#2026-11-19--dlc-settings-and-frontend-0012)

- [2026-11-19 — CLASS exception and DLC settings drafts](#2026-11-19--class-exception-and-dlc-settings-drafts)

- [2026-11-19 — reference import and frontend 0.0.11](#2026-11-19--reference-import-and-frontend-0011)

- [2026-11-19 — empire and DLC reference import draft](#2026-11-19--empire-and-dlc-reference-import-draft)

- [2026-11-19 — field zoom and frontend 0.0.10](#2026-11-19--field-zoom-and-frontend-0010)

- [2026-11-19 — card frame and height, zoom draft](#2026-11-19--card-frame-and-height-zoom-draft)

- [2026-11-19 — game images and frontend 0.0.8](#2026-11-19--game-images-and-frontend-008)

- [2026-11-19 — image and expanded card specifications](#2026-11-19--image-and-expanded-card-specifications)

- [2026-11-19 — bridges and frontend 0.0.7](#2026-11-19--bridges-and-frontend-007)

- [2026-11-19 — simple routes and bridges draft](#2026-11-19--simple-routes-and-bridges-draft)

- [2026-11-19 — tree connections and frontend 0.0.6](#2026-11-19--tree-connections-and-frontend-006)

- [2026-11-19 — tree connection specification draft and gap expansion](#2026-11-19--tree-connection-specification-draft-and-gap-expansion)
- [2026-11-19 — connection highlighting and bottom exit](#2026-11-19--connection-highlighting-and-bottom-exit)
- [2026-11-19 — left trunk for a mixed branch](#2026-11-19--left-trunk-for-a-mixed-branch)
- [2026-11-19 — tree connection element and attachments](#2026-11-19--tree-connection-element-and-attachments)
- [2026-11-19 — tree grid and frontend 0.0.5](#2026-11-19--tree-grid-and-frontend-005)
- [2026-11-19 — tree order and grid specification draft](#2026-11-19--tree-order-and-grid-specification-draft)
- [2026-11-19 — branches with a parent in another area](#2026-11-19--branches-with-a-parent-in-another-area)
- [2026-11-19 — lower-tier continuation placement](#2026-11-19--lower-tier-continuation-placement)
- [2026-11-19 — branch order and vacant cells](#2026-11-19--branch-order-and-vacant-cells)
- [2026-11-19 — initial tree placement rules](#2026-11-19--initial-tree-placement-rules)
- [2026-11-19 — manifests, separate documents and frontend 0.0.4](#2026-11-19--manifests-separate-documents-and-frontend-004)
- [2026-11-19 — manifest and separate database storage draft](#2026-11-19--manifest-and-separate-database-storage-draft)
- [2026-11-19 — technology parent and child enrichment implementation](#2026-11-19--technology-parent-and-child-enrichment-implementation)
- [2026-11-19 — parent and child enrichment specification draft](#2026-11-19--parent-and-child-enrichment-specification-draft)
- [2026-11-19 — tree relationship enrichment approach](#2026-11-19--tree-relationship-enrichment-approach)
- [2026-11-19 — preliminary event access analysis](#2026-11-19--preliminary-event-access-analysis)
- [2026-11-19 — complete analytical predecessor selection pass](#2026-11-19--complete-analytical-predecessor-selection-pass)
- [2026-11-19 — anti-ship weaponry functional group](#2026-11-19--anti-ship-weaponry-functional-group)
- [2026-11-19 — functional criterion order comparison and swap](#2026-11-19--functional-criterion-order-comparison-and-swap)
- [2026-11-19 — planet class change functional group](#2026-11-19--planet-class-change-functional-group)
- [2026-11-18 — object capacity affinity before empire filtering](#2026-11-18--object-capacity-affinity-before-empire-filtering)
- [2026-11-18 — production affinity before empire filtering](#2026-11-18--production-affinity-before-empire-filtering)
- [2026-11-18 — analytical predecessor rule review](#2026-11-18--analytical-predecessor-rule-review)
- [2026-11-18 — ambiguity log with field snapshot](#2026-11-18--ambiguity-log-with-field-snapshot)
- [2026-11-18 — indirect functional affinity](#2026-11-18--indirect-functional-affinity)
- [2026-11-18 — technology functional groups](#2026-11-18--technology-functional-groups)
- [2026-11-18 — direct functional object relations](#2026-11-18--direct-functional-object-relations)
- [2026-11-18 — availability condition matching rule](#2026-11-18--availability-condition-matching-rule)
- [2026-11-18 — direct object upgrade rule](#2026-11-18--direct-object-upgrade-rule)

- [2026-11-18 — construct dictionary for technology analysis](#2026-11-18--construct-dictionary-for-technology-analysis)
- [2026-11-18 — working data cleanup preparation](#2026-11-18--working-data-cleanup-preparation)
- [2026-11-18 — parallel file processing implementation](#2026-11-18--parallel-file-processing-implementation)
- [2026-11-18 — parallel file processing draft](#2026-11-18--parallel-file-processing-draft)
- [2026-11-18 — reusable element libraries implemented](#2026-11-18--reusable-element-libraries-implemented)
- [2026-11-18 — reusable element library draft](#2026-11-18--reusable-element-library-draft)
- [2026-11-18 — validation and build optimization implemented](#2026-11-18--validation-and-build-optimization-implemented)
- [2026-11-18 — validation and build optimization draft](#2026-11-18--validation-and-build-optimization-draft)
- [2026-11-18 — fifteen databases and streaming reads](#2026-11-18--fifteen-databases-and-streaming-reads)
- [2026-11-18 — conditional import exceptions](#2026-11-18--conditional-import-exceptions)
- [2026-11-18 — confirming seven stage 12 blockers](#2026-11-18--confirming-seven-stage-12-blockers)
- [2026-11-18 — draft extension to 15 databases](#2026-11-18--draft-extension-to-15-databases)
- [2026-11-18 — alloy production branch and ordering within a branch](#2026-11-18--alloy-production-branch-and-ordering-within-a-branch)
- [2026-11-18 — anchor clarification and placement between prerequisites](#2026-11-18--anchor-clarification-and-placement-between-prerequisites)
- [2026-11-18 — reviewing proposed continuations for nine technologies](#2026-11-18--reviewing-proposed-continuations-for-nine-technologies)
- [2026-11-18 — extended chain rules reanalysis](#2026-11-18--extended-chain-rules-reanalysis)
- [2026-11-18 — removed repeatable technology area restriction](#2026-11-18--removed-repeatable-technology-area-restriction)
- [2026-11-18 — infinitely repeatable technology placement](#2026-11-18--infinitely-repeatable-technology-placement)
- [2026-11-18 — standard empire path in reference mode](#2026-11-18--standard-empire-path-in-reference-mode)
- [2026-11-18 — selection procedure and functional continuations](#2026-11-18--selection-procedure-and-functional-continuations)
- [2026-11-18 — ID priority for technology chain selection](#2026-11-18--id-priority-for-technology-chain-selection)
- [2026-11-17 — database set implementation and interface 0.0.2](#2026-11-17--database-set-implementation-and-interface-002)
- [2026-11-17 — specifications for a three-database localized set](#2026-11-17--specifications-for-a-three-database-localized-set)
- [2026-11-17 — mandatory prerequisites and additional databases](#2026-11-17--mandatory-prerequisites-and-additional-databases)
- [2026-11-17 — analysis of 39 ambiguous continuations](#2026-11-17--analysis-of-39-ambiguous-continuations)
- [2026-11-17 — initial tree layout rules](#2026-11-17--initial-tree-layout-rules)
- [2026-11-17 — chain rules document and starting technologies](#2026-11-17--chain-rules-document-and-starting-technologies)
- [2026-11-17 — technology chain research](#2026-11-17--technology-chain-research)
- [2026-11-17 — first frontend implementation](#2026-11-17--first-frontend-implementation)
- [2026-11-17 — localized diagnostic messages](#2026-11-17--localized-diagnostic-messages)
- [2026-11-17 — diagnostic technical detail contents](#2026-11-17--diagnostic-technical-detail-contents)
- [2026-11-17 — backend and frontend validation responsibilities](#2026-11-17--backend-and-frontend-validation-responsibilities)
- [2026-11-17 — diagnostic report saving](#2026-11-17--diagnostic-report-saving)
- [2026-11-17 — diagnostics and error response](#2026-11-17--diagnostics-and-error-response)
- [2026-11-17 — localization index records and data errors](#2026-11-17--localization-index-records-and-data-errors)
- [2026-11-16 — technology requirement tree and links](#2026-11-16--technology-requirement-tree-and-links)
- [2026-11-16 — ready container and technology catalog model](#2026-11-16--ready-container-and-technology-catalog-model)
- [2026-11-16 — Worker protocol for database opening](#2026-11-16--worker-protocol-for-database-opening)
- [2026-11-16 — frontend structure and resource locations](#2026-11-16--frontend-structure-and-resource-locations)
- [2026-11-16 — frontend technology stack](#2026-11-16--frontend-technology-stack)
- [2026-11-16 — status panel and database actions in the menu](#2026-11-16--status-panel-and-database-actions-in-the-menu)
- [2026-11-16 — loading states, cancellation, and database replacement](#2026-11-16--loading-states-cancellation-and-database-replacement)
- [2026-11-16 — prepared database reading and adapter in a Web Worker](#2026-11-16--prepared-database-reading-and-adapter-in-a-web-worker)
- [2026-11-16 — explicit database opening and initial interface startup](#2026-11-16--explicit-database-opening-and-initial-interface-startup)
- [2026-11-16 — database adapter specification for the interface](#2026-11-16--database-adapter-specification-for-the-interface)
- [2026-11-16 — shared localized string lookup specification](#2026-11-16--shared-localized-string-lookup-specification)
- [2026-11-16 — agreed interface palettes and typography](#2026-11-16--agreed-interface-palettes-and-typography)
- [2026-11-16 — color and typography dictionary specification](#2026-11-16--color-and-typography-dictionary-specification)
- [2026-11-16 — main window specification](#2026-11-16--main-window-specification)
- [2026-11-16 — scrollbar specification](#2026-11-16--scrollbar-specification)
- [2026-11-16 — technology tier column specification](#2026-11-16--technology-tier-column-specification)
- [2026-11-16 — research area region specification](#2026-11-16--research-area-region-specification)
- [2026-11-16 — technology field specification and predecessor grouping](#2026-11-16--technology-field-specification-and-predecessor-grouping)
- [2026-11-16 — technology variant list interaction](#2026-11-16--technology-variant-list-interaction)
- [2026-11-16 — labels for technology variants with identical titles](#2026-11-16--labels-for-technology-variants-with-identical-titles)
- [2026-11-16 — manual variants and technology layout refinement](#2026-11-16--manual-variants-and-technology-layout-refinement)
- [2026-11-16 — technology viewport specification](#2026-11-16--technology-viewport-specification)
- [2026-11-16 — bottom menu button group specification](#2026-11-16--bottom-menu-button-group-specification)
- [2026-11-16 — menu panel specification](#2026-11-16--menu-panel-specification)
- [2026-11-16 — technology card specification and tooltip heading](#2026-11-16--technology-card-specification-and-tooltip-heading)
- [2026-11-16 — menu collapse button specification](#2026-11-16--menu-collapse-button-specification)
- [2026-11-16 — localized string lookup configuration](#2026-11-16--localized-string-lookup-configuration)
- [2026-11-16 — interface text sources](#2026-11-16--interface-text-sources)
- [2026-11-16 — theme toggle and string identifiers](#2026-11-16--theme-toggle-and-string-identifiers)
- [2026-11-16 — Language selector specification](#2026-11-16--language-selector-specification)
- [2026-11-16 — separate persistence design](#2026-11-16--separate-persistence-design)
- [2026-11-16 — Selection control specification](#2026-11-16--selection-control-specification)
- [2026-11-16 — Button and Tooltip specifications](#2026-11-16--button-and-tooltip-specifications)
- [2026-11-16 — shared button and tooltip](#2026-11-16--shared-button-and-tooltip)
- [2026-11-16 — Icon element specification](#2026-11-16--icon-element-specification)
- [2026-11-16 — Text element specification](#2026-11-16--text-element-specification)
- [2026-11-16 — UI element list](#2026-11-16--ui-element-list)
- [2026-11-16 — interface styling dictionary](#2026-11-16--interface-styling-dictionary)
- [2026-11-16 — initial interface concept](#2026-11-16--initial-interface-concept)
- [2026-11-16 — implemented localization in the database](#2026-11-16--implemented-localization-in-the-database)
- [2026-11-16 — localization in the database specification](#2026-11-16--localization-in-the-database-specification)
- [2026-11-15 — script value expansion implementation](#2026-11-15--script-value-expansion-implementation)
- [2026-11-15 — script value expansion specification](#2026-11-15--script-value-expansion-specification)
- [2026-11-15 — implemented effect and trigger expansion](#2026-11-15--implemented-effect-and-trigger-expansion)
- [2026-11-15 — effect and trigger expansion design](#2026-11-15--effect-and-trigger-expansion-design)
- [2026-11-15 — implemented static-variable substitution](#2026-11-15--implemented-static-variable-substitution)
- [2026-11-15 — static-variable substitution specification](#2026-11-15--static-variable-substitution-specification)
- [2026-11-15 — static variable directory](#2026-11-15--static-variable-directory)
- [2026-11-15 — explicit inline_script path exceptions](#2026-11-15--explicit-inline_script-path-exceptions)
- [2026-11-15 — vanilla issue TODO and color exception](#2026-11-15--vanilla-issue-todo-and-color-exception)
- [2026-11-15 — excluded scripted effect library](#2026-11-15--excluded-scripted-effect-library)
- [2026-11-15 — stage six implementation: syntax-tree database](#2026-11-15--stage-six-implementation-syntax-tree-database)
- [2026-11-15 — stage six specification: backend simplification](#2026-11-15--stage-six-specification-backend-simplification)
- [2026-11-15 — parsing results as the database foundation](#2026-11-15--parsing-results-as-the-database-foundation)
- [2026-11-15 — implemented inline_script expansion](#2026-11-15--implemented-inline_script-expansion)
- [2026-11-15 — stage five specification: inline_script expansion](#2026-11-15--stage-five-specification-inline_script-expansion)
- [2026-11-15 — inline_script directory and expansion requirements](#2026-11-15--inline_script-directory-and-expansion-requirements)
- [2026-11-15 — extracted families removed from the working list](#2026-11-15--extracted-families-removed-from-the-working-list)
- [2026-11-15 — set_, add_, and remove_ family lists](#2026-11-15--set_-add_-and-remove_-family-lists)
- [2026-11-15 — initial is_ and has_ construct inventories](#2026-11-15--initial-is_-and-has_-construct-inventories)
- [2026-11-15 — variables and substitutions excluded from lists](#2026-11-15--variables-and-substitutions-excluded-from-lists)
- [2026-11-15 — two scalar-use lists](#2026-11-15--two-scalar-use-lists)
- [2026-11-15 — third frequency pass](#2026-11-15--third-frequency-pass)
- [2026-11-15 — fourth-stage parser implementation](#2026-11-15--fourth-stage-parser-implementation)
- [2026-11-15 — fourth-stage parser specification](#2026-11-15--fourth-stage-parser-specification)
- [2026-11-15 — logical operators and opaque inline_script](#2026-11-15--logical-operators-and-opaque-inline_script)
- [2026-11-15 — keyword id](#2026-11-15--keyword-id)
- [2026-11-15 — second frequency pass](#2026-11-15--second-frequency-pass)
- [2026-11-15 — keywords and boolean values](#2026-11-15--keywords-and-boolean-values)
- [2026-11-15 — text element frequency research](#2026-11-15--text-element-frequency-research)
- [2026-11-15 — third-stage implementation: configurable parser](#2026-11-15--third-stage-implementation-configurable-parser)
- [2026-11-15 — third-stage specification: parser and syntax configuration](#2026-11-15--third-stage-specification-parser-and-syntax-configuration)
- [2026-11-15 — script syntax description](#2026-11-15--script-syntax-description)
- [2026-11-15 — vanilla script pattern research](#2026-11-15--vanilla-script-pattern-research)
- [2026-11-15 — second backend stage implementation](#2026-11-15--second-backend-stage-implementation)
- [2026-11-15 — second-stage backend specification](#2026-11-15--second-stage-backend-specification)
- [2026-11-15 — first backend stage implementation](#2026-11-15--first-backend-stage-implementation)
- [2026-11-15 — separate specifications for subsequent stages](#2026-11-15--separate-specifications-for-subsequent-stages)
- [2026-11-15 — backend specification and directory structure](#2026-11-15--backend-specification-and-directory-structure)
- [2026-11-15 — strict schema and eligibility conditions](#2026-11-15--strict-schema-and-eligibility-conditions)
- [2026-11-15 — stage-one JSON database model](#2026-11-15--stage-one-json-database-model)
- [2026-11-15 — Russian and English localization sources](#2026-11-15--russian-and-english-localization-sources)
- [2026-11-15 — technology object model](#2026-11-15--technology-object-model)
- [2026-11-15 — project global variables](#2026-11-15--project-global-variables)
- [2026-11-15 — technology tree research](#2026-11-15--technology-tree-research)
- [2026-11-15 — first specification part](#2026-11-15--first-specification-part)
- [2026-11-15 — initial concept](#2026-11-15--initial-concept)

## 2026-11-20 — reference data preparation profile

The source profile now lists all 30 WEB_STTV datasets, including the DLC catalog and descriptors, and output paths for scripts, libraries and the RU/EN dictionary. A draft specification describes running the two readers in one invocation. [Profile](../config/parser_sources.json) · [Draft specification](../../Instruments/Stellaris_Parser/Docs/TZ_PREPARE_ALL_EN.md)

The specification assigns the RU/EN dictionary one dedicated process in addition to the script worker limit. It starts alongside library preparation. The command waits for both the scripts and the dictionary.

The standalone Stellaris Parser implements `prepare-all`. The reference profile selects TXT and DLC files by exact paths and globs. A dedicated process prepares the dictionary in the loader's format. The command reports failure of either task and writes only output artifacts to the result directories. [Run instructions](../../Instruments/Stellaris_Parser/README_EN.md#full-preparation)

## 2026-11-20 — separate parser, loader and server

Extracted Stellaris Parser and the shared document package format. The loader and server use separate MongoDB profiles. Workspace outputs moved to `TMP/WEB_STTV`. Verified all 303,500 dictionary documents. [Results and commands](BACKEND_STAGE_23_EN.md)

## 2026-11-20 — research tools and fixture migration

Moved 19 research scripts and three reference fixtures out of the working directories. Updated test and documentation paths, tool arguments and checks for the current parser API. Section 10 of AGENTS.md now covers reusable materials.

## 2026-11-20 — backend separation draft

Removed the requirement to rebuild the file-backed test setup after cleanup. Stage 23 acceptance now uses the localization JSON package and the `wiki.localization` MongoDB collection.

Revised the stage 23 draft. The independent parser belongs in `Instruments/Stellaris_Parser/`. The loader and server have separate MongoDB connection configurations. The migration to `TMP/WEB_STTV/` identifies tools and test references worth keeping before manual cleanup.

Drafted the separation of the local parser, MongoDB loader and server. Specified the package for finished documents and boundary tests using the stage 22 dictionary. [Stage 23 specification](TZ_BACKEND_STAGE_23_EN.md)

## 2026-11-20 — loading the dictionary into MongoDB

Added preparation, batch loading and full comparison commands, MongoDB and Vault reference configuration, a schema and tests. The test server holds 303,500 documents with raw text and priority selections. Repeat import and recovery from a failed batch were verified. [Stage 22 guide](BACKEND_STAGE_22_EN.md)

## 2026-11-20 — MongoDB localization import draft

The [stage 22 specification](TZ_BACKEND_STAGE_22_EN.md) describes a document per language and key, retention of every source definition, translation selection and acceptance checks for the first import into `wiki.localization`. It records the size of the current RU and EN game sources.

## 2026-11-19 — technology acquisition analysis and version 0.0.13

Implemented recursive DLC restrictions and the approved acquisition analysis: 30 database kinds, crisis paths/levels, source-file index, grant callers and guards, conservative `has_technology`. Added source/effect/entry configuration, generated schemas and manifest version 2. The graph is reused between DLC applications; the frontend does not read the technical index. New set: `data/stage21_acquisition/database_set`; service configuration points to it. Checks and limitations, including unconfirmed random-option selection, are documented in the [guide](BACKEND_STAGE_21_EN.md). No services or game were started.

## 2026-11-19 — stage 21 progress and technology acquisition research

- The approved main stage 21 scope added ascension perk, tradition and category import/RU/EN localization, grouped DLC configuration, a recursive three-valued graph, cycle/limit handling, evidence and coverage. Calculation revisions, schemas and selective reading were updated; the frontend accepts 28 kinds and explicitly rejects incomplete older sets.
- Full `data/stage21` preparation completed in 557.156 s. Checks covered 86 DLC profiles, Weaver weapon removal without BioGenesis, and publication of three reference combinations plus reuse of the full profile. Targeted backend checks and 70 frontend tests passed; 3 real-data checks were skipped in the general run. No HTTP/Vite services were started; browser acceptance was not performed and the stage is not declared complete.
- [Cosmogenesis acquisition was investigated separately](RESEARCH_COSMOGENESIS_ACQUISITION_EN.md): crisis levels unlock research options through a DLC-dependent path; no confirmed route bypassing Machine Age was found. All six Lathe consumers have their own direct DLC restriction; missiles and torpedoes have alternative conditions. All 43 matrix profiles without Machine Age were checked.
- The user chose to extend the specification with acquisition analysis. A [RU/EN addendum](TZ_BACKEND_STAGE_21_ACQUISITION_EN.md) proposes two crisis catalogs, a technical source/grant/call index, acquisition-specific rules, coverage and diagnostics. Textual inventory found commands in 131 source files. Addendum code is not implemented; its requirements await approval. Main-specification status and documentation pointers were updated.

## 2026-11-19 — recursive DLC dependency draft

- Prepared RU/EN [stage 21 drafts](TZ_BACKEND_STAGE_21_EN.md): recursion through nested conditions and object references for the entire DLC catalog, cycles, caching, evidence and coverage reporting.
- Proposed three new database kinds and source variables: `ascension_perks`, `traditions`, `tradition_categories`. A limited inventory found 49, 234 and 33 root definitions with no duplicate IDs or syntax errors; full import was not run.
- Distinguished object availability from empire possession, selection restrictions from existence, and DLC restrictions from zero weight. Proposed an all-DLC test matrix without exhaustive combination enumeration.
- Backend stage 20 and frontend stage 10 guides now explicitly record that weaver weapons are not yet excluded through the indirect BioGenesis dependency. Updated documentation links. Code, configuration and product version are unchanged; approval is pending and no services were started.

## 2026-11-19 — DLC settings and frontend 0.0.12

- Implemented backend stage 20 and frontend stage 10: tree/DLC navigation, thumbnails, accessible switches, draft/apply/discard/cancel behavior.
- Python evaluates DLC-caused potential prohibitions and zero-weight modifiers. Unknown conditions and base zero weight do not exclude technologies. Parents are selected after filtering; later criteria cannot restore hidden candidates.
- Added DLC rule configuration, visibility revisions/evidence and persisted reusable combinations. Selected technology variants are retained.
- Added an explicitly launched loopback service with set/revision checks, sequential operations, cancellation and declared-resource reads. The interface never invokes the game builder.
- The frontend adopts snapshots atomically, streams/verifies new bytes and retains unchanged catalogs/images. Errors retain the previous tree.
- Prepared 32 thumbnails for 36 DLC. The stage 20 set contains 822 unique images and 543 documents; source data and the stage 19 reference are preserved. All/none/mixed profiles yielded 678/543/544 visible technologies.
- Updated 36 generated schemas, RU/EN strings, styling dictionary, README and guides. Added semantics, API, snapshot and UI tests. Details: [backend](BACKEND_STAGE_20_EN.md), [frontend](frontend/FRONTEND_STAGE_10_EN.md).


## 2026-11-19 — CLASS exception and DLC settings drafts

- Approved and implemented trait-icon CLASS exceptions: prefer an explicit value in the call chain, then the object's sole leader_class, then leader for multiple classes. Rules, allowed classes and files are configured; missing/unknown evidence remains an error. Extended the schema and focused tests while preserving substitution provenance.
- Completed stage 19 acceptance: published 25 kinds and 543 documents, imported all 1127 traits, verified 791 images and both tree combinations. Existing source data and parent/child decisions match the reference; new-set browser checks: 29 passed, one conditional scenario skipped.
- Prepared RU/EN drafts for [backend stage 20](TZ_BACKEND_STAGE_20_EN.md) and [frontend stage 10](frontend/TZ_FRONTEND_STAGE_10_EN.md). All DLC enabled initially, explicit application and both DLC restriction types are agreed. Local Python invocation, atomic combination updates, pictures and view states are proposed; new section code was not implemented.
- Inspected expanded technology DLC predicates: 143 technologies and 166 occurrences. Updated documentation indexes, UI inventory and VANILLA-001 status; game files remain unchanged. Exception and full-set acceptance results: [stage 19 guide](BACKEND_STAGE_19_EN.md).

## 2026-11-19 — reference import and frontend 0.0.11

- Added ten database kinds, source locations and RU/EN targets; the registry now contains 25 kinds. Origins remain in `civics`, leader traits remain in `traits`.
- Nested DLC indexes and flat descriptors share object selection; exact `name` matching, document references, per-language localization fallback and link checks do not infer ownership.
- Added the approved `sttv_dlc_metadata_store_separator` exception with original coordinates and diagnostics. Schemas were regenerated.
- Frontend 0.0.11 supports the expanded registry, nested addresses and technical DLC name fallback. Initial loading stays selective; no empire controls are added.
- Updated tests and bilingual documentation. All 450 original documents match the reference. `VANILLA-001` stopped the full build; the new set is not published and the reference is preserved. Checks and limitations: [guide](BACKEND_STAGE_19_EN.md).

## 2026-11-19 — empire and DLC reference import draft

- Prepared the RU/EN [stage 19 specification](TZ_BACKEND_STAGE_19_EN.md): ten new kinds, a shared civic/origin source, RU/EN text, DLC catalog and descriptors, and a scoped exception for the missing operator.
- Defined nested DLC indexing, references to separate package documents, selective reading of a 25-kind set and preservation of existing build mechanisms. DLC ownership, user controls and condition evaluation are outside import scope.
- An initial structural pass of 60 TXT files across nine directories found no syntax errors or duplicate root-object IDs. Found 36 DLC catalog entries and 32 descriptors; full expansion and a new set build have not yet been run.
- Updated README and general specification links. This draft awaits approval; executable code, schemas, runtime configs and the application version remain unchanged.

## 2026-11-19 — field zoom and frontend 0.0.10

- Implemented the approved [field zoom specification](frontend/TZ_FRONTEND_STAGE_9_EN.md); frontend version is 0.0.10. Initial 50% and the available values are configured in `config/frontend/zoom.json`.
- The setting uses existing UI-kit elements, is localized in RU/EN and is available before database opening. Zoom does not trigger set reads or tree recalculation.
- Cards, fonts, images and SVG scale together; scroll bounds match the rendered field, preserving its centre with edge clamping. Menus, tooltips and scrollbars retain their size.
- The setting survives language, theme, menu and set changes within the session; page reload restores initial 50%. Previous tooltips and highlighting close on zoom changes.
- Build/TypeScript, 65 unit checks and 27 browser checks passed. The standard unit run skipped 3 checks requiring separate inputs; the production browser run skipped 2 development-configuration interception scenarios and 1 separate large monolithic input. The real 679 technologies were checked in RU/EN at 50%, 100% and 150%.


## 2026-11-19 — card frame and height, zoom draft

- Frontend updated to 0.0.9. Rarity/danger colours fill the entire frame band; the inner surface retains the research-area colour.
- Minimum height reduced from 188 to 158 px, preserving full names and the shared measured height required by images/text.
- Prepared the [field zoom draft](frontend/TZ_FRONTEND_STAGE_9_EN.md): initial 50%, menu control, and unified card/font/connection scaling. Implementation awaits specification approval.
- Production build with TypeScript and 10 browser checks passed, including the real 679-technology set in RU/EN. Two development-configuration interception scenarios were skipped for the production build.


## 2026-11-19 — game images and frontend 0.0.8

Implemented approved backend stage 18 and frontend stage 8. Added resource configuration, standalone DDS→PNG preparation, explicit `--prepare-assets`, deduplication, verified reuse, shared manifest registry and RU/EN categories. Extended schemas and auditing; `presentation` does not alter semantic tree inputs.

Cards now include images, full names, categories, game tier, starting marker, base cost/weight and finite repetitions. Missing numeric rows are hidden; zeros remain visible. Added research colors, rarity/danger frames, shared height measurement, image caching/release and corruption diagnostics. Preserved tooltips, parents, logical positions and bridges. Frontend version: 0.0.8.

Prepared the current set: 679 technologies, 206 variants, 791 PNG images, 13 RU/EN categories. Verified all 885 references, images and preservation of 35 documents; repeat preparation took 12.69 s without rewrites. Passed 23 backend checks, 65 frontend unit checks, a separate real-combination check, 24 browser checks, TypeScript and production build. One large monolithic-file browser test was skipped. Guides: [backend](BACKEND_STAGE_18_EN.md), [interface](frontend/FRONTEND_STAGE_8_EN.md).

## 2026-11-19 — image and expanded card specifications

- Prepared paired RU/EN draft specifications for backend stage 18 and frontend stage 8: PNG copies of game icons, set resource registry, reuse and research category names.
- Defined full names, game tier, starting marker, base cost/weight, finite repetitions, area colors and dangerous-frame precedence over rare styling.
- Per the user's clarification, missing cost and weight are hidden with their labels; explicit zero stays visible. Specified content-based common card dimensions and consistent connection geometry.
- Linked the drafts from the main specification index, card document and UI element list. This is a design iteration; code and the prepared set were unchanged.

## 2026-11-19 — bridges and frontend 0.0.7

- Implemented approved frontend stage 7: simple routes replace A*, perpendicular crossings use a continuous horizontal bridge with a field-colored underlay.
- Added arc/clearance configuration, crossing and full bridge-bound checks, bend and path-length statistics. Logical card placement and connection coverage are preserved.
- Following user clarification, children sharing an exit use one corner; branch dots sit at corner vertices without offsets. Bridge highlighting follows the horizontal path without changing layering.
- Checked 61 synthetic scenarios, four real layouts, TypeScript, production build and 21 browser tests; optional giant JSON was skipped. Maximum real-path bends fell from 24/34 to 3/4. Updated bilingual specifications, guide and links. Databases were not rebuilt.

## 2026-11-19 — simple routes and bridges draft

- Prepared the bilingual [stage 7 specification](frontend/TZ_FRONTEND_STAGE_7_EN.md) from agreed decisions: readable route shape, permitted crossings with horizontal bridges and gap expansion for readability.
- Documented crossings versus junctions, a continuous upward arc, local underlay, independent highlighting without layer changes, bridge data/configuration, diagnostics and checks on synthetic diagrams and the existing set.
- Added next-stage status to the connection specification; updated README and general specification links and corrected the general specification's stage 5 link. Historical stage 6 requirements are retained with an explicit note about replacing the crossing prohibition.
- Documentation only. The consolidated specification awaits approval; implementation, configuration, databases and version `0.0.6` remain unchanged.

## 2026-11-19 — tree connections and frontend 0.0.6

- Implemented the approved [stage 6 specification](frontend/TZ_FRONTEND_STAGE_6_EN.md): orthogonal selected-parent connections within each area, arrows, shared trunks and junctions. Separate modules handle search, gaps, geometry and the UI element.
- Cards preserve stage 5 logical positions; required gaps expand locally and columns align across areas. Prohibited intersections and card penetration are checked before rendering.
- Hovering highlights the complete parent path in blue and child paths in orange, including shared sections; sibling branches remain normal. Styling lives in both theme dictionaries; parameters reside in `config/frontend/connections.json`.
- Reports now include `tree.connections`; routing errors carry combination, language and settings context. Added synthetic and browser checks including the real set: 679 cards, 464/463 connections, RU/EN, both themes and logical positions unchanged from stage 5.
- Bumped package and lock-file versions to `0.0.6`. Updated bilingual specifications, the [guide](frontend/FRONTEND_STAGE_6_EN.md), README and links. Databases and backend remain unchanged; no database build was launched.

## 2026-11-19 — tree connection specification draft and gap expansion

- Recorded the agreed expansion of required gaps for lines while preserving logical card positions and minimum padding before Level-0.
- Prepared RU/EN [frontend stage 6 specifications](frontend/TZ_FRONTEND_STAGE_6_EN.md): attachments, shared trunks, routing without crossings, unified field geometry, highlighting, configuration, diagnostics and checks for two prepared combinations.
- Updated the connection element specification and main specification index. The consolidated draft awaits approval; code, databases and version 0.0.5 remain unchanged.

## 2026-11-19 — connection highlighting and bottom exit

- Added the agreed bottom exit to a left trunk when a connection enters from the left to both connection specification versions; parent exits and child entries may use different sides.
- Added card hover highlighting: one color for the immediate parent connection and another for immediate child connections. Documented highlighting of shared trunk segments, clearing and separate styling variables.
- Linked the card specification to the new behavior. Only documentation changed; connection rendering has not yet been implemented.

## 2026-11-19 — left trunk for a mixed branch

- Added the agreed rule to both versions of the [connection specification](frontend/elements/TZ_CONNECTION_EN.md): when a root's left side is free, its own-column children share a left trunk while rightward continuations use its right side.
- Added a diagram and planned check; occupied-side and leftward-transition cases remain open. Only documentation changed.

## 2026-11-19 — tree connection element and attachments

- Added the [connection element draft specification](frontend/elements/TZ_CONNECTION_EN.md): four attachment points, parent connections within a research area, side trunks for multiple children, and a ban on crossings and merging connections from different parents.
- Recorded separate attachment, routing and rendering responsibilities, arrows toward children, junction dots and dictionary styling. Trunk side selection and obstacle routing remain open.
- Added the element to the UI list and updated both language versions. Only documentation changed; code and databases remain unchanged.

## 2026-11-19 — tree grid and frontend 0.0.5

Implemented the approved [stage 5 specification](frontend/TZ_FRONTEND_STAGE_5_EN.md): the grid uses saved parents, children and combination variants. Added layout configuration, separate tree modules, language sorting, starting-root and direct-continuation priority, repeatable technology placement in column 6 and local roots at cross-area links.

Removed independent column sorting and hidden the manual variant picker. Cards and sorting share name lookup; keyboard order follows trees. Added combination/graph contract checks, RU/EN messages and report version 4 with field parameters. Identical starting-flag repetitions are accepted; conflicting values fail.

Passed 49 synthetic tests, verification of two prepared combinations in RU/EN, 16 browser scenarios, TypeScript and the build. All 679 technologies are placed without overlap; opening reads only 35 technology documents. Version raised to 0.0.5. Measurements, completed and skipped checks are in the [guide](frontend/FRONTEND_STAGE_5_EN.md).

## 2026-11-19 — tree order and grid specification draft

- Recorded agreed whole-tree ordering: trees beginning with a starting technology first, then others; current-language name and ID within each group. Starting descendants stay in their branches; cross-area branch starts follow the common order.
- Prepared the [frontend stage 5 specification draft](frontend/TZ_FRONTEND_STAGE_5_EN.md): extracting stored parents/children and combination parameters, configuration, row placement and branch heights, diagnostics and checks. The user chose a prepared-combination stage; manual variant changes and backend calls are deferred.
- Distinguished agreed decisions from proposed technical details. Updated RU/EN rules, README, specification index and tables of contents. Checked links and the current manifest contract; code, product configuration and databases are unchanged, and product tests were not run. The specification awaits approval.

## 2026-11-19 — branches with a parent in another area

- Recorded the [grid rule](frontend/TECHNOLOGY_CHAINS_AND_SORTING_EN.md#single-tree-placement) placing a technology in its own area and column as a branch start when its parent belongs to another area. The cross-area link is not currently displayed or used for geometry; parents, children and prerequisites remain in the data.
- Clarified physics placement for encryption and decryption. Displaying links to all prerequisites is deferred to later stages; the general ordering of multiple trees remains under design.
- Updated RU/EN documentation and tables of contents. Checked internal links and rule consistency; code and databases are unchanged and product tests were not run.

## 2026-11-19 — lower-tier continuation placement

- Recorded the agreed model in the [grid rules](frontend/TECHNOLOGY_CHAINS_AND_SORTING_EN.md#single-tree-placement): a lower-tier continuation retains its column and shares the parent's row where possible; overlap moves its entire branch downward. Added an example with a cell occupied by an ancestor.
- Recorded confirmation of the parents of all ten reviewed technologies. Cross-area encryption and decryption placement remains the next design question; zero-weight and special-acquisition markers are deferred to later stages.
- Updated both language versions and tables of contents. Only documentation changed; code and databases are unchanged. Checked links and wording consistency; product tests were not run.

## 2026-11-19 — branch order and vacant cells

- Recorded branch order taking priority over packing in the [grid rules](frontend/TECHNOLOGY_CHAINS_AND_SORTING_EN.md#single-tree-placement): a side branch cannot fill the parent's row above a same-tier main continuation. Added the agreed example.
- Checked the base combination in the prepared stage 17 set: no multiple digit-stripped ID continuations were found; confirmed 10 links toward a lower display tier, including eight within a research area. Handling these links remains under discussion.
- Updated only RU/EN documentation and tables of contents. Game sources, product code and databases are unchanged; local links were checked, product tests were not run.

## 2026-11-19 — initial tree placement rules

- Recorded agreed display-tier columns, continuation alignment, same-tier vertical placement and reserved child-branch space in the [chain rules](frontend/TECHNOLOGY_CHAINS_AND_SORTING_EN.md#single-tree-placement).
- Direct continuation by digit-stripped ID equality takes priority over alphabetical child ordering. Additional prerequisites remain in the data but are not displayed at this stage.
- Updated both language versions and tables of contents. This is a design clarification: code and databases are unchanged; wording and links were checked, product tests were not run.

## 2026-11-19 — manifests, separate documents and frontend 0.0.4

- Implemented backend stage 17 and frontend stage 4: `config/storage.json`, persistent documents, a manifest indexing all 15 kinds, stable references and separate source/snapshot revisions.
- Removed monolithic merging and the old file-opening route. Added selective readers, streaming hashing, full audits, bounded projection processes and indexed event selection.
- Tree enrichment and localization refresh use immutable versions, root locking and atomic manifest switching. Other combinations are preserved; unchanged documents are not rewritten.
- Frontend 0.0.4 opens a directory and initially reads technologies only. Its internal API supports kind/object/anonymous-root requests with cancellation and retry. Added SHA-256 through `@noble/hashes` 2.4.0, loading states, RU/EN diagnostics and report version 3. Vite ignores the working directory.
- Updated schemas, tests and bilingual guides. All 450 documents and 679 decisions match the reference; checked 206 variants, three combinations, full audit and 14 browser scenarios. Explicit loading of all kinds retained control catalogs and 60 upgrade witnesses.
- Build: 387.885 s; first calculation with publication: 41.126 s; later forced calculation: 22.384 s; reuse: 3.697 s; initial loader opening: 2.601 s. Conditions and limits are documented in the [stage 17 guide](BACKEND_STAGE_17_EN.md).


## 2026-11-19 — manifest and separate database storage draft

- Prepared bilingual drafts for [backend stage 17](TZ_BACKEND_STAGE_17_EN.md) and [frontend stage 4](frontend/TZ_FRONTEND_STAGE_4_EN.md): one processed JSON per source file, an object-index manifest, separate document addresses and set revisions.
- Recorded agreed verification on read, separate full audit and explicit frontend directory opening. Proposed publication by manifest replacement, parallel evidence preparation and loading technology data without mandatory reads of other kinds.
- Specified anonymous objects, `on_actions` fragments, service-reference changes, preservation of localization and combinations, limitations and future tests. Updated README and specification-index links. Only documentation changed; code, configuration, schemas and databases remain unchanged and product tests were not run.

## 2026-11-19 — technology parent and child enrichment implementation

- Implemented the [stage 16 specification](TZ_BACKEND_STAGE_16_EN.md): a standalone Python operation and CLI over 15 prepared databases, 13 separately configured criteria, profiles and combination variants.
- Parents are recorded on objects and children immediately appended to parents; ambiguities receive diagnostics. Localization, original prerequisites and other combinations are retained.
- Added separate input/rule/parameter/result revisions, freshness checking, explicit recalculation, destination locking and atomic publication of the technology database only. Related databases are read sequentially; events are retained only through explicit action routes.
- The generator produces five new schemas; database schema and validation cover enrichment, record placement, reciprocity, cycles and revisions. Added synthetic and actual-data checks, a [guide](BACKEND_STAGE_16_EN.md) and a working database copy.
- All 679 base decisions and 12 control examples matched the reference: 178 roots, 501 parents, no ambiguities or cycles. Checked 206 variants and three combinations; results and timings reside in `data/stage16`.
- Frontend, grid, API and event-based technology acquisition remain unchanged. Original game files and the 14 related databases were not modified.

## 2026-11-19 — parent and child enrichment specification draft

- Prepared bilingual [stage 16 specification](TZ_BACKEND_STAGE_16_EN.md): a standalone Python operation and CLI, extensible rules, variant selection, immediate child updates, per-combination results inside the database, revisions and safe publication of only the technology file.
- Defined acceptance using 679 base technologies, checks for all 206 variants and a proposed diagnostic policy for the 23 variants without explicit `inherit_effects`. The document does not claim a new complete pass or implementation checks have run.
- Updated the specification index, README and agreed approach. Grid, API and frontend work are excluded from this stage. Code and databases are unchanged; the specification awaits approval.

## 2026-11-19 — tree relationship enrichment approach

- Recorded the [agreed approach](TECHNOLOGY_TREE_ENRICHMENT_EN.md): Python parent calculation using prepared databases with immediate child-list updates, per-object results by combination and separate extensible rule configuration.
- Covered combination parameters, separate source and enrichment revisions, future frontend invocation and one object per future MongoDB document. Final schemas, API and grid require a specification; MongoDB migration remains deferred.
- Updated RU/EN documentation; product code, configurations and databases were unchanged.

## 2026-11-19 — preliminary event access analysis

- Following the user's subsequent decision, event analysis was deferred and its findings retained; current work moves to grid design. This decision did not change code or layout rules.
- Additionally inspected Omega Theory: its own ordinary draw depends on researching two mandatory event-gated prerequisites. Extended the proposal to trace indirect dependencies through the full AND/OR graph rather than only the selected parent; checked example events and the special projects invoking them.
- A separate [investigation](frontend/CHAIN_EVENT_ACCESS_EN.md) records the task of accounting for technology access through event outcomes. Inspected direct L-Gate activation access, flag-gated L-Gate insight eligibility and psi drive event access coexisting with a technology prerequisite.
- Described proposed analysis of access, grants and progress, recipient scopes, conditions and alternative routes. Distinguished a test route; event-exclusive acquisition requires further full analysis.
- Updated the chain rules link and Russian documentation. Code, databases and sorting were unchanged; neither a complete event access pass nor in-game verification was performed.

## 2026-11-19 — complete analytical predecessor selection pass

- Completed a [full pass of all agreed criteria](frontend/CHAIN_RULES_FULL_REVIEW_EN.md) across 679 base technologies: 178 roots and 501 uniquely selected parents, including all 89 multiple-requirement cases. No ambiguities or cycles remain; all 12 acceptance examples match.
- Five decisions changed from the previous complete pass. Confirmed alloys' production affinity, Mega-Engineering's starbase capacity affinity, and the terraforming, weaponry and mobile combat ship functional groups.
- Checked input integrity, parents belonging to original requirements, candidate reduction rules and traversal-order independence. Saved research settings, scripts, evidence, traces and an empty ambiguity log with a mode snapshot in `data/chain_analysis/final_review/`.
- Confirmed 19 repeatable technology moves to display column 6; recorded edge properties for future placement. Updated RU/EN documentation. Product code and published databases remain unchanged; variants and card geometry were not tested.

## 2026-11-19 — anti-ship weaponry functional group

- Recorded the approved [weaponry rule](frontend/CHAIN_WEAPONRY_EN.md): weapon components or a confirmed route from an unlocked object through an action and event to ship damage. Routes and types belong in configuration; conditions and sources are retained.
- Checked its impact in isolation across 679 base technologies: only Stellar Cannon receives a different functional group result — UV Lasers. The other 678 candidate sets match; the new edge creates no cycle. Mega-Engineering receiving the group does not change its selection.
- Saved research scripts, report and evidence in `data/chain_analysis/weapon_review/`; updated both language versions of rules and links. Product code and published databases remain unchanged. No complete final pass of all new criteria or variant check was performed.

## 2026-11-19 — functional criterion order comparison and swap

- Performed an [analytical comparison of both orders](frontend/CHAIN_CRITERIA_ORDER_REVIEW_EN.md) across 679 base technologies, recomputing functional evidence and verifying SHA-256 hashes of eight source databases.
- Only Juggernaut changed its parent from Citadel to Battleships; the other 678 have identical candidate sets after the compared rules. Checked absence of new cycles, prerequisite membership and candidate reduction behavior.
- A separate check of 128 area/category combinations also found no changes to other technologies; its scope excludes full variant semantics and effect inheritance.
- Following the user's conditional agreement, placed functional groups before direct relations in RU/EN documents. Research scripts and reports are saved in `data/chain_analysis/order_review/`; product code and databases remain unchanged.

## 2026-11-19 — planet class change functional group

- Added the approved [planet class change group](frontend/CHAIN_FUNCTIONAL_GROUPS_EN.md#planet-class-change) in RU/EN: `terraform_link` type, different `from`/`to` values and technology access requirements in `condition`, retaining their logic.
- Recorded the expected Terrestrial Sculpting → Volcanic Terraforming chain. Both game requirements and the previously agreed placement between branches are preserved; criterion order remains unchanged.
- Extended the transition field dictionary and updated the general chain document and contents. Previous totals are marked as a snapshot preceding the new group; product code, databases and the research algorithm remain unchanged.

## 2026-11-18 — object capacity affinity before empire filtering

- Recorded the approved [object capacity affinity criterion](frontend/CHAIN_CAPACITY_AFFINITY_EN.md) in RU/EN: a technology's own bonus is linked to an object using that capacity and the technology unlocking it.
- Placed the rule after production bonuses, immediately before the empire filter. Recorded configurable field mappings and the expected Citadel → Mega-Engineering chain after the empire profile excludes the nomadic candidate.
- Aligned the overall order, production criterion document and effects dictionary. Previous totals remain a snapshot preceding both new rules; product code, databases and the research calculation were not changed.

## 2026-11-18 — production affinity before empire filtering

- Recorded the approved [production bonus criterion](frontend/CHAIN_PRODUCTION_AFFINITY_EN.md) in RU/EN: a technology's own modifier is linked to an economic category, jobs and objects unlocked by a candidate.
- Placed the criterion immediately before the empire filter. Updated the overall order, dictionary links and the Ceramo-Metal Alloys → Holographic Casts example.
- Documentation changes only; prior totals are marked as a snapshot preceding the new rule. Product code, research calculations and databases were not changed.

## 2026-11-18 — analytical predecessor rule review

- Reviewed 679 base technologies in the current database set. Of 89 technologies with multiple prerequisites, 86 received one candidate; three ambiguities remain and two expected-chain mismatches were identified.
- Added findings, causes and coverage limits to the [chain research](frontend/TECHNOLOGY_CHAINS_AND_SORTING_EN.md#current-rule-set-review). Separately checked 128 combinations of seven area/category-changing variants for the first four criteria.
- Saved research calculations, current-data projections, evidence and traces under `data/chain_analysis/current_review/`. Rules, product code and published databases were not changed; no manual parent assignments were introduced.

## 2026-11-18 — ambiguity log with field snapshot

- Recorded the user's clarification in RU/EN: manual predecessor selection is deferred; ambiguous technologies enter a [log with field state and settings](frontend/CHAIN_AMBIGUITIES_EN.md).
- Defined record contents, candidates and selection traces, and a snapshot of mode, representations, language and effective settings at calculation time. Original context is preserved across later changes and report export.
- Updated general chain rules. Documentation changes only; logging is not implemented yet, and code, configuration and databases remain unchanged.

## 2026-11-18 — indirect functional affinity

- Recorded the approved [indirect affinity criterion](frontend/CHAIN_INDIRECT_AFFINITY_EN.md) in RU/EN: configurable search through a candidate's original prerequisites with an initial depth of one transition.
- Defined condition preservation, selection of the candidate itself, the shared filtering procedure and the armor example using a matching modifier. Linked the rule from general rules, functional groups and the effect dictionary.
- Documentation changes only. Code, configuration, databases and layout remain unchanged.

## 2026-11-18 — technology functional groups

- Recorded the approved [functional group rule](frontend/CHAIN_FUNCTIONAL_GROUPS_EN.md) in RU/EN: definitions through configurable object features, technology group sets and candidate selection by a shared group.
- Added the checked battleship, juggernaut and citadel example, classification boundaries and links from general chain rules and the effect dictionary.
- Documentation changes only. Code, configuration, databases and layout remain unchanged.

## 2026-11-18 — direct functional object relations

- Recorded the approved [functional relation criterion through unlocked objects](frontend/CHAIN_DIRECT_RELATIONS_EN.md) in RU/EN: using or enhancing a candidate's object while retaining conditions and sources.
- Defined exclusion of costs, resource consumption and AI weights, the shared selection procedure and the dark matter detector example. Linked the rule from the dictionary and general rules; marked the former L-10 order as historical and subject to the current design refinements.
- Documentation changes only. Code, configuration, databases and layout remain unchanged.

## 2026-11-18 — availability condition matching rule

- Recorded the approved [criterion for complete matching of nonempty `potential` blocks](frontend/CHAIN_AVAILABILITY_EN.md) after expansion, retaining condition structure and excluding provenance metadata from comparison.
- Described selection results, skipping empty results, criterion boundaries and the religious technology example. Linked it from general chain rules and the empire condition dictionary; updated Russian documentation.
- Code, configuration, databases and current layout remain unchanged.

## 2026-11-18 — direct object upgrade rule

- Recorded the approved predecessor criterion using `upgrades` and `upgrades_to` in a separate bilingual [document](frontend/CHAIN_DIRECT_UPGRADES_EN.md), including subtraction of shared mandatory requirements for comparison only.
- Defined filtering of remaining candidates, skipping empty results, retaining witnesses without counting them as votes, and boundaries for complex logic. Added examples and links from the general chain document and dictionary.
- Documentation changes only; code, configuration and databases remain unchanged.

## 2026-11-18 — construct dictionary for technology analysis

- Created a bilingual [dictionary](semantics/README_EN.md) in `Docs/semantics/`: six sections grouped by construct purpose and a shared index.
- Recorded context, value forms, game meaning, analytical use and sources. Conditional variants, identically named fields, hidden checks and forms of `custom_tooltip` are described separately.
- Linked the dictionary from README. This is reference documentation for subsequent design; code, configuration, databases and historical `language/keywords/` inventories remain unchanged.

## 2026-11-18 — working data cleanup preparation

- The last successful complete stage 15 run is the reference: checksums of all fifteen files in `data/databases/` match `data/stage15/rebuilt/acceptance.json`.
- `data/reports/history_cleanup.json` records a plan to remove 2876 historical and temporary files totaling 23.99 GiB. Current databases, reports, libraries, runtime tools, final verification results and chain research used by the frontend test are preserved.
- Automatic approval rejected both the bulk deletion and a narrower attempt to delete two duplicate build directories with `blocked by policy`. No files were deleted; the plan has status `blocked`. Code and configuration are unchanged.

## 2026-11-18 — parallel file processing implementation

- Added a shared pool of separate Windows processes for files of one database, reused across fifteen sequential database builds. `config/parallel.json` controls worker count (`10` by default) and intermediate storage; added the 23rd generated schema.
- Workers load libraries and prepare rules once, reuse localization tables and resolved texts, and isolate variables, history and job statistics. Cumulative call numbering is preserved through coordinator-assigned offsets.
- Documents are validated and written separately. The coordinator checks completeness, duplicates and checksums, then streams JSON together in original order without reparsing. This shared mechanism replaces the former sequential writer; `workers=1` uses the same path.
- Introduced `sttv.document_hashes.v1`; `set_id` changes while game-document format remains version `6`. Added job, initialization, phase, memory and temporary-file measurements, worker-failure handling and cancellation with cleanup restricted to operation-owned files.
- All 240 backend tests and 33 frontend checks passed without skips. Three complete builds (`1/reuse`, `10/reuse`, `10/rebuild`) are byte-identical and preserve stage 14 content except for the new `set_id`; game counters, diagnostics and hashes of 1612 reference inputs match. Each of the 450 documents was validated once.
- Complete `reuse` time fell from 34:44 to 8:20 (4.17 times faster); ten-worker `rebuild` took 8:31. Process-tree peak memory increased from 4.09 to 21.34 GiB. The fixed sample's three-pass median fell from 20.516 to 8.225 s, with all six outputs identical. Measurement conditions and limits are recorded in the [stage 15 guide](BACKEND_STAGE_15_EN.md).
- Updated bilingual specifications, guide and README. Game sources and the frontend were not modified.

## 2026-11-18 — parallel file processing draft

- Prepared the bilingual [stage 15 specification](TZ_BACKEND_STAGE_15_EN.md): ten workers within the current database and pool reuse across fifteen sequentially built members.
- Defined configuration, worker loading of prepared libraries, independent document contexts, validation before writing and streaming intermediate JSON merging in fixed order.
- Specified cross-document checks, revised `content_hash` derived from document hashes, implications for `set_id`, failure handling, measurements and `1`/`10` comparison.
- Updated shared specification and README links and status. Code, configurations and schemas are unchanged; the new specification awaits approval.

## 2026-11-18 — reusable element libraries implemented

- Implemented five persistent libraries, a shared manifest, content/rule freshness verification and explicit `--rebuild-libraries` and `--reuse-libraries` modes.
- Library contents, sources, reading options and destinations are configured in `config/libraries.json`; duplicate parser settings were removed. Added four generated schemas.
- Prepared tokens, parameters and constant trees are reused during expansion. Invocation state and results remain independent; one snapshot serves the complete dataset set and analytical operations.
- Added persistence, integrity, freshness, mode, ownership and context-isolation checks. Checked 231 unique backend tests; 33 frontend checks passed without skips, as did an analytical invocation using saved libraries.
- Both modes built fifteen databases byte-identical to stage 13: 450 documents and 11,762,739,507 bytes. The `set_id`, hashes of 1,612 game/localization inputs, logical counters and statuses were preserved.
- Full builds took 29.4 minutes in `rebuild` and 33.9 minutes in `reuse`, versus the 34.4-minute reference; peak memory was 2.04 and 2.50 GiB versus 1.65 GiB. Library JSON totals approximately 511 MiB. `reuse` loaded five artifacts without plan preparation; one snapshot served all fifteen databases. Mode timing differences and measurement limits are recorded in the guide.
- Commands, architecture and results are in the [stage 14 guide](BACKEND_STAGE_14_EN.md). Game sources and the interface were not modified.

## 2026-11-18 — reusable element library draft

- Prepared the bilingual [stage 14 draft](TZ_BACKEND_STAGE_14_EN.md) for inline templates, effects, triggers, script values and supporting shared static definitions. The snapshot persists as JSON and serves every dataset in one operation.
- Specified separate library/address configuration and explicit mutually exclusive `--rebuild-libraries` / `--reuse-libraries` switches. Failed reuse never triggers a hidden rebuild; source, configuration, version and artifact-integrity checks are required.
- Described immutable plans, separate call state, parameters and conditional fragments, nesting, provenance, validation and measurements. Multiprocessing remains a later stage; the fifteen user-facing databases retain their format.
- Updated links and status in RU/EN README and the shared specification. Only documents changed; code, configurations and databases were not modified. The draft awaits approval.

## 2026-11-18 — validation and build optimization implemented

- Implemented approved stage 13: checks prepared from the active schema once per operation, direct `kind` dispatch and a shared traversal of structure, provenance and localization. Unknown schema constraints are rejected; no game command registry is introduced.
- Single and set builds now process, localize, validate and write documents individually. Real addresses, cross-document duplicate indexes, cumulative counts and canonical hashes are preserved. Removed repeated complete audits and rereading unchanged temporary databases.
- Added phase, rule preparation and document validation measurements to reports and their schemas. Initial write failure cleans the temporary file; validation diagnostics include the source file. A single-build report is saved once after measuring database publication, with truthful `database_written` on failure.
- Complete build: 2061.189 s instead of 5490.835 s, a 2.66× speedup, with peak process working set of 1.65 GiB. All fifteen databases, the shared `set_id` and 1625 inputs match the control; 450 documents were validated once. Six control examples show 2.50–6.08× faster validation using medians of three runs.
- Passed 213 backend tests, 33 frontend checks and a real browser opening of fifteen files: 679 cards, language and theme changes, tooltip and variants. Source warnings are retained. Detailed results and limitations are in the [stage 13 guide](BACKEND_STAGE_13_EN.md); acceptance artifacts reside under `data/stage13/`.
- Updated README, specification status and the bilingual guide. Database format, game sources and interface behavior were not changed.

## 2026-11-18 — validation and build optimization draft

- Prepared the RU/EN [stage 13 specification draft](TZ_BACKEND_STAGE_13_EN.md): direct `kind` dispatch, one rule source prepared once, a shared traversal and document processing. Status: discussion and approval.
- Complete validation of finished documents remains part of builds; repeated validation of unchanged output after writing is removed. Specified preservation of checks, addresses, cross-document duplicate detection, hashes and formatted JSON, together with publication failure behavior.
- Defined measurements, schema-oracle comparisons, negative tests and a fifteen-database acceptance build. MongoDB, parallel execution and game-data changes are excluded.
- Updated README links and shared specification status, including completed stage 12. Product code, configurations and published databases were not changed; speedup has not yet been measured.

## 2026-11-18 — fifteen databases and streaming reads

- Implemented the shared registry of fifteen roles, twelve additional sources and separate localization configurations. Database version is now 6; JSON uses LF newlines and two-space indentation.
- Preserved all terraforming transitions, handler fragments and conditional event descriptions; added event IDs and compact catalogs for new roles.
- Connected scoped import exceptions, case-insensitive parameters, structural expansion of effects with `no`, and common static declarations in mixed environments. Every exception application is reported.
- Frontend 0.0.3 opens fifteen files as one set. After confirming the `File.text()` limit, the user approved streaming JSON: two passes, document adaptation, released trees and deferred cross-reference checks.
- Updated schemas, RU/EN messages, guides, tests and diagnostics. All 203 Python checks, 31 controlled frontend tests, two real-data tests and browser scenarios passed, including opening the complete set. Game files were unchanged; new sorting rules are not enabled.
- Published fifteen databases: 450 documents, 15,599 definitions, 22,345 localization targets and 10.95 GiB. Building took 91.5 minutes; opening in Chromium took 264.60 seconds with no page errors. All 679 cards, languages, themes, tooltips and variants were verified. The index retains 214 missing-localization warnings; stage guides contain detailed reports and limitations.

## 2026-11-18 — conditional import exceptions

- Prepared `config/parser/source_exceptions.json`: a narrowly matched trailing separator removal, binding `RELIC` to `SELECTED_RELIC` for two events, and temporary `RANDOM = 0` in nomad calls. Three rules are restricted to four root sources and explicit conditions.
- The [bilingual addendum](SOURCE_IMPORT_EXCEPTIONS_EN.md) and stage 12 specification record the agreed case-insensitive parameters, exception integration and mandatory application reporting. Proposals for `effect = no` and mixed static environments are described separately.
- Traced the `effect = no` restriction to the stage 8 specification and expander, independently of the removed command registry. The new rules file is not wired yet; product code, active settings and published databases are unchanged.

## 2026-11-18 — confirming seven stage 12 blockers

- Rechecked seven complete files from the historical list with the current parser: all seven reproduced previous errors representing six causes. Results, call chains and the reproduction script reside in `data/stage12/problem_recheck/`.
- Three separate Shroud trigger calls confirmed a resolver limitation: two environments resolve globals identically to 1500/3000/5000, but their tuple is rejected before lookup.
- Added a [bilingual research report](RESEARCH_STAGE_12_BLOCKERS_EN.md) and updated the stage 12 obstacle section. Distinguished source discrepancies, parser limitations and unverified engine behavior.
- Hashes confirmed unchanged consumed inputs, backend code, configuration and published databases. No fixes or stage 12 implementation were performed; each file stopped at its first error.

## 2026-11-18 — draft extension to 15 databases

- Drafted RU/EN [backend stage 12](TZ_BACKEND_STAGE_12_EN.md) and [frontend stage 3](frontend/TZ_FRONTEND_STAGE_3_EN.md): 12 new databases, localization and opening the shared 15-file set. Status: awaiting approval.
- Specified source variables, distinct identity/text rules, repeated terraforming transitions, technical handlers and event descriptions.
- Included the user's multiline, two-space-indented JSON requirement; separated canonical hashing from output formatting.
- Parsed 332 TXT files initially without call expansion; no syntax errors were found. Results reside in `data/stage12/specification_research/source_inventory.json`. Seven expansion errors from the historical report are listed for rechecking, without claiming they were fixed.
- Updated README and general specification links. Product code, configuration and published databases were not changed in this iteration.

## 2026-11-18 — alloy production branch and ordering within a branch

- With user agreement, changed the Ceramo-Metal Alloys anchor to Holographic Casts and recorded the display chain Holographic Casts → Ceramo-Metal Alloys → Armor Hardening while preserving all other game requirements.
- Clarified R-05/L-04: vertical predecessor/continuation ordering applies within one branch, rather than to every cross-branch link. Volcanic Terraforming between two branches is no longer described as a specific exception.
- Aligned related wording in both chain documents. Historical reports remain snapshots of previous research runs; product code was unchanged.

## 2026-11-18 — anchor clarification and placement between prerequisites

- Recorded Ceramo-Metal Alloys as the Armor Hardening anchor, matching special availability for Metacognitive Faith, and candidate seniority for Cross-Model Standardization.
- Following the user's explicit clarification, Volcanic Terraforming is placed vertically between its prerequisites; R-05/L-04 now include this exception while preserving game dependencies.
- Confirmed `ship_armor_hardening_add` in both the Armor Hardening component and an armor component reached through a Ceramo-Metal Alloys predecessor in the component database. Recorded indirect functional selection as a hypothesis distinct from the agreed anchor choice.
- Updated RU/EN documentation and saved `data/chain_analysis/armor_function_evidence.json`. Confirmed two candidates for each of the nine previous ambiguities, while original sets contain up to five. Production sorting was unchanged.

## 2026-11-18 — reviewing proposed continuations for nine technologies

- Recorded seven user-proposed anchors and two conditional placements below multiple predecessors; inspected game definitions and five branch pairs against the database graph.
- Distinguished sequential chains, common ancestors and converging branches. Confirmed no sequential dependency between Armor Hardening candidates or Volcanic Terraforming candidates; described the separate constraint of placement below both prerequisites.
- Clarified the federation exception for religious technology access, the production effect of Ceramo-Metal Alloys, and the robotics functions of both Cross-Model Standardization candidates.
- Updated the bilingual chain document and saved `data/chain_analysis/nine_case_review.json`. Preferences are not presented as completed general criteria; production sorting and the earlier report were unchanged.

## 2026-11-18 — extended chain rules reanalysis

- Rechecked 679 technologies in the current three-database set, including 89 with multiple prerequisites. Confirmed that the published set matches `data/stage11/browser_set`.
- Recorded the user-confirmed standard empire profile for the run; unknown conditions do not exclude candidates. Added research checks for L-11 and L-13 with early termination at one candidate and preservation on empty filter results.
- Twelve cases remain without a general automatic choice, or nine after incorporating three previously agreed functional continuations. The new filters resolved four of the previous thirteen; L-12 moves nineteen technologies to column 6.
- Saved reproducible scripts and a step-by-step JSON report in `data/chain_analysis/`; passed 27 checks and examined criterion order sensitivity. Updated both language versions of the chain document; product code and databases were unchanged.

## 2026-11-18 — removed repeatable technology area restriction

- Following the user's clarification, L-12 requires any technology prerequisite, without matching research areas. The `levels = -1` and `tier = 5` conditions remain.
- The number of technologies for column 6 increased from 17 to 19, now including both strike craft repeatables. Their area remains society and their prerequisite remains in engineering. L-13, selecting the highest-tier candidate, is unchanged.
- Updated RU/EN and contents; sorting code and databases are unchanged.

## 2026-11-18 — infinitely repeatable technology placement

- Added L-12/L-13: move infinitely repeatable game-tier-5 technologies with a prerequisite in their own area to display column 6, and prefer the highest game-tier candidate when selection is ambiguous. Clarified the exception to matching display columns with game tiers; original fields and dependencies are preserved.
- Under the initial rule, 17 of 21 infinitely repeatable technologies met the move condition. Recorded four exceptions, including two strike craft technologies with a prerequisite in another area. For both explosive weapon repeatables, the higher of the two prerequisites is tier-4 `tech_swarmer_missiles_2`.
- Updated both document languages and contents. These are design changes; sorting code, databases and the previous full analysis report are unchanged.

## 2026-11-18 — standard empire path in reference mode

- Added chain rule L-11: resolve ambiguity in reference mode by excluding candidates that require nonstandard empire types and preferring the standard empire's path.
- Recorded the Juggernaut example, preservation of original requirements, the general empty-result skip procedure, and future tree recalculation based on a user-defined empire. The full parameter set and exact filter precedence remain design questions.
- Updated both language versions and their contents. Code, databases and previous numerical analysis results are unchanged.

## 2026-11-18 — selection procedure and functional continuations

- Explicitly recorded stopping at one candidate, skipping rules with empty results and never restoring previously eliminated candidates in the chain document.
- Recorded three desired anchors: arkship construction for civilian arkships, the detection array for dark matter detection, and UV lasers for the Stellar Cannon. Documented supporting vanilla code relationships and proposed a final selection group based on direct relationships and the function of unlocked objects.
- Identified the additional sources required for automation; functional classification is still being designed, and production sorting and database coverage are unchanged. The research script now explicitly skips evaluating subsequent criteria after reaching one candidate; previous numerical results are preserved.

## 2026-11-18 — ID priority for technology chain selection

- Recorded the chain-selection order: equal IDs after removing digits → research area → category → previously agreed mandatory-prerequisite priority. All game dependencies remain intact.
- Checked the published three-database set through current adapters: 679 base technologies, including 89 with multiple prerequisites. The first three criteria leave 22 ambiguities; mandatory status leaves 19; additionally using explicit object upgrades leaves 16. Within the previous 39 cases, the corresponding remaining counts are 19, 16 and 13.
- Saved the reproducible analysis, input file hashes and step-by-step decisions in `data/chain_analysis/audit_id_priority.ts` and `id_priority_analysis.json`. Frontend sorting code is unchanged; geometric placement rules were not tested by this analysis.

## 2026-11-17 — database set implementation and interface 0.0.2

- Implemented approved backend stage 11 and frontend stage 2. Added `COMPONENTS_DIR`, `BUILDINGS_DIR`, a shared three-database coordinator, set configuration and generated schemas.
- Updated database format to version 5: member roles and a deterministic shared `set_id`. All members are prepared and input integrity verified before publication; reports record actual partial writes on failure. Databases use compact JSON without removing data.
- Extended RU/EN localization to components and buildings: identities from `key`, explicit shared `component_set` descriptions, and separate conditional building descriptions. Individual set-member enrichment is rejected.
- Interface `0.0.2` opens three files in one action. The Worker retains full trees and returns compact catalogs, qualified references, a shared string index, object requirements, upgrades and technology-continuation evidence.
- Updated progress, retry and cancellation, RU/EN messages, diagnostic export version 2 and tests. Upgrade evidence does not invent technology prerequisites or change the current card layout.
- Invocation and validation results: [backend](BACKEND_STAGE_11_EN.md), [frontend](frontend/FRONTEND_STAGE_2_EN.md).


## 2026-11-17 — specifications for a three-database localized set

- Prepared separate RU/EN backend-stage-11 and frontend-stage-2 specifications for approval: technologies, components and buildings, full standard expansion, localization and joint opening of three JSON files.
- Recorded user answers: one selection of a three-file set, with immediate RU/EN names and descriptions for all three databases. Investigated ID shapes, localization suffixes and conditional building descriptions; saved the research inventory under `data/stage11/specification_research/`.
- Proposed configurable source sets, a shared deterministic content identifier, qualified references, shared component descriptions and retained conditional building descriptions; specified explicit object links and separate evidence of technology continuations.
- Updated README, main specification and chain-document pointers. A new layout algorithm and build/interface implementation are outside this iteration; runtime configurations and databases were unchanged.

## 2026-11-17 — mandatory prerequisites and additional databases

- Recorded approved rule L-08 in the RU/EN chain document: among area/category candidates, a mandatory prerequisite takes priority over an optional `OR` member; multiple mandatory candidates remain ambiguous.
- Added the five pairs selected by this rule. Updated the research: including object upgrades and effects, 26 of 39 cases now have a basis for selection, with 13 still ambiguous.
- Recorded the next scope: separate component and building databases in the backend, with frontend support for three databases. Shared parsing and source addressing are outlined as the basis for a separate specification; code, databases and current sorting were unchanged.

## 2026-11-17 — analysis of 39 ambiguous continuations

- Prepared a bilingual [analysis of all 39 cases](frontend/RESEARCH_AMBIGUOUS_CHAINS_EN.md) with multiple same-area/category prerequisites: examined graph structure, tiers, actual modifiers, eligibility restrictions and logical alternatives without comparing names or ID fragments.
- Tested independent-branch preservation locally and globally: found unique structural choices in 19 and 18 cases respectively, including a combat-computer counterexample. No new algorithm was approved.
- Additionally read 83 component and building files; found 60 explicit upgrade witnesses for 16 technologies. Separately checked external changes to capital-productivity effects. Supplemental scan limitations are documented; these data were not added to the current database.
- Research scripts and JSON extracts are saved in `data/chain_analysis/`; links were added to the rules document. Product code, the source database and game files were unchanged.

## 2026-11-17 — initial tree layout rules

- Added the user's six rules on starting technologies, alphabetical ordering, vertical and horizontal continuation, and empty space beneath branches to the bilingual [chain and sorting document](frontend/TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- Recorded the clarification that alphabetical sorting uses the name in the current language, so RU/EN may change the layout. Added preference for a prerequisite matching both `area` and `category`.
- Checked categories of 679 base technologies and 89 objects with multiple predecessors: 44 have one matching candidate, 39 have several, and 6 have none. Saved examples, open questions and `data/chain_analysis/category_analysis.json`; noted eleven category overrides in variants. The implementation and database were unchanged.

## 2026-11-17 — chain rules document and starting technologies

- Created a bilingual [chain and sorting working document](frontend/TECHNOLOGY_CHAINS_AND_SORTING_EN.md) for collecting rules: baseline requirements, approaches under discussion and open decisions are recorded. No new algorithm was approved or implemented.
- Prepared a complete bilingual [starting technology list](frontend/STARTING_TECHNOLOGIES_EN.md): 42 unique objects with `start_tech = yes`, five with `no`, `starting_potential` conditions, tiers and source links.
- Saved the extract to `data/chain_analysis/starting_technologies.json`; all 50 field occurrences were checked against the installed game. Identified four tier-one starting technologies and eleven starting technologies with predecessors. The database, sorting and game files were unchanged.

## 2026-11-17 — technology chain research

- At the user's request, examined all 679 base technologies and 615 links in the prepared database; product code and sorting were unchanged.
- Identified components, linear fragments, and numeric family candidates; examined branches, additional requirements, alternatives, and tier/area transitions separately.
- Identified why chains are not aligned: the current layout sorts columns independently. Found 193 same-tier links and 13 transitions toward smaller `tier` values for subsequent design to address.
- Added bilingual [chain research](frontend/RESEARCH_TECHNOLOGY_CHAINS_EN.md). The research script, complete lists, and independent verification reside in `data/chain_analysis/`; before/after database hashes match.

## 2026-11-17 — first frontend implementation

- Implemented frontend `0.0.1` with React/TypeScript/Vite: UI components, research-area/tier card field, menu, and status panel. Under user clarification, cards do not draw connecting lines yet.
- Added explicit prepared JSON opening, Worker processing, a compact catalog with requirements/links, cancellation/retry, stale-reply protection, and report saving. Startup and refresh never invoke the generator.
- Connected shared source/language/ID localization lookup, the RU/EN index with provenance, warnings, and blocking conflicts. Cards display names, tooltips display names/descriptions, and game strings remain literal.
- Implemented manual variants, localized suffixes for matching titles, movement between areas, two themes, menu collapse, keyboard control, and both scrollbars. Oversized tooltips scroll through the wheel over their card.
- Added interface configuration and styling dictionaries; Inter and SVG icons are local. Added npm configuration, lock file, and ignore rules for dependencies/Sites working data. Node.js and the test browser were prepared only under `data/`.
- Additionally agreed: negative technology requirements stop opening with diagnostics until their counting/layout rules are designed.
- Checked the production build, 16 unit scenarios, and 10 browser scenarios. Real database result: 679 technologies, 206 variants, 615 links, 3,400 string addresses; main-thread catalog size is 2,308,044 bytes without errors or warnings. Screenshots of both themes, a tooltip, and the variant list were visually reviewed.
- Added the bilingual [first frontend guide](frontend/FRONTEND_STAGE_1_EN.md), updated README and the relevant specifications. Game sources and databases were not changed; persistence and portable packaging are outside this stage.

## 2026-11-17 — localized diagnostic messages

- Recorded agreed RU/EN texts and `sttv_diagnostic_<code>` IDs for all seven current codes in the diagnostics specification. Strings use the `builtin` source and empty `params`.
- Code-to-ID mapping resides in diagnostic configuration; translations remain in separate localization files. The missing-translation warning remains in diagnostics and does not replace the successful-load message with the technology count.
- Updated both languages of the diagnostics, status panel, and frontend structure specifications. Only documentation changed; product implementation, configuration, and localization files were not created.

## 2026-11-17 — diagnostic technical detail contents

- Documented agreed `details` contents for all seven current codes; specific paths, IDs, and technical causes are retained in report details.
- Conflicting text provenance reuses the existing `origins` structure associated with each text. All current codes supply `params: {}`; short messages are selected by code without substitutions.
- Updated both languages of the diagnostics, database opening, Worker protocol and result, localization, localization index, and report saving specifications. Product code and data were not changed.

## 2026-11-17 — backend and frontend validation responsibilities

- The database opening specification assigns validation of the produced database to the backend. The frontend retains file-reading and JSON handling, format and version checking, and diagnostics for the adapter's own transformations.
- Aligned the adapter, diagnostics, and Worker result specifications: a repeated schema traversal of the complete database is not required; `invalid_database` refers to inability to perform a transformation, while a shared localization index conflict remains a preparation error.
- Updated both documentation languages and contents. Product code and data were not changed.

## 2026-11-17 — diagnostic report saving

- Added the bilingual [report saving specification](frontend/TZ_DIAGNOSTIC_REPORT_EN.md): manual JSON export of the current completed attempt for external viewing, eight report fields, and `ready`/`empty`/`error` outcomes.
- Added Save report to menu requirements for Ready, Empty catalog, and Error, including success without warnings. It uses the existing Button and is hidden before opening and during loading. An integrated diagnostic viewer, history, and automatic logging are deferred.
- Synchronized diagnostics, database opening, the Worker protocol, structure, menu, status panel, concept, and README. Only documentation changed; code, the database, and backend reports were not modified.

## 2026-11-17 — diagnostics and error response

- Added the bilingual [diagnostics specification](frontend/TZ_DIAGNOSTICS_EN.md): shared `severity`, `code`, `phase`, `params`, and `details` record and seven initial codes.
- Defined an `error` response with one blocking cause and accumulated warnings; `ready.data.diagnostics` contains only warnings. Received diagnostics remain in the main thread after Worker termination, and a Worker failure becomes `worker_failed`.
- Synchronized the Worker protocol and result, database opening, localization and its index, status panel, concept, and README. Only documentation changed; exact nested detail schemas, viewing, and report saving remain separate tasks.

## 2026-11-17 — localization index records and data errors

- Added the bilingual [localization index record specification](frontend/TZ_LOCALIZATION_INDEX_EN.md): `status`, `text`, `origins`, translation provenance, inheritance, and a shared format for database and built-in strings.
- Established `resolved`/`missing` states, identical-text merging, and handling of `null` and empty strings. Differing texts under one ID and language block data preparation and require manual investigation; the `conflict` state and substituting a marker for this error are excluded.
- Synchronized the localization, Text element, Worker result and protocol, adapter, and database opening specifications, concept, and README. Only documentation changed; code and the database were not modified.

## 2026-11-16 — technology requirement tree and links

- Added the bilingual [technology requirements specification](frontend/TZ_TECHNOLOGY_REQUIREMENTS_EN.md): `technology`/`group` nodes, an `AND` root, nesting preservation, and counting for mandatory requirements and `AND`/`OR` alternatives.
- Defined `from`/`to` links with `requirementPaths`, one entry per ID pair, and preservation of all occurrences through derived-tree paths. The structure supports five known operators; counting and layout for `NOT`, `NAND`, and `NOR` remain subject to separate agreement.
- Synchronized result, adapter, protocol, database opening, and technology field specifications, the concept, and README. Only documentation changed; the source database and code were not modified.

## 2026-11-16 — ready container and technology catalog model

- Added the bilingual [Worker result specification](frontend/TZ_WORKER_RESULT_EN.md): `data.technologies`, `links`, `localization.ru/en`, and `diagnostics`; defined technology fields, including derived `prerequisiteIds` and `requirementCount`.
- Established `base` and `swap:N` representation IDs, matching `variantNumber`, string `sourceRef` paths within the current database, and connection of the localization index as source `database`.
- Synchronized adapter, protocol, and database opening specifications, the concept, and README. Marked the model as partial: requirement nodes, link entries, localization records, and diagnostics still require agreement. Only documentation changed; code and the database were not modified.

## 2026-11-16 — Worker protocol for database opening

- Added the bilingual [Worker protocol specification](frontend/TZ_WORKER_PROTOCOL_EN.md): `open_database`, `progress`, `ready`, `error`, shared `type` and `operationId` fields, three processing stages, and publication of the complete prepared result.
- Established response relevance checks by operation number and Worker, cancellation through `terminate()` without acknowledgement, new numbers for retry and replacement, empty-catalog and error distinction, and message localization through stage identifiers and error codes.
- Updated database opening, technology stack, and structure specifications, the concept, and README. The nested `ready` format, detailed diagnostics, and result types remain the next step. Only documentation changed; protocol implementation and checks have not been performed yet.

## 2026-11-16 — frontend structure and resource locations

- Added the bilingual [frontend structure specification](frontend/TZ_STRUCTURE_EN.md): responsibilities of `app/`, `ui/`, `views/`, `data/`, `workers/`, `localization/`, `locales/`, `styles/`, and `assets/`; UI kit categories follow the existing catalog.
- Established component-adjacent CSS, the shared dictionary in `styles/`, configurations in `config/frontend/`, separation of the localization mechanism from translation files, and separation of processing code from the database working directory.
- Clarified data processing and Worker communication boundaries. Updated the concept, technology stack, localization, and styling specifications, and README links. Only documentation changed; no implementation directories, code, or dependencies were added.

## 2026-11-16 — frontend technology stack

- Added the bilingual [technology stack specification](frontend/TZ_TECH_STACK_EN.md): React, TypeScript, plain CSS, and Vite; current-session state uses React's built-in facilities.
- Established independent database processing modules in the Worker, component responsibilities, separate TypeScript type checking, and future development and build acceptance criteria.
- Updated the interface concept, database opening specification, general specification, and README. The `src/frontend/` structure and exact interfaces remain the next design step. Only documentation changed; no code or dependencies were added.

## 2026-11-16 — status panel and database actions in the menu

- Added the bilingual [Status panel specification](frontend/elements/TZ_STATUS_PANEL_EN.md) and its UI element list entry. The panel remains visible across the full window width at the bottom, occupies its own space, and uses shared Text and its own styling dictionary variables.
- Open database, Cancel, and Retry actions reside in the menu above language selection and appear according to current state; collapsing the menu hides them. Bottom menu buttons retain their responsibilities.
- Moved messages from the workspace to the status panel; the field appears only in Ready. The ready message receives the actual base technology count. The menu and viewport sit above the panel without scrollbar overlap.
- Synchronized the concept, database opening, menu, main window, viewport, and styling dictionary specifications. Only documentation changed; interface implementation and checks have not been performed yet.

## 2026-11-16 — loading states, cancellation, and database replacement

- The [database opening specification](frontend/TZ_DATABASE_OPENING_EN.md#interface-states) now establishes five states, stage display without percentages, and complete data publication after success. Language, theme, and menu collapse remain available during processing.
- Distinguished file-dialog cancellation from active-load cancellation. Described Worker termination, stale-result rejection, replacement without retaining or automatically restoring the previous tree, and resetting representations and scrolling while preserving shared interface settings.
- Described blocking errors, nonblocking missing localization strings, and explicit retry for the same file. Extended acceptance criteria and synchronized the concept and main-window, adapter, and localization specifications in both languages. Only documentation changed; behavior checks will follow implementation.

## 2026-11-16 — prepared database reading and adapter in a Web Worker

- Extended the [database opening specification](frontend/TZ_DATABASE_OPENING_EN.md): the browser's standard dialog, File API, JSON reading, and a TypeScript adapter in a Web Worker. Viewing a prepared database does not require a Python service.
- The complete tree stays in the Worker; the interface receives the catalog, requirements and links, and the RU/EN index. Recorded Worker-side `sourceRef` resolution and separation of processing modules from file reading, the DOM, and messaging.
- Added processing-boundary checks and measurements of opening time, memory, and responsiveness with the actual database to acceptance criteria. Synchronized the adapter, localization, main-window specifications, concept, and general distribution section. Only documentation changed; implementation and measurements were not performed.

## 2026-11-16 — explicit database opening and initial interface startup

- Added the bilingual [startup and database opening specification](frontend/TZ_DATABASE_OPENING_EN.md): startup and page refresh load the interface, and the user explicitly selects a prepared JSON through Open database.
- In-memory catalog, requirement, and localization-index preparation is separated from database generation and enrichment. Game-source reading, automatic file opening, and a database update button are outside the first stage.
- Portable packaging is deferred; whether viewing needs a Python service and where the adapter executes remain open decisions. Synchronized the interface concept, adapter and main-window specifications, and the general distribution section. Only documentation changed.

## 2026-11-16 — database adapter specification for the interface

- Added the bilingual [Database adapter specification](frontend/TZ_DATABASE_ADAPTER_EN.md): an in-memory catalog keyed by base IDs, tier, technology requirement trees, representations, and source-node references. Defined effective representation areas, string IDs, and variant numbering without merging identically named blocks.
- Separated extraction, shared predecessor and requirement-count calculation, localization, layout, and user state. `prerequisites` logic is preserved; matching variants across database builds remains a state-persistence responsibility.
- Synchronized links and wording in the concept, Card, and Technology field specifications in RU/EN; added acceptance criteria. Only documentation changed; the source database and code were not modified.

## 2026-11-16 — shared localized string lookup specification

- Added the bilingual [Frontend localization specification](frontend/TZ_LOCALIZATION_EN.md): source, ID, and system language; RU/EN JSON dictionaries; configuration for two readers; and a shared in-memory index. Database lookup uses `requested_key` as the ID and `text` as content.
- Defined merging identical duplicates while preserving provenance, conflict diagnostics, missing-string markers, the distinction between empty text and `null`, no automatic language substitution, and built-in template parameters.
- As requested by the user, game markup is not processed: `text` is displayed as stored. Synchronized the concept, Text specification, and acceptance criteria in RU/EN. Only documentation changed; mechanism code and the database were not modified.

## 2026-11-16 — agreed interface palettes and typography

- The [Styling dictionary specification](frontend/TZ_STYLING_DICTIONARY_EN.md) now records nine color assignments per theme: neutral backgrounds, text, borders, and a muted green accent. Research areas are distinguished by headings.
- Selected Inter with local loading from the portable distribution and an included license. Added sizes, line heights, and weights for six text roles, identical across day and night themes.
- Synchronized RU/EN, the concept, and acceptance criteria. Values were compared with the agreed sample; the minimum calculated text contrast on the listed backgrounds is 4.97:1 by day and 4.65:1 by night. Changes cover documentation; the product interface and CSS dictionary were not implemented.

## 2026-11-16 — color and typography dictionary specification

- Added the bilingual [Styling dictionary specification](frontend/TZ_STYLING_DICTIONARY_EN.md): separate CSS files, shared and element-owned variables, a complete value set in day and night themes, assignments only for agreed states, and reuse of matching values through explicit references.
- Defined identical role typography across both themes, Cyrillic and Latin support, and separation of shared definitions, theme values, and small element assignment files. The concrete palette, font, and sizes remain for the next discussion.
- Synchronized the concept and Text specification in RU/EN and added acceptance criteria. Only documentation changed; the CSS dictionary and interface were not implemented.

## 2026-11-16 — main window specification

- Added the bilingual [Main window specification](frontend/elements/TZ_MAIN_WINDOW_EN.md): UI kit composition, left menu and right viewport, available height, visible-portion changes while retaining field geometry, and independent menu and technology scrolling.
- Defined initial language, theme, menu, technology representations, and viewing position, precedence of supplied restored state, and separate persistence design. Described overlays above content within window bounds and shared language and theme updates.
- Synchronized the concept, Selection control and viewport specifications; added acceptance criteria and the final element link in the reference. All 18 current elements have specification links. Only RU/EN documentation changed; the interface was not implemented.

## 2026-11-16 — scrollbar specification

- Added the bilingual shared [Horizontal and vertical scrollbar specification](frontend/elements/TZ_SCROLLBAR_EN.md): track and thumb, overflow visibility, non-overlapping placement, configurable thickness, and proportional thumb size with a minimum length.
- Defined dragging, track-click scrolling, wheel and `Shift` + wheel, focus through `Tab`, axis arrow keys, and `Home` / `End`. Described container-supplied dimensions and offsets, change notifications, and styling states without geometry changes.
- Updated the viewport specification, concept, acceptance criteria, and both UI element reference links in RU/EN. Only documentation changed; the interface was not implemented.

## 2026-11-16 — technology tier column specification

- Added the bilingual [Technology tier column specification](frontend/elements/TZ_TIER_COLUMN_EN.md): card order supplied by the field, localized “Уровень N” / “Level N” headings in each area, shared width, aligned headings and list starts, configurable gaps, and content-based height.
- Defined retention of an empty column's heading, width, and position, shared scrolling of the heading and cards, and dedicated styling variables. Added acceptance criteria, including a column becoming empty after moving a card on variant selection.
- Synchronized the research area and field specifications, concept, and UI element reference links in RU/EN. Only documentation changed; the interface was not implemented.

## 2026-11-16 — research area region specification

- Added the bilingual [Research area region specification](frontend/elements/TZ_RESEARCH_AREA_EN.md): a container with a localized heading and columns ordered by the field, a shared grid, field width, and height based on the tallest column together with the heading and spacing.
- Defined heading alignment to the `Level-0` edge, built-in RU/EN titles, configurable gaps between regions, shared scrolling of the heading and contents, and dedicated styling dictionary variables. Added acceptance criteria.
- Synchronized the field specification, concept, and UI element reference links in RU/EN. Only documentation changed; the interface was not implemented.

## 2026-11-16 — technology field specification and predecessor grouping

- Added the bilingual [Technology field specification](frontend/elements/TZ_TECHNOLOGY_FIELD_EN.md): research areas, `tier` columns, counting technology requirements only, vertical order, geometry, and moving a card when a selected variant changes its research area.
- Defined consecutive placement for technologies with identical immediate predecessor sets and equal requirement counts, with stable base-ID ordering within a group and dependency precedence retained. Distinguished requirement count from predecessor sets, including `OR` alternatives.
- Updated the concept, UI element list links, and acceptance criteria. Ordering between distinct groups, their placement across columns, and connecting lines remain further design topics. Only RU/EN documentation changed.

## 2026-11-16 — technology variant list interaction

- Defined the shared UI kit dropdown in the [card specification](frontend/elements/TZ_TECHNOLOGY_CARD_EN.md#variant-list-interaction): base version first, variants in database order, current selection marked; confirmation applies the variant and closes the list, while clicking outside or pressing `Escape` closes it without changing the selection.
- Agreed opening with `Enter` / `Space`, arrow key navigation without applying a variant before confirmation, and tooltip suppression while the list is open. Extended card states and acceptance criteria.
- Synchronized the shared Selection control specification and interface concept in RU/EN. Only documentation changed; the interface was not implemented.

## 2026-11-16 — labels for technology variants with identical titles

- Agreed “(Вариант N)” / “(Variant N)” suffixes for matching variant titles in the selection list in the [Technology card specification](frontend/elements/TZ_TECHNOLOGY_CARD_EN.md#variant-labels); the base version retains its title without a suffix.
- Defined numbering by `technology_swap` block order, language-independent numbers, built-in localization for the template, and preservation of original database strings. Extended acceptance criteria and synchronized the concept in RU/EN. Only documentation changed.

## 2026-11-16 — manual variants and technology layout refinement

- Added manual selection of the base version and `technology_swap` separately for each technology to the bilingual [Technology card specification](frontend/elements/TZ_TECHNOLOGY_CARD_EN.md): name and tooltip updates, retained base ID and links, and movement between research areas when a variant overrides the area.
- Described selection data and state, distinguishing blocks with identical titles, prepared database localization, and checks after implementation. List presentation, distinguishing labels, and interaction details remain subject to agreement.
- Synchronized the concept with the discussion: Physics, Society, and Engineering from top to bottom, clouds of related cards, vertical placement within columns, predecessor precedence, and sorting by technology requirements only with `OR` handling.
- Replaced the technology chain row with a research area region in the UI element list; manual family grouping and the proximity algorithm remain further design topics. Only RU/EN documentation changed; code and the database were not modified.

## 2026-11-16 — technology viewport specification

- Added the bilingual [Technology viewport specification](frontend/elements/TZ_TECHNOLOGY_VIEWPORT_EN.md): dimensions to the right of the menu, independent scrolling on two axes, field left alignment, and an initial position at the upper left corner.
- Specified retaining valid offsets when language, theme, window dimensions, or menu state change; offsets outside new ranges are clamped on the corresponding axis. Persistence across launches remains a separate discussion within the shared state mechanism.
- Described background styling through the dictionary for both themes and checks after implementation. The shared Tooltip specification now covers display over the scrollable field without container clipping or affecting scrolling.
- Updated the concept and UI element list links in RU/EN. Only documentation changed; interface implementation has not started yet.

## 2026-11-16 — bottom menu button group specification

- Added the bilingual [Bottom menu button group specification](frontend/elements/TZ_MENU_BUTTON_GROUP_EN.md): one row at the bottom right, identical button dimensions, configurable gap and padding.
- Specified collapsing without reserving space for the hidden theme button while retaining menu button size and group height; state and actions remain with the panel, application, and corresponding components.
- Clarified the shared Tooltip specification: bottom button hints may extend beyond group and panel boundaries without clipping while staying within visible window bounds.
- Updated the concept, Menu panel specification, and UI element list links in RU/EN; described checks after implementation. Only documentation changed; interface implementation has not started yet.

## 2026-11-16 — menu panel specification

- Added the bilingual [Menu panel specification](frontend/elements/TZ_MENU_PANEL_EN.md): main content with language selection at the top and a separate bottom group of collapse and theme buttons.
- Specified vertical scrolling for main content only, independent of technologies; the bottom group remains available at the bottom of the panel.
- Described expanded and collapsed dimensions, retaining active settings when collapsing, application state integration, styling, and checks after implementation. Detailed bottom group layout remains a separate specification.
- Updated the concept and UI element list links in RU/EN. Only documentation changed; interface implementation has not started yet.

## 2026-11-16 — technology card specification and tooltip heading

- Added the bilingual [Technology card specification](frontend/elements/TZ_TECHNOLOGY_CARD_EN.md): uniform configured dimensions, a centered name limited to two lines with overflow ellipsis, the database source, and localization by string IDs.
- Specified a tooltip with the full name and description when any part of the card is hovered. Shared [Tooltip](frontend/elements/TZ_TOOLTIP_EN.md) now supports an optional heading above the body; both parts use shared Text with their respective styling roles.
- Described default and hover card states, dictionary styling for both themes, position assignment by the technology field, and checks after implementation.
- Updated the concept and UI element list links in RU/EN. These are documentation changes; interface implementation has not started yet.

## 2026-11-16 — menu collapse button specification

- Added the bilingual [Menu collapse/expand button specification](frontend/elements/TZ_MENU_TOGGLE_EN.md): a shared button with an icon and tooltip, action-dependent arrows, built-in localized strings, and mouse and keyboard operation.
- Recorded stable button size and bottom placement, the narrow collapsed panel, hiding settings while retaining their values, and workspace expansion without extra space before `Level-0`.
- The agreed initial state is an expanded menu; persistence is included in the future shared application mechanism.
- Updated the concept and UI element list links in both languages. Interface implementation has not started yet.

## 2026-11-16 — localized string lookup configuration

- The [Text specification](frontend/elements/TZ_TEXT_EN.md) now defines three values for shared lookup: source, string ID, and language provided by the system from application state.
- Recorded the choice of separate source configurations: record locations, language branch or file selection, ID matching, and resulting text retrieval. Consumers do not supply an additional `name` / `description` parameter.
- Clarified the need to describe lookup within current nested database records; the concrete configuration format and handling multiple matches remain implementation design topics.
- Updated the interface concept and Language selector specification in RU/EN. Code, product configuration files, and database structure were not changed.

## 2026-11-16 — interface text sources

- The [Text specification](frontend/elements/TZ_TEXT_EN.md) now defines two string lookup parameters: source and identifier. Built-in localized interface files are the default; the application database is selected explicitly and supplies `text` from object localization.
- Clarified identifier resolution within the source, language updates, and the distinction between the display source and the database translation provenance field `source`.
- Updated both language versions of the concept and related Button, Tooltip, Selection control, Language selector, and Theme toggle specifications. Database string addressing remains an implementation design topic.
- Only documentation changed; database structure and code were not modified.

## 2026-11-16 — theme toggle and string identifiers

- Added the bilingual [Theme toggle specification](frontend/elements/TZ_THEME_TOGGLE_EN.md): an icon button with a tooltip, sun/moon actions, menu placement, application throughout the interface, and the night theme on first launch.
- The [Text specification](frontend/elements/TZ_TEXT_EN.md) now requires string identifiers and text lookup from separate localized files using the language setting through a shared mechanism.
- Aligned related Button, Tooltip, Selection control, and Language selector requirements; option values are separate from label identifiers. File format and connecting database technology text remain implementation design topics.
- Updated concepts and UI element list links. These are documentation changes; interface implementation and shared state persistence have not started yet.

## 2026-11-16 — Language selector specification

- Added `Docs/frontend/elements/TZ_LANGUAGE_SELECTOR_RU.md` and `TZ_LANGUAGE_SELECTOR_EN.md`: setting label, RU/EN dropdown, and immediate language changes for the interface, names, and descriptions using prepared database localization.
- Recorded Russian on the first launch and retention of the active selection when the menu collapses. Persistent storage and restoration remain a dependency on the separately designed shared mechanism, without choosing a storage format.
- Added links from the UI element list and base dropdown specification; updated both concepts in RU/EN. Described future checks; the element has not been implemented yet.

## 2026-11-16 — separate persistence design

- Recorded separate design work in the frontend concept for a shared mechanism to persist and restore many settings and items of application state between launches.
- UI elements report changes to the application layer; storage format and writing mechanism remain open decisions for a separate specification. Updated both language versions and contents lists.

## 2026-11-16 — Selection control specification

- Added `Docs/frontend/elements/TZ_SELECT_RU.md` and `TZ_SELECT_EN.md`: a dropdown with one selected option, externally supplied values and labels, selection reporting to the consumer, and mouse and keyboard interaction.
- Recorded dictionary-based styling states and future acceptance criteria. Added links from the UI element list and concept; the element has not been implemented yet.

## 2026-11-16 — Button and Tooltip specifications

- Added separate bilingual specifications `Docs/frontend/elements/TZ_BUTTON_*` and `TZ_TOOLTIP_*` with the current agreed requirements and future acceptance criteria. Extensions remain for subsequent discussion.
- Button uses optional text, icon, and tooltip; documented states, border visibility without content shifts, whole-area mouse and keyboard activation, an accessible name, and distinguishable focus.
- Shared Tooltip binds to an anchor, uses Text, and overlays the interface within visible boundaries. Buttons show it on hover or keyboard focus and hide it when both conditions are absent.
- Updated links in the UI element list and concept in both languages. Component implementation has not started yet.

## 2026-11-16 — shared button and tooltip

- Renamed Icon button to Button and Technology description tooltip to the shared Tooltip in the UI element list. The list still contains 18 elements without their requirements.
- Clarified the concept: button text and icon are optional, the border can be hidden, and buttons and cards use the shared Tooltip element. Their future specifications must reference its separate specification.
- Updated both language versions. Detailed Button and Tooltip specifications remain under discussion.

## 2026-11-16 — Icon element specification

- Created `Docs/frontend/elements/TZ_ICON_RU.md` and `TZ_ICON_EN.md`: shared-set symbol selection, size and placement controlled by the consuming component, preserved proportions, and dictionary colors based on theme and parent state.
- Recorded the absence of an independent click action and described future acceptance criteria. Added links from the UI element list and concept; the element has not been implemented yet.

## 2026-11-16 — Text element specification

- Created `Docs/frontend/elements/TZ_TEXT_RU.md` and `TZ_TEXT_EN.md` with agreed requirements for content, styling roles, parent states, placement, and two text overflow modes.
- Described future acceptance criteria. The UI element reference remains a list; its Text entry and the concept now link to the separate specification. The element has not been implemented yet.

## 2026-11-16 — UI element list

- Added a bilingual list of 18 current interface elements under `Docs/frontend/`: basic elements, composite elements, regions and layout structure, scrolling, and the main view.
- The reference contains only the list; element requirements will be documented separately. Added links from the concept and README.

## 2026-11-16 — interface styling dictionary

- Extended the frontend concept with a separate color and typography dictionary: UI elements use named variables by role and state, with values assigned centrally for day and night themes.
- Optional shared variables cover reused values. Example names are preliminary; the dictionary format and concrete values will be defined in the specification.
- Updated both language versions and their contents lists; this is an interface design change.

## 2026-11-16 — initial interface concept

- Created `Docs/frontend/` with a bilingual concept: window layout, independent scrolling, menu collapse to a narrow strip, left-aligned `Level-0`, chain rows, and `tier` columns.
- Recorded name-only cards with description tooltips, minimal design, and atomic composition of views from UI kit elements. The menu provides RU/EN selection and a day/night theme button to the right of the collapse button; settings are hidden when collapsed.
- Updated the overall concept and README navigation in both languages. Frontend implementation and a separate specification remain subsequent actions; application code and the database are unchanged.

## 2026-11-16 — implemented localization in the database

- Implemented the approved stage-ten specification: independent `sttv.enrichment.localization.enrich_localization`, noninteractive invocation, and a separate configuration. RU/EN technology and variant names/descriptions reside directly in the database.
- Added game YML reading without text coercion, per-key priorities, duplicate diagnostics, recursive ordinary static reference expansion, and inheritance of missing descriptions. Dynamic substitutions remain; unknown tokens carry chains in diagnostics.
- Raised database format to 4: `enrichments.localization` preserves game nodes, history, and analytics. Added inheritance validation, localization-only refresh, and stale-result removal after selection changes. Shared configuration variable expansion moved out of parser loading; other parsing mechanisms are preserved.
- Added two generated schemas, bringing the total to 13. Publication validates the temporary file, input consistency, and source file inventory; errors remain explicit, and database replacement is accurately reported even when report writing fails.
- All 184 tests passed, including 30 new checks. Rebuilt 35 technology files and enriched 679 technologies and 206 variants. Each language has 885 names and 885 descriptions, including 81 inherited variant descriptions. Independently checked 3,540 fields, sources, expanded references, original trees, and history. No errors or warnings; repeated processing is byte-identical.
- The verification database and reports are under `data/stage10/`; previous outputs, frequency lists, and sources are preserved. Database size increased from 138,156,360 to 140,937,166 bytes. Added a bilingual guide and updated concept, README, and specification statuses. Code files remain at most 160 lines; no in-game or visual checks were performed.

## 2026-11-16 — localization in the database specification

- Prepared a bilingual stage-ten draft specification: RU/EN names/descriptions for technologies and variants, per-key source priorities, static references with retained original strings, and inheritance of missing descriptions from base technologies.
- Documented agreed in-database storage as a separate service section beside objects; proposed format 4, a separate refresh operation, safe publication, and reporting. Code, configurations, schemas, and existing databases remain unchanged; the specification awaits approval.
- Recorded the research selection: 679 technologies and 206 variants, plus separate 13 categories and 6 tiers. Each language has every name, 679 base descriptions, and 125 variant-specific descriptions; 81 variants require inheritance. Source/reference inventories are under `data/stage10/specification_research/`; they are not verification of the future implementation.
- Updated the concept, README, and general specification status in both languages. Possible future reference-specific database cleanup is separated from the general-purpose parser and excluded from localization scope.

## 2026-11-15 — script value expansion implementation

- Implemented the approved stage-nine specification: dedicated `script_value` nodes, parameters/defaults, conditional fragments, scope prefixes, nested references, and mixed chains of four invocation kinds. Arithmetic and game state are not evaluated.
- Added `SCRIPT_VALUES_DIR`, the eighth parser configuration, and exclusion of the fifth library from independent traversal. The index uses shared named-library settings, retains environments, and leaves unused bodies unexpanded.
- Raised database format to 3 and report format to 5. New nodes use a single JSON Pointer in shared history; previous invocation kinds retain ranges. Updated serialization, history validation, static substitution, reports, and analysis; generated all 11 schemas.
- All 154 tests passed, including 26 new tests. Technology build: 35 files, 82,246 nodes, 36 script values, 1,776 triggers, 301 inline insertions, and 1,929 static substitutions, without errors or warnings. Independent surrounding/expansion checks, seven additional examples, and byte-identical rebuilding passed.
- Full audit completed: 1,466 successful inputs, two documentation exclusions, 21 failing files; checked 7,464,925 nodes and shared history. Nineteen failures are previous; new cases are an extra argument delimiter and `BONUS` / `$bonus$` mismatch under the current parameter case setting. One previous library input is excluded without fixing its source. All 11,674 successful script value expansions and two failures are counted in the report; new frequency lists are separate, and source/previous-output hashes are unchanged.
- Prepared the bilingual stage-nine guide, updated README, concept, specification statuses, and the stage-eight guide's historical notice. All 102 backend Python files are at most 160 lines. The verification database and reports are under `data/stage9/`; previous results and lists are preserved.

## 2026-11-15 — script value expansion specification

- Prepared the bilingual stage-nine draft: a script value library, dedicated calculation node, parameters, evaluation scopes, mixed expansion, and preservation of arithmetic without evaluating results.
- Proposed `SCRIPT_VALUES_DIR`, a separate reference-form configuration, exclusion of the fifth library from independent traversal, database format 3, report format 5, and single-node addressing in shared history. These changes are not implemented yet.
- Included findings from 15 files with 674 definitions and source references in `common/` and `events/`, plus requirements for diagnostics, static environments, analysis, and synthetic/corpus checks.
- Updated README and general-specification links and statuses in both languages. Code, operational configuration, schemas, and the working database were unchanged; the specification awaits approval.

## 2026-11-15 — implemented effect and trigger expansion

- Implemented approved stage eight: a dedicated named-call module, prebuilt indexes of both libraries, mixed inline expansion, parameters, defaults, and conditional fragments. Added `SCRIPTED_TRIGGERS_DIR`; four libraries are excluded from independent traversal.
- Effects are inserted into the caller's body; boolean triggers retain result boundaries through `AND` and `NOT`. Nonboolean tests use `scripted_trigger_test` with operator, value, and expanded body, without evaluating game results.
- Added separate variable environments for libraries and arguments, shared cycle/depth/created-node limits, and consumed-source verification before publication. Unified `metadata.expansions` history remains separate from analytics.
- An additional test exposed and resolved directive handling in conditional and inline fragments: history contains actually removed markers, and nested insertion positions are adjusted after removal.
- The full audit and repeat after the directive fix matched: 1,481 successful inputs, two documentation exclusions, and 21 failing files, including 17 previous failures. Serialization and history covered 7,177,784 nodes; separate frequency lists were generated. All consumed sources and previous lists were preserved.
- With separate user approval, added `root_definition_files = ["common/game_rules/*.txt"]`: retain root definitions, expand inner calls, and propagate context to root inline insertions. This removes the false `NOMAD` diagnostic caused by a game rule sharing a trigger name. Both directory files passed without errors or warnings. Combining full and targeted runs leaves 20 failing inputs; the guide documents the list and limitations. Full-run frequency lists reflect the state before this targeted correction.
- Connected the seventh parser configuration, `scripted_calls.json`, and tenth generated schema. Database format is now 2 and report format 4; rebuild older databases. Structural consumers and checks were updated without restoring a command profile.
- All 128 tests passed. Real technology build: 35 files, 81,502 nodes, 1,776 expanded triggers, 32 nonboolean tests, 301 inline insertions, and 1,929 static substitutions, with no errors or warnings. Independent comparison of every field and value, byte-identical rebuilding, and source checks passed.
- Verification database and reports go under `data/stage8/`; previous standard outputs and curated lists are preserved. Added a bilingual guide and updated README, concept, and specification statuses. The stage-seven guide is marked historical. All 89 backend Python files remain at most 200 lines; all 10 schemas match their generator.

## 2026-11-15 — effect and trigger expansion design

- Prepared the bilingual stage-eight specification for review: a dedicated scripted effect/trigger expander, inline coordination, indexes, arguments/defaults/conditional fragments, and static-variable environments.
- Proposed a separate node preserving nonboolean tests, unified mixed-call history, database format 2, and report format 4. Adding `SCRIPTED_TRIGGERS_DIR` and excluding its library from traversal are planned in the specification; operational configuration and product code remain unchanged.
- Inspected 80 library files and 35 technology files: 1,691 effects, 1,692 triggers, numeric comparisons, formula arguments, and service directives. Materials are under `data/stage8/specification_research/`; this is an inventory, not completed expansion or game validation.
- Updated README and general-specification links and statuses in both languages. Stage-eight implementation has not started.

## 2026-11-15 — implemented static-variable substitution

- Implemented approved stage seven: separate shared-library reading, local tables and overrides, chains, duplicate/cycle/depth checks, and working-scalar substitution after inline expansion. Formulas are not evaluated; declarations and coordinates are preserved, with no replacement metadata.
- Connected the sixth configuration, `static_variables.json`, and ninth generated schema. Report format is now 3 with a shared-file manifest and aggregate counts; database structure remains version 1. Builds and analysis use one processor; analysis skips declarations.
- All 104 tests passed. Independent technology verification: 35 files, 1,929 substitutions, 67,513 nodes, and 301 inline calls, without errors or warnings; history/provenance preserved and repeat builds byte-identical. The new verified database is `data/stage7/database.json`; the previous standard database is unchanged.
- Full audit: 1,522 successful files, two documentation exclusions, and 17 failures. The previous 16 CLASS/RELIC issues remain; discovered missing variable `@max_unlocked_council_positions` in `common/script_values/01_script_values_paragon.txt:365`. Source defects were not repaired. New frequency lists and reports are under `data/stage7/`; game files, templates, the library, and previous lists were unchanged.
- Added a bilingual stage guide and updated specification status, README, and general-document pointers. All Python files remain at most 200 lines.

## 2026-11-15 — static-variable substitution specification

- Prepared separate `TZ_BACKEND_STAGE_7_RU.md` / `TZ_BACKEND_STAGE_7_EN.md`, awaiting approval. Defined shared-library reading, local overrides, reference chains, scope after inline expansion, diagnostics, and verification.
- Specified no separate replacement history in database metadata. Preserve use-site coordinates and existing inline invocation history; formula evaluation remains outside the stage. Case, duplicate, and two-pass resolution policies are identified as the proposed implementation contract.
- Structurally checked 2,917 shared declarations and 1,228 local declarations from 232 discovered files. Checked 1,929 static references after inline expansion in 35 technology files, with no missing declarations. Research material: `data/stage7/specification_research/`.
- Linked both README files. Product code, configuration, and schemas were not changed; substitution implementation has not started.

## 2026-11-15 — static variable directory

- Added required `SCRIPTED_VARIABLES_DIR = common/scripted_variables`, relative to `STELLARIS_ROOT`. The shared builder/corpus filter excludes the directory and descendants from independent inputs; the path remains inside the game and protected from writes.
- Added a separate excluded-variable-file counter to corpus reports. Future full reports and lists go to `data/stage6/without_scripted_libraries/`, preserving previous results.
- Actual selection check: 23 variable files excluded, reducing independent inputs from 1,564 to 1,541; technology selection remains 35 files. Report: `data/stage6/without_scripted_libraries/selection_report.json`. Full corpus parsing was not repeated.
- All 88 tests passed, including configurable library paths, nested directories, retained neighboring inputs, and game-root confinement. Substitution of `@name` and metadata changes were not implemented. Updated both languages of the README, guide, and specification amendment; extended configurable-directory and source-boundary checks.

## 2026-11-15 — explicit inline_script path exceptions

- Connected a separate `config/parser/exceptions.json`: exact mapping from inline invocation names to permitted relative files, with explanatory reasons. Added an exception for the extensionless `tr_purity_imperfection_remediation_wilderness` file.
- Retained normal `.txt` lookup, `INLINE_SCRIPTS_DIR` confinement, reached-template-only reading, actual provenance, and hashes. Exception patterns and unsafe paths are rejected, as are duplicate normalized names. A missing permitted file does not trigger alternative lookup; cycles use actual template identity.
- Added the fifth parser configuration selection and eighth generated schema, `parser_exceptions.schema.json`. The required configuration is validated and protected from output overwrites. Updated both languages of the specification, guide, README, and investigation.
- All 87 tests passed. Three actual tradition files expanded successfully and passed JSON checks: 75 calls from 16 templates, four exception applications, and no expansion errors. Sources and templates remained unchanged; the full corpus was not run. Report: `data/stage6/inline_exceptions/validation_report.json`.

## 2026-11-15 — vanilla issue TODO and color exception

- Created shared bilingual `TO_DO_RU.md` / `TO_DO_EN.md` in the repository root. Deferred verification and fixes for `CLASS` forwarding across 14 trait files and the suspected `RELIC` typo in two event chains; no game fixes were implemented.
- Investigated `tr_purity_imperfection_remediation_wilderness`: an extensionless file exists, whereas the loader requests `.txt`. Confirmed chains from the Purity, Cloning, and Mutation categories through their shared template; findings and verification boundaries are recorded in a separate bilingual research document. Template lookup rules remain unchanged.
- Added the agreed `trait_bg_active_glow` exception for a block without `=` in `constructs.json`. Parser mechanics are unchanged; the declaration is preserved as a `tagged_block`, while arbitrary names without an operator remain rejected.
- All 17 targeted tests passed. The actual color file parsed successfully and passed JSON schema validation and round-trip loading; its source remained unchanged. The full corpus audit was not rerun. Updated both languages of the README, specification, and guide; targeted report: `data/stage6/known_input_issues/validation_report.json`.

## 2026-11-15 — excluded scripted effect library

- Added `SCRIPTED_EFFECTS_DIR = common/scripted_effects`, relative to `STELLARIS_ROOT`. The shared builder/full-audit filter excludes the directory and all descendants from independent selection; scripted effect expansion was not added.
- The corpus report counts excluded effect files separately from inline templates. New results go to `data/stage6/without_scripted_effects/`, preserving initial reports and research lists.
- All 80 tests passed, including configurable paths, nested directories, retained neighboring sources, and inline expansion. Technology selection remains unchanged at 35 files. The effect library excludes 43 TXT files.
- Updated both languages of the README, guide, and stage-six specification following the user request.
- Repeat audit: 1,542 files and 3,510,653 nodes processed successfully, with 20 previously known problematic inputs remaining. The two excluded failing inputs belong to the effect library; there are no new failures. Sources, templates, and previous research lists remain unchanged.

## 2026-11-15 — stage six implementation: syntax-tree database

- Implemented the approved stage-six specification: persistence of all seven syntax-node kinds, original order, duplicates, provenance, and inline invocation history. The new format is `sttv.parse_database`, version 1; loading requires neither the game nor parser settings.
- Removed the profile, registry, recommendation analyzer, closed technology model, previous localization, and variable evaluation. Removed related modules, configurations, schemas, tests, and unused helpers; retained seven schemas and the in-code generator.
- Configuration now covers sources, parser, and outputs. Added physical-file deduplication, source hashes, repository-confined work-area protection, and structural history checks. Preserved separate database/report publication and truthful status after a partial write failure.
- All 111 baseline tests passed; 78 current tests passed after the transition. Real build: 35 files, 67,513 nodes, and 301 insertions from 10 templates, with no errors or warnings. Independent comparison confirmed every tree field and byte-for-byte repeatability; the standard `data/database.json` was updated.
- The corpus audit verified JSON for 1,583 files and 3,681,397 nodes. The same 22 inputs still fail as in stage five; new frequency lists match the previous reference run byte for byte. Sources and manually processed lists remain unchanged; results are under `data/stage6/`.
- Added a bilingual stage-six guide and updated the README, concept, and specification statuses; previous guides are marked historical. The standard database is 107,520,690 bytes; memory and known expansion limitations are documented in the guide.

## 2026-11-15 — stage six specification: backend simplification

- Prepared a bilingual stage-six specification draft: one JSON containing source-file trees, preserving order, duplicates, provenance, and inline invocation history.
- Defined simplified configuration and building, structural checks, and removal of the profile, registry, dependent analyzer, and previous domain conversion; enrichment belongs to later stages.
- Defined checks and cleanup boundaries: preserve the parser, expansion, useful statistics, and research material. Updated README and concept links and statuses in both languages.
- Approval is pending. Code, active configurations, schemas, profile, and working database were not changed in this iteration.

## 2026-11-15 — parsing results as the database foundation

- Updated the concept following the user decision: the primary result is JSON after parsing; a closed domain model and command profile cease to be storage prerequisites in the target architecture.
- Enrichment by specific fields and rules belongs to later stages; the concrete JSON format is not selected yet.
- Updated processing, launch and refresh workflows, README, and the previous model/specification status in both languages. Code, schemas, the profile, and working data were unchanged in this iteration.

## 2026-11-15 — implemented inline_script expansion

- Implemented the approved fifth stage: separate configuration, template loading, substitution, nested calls, isolated bindings, cycle detection, and diagnostics with physical provenance.
- Upgraded the database to format 2: call history outside analysis, JSON Pointers to results, and sources on script entries, repeated values, and variables. Updated the builder, analyzer, generator, and 12 schemas.
- With separate user approval, profile revision 2 adds five commands exposed by expansion. All other effective rules are preserved.
- Rebuilt the technology database: 679 technologies, 206 variants, 301 calls, and no errors. Comparison confirms changes only in 261 technologies containing inclusions.
- The corpus audit loads reachable templates only and writes new frequency/scalar lists under `data/stage5/`; existing research lists are preserved. The full corpus has 22 unsuccessful inputs; its limitations and complete report are separate from the successful technology build.
- Added and updated checks, bilingual backend guidance, the database model, README, and specification status. Game files were not modified.

## 2026-11-15 — stage five specification: inline_script expansion

- Following the user's clarification, `INLINE_SCRIPTS_DIR` is excluded from independent inputs during a general pass: templates are loaded only through reached calls, including nested calls. Updated analysis, diagnostics, and the verification criterion in both specification versions.
- Added separate `TZ_BACKEND_STAGE_5_RU.md` and `TZ_BACKEND_STAGE_5_EN.md` documents covering invocation forms, argument substitution, nesting, tree insertion, and diagnostics.
- Specified invocation history excluded from analysis, inserted-node provenance, and proposed changes to the strict database contract. Defined scope, unsupported-form handling, and verification criteria.
- Updated both README versions with links and status. The specification awaits approval; code, active configurations, schemas, and working frequency lists were not changed in this iteration.

## 2026-11-15 — inline_script directory and expansion requirements

- Added `INLINE_SCRIPTS_DIR = common/inline_scripts` to `global_variables.json`, relative to `STELLARIS_ROOT`, and documented it in both README versions.
- Recorded the user's requirements for nested calls, per-invocation argument retention, expansion inside the calling object's body, and separate metadata excluded from analysis.
- Verified loading the updated variables and existence of the configured directory. Expansion and metadata format remain under design; the stub is unchanged.

## 2026-11-15 — extracted families removed from the working list

- At the user's request, removed 635 entries belonging to the extracted `is_`, `has_`, `set_`, `add_`, and `remove_` families from `data/text_frequency/scalar_analysis/scalar_assignments.txt`.
- The working TXT retains 3,123 entries with their text, frequencies, and order preserved. The original analysis JSON and separate family inventories are unchanged.
- Documentation distinguishes the remaining working TXT from the complete analysis snapshot in JSON.

## 2026-11-15 — set_, add_, and remove_ family lists

- Extracted three more families from the same `scalar_assignments.txt` into separate directories: `set` — 132 names, `add` — 40, `remove` — 44. Retained the existing JSON inventory format.
- Updated family listings, bilingual documentation, and reports. The research exporter accepts selected families and preserves earlier report entries.
- Verified 216 new entries and their examples against source files; the combined check covers 635 entries. The `is`/`has` inventories and original frequency data are unchanged.

## 2026-11-15 — initial is_ and has_ construct inventories

- Created separate `language/keywords/is/` and `language/keywords/has/` directories with initial JSON inventories of 235 and 184 names. Each retains frequencies, observed operators, and a source-linked example.
- Inventories await semantic review; conditions, definition fields, and other roles are not assigned one shared rule solely from their prefix. Further subdivision within each family is planned without duplicate records.
- Added bilingual documentation of structure, fields, examples, and the rule/localization review workflow. Linked the catalog from the README files.
- Verified membership, order, counts, all 419 examples against source coordinates, and source hashes. Original frequency lists, game files, and parser behavior are unchanged.

## 2026-11-15 — variables and substitutions excluded from lists

- Added a shared filter for script variables written as `@name` and text containing `$NAME$` substitutions, including compound names, to the frequency and scalar-use research handlers.
- Rebuilt the general list and both scalar lists with their JSON reports. Retained 56,268 general entries, 3,758 names with scalar right-hand sides, and 33,880 texts occurring only as scalar values.
- Comparison against the saved third-pass snapshot confirms only variable and substitution rows were removed; other frequencies and structural details match. Formulas without substitutions and embedded `@` references remain.
- Updated bilingual research documents. Fixtures and report checks passed; game files, product code, configurations, schemas, profile, and database are unchanged.

## 2026-11-15 — two scalar-use lists

- Extracted 6,835 names with scalar right-hand sides in every assignment and 34,283 texts occurring only as scalar values from the current corpus AST. Criteria cover checked files outside skipped inline calls.
- Saved both TXT/JSON lists, the complete role/form inventory with examples, a report, and checks under `data/text_frequency/scalar_analysis/`. Frequencies for all 59,828 input texts match the third pass; lists do not overlap.
- Added bilingual `RESEARCH_SCALAR_USAGE_RU.md` / `RESEARCH_SCALAR_USAGE_EN.md`. The original frequency list, parser rules, configurations, profile, database, and game files are unchanged; language classification was not automatically extended.

## 2026-11-15 — third frequency pass

- Recounted the current parser AST, excluding 36,026 logical-operator names and 6,885 complete inline_script calls while preserving logical bodies.
- Retained case merging, yes/no exclusion, and the global minimum count of 2. Result: 59,828 distinct elements and 1,553,955 occurrences.
- Counted 2,235 files; excluded two prose documents and recorded the known common/named_colors/01_trait_colors.txt:65 error without lexical fallback. No unexpected diagnostics.
- Adapted the research handler and checks in TMP; updated reports and bilingual documentation. Previous artifacts are retained in pass_2_snapshot. Sources, product code, configurations, schemas, profile, and database are unchanged.

## 2026-11-15 — fourth-stage parser implementation

- Implemented the approved specification: separate `logical_operators.json`, `LogicalOperation` nodes, mandatory loading of three configurations, and consistency checks.
- Token reading now follows parser requests. `inline_script` is passed as an opaque value to an expansion function with an empty stub; its contents are not parsed, while source text and skip coordinates remain available.
- Updated database projection, builder, analyzer, schema generation, and `skipped_inline_scripts` counters. The command profile and database schema remain; other strict checks still apply.
- All 101 tests passed. Of 2,238 corpus files, 2,235 parsed, with two prose documents and the known line-65 error in `common/named_colors/01_trait_colors.txt` accounted separately. Found 36,026 logical nodes and 6,885 skips.
- The database matched an independently transformed baseline: 301 inline entries removed, with 679 technologies, 206 variants, and RU/EN names preserved. Source hashes are unchanged; analysis completed fully.
- Added a bilingual stage-four guide and updated the specification, README files, database model, keyword classification, and historical guide pointers. Reports reside in `data/stage4/`; the frequency list was not recalculated.

## 2026-11-15 — fourth-stage parser specification

- Prepared bilingual `TZ_BACKEND_STAGE_4_RU.md` / `TZ_BACKEND_STAGE_4_EN.md` for approval: a separate logical-operator configuration, `LogicalOperation` node, opaque-value reading, and an `inline_script` expansion function with an empty stub.
- Incorporated the user's clarification: both reference and block are skipped in full; the opaque scalar is handler input, not a retained result node. Internal inline-parsing rules were not designed.
- Specified integration, skip counters, source-text preservation, ignored-value boundary checks, and comparison against an independently prepared database with inline entries removed. The former unchanged-database equality requirement is replaced by an explicitly bounded comparison.
- Updated the keyword document, README files, and a database-model note in both languages. This is a stage draft: code, configurations, schemas, working database, and frequency list were unchanged.

## 2026-11-15 — logical operators and opaque inline_script

- Added the basic `AND`, `OR`, `NOT`, `NAND`, `NOR` rule to both keyword-document versions: case-insensitive recognition of named blocks, preserving order, repetitions, lists, and nesting without evaluating conditions.
- Following the user's clarification, both `inline_script` value forms — reference and block — are described as one opaque scalar. Content parsing, reference following, and template expansion are deferred; no internal inline-processing rules were introduced.
- Retained the started call and template research only in `TMP/WEB_STTV/text_frequency/`: repeatable handlers, an inventory, and a separate string-fragment report. These materials are neither parser rules nor product inputs.
- Updated contents and document status. Changes concern documentation and temporary research materials; product code, configurations, schemas, database, frequency list, and game sources were unchanged.

## 2026-11-15 — keyword id

- Following user agreement, added `id` to the bilingual keyword document as a field defining or specifying the identifier of an object or group, with one entry covering different object types.
- Recorded its purpose, the `id = identifier` form, examples, and findings from checking all 20,358 occurrences. Added a research-report link, vanilla example coordinates, and aura documentation explaining identifier-based grouping.
- Updated contents and document status. Verified links, examples, numerical data, and consistency between language versions. Only documentation changed; the parser, configurations, database, and frequency list remain unchanged.

## 2026-11-15 — second frequency pass

- At the user's request, recalculated statistics without case sensitivity using Unicode `casefold`; excluded whole `yes`/`no` elements in all cases and elements with a total frequency of 1. Minimum frequency is applied after merging all files and case variants.
- Updated TXT, JSON, report, manifest, and verification outputs in `data/text_frequency/`. Retained 61,033 elements and 1,632,370 occurrences; excluded 106,535 `yes`/`no` occurrences and 96,750 singleton elements.
- Updated the research handler and checks in `TMP/WEB_STTV/text_frequency/`, the bilingual counting description, and the keyword document's link explanation. The new run exactly matches an independent transformation of the previous report; all 2,238 source files retained their hashes.
- Verified case normalization, exclusion boundaries, filtering after global counting, totals, ordering, uniqueness, and TXT/JSON correspondence. Parser code/configurations, schemas, profile, and database remain unchanged.

## 2026-11-15 — keywords and boolean values

- Created the bilingual [Keywords and values](KEYWORDS_AND_VALUES_EN.md) document to incrementally record verified and agreed interpretations.
- Following the user's decision, classified `yes` and `no` as boolean values. Recorded their `true`/`false` equivalents, rule boundaries, examples, and findings from checking all 106,529 occurrences.
- Added README links. Checked contents, links, numerical data, and consistency between language versions. Only documentation changed; parser implementation, configurations, and database remain unchanged.

## 2026-11-15 — text element frequency research

- At the user's request, produced a combined list of text elements without role classification, sorted by decreasing frequency. The existing tokenizer processed 2,236 vanilla `.txt` files from `common/` and `events/`; two prose instruction files were excluded.
- Measured 1,835,655 occurrences and 158,592 distinct texts. TXT, JSON, report, and manifest are saved in `data/text_frequency/`; the research handler and checks are in repository-root `TMP/WEB_STTV/text_frequency/`.
- Added a bilingual [counting description](RESEARCH_TEXT_FREQUENCY_EN.md). Verified fixtures, token coverage, totals, ordering, uniqueness, and TXT-to-JSON round trips. Hashes of all 2,238 source files remain unchanged.
- Product code, configuration, schemas, profile, and database were not changed. Results support the user's manual review; this is research, not a new specification.

## 2026-11-15 — third-stage implementation: configurable parser

- Implemented the approved separation of syntax loading, tokenization, compound-value reading, node representation, structural parsing, and projection into the current database format. Added two compact configurations and two schemas through the existing generator.
- The parser preserves text, order, repetitions, quotation, coordinates, parameters with defaults, formulas, conditional fragments, anonymous blocks, and color blocks. Unknown game commands parse without a profile or semantic validation.
- The builder and analyzer use selected configurations, checking structure, conflicts, protected paths, and operator agreement with the registry. Unrepresentable forms produce explicit diagnostics without string substitution or partial database publication. The analyzer respects configured parameter notation.
- Passed 79 tests. Successfully parsed 2,235 of 2,238 vanilla `.txt` files; two documents are reviewed separately, and one known entry missing an operator produces the expected diagnostic. Reconstructed 3,852,812 significant tokens with no unexpected failures.
- The database matches the baseline byte for byte: 679 technologies and 206 variants. All 2,950 source hashes are unchanged; all 75 backend and test Python files are at most 200 lines. Reports are saved in `data/stage3/`.
- Added the [third-stage guide](BACKEND_STAGE_3_EN.md), updated specification status, README files, and related guides. The previous profile is retained within the agreed scope; UI, game-condition evaluation, and registry replacement were not implemented.

## 2026-11-15 — third-stage specification: parser and syntax configuration

- Prepared bilingual `TZ_BACKEND_STAGE_3_RU.md` / `TZ_BACKEND_STAGE_3_EN.md` for approval: an independent engine, two compact configurations, internal nodes, integration, and checks against the researched corpus.
- Separated syntax parsing, conversion to the strict database model, and game-command semantic validation. The parser requires no command registry; reconsidering the need for existing command validation is proposed separately. Removing the previous profile is outside this stage.
- Specified preservation of order, quotation, formulas, parameters, and conditional fragments, diagnostics, and explicit rejection of conversions that lose structure. Defined configuration limits and acceptance criteria.
- Updated README files. Checked contents, links, JSON examples, and consistency between language versions. Only documentation changed; code, configuration, schemas, and database remain unchanged. Implementation tests were not run; the specification awaits approval.

## 2026-11-15 — script syntax description

- Prepared bilingual `SCRIPT_SYNTAX_RU.md` / `SCRIPT_SYNTAX_EN.md` for discussion: operators, special symbols, values and variables, construct types, includes, references, scopes and order preservation.
- Compared shipped documentation with code. Distinguished observed forms, documentation-only information and unestablished boundaries; absence of a mention is not treated as a prohibition.
- Separated `inline_script`, scripted trigger/effect calls, script values and substitutions. Clarified that observed `include` and `included_*_sets` fields describe domain lists rather than file inclusion.
- Added an abbreviated structural outline and source coordinates. Checked contents, links and language-version consistency. Product code, profile, schemas, configuration and database were not changed; this is not a new specification.

## 2026-11-15 — vanilla script pattern research

- Recursively researched `common/` and `events/` as requested: 2,238 `.txt` files, 1,625,934 lines and six other files with full paths. Added bilingual [pattern research](RESEARCH_SCRIPT_PATTERNS_EN.md).
- Identified shared structural forms, lists and mixed blocks, formulas, substitutions and conditional fragments; separated syntax from definition catalogs and domain interpretation. Prose documentation and a questionable entry without `=` are recorded separately.
- Saved measurement scripts, file manifest, statistics, source examples and definition catalog in `TMP/WEB_STTV/script_patterns/`. Verified reconstruction of 3,852,991 significant tokens across 2,236 files; two prose documents were reviewed separately. All 2,244 source hashes remain unchanged.
- Product code, profile, schemas, configuration and database were not changed. This research supports further design discussion; no new specification was created.

## 2026-11-15 — second backend stage implementation

- Implemented the approved specification: code is organized into nine packages and a build coordinator; tests are grouped by subsystem. Schema generation moved from `data/` into permanent code; fields and cardinality share one contract.
- Added closed schemas for profiles, registries, analysis and generation reports. The initial JSON profile preserves effective former-registry rules through 67 templates and 89 groups; `schemas/script_rules.json` was removed.
- Added supplied/user profile selection, reference/conflict checks, reproducible generation, safe writes and reporting of partially saved outputs. An invalid profile cannot reuse the old registry.
- The analyzer reads technologies and explicitly connected command documentation, scripted triggers and inline files. Observations retain coordinates and unknown scopes; recommendations are bound to a profile fingerprint and require user decisions.
- All 54 tests pass. Database bytes match the reference: 679 technologies and 206 variants. Independent comparison of 7,337 field occurrences passes; hashes of 741 source files remain unchanged. All Python files stay within 200 lines.
- Added the [second-stage guide](BACKEND_STAGE_2_EN.md); updated both README versions, database model, first-stage guide and specification status. Sources were unchanged; Git was not used. UI, HTTP service and portable packaging are outside this stage.

## 2026-11-15 — second-stage backend specification

- Prepared a separate `TZ_BACKEND_STAGE_2_RU.md` / `TZ_BACKEND_STAGE_2_EN.md` pair for the agreed changes. Shared principles and the database model remain linked; no large new sections were appended to the first-stage specification.
- Documented backend packages, permanent schema-generation code, shared field descriptions, JSON-profile inputs, shared rule blocks, conflicts, and reproducible registry generation.
- Defined analyzer inputs, additional sources, observations, and recommendations with evidence and uncertainties. Required explicit user decisions, programmatic operations without an interactive CLI, and user outputs within `WORK_DIR`.
- Added builder-integration requirements, preservation of previous outputs on failure, and acceptance criteria including first-stage database equality for unchanged sources. README now links the draft and states its status.
- Checked links, contents, the JSON example, and language-version consistency. Only documentation changed; code, configuration, schemas, sources, and the completed database were not modified. Second-stage implementation awaits specification approval.

## 2026-11-15 — first backend stage implementation

- Implemented the approved modular Python builder: configuration, direct source reading, parsing, strict-model conversion, RU/EN names, contextual validation, reporting, and atomic database replacement.
- Added profiles in `config/backend.json`, closed database/configuration/report schemas, and an explicitly declared script-command registry. Created a CLI and callable build function; pinned `jsonschema` in `requirements.txt`.
- Built a database containing 679 technologies, 206 variants, 13 categories, and 6 tiers. All 885 records have names in both languages. There are no errors; 1,265 external variables remain unresolved and 7 repeated fields are retained with diagnostics.
- Passed 29 synthetic checks, an independent comparison of 7,337 field occurrences, reproducibility checks, source-free completed-database validation, and previous-output preservation on failure. Hashes of 741 source files remained unchanged. All Python files, including tests, are below 200 lines.
- The environment, database, and reports are in the ignored `data/` folder. The research audit is used only for independent validation, not as a product input. Added an [operation guide](BACKEND_STAGE_1_EN.md); updated README, concept, specification status, and database-model documentation in both languages.
- The UI, HTTP service, images, and portable distribution are outside this iteration. Game and Workshop files were not modified; no Git commands were run.

## 2026-11-15 — separate specifications for subsequent stages

- Both [specification](TZ_EN.md#organizing-specifications-by-stage) versions now require each subsequent stage to have a separate `_RU` / `_EN` document pair referencing shared principles and data models.
- Documented naming, stage-specification contents, and adding links to README. The current document retains shared decisions and the first stage. Updated and checked contents and links.

## 2026-11-15 — backend specification and directory structure

- Added general principles to the [specification](TZ_EN.md): modular and extensible code, DRY, configurable parameters, and file-size rules of up to 200 lines, review at 201–300, and mandatory splitting above 300 with justified exceptions.
- Drafted the first backend stage: direct reading of limited sources, in-memory parsing, a strict database model, RU/EN names, diagnostics, validated saving, rebuilding, and acceptance criteria. Implementation awaits specification approval.
- Created empty `src/frontend/`, `src/backend/`, and `data/` directories. Added configurable `WORK_DIR` with value `data` to `global_variables.json` and `/WEB_STTV/data/` to the root `.gitignore`. Other configuration values were preserved, and no Git commands were run.
- Aligned the concept and database model with eliminating persistent source copies and intermediate snapshots. Updated README files, working-folder documentation, project status, and contents in both languages.
- Checked links and contents, JSON examples and configuration, consistency of new specification sections, directory existence, and the working-folder ignore rule. Builder code, schemas, and builder output have not been created; game and Workshop sources were unchanged.

## 2026-11-15 — strict schema and eligibility conditions

- Required a closed schema in both [database model](DATABASE_MODEL_EN.md) versions: only declared fields, types, and handling rules, including nested `ScriptBlock` commands. Unknown constructs go into a separate report and prevent replacement of the working database with partial output.
- Distinguished predecessor requirements, general and starting conditions, draw weights, AI preferences, and variant triggers. Added source examples and separated storing conditions from evaluating eligibility for a particular country.
- Clarified that a conditional variant belongs to its base technology through `technology_swap` nesting; `name_key` is a localization key, and no separate `parent_id` is introduced.
- Updated contents and validation requirements. Checked links, JSON examples, field coverage, and language-version consistency. Only documentation changed; the machine-readable schema, complete nested-command set, and implementation remain future work.

## 2026-11-15 — stage-one JSON database model

- Created a bilingual [JSON database model](DATABASE_MODEL_EN.md) covering technology-directory definitions, categories, tiers, and local variables, with Russian and English localization limited to technology and variant names.
- Described root collections, record and name provenance, conversion of all observed game fields, `all` / `any` requirements, script blocks, repetitions, and explicitly unresolved external variables. Added JSON examples, including a name with verified provenance.
- Documented name lookup priorities, missing versus empty translations, and preservation of original game markup. Descriptions and other localized text are outside this stage's scope.
- Checked JSON examples, field coverage, language-version consistency, links, and contents. Updated README and game-object model links. The format remains a proposal for discussion; no builder or working database was created, and the specification and global variables were unchanged.

## 2026-11-15 — Russian and English localization sources

- Added `WORKSHOP_DIR`, `RU_LOC_TIER_1`, `RU_LOC_TIER_2`, `RU_LOC_TIER_3`, and `EN_LOC_TIER_1` to `global_variables.json` using the directories supplied by the user.
- Preserved the first two Russian sources' dependency on `WORKSHOP_DIR` through `${WORKSHOP_DIR}/...` strings. Both README versions describe this convention, vanilla paths relative to `STELLARIS_ROOT`, and separate per-key text selection for Russian and English.
- Checked JSON validity, documentation links and contents, and the existence of all specified directories after path resolution. Source files were unchanged; the loader and localization collection have not been implemented yet.

## 2026-11-15 — technology object model

- Created a bilingual [technology model description](TECHNOLOGY_MODEL_EN.md): all 25 observed base-definition fields and 9 variant fields, their types, purpose, example values, and observed cardinalities.
- Described nested requirements, conditions, calculations, effects, description parameters, and selection groups. Addressed IDs, related data, missing and repeated fields, and the distinction between the source model and a future JSON format separately.
- Prepared the temporary `TMP/WEB_STTV/technology_model_inventory.json` inventory; compared tables with 679 definitions and 206 variants. Checked links, contents, and matching examples in both language versions. Updated README links.
- The specification, global variables, and application code were unchanged. Game files were used read-only; engine behavior was not tested in the game.

## 2026-11-15 — project global variables

- Created the shared [global_variables.json](../global_variables.json) file with the already defined `STELLARIS_ROOT` and `TECH_PATH` variables. The file is intended for variables from any part of the project.
- Documented the variables, their values, and the relationship between `TECH_PATH` and the game root in both README versions; updated status and contents.
- Checked JSON syntax and the existence of the game root and technology directory. Loading the variables in the application has not been implemented yet.

## 2026-11-15 — technology tree research

- Added a bilingual [technology tree research report](RESEARCH_TECH_TREE_EN.md) for the installed Stellaris Cygnus v4.5.4 (1b4f). Examined 679 base definitions, 615 references, logical requirement groups, tiers, eligibility and research draws, conditional variants, and repeatable research.
- Created a temporary audit script and JSON with source structures, requirement expressions, diagnostics, and hashes in `TMP/WEB_STTV/`. Compared two parsers across 58 files; checked references, absence of cycles, and base image availability. Recorded conflicting repeated weights in three technologies and the verification limits separately.
- Updated both README versions with research links. The specification and application code were not changed; research does not replace discussion and approval of further decisions. No in-game checks were performed. Vanilla files were used read-only.

## 2026-11-15 — first specification part

- At the user's request, created the first part of the bilingual [specification](TZ_EN.md): Python for collection, transformation, and the local service; TypeScript for the interface; HTML/CSS for markup and styling; JSON for storage and data exchange.
- Recorded responsibility boundaries, separate JSON validation, and portable packaging through PyInstaller in `onedir` mode without requiring users to install Python or a web server separately.
- Described planned checks for future implementation and remaining decisions. Updated both concept and README language versions with specification links.
- The full specification is still being developed. No application code, database, or executable distribution was created at this stage, and no software release version was assigned. Vanilla files are unchanged.

## 2026-11-15 — initial concept

- Created the `WEB_STTV` project directory with a bilingual overview, concept, and changelog.
- Described the primary tree view with vanilla images, a local portable Windows distribution, and first launch with an empty database and source setup.
- Recorded separate information collection, transformation into an internal database, and presentation processes; described JSON as the proposed format, localization priorities per key, and database rebuilding.
- Recorded open decisions separately. No technical specification, application code, database, or executable distribution was created at this stage, and no software release version was assigned. Vanilla files are unchanged.

[История изменений на русском](CHANGELOG_RU.md).
