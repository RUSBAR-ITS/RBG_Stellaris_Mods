# Second backend stage — modules, schemas, and rule profiles

## Contents

- [1. Status and basis](#1-status-and-basis)
- [2. Goal and boundaries](#2-goal-and-boundaries)
- [3. Module structure](#3-module-structure)
- [4. Definition sources](#4-definition-sources)
- [5. Application schema generation](#5-application-schema-generation)
- [6. Input rule profile](#6-input-rule-profile)
- [7. Rule blocks and registry generation](#7-rule-blocks-and-registry-generation)
- [8. Analyzer inputs](#8-analyzer-inputs)
- [9. Observations and recommendations](#9-observations-and-recommendations)
- [10. Configuration and file placement](#10-configuration-and-file-placement)
- [11. Programmatic operations](#11-programmatic-operations)
- [12. Builder integration](#12-builder-integration)
- [13. Errors and persistence](#13-errors-and-persistence)
- [14. Validation and acceptance](#14-validation-and-acceptance)
- [15. Implementation sequence and deliverables](#15-implementation-sequence-and-deliverables)

## 1. Status and basis

Date: **2026-11-15**. Project: **Stellaris Technological Tree View**, directory: `WEB_STTV`.

**Status: approved by the user, implemented and validated on 2026-11-15.** Instructions and results are documented in the [second-stage guide](BACKEND_STAGE_2_EN.md).

This document continues the [first stage](TZ_EN.md#3-first-backend-stage--database-building). The [shared principles and file-size limits](TZ_EN.md#2-project-structure-and-coding-principles), [database model](DATABASE_MODEL_EN.md), and repository rules apply. The actual first-stage implementation is documented in the [builder guide](BACKEND_STAGE_1_EN.md).

When the specification was prepared, stage one already built a database from current sources. Nested-command rules resided in a single `schemas/script_rules.json`; the generator for three JSON schemas was in the ignored `data/make_schemas.py`. Field descriptions were partly duplicated between the generator and `contracts.py`. These circumstances motivate this stage.

## 2. Goal and boundaries

The result is a modular backend with reproducible application-schema generation, configurable game-rule profiles, and an analyzer that proposes evidence-based profile changes.

The scope includes:

- Organizing existing code into packages and updating imports, tests, and working validation tools.
- Moving the schema generator into the permanent codebase and removing duplicated field descriptions.
- A closed input-profile format, shared rule blocks, a generator, and validation of the resulting registry.
- A supplied initial profile based on the current registry and support for user profiles.
- Analysis of selected sources, comparison with a profile, and structured recommendations.
- Integration of the selected profile into database building and programmatic operations for a future web UI.

The scope excludes a web UI, HTTP service, interactive user CLI, portable packaging, automatic acceptance of recommendations, execution of game conditions, and a complete engine-language specification. The database retains `format_version: 1`; localization remains RU/EN names, and database content is not expanded.

Profiles can change supported commands and their parameters within implemented language forms. Syntax the parser does not understand, or a new technology-object field, requires separate agreement on the model and processing.

## 3. Module structure

Existing responsibilities are allocated as follows; individual filenames within packages may be refined during implementation without changing these boundaries:

| Package within `src/backend/sttv/` | Responsibility |
| --- | --- |
| `common/` | Shared errors, JSON handling, product paths, JSON Schema validation, diagnostics |
| `sources/` | Source settings, file selection, reading, and source locations |
| `script/` | Game-language parser, local variables, command validation using a supplied registry |
| `technologies/` | Shared field contracts, collection and conversion of technologies, variants, categories, and tiers |
| `localization/` | Reading names and selecting translations by key and priority |
| `database/` | Completed-database and reference validation, persistence, and output replacement |
| `schema_generation/` | Shared helpers and separate declarations for application-schema generation |
| `rules/` | Loading, validation, expansion, and persistence of profiles and registries |
| `analysis/` | Observation collection, profile comparison, and recommendation preparation |

`builder.py` remains the build coordinator at the package root, and `src/backend/main.py` remains the CLI entry point. The shared product-root definition moves from `schema.py` into `common/paths.py`; moving files must not break path resolution from a different working directory.

Tests are grouped by the subsystem they validate. Shared fixtures remain shared. Cohesive functions must not be fragmented or lines compressed merely to meet file counts; the 200/300-line thresholds apply.

The generator in `data/` moves into `src/backend/sttv/schema_generation/` with a callable entry point. Its logic is not duplicated in a temporary folder or separate tool. A `tools/` directory for a second generator copy is unnecessary. Old import and invocation paths are not preserved through compatibility layers; instructions are updated.

## 4. Definition sources

Three kinds of data are distinguished:

| Kind | Defines | Changed through |
| --- | --- | --- |
| Application contracts | Database, configuration, and report structure; supported conversion methods | Implementation and its corresponding specification |
| Game-rule profile | Commands, contexts, scopes, arguments, and other parameters for a selected version | Validated JSON data |
| Analyzer observations | What actually occurred in selected sources | A new analysis run; observations do not authorize commands by themselves |

Technology, variant, category, and tier fields receive one declarative description: name, allowed context, type, cardinality, and conversion method. Both the schema generator and converter consume it. Independent lists of the same fields across modules are removed.

Shared representations of values, repeated assignments, and source locations are defined once and reused. A game-rule profile cannot add arbitrary database fields or disable structural validation.

## 5. Application schema generation

Generation of `database.schema.json`, `backend.schema.json`, and `report.schema.json` remains an explicit development operation. It uses declared contracts, does not infer constraints from a particular completed database, and does not require an installed game.

The database schema preserves the existing model. The configuration schema is extended only with this stage's settings. Report-structure changes are declared explicitly; analyzer observations and recommendations receive a separate schema and are not embedded in the database.

Additional closed schemas are created for the profile, generated registry, analysis settings, and analysis result. Schema-building helpers are reused; each schema has its own compact declaration.

Identical declarations must produce byte-identical outputs. JSON and schema correctness are checked before file replacement. Generated schemas remain project artifacts in `schemas/`. Ordinary database builds read them without rewriting installation files.

## 6. Input rule profile

A profile is a JSON document with a closed structure and explicitly declared references between sections. Unknown properties and unsupported argument forms are errors.

| Section | Contents |
| --- | --- |
| Identification | `format_version`, `profile_id`, profile revision, target game version |
| Provenance | Rule sources and evidence: file, position or record key, source version when known |
| Value types | Named descriptions based on supported kinds: boolean, number, integer, identifier, string, enum, block, inline; allowed reference forms and constraints |
| Scopes | Named scopes and references to them from rules |
| Contexts | Allowed command groups, required arguments, and nested-block restrictions |
| Rule templates | Shared argument types, operators, scopes, transitions, and cardinality |
| Command groups | Explicit command-name lists, usage context, and template reference |
| Individual differences | Explicit changes to a particular rule, with justification |
| Inline inclusions | Inclusion paths, allowed invocation forms, parameter names and types |

JSON field names are English. Profile-format version, content revision, and game version have distinct meanings; none replaces the database's `format_version`. The game version declares intended applicability rather than proving rule completeness or correctness.

Profiles contain no executable Python. Changing command lists, operators, types from the supported set, scopes, or arguments must not require editing Python. References to unknown templates, contexts, and scopes are rejected.

The initial profile transfers the existing registry's effective rules, including current defaults. Migration must not broaden them merely because the engine is presumed to behave differently. Unknown rule provenance is marked explicitly; checks against current files are not presented as confirmation of all engine-supported forms.

## 7. Rule blocks and registry generation

Shared rules reside in named blocks. A group associates an explicit command list with a template and context; individual differences change only explicitly listed properties. Unchanged common parts are not copied into every profile entry.

Illustrative profile fragment, not a complete document:

```json
{
  "value_types": {
    "boolean": {
      "kind": "boolean"
    }
  },
  "templates": {
    "country_boolean": {
      "rule": {
        "type": "boolean",
        "scopes": [
          "country"
        ],
        "operators": [
          "="
        ],
        "many": true,
        "context": null,
        "scope": null
      }
    }
  },
  "command_groups": [
    {
      "context": "condition",
      "template": "country_boolean",
      "commands": [
        "is_ai"
      ],
      "evidence": []
    }
  ]
}
```

The generator validates structure and references, expands templates, applies explicit individual differences, validates the resulting rules, and produces a registry. Identical duplicates within one context are consolidated; incompatible definitions are errors. The last entry in a file gains no hidden precedence. The same name in different contexts is allowed when those contexts are explicitly separated.

Recursive nested conditions are allowed under the declared grammar. Cyclic template inheritance and ambiguous merging are prohibited. Arbitrary multiple inheritance is unnecessary: shared blocks, explicit references, and individual differences suffice.

The registry stores selected-profile identity and a content fingerprint, or an associated validated provenance record. Reproducibility must not depend on current time or dictionary traversal order. Validation consumes the expanded registry; particular game-command names are not duplicated in Python.

## 8. Analyzer inputs

The analyzer receives the current profile and explicit reading settings. Technologies use the existing `TECH_PATH` and first-stage reading profiles, without scanning the entire game installation.

Additional sources are explicitly connected:

| Source kind | Extracted information |
| --- | --- |
| Game-command documentation | Documented argument forms, scopes, operators, and examples where the document format permits |
| Scripted-trigger definitions | Names, parameters, and actual definition structure |
| Inline-inclusion files | Paths, parameters, and construct usage |

Each additional source specifies an identifier, kind, path or global-variable reference, pattern, recursion, encoding, and enabled state. A source version is supplied when known; agreement with the game version is not assumed automatically. Supported reading formats must be declared and tested with samples.

Disabled sources are neither read nor required. An unavailable enabled source or unsupported format produces diagnostics; incomplete analysis is not presented as complete. Machine-specific paths are not embedded in code.

Additional directories are used only by the analyzer to prepare recommendations. Ordinary database builds remain limited to first-stage inputs. External script definitions are neither executed nor expanded into the database.

## 9. Observations and recommendations

Analysis results contain separate observation, recommendation, and diagnostic collections plus information about sources actually read. Their structure is closed and validated by its own schema.

An observation retains the command, original nesting path, context and scope when established, argument form, operator, and file/line reference. Scope is not guessed across an unknown scope-changing command. Repeated observations may be grouped while preserving supporting sources.

A recommendation contains:

- A stable identifier and proposed-change kind.
- Its profile target, the current rule or its absence, and one or more proposed alternatives.
- Its basis: observed usage, documentation, or an explicitly labeled inference.
- Supporting references, contradictions, and unresolved questions.
- The identifier and fingerprint of the profile against which it was prepared.

Recommendations cover adding a command to a suitable group, creating a group or block structure, adding an argument form, operator, scope, or inline parameter. Insufficient evidence produces a review question with possible alternatives rather than a mandatory change.

An argument appearing in every example does not prove it is required; a command absent from examined files is not thereby invalid. The analyzer does not authorize commands merely from similar names or suffixes, remove restrictions, or apply recommendations automatically.

The user selects and adjusts profile changes. At this stage, profiles may be edited as JSON and passed to programmatic operations. Recommendations based on an earlier revision require comparison with the current profile; silently applying stale recommendations is prohibited.

## 10. Configuration and file placement

| Path relative to the product or working folder | Purpose |
| --- | --- |
| `src/backend/sttv/schema_generation/` | Permanent schema-generation code |
| Product `profiles/` | Supplied validated profiles and shared rule blocks |
| Product `schemas/` | Generated application-structure schemas |
| `config/backend.json` | Active-profile selection and relative generated-rule output path |
| `config/analysis.json` | Additional sources and analysis settings |
| `WORK_DIR/profiles/` | User profiles |
| `WORK_DIR/rules/script_rules.json` | Default working registry |
| `WORK_DIR/reports/` | Generation and analysis reports |

Output names are configurable. Profile selection explicitly distinguishes the path base: product directory for a supplied profile or `WORK_DIR` for a user profile. Searching several directories for the first suitable profile is prohibited.

User outputs are saved inside `WORK_DIR`. Game-rule generation does not rewrite supplied profiles, schemas, or code. After migration, the old `schemas/script_rules.json` ceases to be an independently editable source; instructions and links are updated, and no parallel fallback rule copy is introduced for the builder.

Global paths and existing localization priorities are not duplicated. Changing `WORK_DIR` neither moves nor deletes earlier outputs. The application does not modify `.gitignore` or execute Git commands.

## 11. Programmatic operations

Separate callable operations load a profile, validate a profile, analyze sources, generate a registry, and safely save a selected result. Generating a validated registry does not trigger source analysis.

Each operation takes explicit data/settings and returns a structured result or structured error. Operations are available without a terminal and do not invoke `input()`, picker dialogs, or an HTTP service. Shared logic does not reside in the CLI.

A future web UI can display recommendations, collect user decisions, and pass an updated profile to the same operations. This stage tests those interactions through programmatic calls and fixtures without building a UI.

## 12. Builder integration

A build selects the configured profile, validates it, and expands it into a working registry. The builder uses that validated result. An old registry cannot bypass an error in a new profile; building does not start analysis or automatically accept recommendations.

Declared source versions and the profile's target version are compared when both are known. A mismatch is reported explicitly and never causes automatic selection of another rule version. Analyzing a new version against an earlier profile is allowed as a way to identify differences.

The initial profile must reproduce first-stage behavior on the same files, including unknown constructs, errors, repeated values, unresolved references, and name priorities. With unchanged sources, the resulting `database.json` must be byte-identical.

A completed database is validated without access to game directories: supplied schemas and an explicitly selected rule registry suffice. A required but missing registry is reported; sources are not silently read to reconstruct it.

## 13. Errors and persistence

Diagnostics distinguish source-reading failures, profile-structure errors, rule-reference errors, generation conflicts, unsupported constructs, and write failures. Profile errors identify a property path; source errors include available file/line locations. An unknown construct can be an analyzer observation while remaining a database-build error until the profile is explicitly expanded.

Saving a user profile or registry first validates the new document, writes a temporary file beside its target, rereads it, and replaces the target. A pre-replacement failure preserves the previous output. Profile or generation errors do not replace the previous database with a partial result.

Operations involving several files report which outputs were actually written; atomic replacement of one file is not presented as a transaction across all files. Final paths are checked against `WORK_DIR` and protected sources. Ordinary operations have read-only access to product schemas and profiles.

Source files and a persistent full parse tree are not copied. Reports may retain locations, fingerprints, and small excerpts needed to substantiate recommendations.

## 14. Validation and acceptance

1. Code is organized into the declared packages, imports work from another current directory, and the existing entry point is updated. Shared principles, DRY, and file-size limits are respected.
2. The schema generator runs from the permanent codebase without `data/` files or the game. Repeated generation is reproducible; schemas are valid and closed.
3. Fields and cardinalities for base technologies, variants, categories, and tiers are declared once. Generation/conversion agreement, rejection of extra fields, and preservation of the database model are verified.
4. The initial profile reproduces the original registry's effective rules. Both positive and negative scenarios are retained, beyond simply building current files successfully.
5. Fixture-based profile changes alter accepted commands, operators, scopes, and parameters without editing Python. Configuration cannot authorize an unsupported syntax kind.
6. Shared templates, individual differences, identical duplicates, conflicts, missing references, cycles, required arguments, and cardinalities are tested. An invalid profile does not produce a working registry.
7. The analyzer finds known and new constructs, preserves locations, distinguishes observations from inferences, and offers alternatives for ambiguity. Unknown scopes are not replaced with known ones.
8. Tests cover supported additional sources, a disabled source, an unavailable enabled source, an unsupported format, and unknown/mismatched versions. Analysis does not require every additional source at once.
9. Recommendations are bound to a profile content revision. They do not change the profile themselves; stale and contradictory recommendations require reconsideration.
10. Analysis, validation, generation, and persistence are callable programmatically without an interactive user CLI. JSON results conform to declared schemas.
11. Supplied/user profile selection and `WORK_DIR` behave correctly. Tests cover forbidden writes to sources and product files, preservation of earlier outputs on failure, and absence of hidden reuse of an old registry.
12. Existing first-stage checks pass with updated imports, along with meaningful new checks and a current-source build. Unchanged inputs produce a byte-identical database; source changes are not misrepresented as regressions.
13. A completed database is validated without game sources when schemas and the selected registry are available. Source hashes remain unchanged. Original-source counts are references rather than program constants.
14. Both guide versions, README, configuration documentation, and changelog are updated. Performed checks and unconfirmed engine properties are distinguished.

The criteria were checked during implementation. Actual results and limitations are listed in the [guide](BACKEND_STAGE_2_EN.md#validation-and-limitations).

## 15. Implementation sequence and deliverables

After specification approval, capture the first-stage reference result for unchanged inputs. Then move modules and the generator, consolidate field declarations, create profiles and registry generation, integrate them into the builder, implement the analyzer, and perform validation.

The permanent codebase contains modules, generators, schemas, the supplied profile, and tests. User profiles, registries, and reports reside in the selected working directory. Documentation records operation invocation, settings, initial-profile provenance, and analysis limitations.

[ТЗ на русском](TZ_BACKEND_STAGE_2_RU.md) · [Project overview](../README_EN.md).
