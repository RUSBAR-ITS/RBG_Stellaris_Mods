# Stellaris Technological Tree View — stage six specification: parsing results database

## Contents

- [1. Status and goal](#1-status-and-goal)
- [2. Stage scope](#2-stage-scope)
- [3. Build process and modules](#3-build-process-and-modules)
- [4. Sources and configuration](#4-sources-and-configuration)
- [5. Persisted JSON format](#5-persisted-json-format)
- [6. Checks, errors, and publication](#6-checks-errors-and-publication)
- [7. Removing previous mechanisms](#7-removing-previous-mechanisms)
- [8. Acceptance criteria](#8-acceptance-criteria)
- [9. Implementation order and deliverables](#9-implementation-order-and-deliverables)

## 1. Status and goal

**Approved by the user on 2026-11-15; stage six implementation is authorized.**

Implemented. Operation, format, and verification results: [stage-six guide](BACKEND_STAGE_6_EN.md).

The basis is the [updated concept](CONCEPT_EN.md), the working [stage-five parser](BACKEND_STAGE_5_EN.md), and the user's decision to persist parsing results as the primary database. This specification supersedes earlier requirements for a mandatory domain model, command profile, and localization retrieval during a build.

Goal: reduce the backend to source reading, syntax parsing, `inline_script` expansion, and JSON persistence of the resulting tree. A new game name or field must not require a profile, registry, or allowed-field list change.

The proposed storage unit is a parsed source file. All documents in the selected set are saved in one `database.json`. The node format describes our parser's output; game-name semantics are not validated at this stage.

## 2. Stage scope

Included:

- Replacing the domain builder with general tree persistence; reading saved JSON without the game or reparsing.
- Removing the profile, registry generation, and their dependent analyzer; reducing configuration, schemas, reports, and tests.
- Preserving the working parser, syntax configurations, nested expansion, and node provenance.
- Adapting independent frequency statistics and corpus checks to the simplified configuration.

Later stages cover RU/EN localization, numeric and formula evaluation, interpreting `prerequisites` and conditions, identifying technologies and variants, indexes, images, UI, and portable distribution. Do not introduce a plugin enrichment framework, empty enrichment sections, or a replacement game-command rule system now.

Grammar and expansion behavior remain at stage five. Its known limitations are neither fixed incidentally nor hidden by removing validation. Mod handling, override precedence, and multiple game roots are not added.

## 3. Build process and modules

Sequence: load configuration → select files → read → parse with expansion → serialize the tree → check result structure → publish JSON and report.

| Area | Responsibility after the change |
| --- | --- |
| `sources/` | Paths, file selection, read-only access, expansion-context creation |
| `script/` and `script/inlining/` | Existing syntax nodes, parsing, and expansion; node serialization without domain conversion |
| `database/` | Document container assembly, structure and metadata checks, JSON writing and reading |
| `common/` | Errors, report, JSON, shared path checks, and safe persistence |
| `schema_generation/` | Generation of the remaining configuration, result, and report schemas only |
| `builder.py`, `main.py` | Small operation coordinator and existing noninteractive entry point |

The build operation remains callable from Python and returns a report; the CLI accepts variables and configuration paths and returns a nonzero exit code on failure. Loading a saved database takes its JSON path without loading game, localization, or parser settings.

Serialization must not import technologies, localization, or command rules. Database consumers receive ordinary JSON objects; loading does not require reconstructing `Source.text`, tokens, or Python parser objects.

Follow the shared modularity, DRY, and file-size requirements. Do not introduce compatibility layers for the old format.

## 4. Sources and configuration

Keep `sources`, `parser`, and `outputs` in `config/backend.json`. Replace `definitions` with a source list; remove `rules` and `localization`. Initial source:

```json
{
  "sources": [
    {
      "variable": "TECH_PATH",
      "pattern": "*.txt",
      "recursive": true,
      "encoding": "utf-8-sig"
    }
  ]
}
```

This is a configuration fragment. It includes the technology directory and its `category` and `tier` subdirectories without assigning different domain models to them. `parser` retains four file selections: `lexical`, `constructs`, `logical_operators`, and `inline_scripts`. `outputs` retains `database` and `report` paths relative to `WORK_DIR`.

Require `STELLARIS_ROOT`, `WORK_DIR`, `INLINE_SCRIPTS_DIR`, `SCRIPTED_EFFECTS_DIR`, `SCRIPTED_VARIABLES_DIR`, and selected source variables; the initial configuration uses `TECH_PATH`. Resolve source paths relative to `STELLARIS_ROOT` and keep them inside it. `WORK_DIR` defaults to `data`; the permitted write area remains inside the repository and cannot overlap sources, code, or configurations.

`WORKSHOP_DIR`, `RU_LOC_TIER_*`, and `EN_LOC_TIER_*` may remain in the shared variables file for later stages. They are not required build inputs: missing Workshop or localization directories do not block this build. Known external sources remain protected against writes.

Select files in stable relative-path order; process the same physical file from overlapping selections once. Always exclude `INLINE_SCRIPTS_DIR` from independent traversal and read templates only through calls, including nested calls. Do not copy source files to the working directory. A missing selected directory or entirely empty selection is an error; an existing empty script is valid.

User-requested amendment dated 2026-11-15: add `SCRIPTED_EFFECTS_DIR = common/scripted_effects`, relative to `STELLARIS_ROOT`. Exclude the directory and descendants from independent selection using the shared builder and full-corpus filter; count excluded effect files separately from inline templates. Do not implement scripted effect expansion yet. The excluded directory need not exist unless explicitly selected as a source. For checks 7–8 below, initial counts remain a historical reference: compare new selection and failures with the previous report, write results under `data/stage6/without_scripted_effects/`, and preserve initial reports and lists.

Subsequent user request dated 2026-11-15: add required `SCRIPTED_VARIABLES_DIR = common/scripted_variables`, relative to `STELLARIS_ROOT`, with the same path restrictions and exclusion of the directory and descendants from independent traversal. Count excluded variable files separately. Future full audits use `data/stage6/without_scripted_libraries/`, preserving previous reports. This iteration verifies filtering and selected files without repeating full corpus parsing. Design static-variable substitution separately; this amendment neither implements substitution nor changes metadata.

Additional targeted user request dated 2026-11-15: include `trait_bg_active_glow` in `config/parser/constructs.json` → `tagged_blocks` alongside `rgb` and `hsv`. Preserve `trait_bg_active_glow { ... }` as a `tagged_block` without inserting the absent `=`. Other names do not gain permission to use this form. Check the actual `common/named_colors/01_trait_colors.txt`, JSON serialization, and rejection of unconfigured names. Record `CLASS` and `RELIC` issues in the shared bilingual TODO; investigate references and the actual file for the missing tradition template without changing its loading rules.

Further user request dated 2026-11-15: connect a separate `config/parser/exceptions.json` through the fifth selection, `parser.exceptions`. Declare `format_version: 1` and `inline_script_files`: exact invocation names map to relative `file` paths and a required explanatory `reason`. The first exception permits the extensionless `traditions/tr_purity_imperfection_remediation_wilderness` file. Validate paths, duplicate normalized names, configuration, and output protection; do not search arbitrary alternatives. Explicit exception priority, actual history/hash paths, template-root confinement, and retained cycle checks are required. This amendment supersedes the earlier restriction against loader changes: add the eighth schema, `parser_exceptions.schema.json`, and verification of the three tradition files. A full corpus audit is not required for this targeted amendment.

## 5. Persisted JSON format

The new format has its own identifier, `sttv.parse_database`, and `format_version: 1`. It is not the previous domain database version 1 or 2. The container below represents an empty source script:

```json
{
  "format": "sttv.parse_database",
  "format_version": 1,
  "documents": [
    {
      "source": {
        "root": "STELLARIS_ROOT",
        "file": "common/technology/example.txt"
      },
      "items": [],
      "metadata": {
        "inline_scripts": []
      }
    }
  ]
}
```

`documents` is an ordered file array; `items` is an ordered node array. Relative paths use `/`. Preserve nested elements, repeated names, standalone values, and mixed blocks without turning them into dictionaries keyed by game names. Do not merge definitions from different files or choose a winning duplicate.

Every node contains a string `kind`, the existing syntax-node fields, and its `span` and `origin`. Tuples become arrays. Names and values retain their case; logical-operator normalization remains exactly what the parser already performed.

| `kind` | Node fields besides `span` and `origin` |
| --- | --- |
| `scalar` | `raw`, `text`, `quoted`, `parameters` |
| `formula` | `raw`, `opener`, `body` |
| `block` | `items` |
| `tagged_block` | `tag` — scalar node; `block` — block node |
| `conditional` | `parameter`, `negated`, `items` |
| `assignment` | `key` — scalar node; `operator`; `value` — value node |
| `logical_operation` | `operator`, `name` — original scalar node, `assignment_operator`, `body` — block node |

Preserve `raw` and `text` as returned by the parser; do not perform additional unescaping. Scalar numbers, `yes`/`no`, identifiers, and `@name` references remain text; `quoted` records quotation. Parameters are objects `{name, default, raw, span}`, including `default: null`. Declarations such as `@name = ...` remain ordinary tree entries. Formulas, references, and parameters outside expanded invocations are not evaluated.

`span` contains `start`, `end`, `line`, `column`, `end_line`, and `end_column`, preserving current parser semantics: zero-based offsets, exclusive end, one-based lines and columns. Preserve `origin` without information loss: `root`, `file`, `span`, and `inline_call_id`; composed text also carries `generated_span`, `fragments`, and nested `placeholder` records. Generated-text coordinates must not be presented as physical template coordinates.

After successful expansion, `InlineInvocation` is absent from `items`. Its information exists only in `document.metadata.inline_scripts`: `id`, `parent_id`, `call_site`, `form`, `script`, `template`, `arguments`, and `insertion`. Preserve original and substituted arguments, nested invocation relationships, and empty insertions.

`insertion.container` is the existing JSON Pointer relative to its document, such as `/items/0/value/items`; `index` and `count` specify the inserted element range. Preserving node structure eliminates the previous history projection into domain database `result_paths`. Invocation identifiers must unambiguously connect history and `origin` within a document; stability across rebuilds is not promised.

Analytical traversal follows child-node fields only. `origin`, `span`, `parameters`, and `metadata` do not create additional game-text occurrences. Invocation history is not counted again alongside expanded content.

Do not persist the complete source text, lexical-token array, separate comments, whitespace, or BOM. The saved syntax tree supports analysis; byte-for-byte source reconstruction is not a goal. The representation has no domain-level `technologies`, `fields`, `name`, `name_sources`, computed dependencies, or empty enrichment section; game entries with those names inside the tree are preserved like any others.

## 6. Checks, errors, and publication

Check configuration, permitted paths, reading and encoding, syntax, expansion errors, JSON validity, node shape, and metadata-link integrity. Do not validate the existence of game commands, technologies, or categories, field types by game name, technology eligibility, prerequisite cycles, or resolution of ordinary `@name` references. A repeated game field is not itself a warning.

The result schema describes the container and listed syntax-node kinds, not a Stellaris vocabulary. Do not restrict `key.text` or other game names to enumerations. Removing the profile does not permit corrupted trees: an unknown node type must not be silently discarded or converted to a string.

Keep seven schemas: `backend.schema.json`, four `parser_*.schema.json` files, `report.schema.json`, and a rewritten `database.schema.json`. Keep the generator in the codebase; generation does not require game files or a profile. Check insertion ranges, parent existence and absence of `parent_id` cycles, and identifier consistency between history and provenance. These checks do not interpret game conditions.

The report retains status, whether the database was written, errors and warnings with locations and call chains, selected/successful/failed file counts, node counts, and inline statistics. Define the node count as all serialized objects with `kind`, including scalar keys and values, excluding history. Remove technology/variant counts and registry-write flags. Record paths and SHA-256 hashes of read sources and reached templates; do not embed the report in the game tree.

Do not publish a partial database after a read, parse, expansion, or structural-check error. Preserve the last successful JSON. Prepare the complete result in a temporary file before replacing the destination; temporary files belong in the permitted work area and are cleaned up after the operation.

Database and report are separate files: do not promise a joint atomic transaction. If database replacement succeeds but report writing fails, return failure and truthful `database_written: true`. A database-write error must not be reported as a successful build. Identical sources and configurations produce identical database JSON; any run timestamp needed by the report stays outside the database.

## 7. Removing previous mechanisms

| Area | Action within this stage |
| --- | --- |
| `profiles/stellaris_4_5_4.json`, `rules/` package | Remove the profile, registry compilation, and registry validation |
| `analysis/` package, `config/analysis.json` | Remove the profile recommendation analyzer and its configuration |
| `technologies/` package | Remove closed contracts, domain conversion, relationship computation, and provenance projection |
| `localization/` package | Remove current enrichment of the old model; future name retrieval is designed separately |
| `script/rules.py`, `values.py`, `variables.py` | Remove domain value validation and variable evaluation after checking dependencies |
| `script/serialization.py` | Replace `DataEntry` and domain projection with syntax-node serialization |
| `database/validation.py`, `storage.py`, builder, and settings | Reduce to the new format and process |
| `profile`, `registry`, `analysis`, `analysis_report`, `generation_report` schemas | Remove files and their generators; retain shared helpers still in use |
| Tests of removed mechanisms | Remove alongside those mechanisms; replace build checks with checks of the new result |

Do not leave removed modules disabled for hypothetical future use. Move any useful shared helper they contain to the appropriate retained module and update imports. Do not delete the general parser or expansion merely because they sit alongside old code.

Preserve `language/keywords/`, research, and agreed classifications as reference material; they do not become build inputs. Preserve frequency and scalar statistics and independent parser/expansion tests. Check for active imports or invocations of the removed profile, registry, and analyzer, including test utilities.

Keep previous specifications and stage results as history; the current README and new guide must clearly identify the current process. Do not delete or overwrite old generated reports and research lists in `data/` and `TMP/` during code cleanup. A successful new build replaces the standard `database.json` with the new format. Old-database migration and loading through the new loader are unsupported; recognize incompatible formats and report that rebuilding is required.

## 8. Acceptance criteria

1. Building works without a profile, registry, Workshop, or localization directories. Unknown game fields and commands are saved without adding rules.
2. All seven node kinds survive JSON writing and reading with their fields, order, duplicates, case, quotes, parameters, and provenance intact. Cover formulas, anonymous and mixed blocks, conditional fragments, and tagged blocks; do not use the previous restrictive `DataEntry`.
3. Nested and repeated inline calls with different arguments expand as before. History, empty insertions, and relative pointers remain correct after serialization; history does not increase frequencies.
4. Corrupted JSON structure, history links, and insertion ranges are rejected. Missing templates, substitution failures, cycles, and depth limits remain expansion errors.
5. Verify read-only sources, path protection, file deduplication, optional localization, repeatability, and loading without game access. A failed build preserves the previous database; publication errors are reported truthfully.
6. Parse the installed technology directory and compare serialized trees with current parser results. The expected 301 expanded calls from 10 templates are stage-five reference observations for unchanged sources, not code limits. Technology count is not a mandatory counter in the new builder.
7. Repeat the existing `common/` and `events/` audit, excluding templates as independent inputs and retaining existing explicit documentation-TXT exclusions. Compare against stage five: 1,583 successful and 22 failed inputs for the same corpus. Check serialization of successfully parsed trees; report known errors separately rather than presenting the whole corpus as a successfully built database.
8. Preserve frequency filters: case-insensitive merging; exclusion of `yes`/`no`, recognized logical operators, inline calls as history records, variables and substitutions, and frequencies of 1. Write new results under `data/stage6/`; do not alter previous manually processed lists.
9. Check generation of seven schemas, retained module tests, absence of active dependencies on removed subsystems, documentation, and both language versions. Record actual counts, result size, and limitations in the stage report.

## 9. Implementation order and deliverables

After specification approval:

1. Capture baseline parser and expansion checks; implement serialization and reading of the new container.
2. Convert the builder, settings, schemas, and report to the new process.
3. Remove the listed subsystems and unused dependencies; adapt retained tests and utilities.
4. Run synthetic and real-source checks under `data/stage6/`, then publish the standard database after successful technology-set verification.
5. Update the README and changelog; create a bilingual stage-six guide covering format, operation, checks, and limitations. Explicitly mark descriptions of the old domain database as historical.

The deliverable is a standalone JSON database of syntax trees and a reduced backend without a game-command profile. Specific enrichment actions and their storage model will be agreed in subsequent specifications.
