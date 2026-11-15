# Stellaris Technological Tree View — stage seven specification: static variables

## Contents

- [1. Status and objective](#1-status-and-objective)
- [2. Scope](#2-scope)
- [3. Sources and configuration](#3-sources-and-configuration)
- [4. Declarations and name resolution](#4-declarations-and-name-resolution)
- [5. Substitution and inline_script](#5-substitution-and-inline_script)
- [6. Tree and metadata](#6-tree-and-metadata)
- [7. Build process and modules](#7-build-process-and-modules)
- [8. Errors and reporting](#8-errors-and-reporting)
- [9. Verification and acceptance](#9-verification-and-acceptance)
- [10. Implementation deliverables](#10-implementation-deliverables)

## 1. Status and objective

**Approved by the user on 2026-11-15; substitution implementation is authorized.**

Based on the [concept](CONCEPT_EN.md), [shared development principles](TZ_EN.md#2-project-structure-and-coding-principles), [current backend](BACKEND_STAGE_6_EN.md), and the user's decision to substitute static variables without separate replacement history in metadata. `SCRIPTED_VARIABLES_DIR` and its exclusion from independent selection are already implemented.

Objective: replace `@name` references in working tree values with declared static values. The resulting JSON remains a database of parsing results; no technology domain model or game-command registry is reintroduced.

Preparation structurally checked 23 files under `common/scripted_variables/`: 2,917 declarations, all numeric scalars, with no duplicate names or case collisions. In 232 files found by declaration-line searches outside that library, 1,228 declarations were structurally checked; all are top-level. After inline expansion, the 35 technology files contain 1,929 value references, all with declarations; this selection contains no quoted references or references preceding a local declaration. These observations concern current files and do not prove every engine rule. Research material: `data/stage7/specification_research/`.

## 2. Scope

Include shared-library reading, local declarations, reference chains, scalar substitution, diagnostics, and integration with builds and analysis. Do not create per-replacement history, per-node lists of variables used, or before/after value copies.

Outside scope: evaluating `@[ ... ]` and `@\[ ... ]`, game-state variables such as `set_variable`, `value:...`, `event_target:...`, localization, scripted effect/trigger expansion, mod support, and additional `$PARAM|default$` / `[[PARAM] ... ]` rules. Do not fix `CLASS` or `RELIC` issues from the [TODO](../../TO_DO_EN.md). Formulas occurring as ordinary values remain unchanged, including their contents.

## 3. Sources and configuration

The shared library is `STELLARIS_ROOT / SCRIPTED_VARIABLES_DIR`, defaulting to `common/scripted_variables`. Read it separately; do not add its files to `documents` or frequency lists as independent inputs. Retain the existing `INLINE_SCRIPTS_DIR` and `SCRIPTED_EFFECTS_DIR` traversal exclusions.

Add a sixth configuration selection: `config/backend.json` → `parser.static_variables`, using existing `product` / `work` bases. Its default target is `config/parser/static_variables.json`:

```json
{
  "format_version": 1,
  "prefix": "@",
  "name_pattern": "[A-Za-z_][A-Za-z0-9_]*",
  "case_sensitive": true,
  "pattern": "*.txt",
  "recursive": true,
  "encoding": "utf-8-sig",
  "max_reference_depth": 64
}
```

Apply `name_pattern` as a full match to the name without its prefix. Reject invalid expressions, patterns accepting an empty name, empty prefixes, and nonpositive depth limits. Configuration must not conflict with formula or parameter notation; retain the precedence of existing syntax constructs. Do not add error-policy switches or a separate inventory of game variables.

Read the library in stable relative-path order, accounting for identical physical files once. Reuse pattern, encoding, and directory-boundary checks; file links cannot escape the permitted directory. Do not copy or modify sources. The directory becomes required for a build and must exist; an existing empty directory is valid, for example when testing local variables only. A selected-file read failure blocks the build. Caches last one operation; the next build rereads sources.

Declare a ninth generated schema, `parser_static_variables.schema.json`; update declarations for `backend.schema.json` and `report.schema.json`, then run the existing generator. Do not edit generated schemas manually.

## 4. Declarations and name resolution

A declaration is a top-level assignment using `=`, an unquoted `@name` key, and a scalar value. A scalar without unresolved parameters is allowed: numeric text, `yes`/`no`, an identifier, or a quoted string. Numeric conversion is unnecessary: `0.50` remains `0.50`. An unquoted `@other` value refers to another static variable; quoted `"@other"` is a literal string.

Formulas and blocks as declaration values are unsupported in this stage and cause a diagnostic error. Do not invent a scope for nested declarations: reject them. An unresolved parameter in a declaration name or value is also an error. Shared files may contain declarations, comments, and blank lines; reject other standalone constructs in the library.

Resolution rules for implementation:

1. Collect the complete shared declaration table and resolve its chains within the shared scope.
2. After inline expansion, collect a separate table of top-level local declarations for each input document. Local names override shared names; declarations never leak to another document.
3. Local chains search the local table first, then resolved shared values. Shared chains are not recalculated through local overrides: their results are identical for all documents.
4. Collect tables before resolving references, allowing references to later declarations. Check all declarations, including unused chains.
5. A repeated name within one scope is an error, even when values match. A local override of a shared name is valid. Do not choose a winner by incidental file order.
6. Names are case-sensitive by default. With `case_sensitive: false`, apply the same normalization to declarations, lookup, and duplicate detection; preserve original spelling in nodes.
7. Cycles and exceeding `max_reference_depth` are distinct errors. Count depth as transitions between declarations; a direct scalar declaration has depth zero.

Two-pass resolution, duplicate handling, and configurable case matching define the backend contract here. Do not present these choices as runtime-verified engine rules for all edge cases. The current verified selection does not require choosing between conflicting declarations.

## 5. Substitution and inline_script

Order: existing parser → complete nested `inline_script` expansion with current `$PARAM$` substitution → static-variable resolution → serialization. The base syntax parser does not read the variable library itself and retains the ability to return the original tree.

Replace only an entire unquoted scalar value matching reference notation. This includes assignment values and standalone list items at any depth. Do not replace field names, declaration keys, tags, logical-operation names, comment text, quoted strings, fragments such as `prefix_@name`, `flag@root`, or formula contents. Do not classify a scalar containing unresolved `$PARAM$` as a static reference.

After expansion, references in an inserted working body use the caller document's table. Argument `VALUE = @cost` inserted as `amount = $VALUE$` first becomes `amount = @cost`, then receives its value. If the template inserts the argument inside quotes, the resulting string remains literal. Nested insertions follow the same rule; the shared template cache must not leak substituted values between documents.

A declaration inserted at document top level joins that document's local table; one inserted inside a block is an unsupported nested declaration. Do not add static-variable resolution to `inline_script` paths: path expansion occurs earlier. Do not change current missing-template or missing-argument handling to bypass this restriction.

Working-value illustration:

```text
@base = 100
@cost = @base
tech_example = { cost = @cost }
```

After substitution, `tech_example.cost` is a scalar with `raw: "100"`, `text: "100"`, `quoted: false`, and `parameters: []`. Local declarations remain in their original form in the tree.

## 6. Tree and metadata

The replaced scalar receives the resolved literal's `raw`, `text`, `quoted`, and empty `parameters`. Preserve its own `span` and `origin` from the reference use site, including existing inline provenance. Do not move declaration coordinates onto the use site: coordinates identify the original reference, not the length of the substituted text.

No new node fields or `metadata` sections are required. Do not append `@name` replacements to existing `inline_scripts` history; its arguments remain as passed during expansion. Do not attach declaration provenance or resolution chains to every replaced value's `origin`. The chain is available only in an error message when resolution fails.

Node order and count remain unchanged. Local declarations preserve original values, including references in chains; these are existing source-tree entries, not additional replacement history. Keeping nodes in place preserves `insertion` ranges and invocation-history links.

The structural database format remains `sttv.parse_database`, `format_version: 1`; node kinds and the container schema are unchanged. For a processed working scalar, `raw` now means the substituted literal's text, so it need not match source text at `span`. Loading the database still requires no game, configuration, or repeated substitution. Merely reading an older database does not resolve its values; rebuilding is required.

Analysis consumes the processed tree. Skip complete top-level static declarations in frequency lists so their keys and original values are not counted as additional working uses. Retain existing filters for `yes`/`no`, parameters, logical operators, and single occurrences. Metadata remains excluded from traversal.

## 7. Build process and modules

Build sequence: load and validate settings → read and resolve shared declarations → select independent files → parse each file with inline expansion → resolve local declarations and replace working references → serialize → validate structure → publish.

Separate responsibilities: library reading and hashes in `sources/`, tables and node traversal in a compact module or package `script/variables/`, and coordination in the existing builder. Use one processor for database builds and corpus analysis; do not implement duplicate algorithms. Serialization remains generic and does not resolve names itself.

Apply DRY, existing reading/checking helpers, and established error handling. Target files below 200 lines; files above 300 require functional separation except for a justified indivisible block. No new dependencies, interactive CLI dialogue, or command registry is needed.

## 8. Errors and reporting

Diagnose unavailable libraries, configuration/read errors, invalid or unsupported declarations, repeated names, unknown references, cycles, and depth limits. Reference errors identify the name, source file, line/column, and name chain; conflicts identify both declarations. Reuse diagnostic fields and message text without recording all successful replacements.

A shared-library error stops the build before documents are processed. A document error is recorded against that document; other files may still be processed for reporting. Any error prevents publication of a new database and preserves the previous successful one. Do not substitute fallback values or publish an unresolved reference as successfully processed.

Extend only the operational report: `static_variable_sources` maps read library files' game-relative paths to SHA-256. `counts.static_variables` contains `files`, `global_definitions`, `local_definitions`, `references`, and `substituted`; references inside declarations are excluded from the last two counters. Counts reflect the portion actually processed, including on failure; library files do not increase `selected_files`. Increment report format from 2 to 3; retain existing fields' meanings and do not migrate old reports.

Input manifests and aggregate counters are not per-substitution metadata and are not stored in the database. Write verification results under `WORK_DIR/stage7/`; verification runs must not overwrite previous databases, research reports, or manually curated lists.

## 9. Verification and acceptance

1. Shared/local variables, local overrides, two-document isolation, forward references, and chains at both levels resolve under section 4. A shared chain retains its own scope when a local name overrides one of its dependencies.
2. Verify both case modes, duplicates within a file and across shared files, unknown names, self-reference, multi-name cycles, the depth boundary, unused erroneous chains, nested declarations, and unsupported formula declarations.
3. Preserve numeric spelling; substitute identifiers, booleans, and strings as syntax scalars. Leave quoted `"@name"`, composite names, and formulas unchanged. Unresolved parameters are not static references.
4. Substitution works in lists, nested blocks, and nested inline expansions, including argument `VALUE = @cost` and two documents with different local values. History, coordinates, node counts, and ordering remain valid; no variable metadata is added.
5. Verify configurable directories, recursive selection, empty libraries, missing directories, configuration errors, source/path protection, and rereading changed libraries on the next run. Shared files are not standalone documents or duplicated through overlapping selection.
6. Generated schemas match declarations. JSON passes structural checks and loading without the game; rebuilding unchanged inputs is byte-for-byte reproducible. A failed build preserves the previous database. All current tests pass.
7. Build the installed game's technology selection in a separate work folder: verify resolution of every recognized working reference and preservation of sources, inline history, and coordinates. Current research controls are 35 files and 1,929 references; explain changed counts when inputs change instead of hardcoding them.
8. Audit all `common/` and `events/` files with the three current library exclusions, then write new frequency lists under `stage7/text_frequency/`. Distinguish previous expansion failures from new resolution errors; the historical remainder of 16 files is not a guaranteed result. A corpus report may be partial, but a working database must be fully successful. Report new source issues outside this specification to the user.

## 10. Implementation deliverables

Substitution code, configuration, schema declarations and generated outputs, checks, a separate bilingual stage report/guide, and updated README and changelog. Verification records sources and coverage limits. Nothing is written to the game; runtime game checks and vanilla bug fixes are outside this stage.

Operation and implementation results are described in the [stage guide](BACKEND_STAGE_7_EN.md). [Русская версия ТЗ](TZ_BACKEND_STAGE_7_RU.md).
