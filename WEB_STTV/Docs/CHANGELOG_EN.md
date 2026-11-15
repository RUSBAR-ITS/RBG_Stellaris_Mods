# Stellaris Technological Tree View — changelog

## Contents

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
