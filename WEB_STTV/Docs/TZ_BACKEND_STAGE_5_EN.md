# Stellaris Technological Tree View — stage five specification: inline_script expansion

## Contents

- [1. Status and goal](#1-status-and-goal)
- [2. Scope and evidence](#2-scope-and-evidence)
- [3. Configuration and template lookup](#3-configuration-and-template-lookup)
- [4. Invocation and argument parsing](#4-invocation-and-argument-parsing)
- [5. Substitution and nested calls](#5-substitution-and-nested-calls)
- [6. Tree insertion and module boundaries](#6-tree-insertion-and-module-boundaries)
- [7. Metadata and node provenance](#7-metadata-and-node-provenance)
- [8. Builder and strict database model](#8-builder-and-strict-database-model)
- [9. Analysis and reports](#9-analysis-and-reports)
- [10. Errors and reproducibility](#10-errors-and-reproducibility)
- [11. Verification and acceptance criteria](#11-verification-and-acceptance-criteria)
- [12. Deliverables](#12-deliverables)

## 1. Status and goal

**Approved by the user on 2026-11-15; implementation authorized.** The agreed direction is to replace the empty stub with actual `inline_script` expansion, handle nested calls, and retain their arguments as metadata excluded from analysis.

References: [general requirements](TZ_EN.md), [implemented stage four](BACKEND_STAGE_4_EN.md), [syntax description](SCRIPT_SYNTAX_EN.md), and [current database model](DATABASE_MODEL_EN.md). This document defines the next stage's changes; it does not describe existing behavior.

Outcome: the working tree contains parsed template constructs with substituted arguments at each invocation position. Their origin is available through `metadata.inline_scripts` and node provenance. Repeated invocations of the same file remain distinct calls.

## 2. Scope and evidence

The stage covers template loading, both invocation forms, textual argument substitution, recursive expansion, result provenance, adaptation of existing tree consumers, and the required closed-schema changes. Support is not restricted to the ten templates used by technologies in the current installation.

Excluded: executing game conditions, calculating weights or effects, expanding scripted triggers/effects, loading global game variables, replacing the command profile, continuing keyword classification, the interface, and portable packaging. Template expansion does not prove that a command is valid in its game context.

The game documentation at `STELLARIS_ROOT/common/inline_scripts/00_README.txt` describes file inclusion, string parameters, and passing multiple commands inside a string. Actual examples and the previous audit are recorded in `TMP/WEB_STTV/text_frequency/inline_scripts_inventory.json`. That snapshot contains:

- 6,885 physical invocation sites: 1,532 references and 5,353 blocks; 246 invocation sites occur inside templates.
- Empty and multiline strings, code fragments, `@name` references, and substitutions in arguments and nested invocation paths.
- 301 calls with existing targets in `common/technology/`, using 10 distinct templates; no nested calls were found in this static closure.
- 45 parameterized paths and 5 static references to missing TXT files across the full corpus. These are baseline observations, not guaranteed results of future expansion.

Conditional fragments `[[...]]` and parameter defaults `$NAME|value$` were not found in the inspected inline templates. Executing them is outside this stage: expansion requiring such a form produces a specific unsupported-form error. Their existing syntactic representation outside expansion is preserved.

All game sources are read-only. Full source copies are not placed in the working directory. Working output goes to the configured `WORK_DIR`; temporary checks may use `TMP/WEB_STTV/`.

## 3. Configuration and template lookup

Use the existing `INLINE_SCRIPTS_DIR = common/inline_scripts` variable from `global_variables.json`. Resolve it against `STELLARIS_ROOT`, verify that the directory exists, and include it among protected sources. Load templates by reference without requiring another full-game scan.

Add `config/parser/inline_scripts.json` and its required `parser.inline_scripts` selection in `config/backend.json`, using the existing form `{ "base": "product", "path": "config/parser/inline_scripts.json" }`.

```json
{
  "format_version": 1,
  "path_field": "script",
  "parameter_case_sensitive": true,
  "extension": ".txt",
  "encoding": "utf-8-sig",
  "max_depth": 64
}
```

`max_depth` is a positive limit on the active call chain; the first call has depth 1. The initial value of 64 is a limit of our handler, not a claimed Stellaris engine limit. Argument names are matched exactly by default, retaining case; this is an explicit parameter-handling policy, not a statement about case sensitivity throughout the language.

The `inline_script` name and its matching mode stay in `constructs.json`; the same mode applies to `path_field`. Parameter, string, comment, and block delimiters come from the existing configurations. Do not create a second set of lexical rules or an allowlist of templates or parameters.

An invocation path is a relative name without an extension. After substitution and removal of outer quotes, `technologies/rare_technologies_weight_modifiers` resolves to `INLINE_SCRIPTS_DIR/technologies/rare_technologies_weight_modifiers.txt`. Support subdirectories and separator normalization. Absolute paths and resolved paths outside the template root are rejected; do not automatically try another directory or a similarly named file.

Update settings loading, source validation, and the schema generator together. Configuration read errors must not activate hidden fallback values.

## 4. Invocation and argument parsing

Support these forms:

```text
inline_script = "technology/archaeotech_weight"
inline_script = {
    script = technologies/rare_technologies_weight_modifiers
    TECHNOLOGY = tech_pk_cracker
}
```

The short form supplies no arguments. A block contains exactly one scalar path field and zero or more named scalar arguments using `=`. The position of the path field relative to arguments does not matter. Duplicate path fields, duplicate arguments, an empty path, a missing path field, and nonscalar arguments are errors.

The invocation block uses argument parsing: `NOT = no`, `IS = yes`, or `OR = "..."` are arguments, not logical operations. A string containing game commands remains an argument value until inserted into a template. Code blocks are passed as strings, as in game sources; this specification does not introduce arbitrary unquoted blocks as argument values.

Store each argument separately as `name`, `raw`, and `value`: the original name, exact value notation in the source file, and substitution text after applying the outer context and string framing rules. `raw` includes original quotes and line breaks where present. `value` is always a string: numbers, `yes`, `no`, and `@name` are not converted to Python numbers or Booleans during binding.

Use the existing string and escape rules. Outer quotes frame an argument; quotes required by the inserted code itself are retained according to those rules. A supplied empty string differs from a missing argument. Retain unused arguments in metadata; report a warning instead of adding them to the working tree.

## 5. Substitution and nested calls

Process each invocation in this order:

1. Read its form. Inside a template, obtain the effective path and values from the parent's substituted text while preserving links to the original notation.
2. Create an isolated environment from explicitly supplied arguments. A nested call receives parent values through its own invocation text; it does not implicitly inherit the parent's dictionary.
3. Locate and read the template. Substitute values for `$NAME$` in meaningful text: names, values, strings, compound identifiers, formulas, and paths. Comments neither introduce required parameters nor expand into code.
4. Parse the resulting text with the shared parser. Logical constructs in inserted code are recognized using the active operator configuration.
5. Expand nested calls with the same handler and insert their results at the original invocation positions.

Substitution is textual and occurs **before structural parsing of the template body**. It must support an argument containing several constructs, rather than only replacing one already parsed node. Existing parameters in untouched source files outside an inline context continue to follow the previous parsing rules.

A binding pass must not reinterpret a substituted value as a new argument of the same invocation. Do not repeatedly replace `$...$` until all dollar signs disappear. A parameter without a binding in meaningful expanded text is an error identifying the parameter and call chain, not an empty string or a silently retained fragment.

Nested argument forwarding example, using synthetic test files:

```text
# Caller
inline_script = { script = example/outer TECHNOLOGY = tech_example }

# example/outer.txt
inline_script = { script = example/inner TECH = $TECHNOLOGY$ }

# example/inner.txt
has_technology = $TECH$

# Expanded result
has_technology = tech_example
```

In the child call's metadata, `TECH.raw` remains `$TECHNOLOGY$`, while `TECH.value` is `tech_example`. Both invocations are retained, with the child referencing its parent. If a parent argument generates the invocation text itself, provenance points to that argument rather than an invented template line.

The inline handler does not execute `@name`, `value:...`, scope references, or game conditions. Following textual insertion, these retain their position in the calling context; existing local-variable resolution is performed by the subsequent consumer. A template does not become a separate game scope merely because it resides in another file.

## 6. Tree insertion and module boundaries

Replace the behavior of `expand_inline_script`: it returns expanded nodes and invocation information. Insert nodes into the containing sequence at the invocation position without adding a game block. Preserve order, duplicate keys, adjacent entries, and empty parent blocks. An empty template inserts zero nodes but still creates an invocation metadata record.

Use compact modules for invocation parsing, template loading and lookup, binding and substitution, nesting control, and provenance. Reuse shared helpers and the current parser; do not write an independent game-language parser for inclusions. File organization follows the module-size constraints in the [general specification](TZ_EN.md#23-file-size).

The parser does not discover the game directory itself. The loader supplies an expansion context containing template access, configuration, the call chain, and a metadata collector. Production builder and analyzer entry points use this shared path. Tests can supply templates from memory.

Retain a separate way to read **a template without arguments** syntactically for research. This is an explicit input-document role, not an automatic fallback after an expansion error. In this role, parameters and invocations remain available to research code as source constructs; the result is not presented as an expanded object or used to build the finished database.

Read text and its checksum may be cached within one run. Substituted results, environments, and mutable nodes are not shared between calls. Cycle detection uses the active chain of canonical paths; independent repeated calls are not cycles. Repeated files in the active chain are rejected even when arguments differ; parameterized self-recursion is outside this stage.

## 7. Metadata and node provenance

Add `metadata.inline_scripts` to the tree document as an ordered array of invocation records. Order is depth first, with parents before children. With no calls, the value is `[]`. Service records are not members of `items`, `Block.items`, or logical-operation bodies.

The common part of an invocation record:

| Field | Type and purpose |
| --- | --- |
| `id` | String; an invocation identifier unique within the run output, reproducible for identical inputs and traversal order |
| `parent_id` | String or `null`; the immediate parent invocation |
| `call_site` | Source file and invocation span; generated text references the argument/fragment that produced it |
| `form` | `reference` or `block` |
| `script` | Object with `raw` and `value`: original path notation and effective name after substitution |
| `template` | File relative to `INLINE_SCRIPTS_DIR`, including its extension |
| `arguments` | Array of `{name, raw, value}` in source order; `[]` for the short form |

In the AST, records also contain `insertion = {container, index, count}`. `container` is a JSON Pointer to a node sequence in the final document, `index` is the zero-based insertion start, and `count` is the number of inserted nodes in that sequence after nested expansion. Parent and child ranges may overlap; empty results have `count = 0`. Compute positions against the final tree, not an intermediate list before substitution.

Every node retains provenance: a source identifier (`STELLARIS_ROOT`, `TECH_PATH`, or `INLINE_SCRIPTS_DIR`), relative file path, original span, and `inline_call_id` or `null`. Spans follow the existing `Span` convention: offsets start at 0, ends are exclusive, and lines and columns start at 1. For synthetic text, additionally distinguish the span after substitution from the source fragments that produced it. Do not present a generated-text line as a physical-file line.

Links must allow diagnostics to identify the invocation, template, and argument responsible for an error, including after multiline substitution. Retaining provenance does not require copying every complete template body into every metadata record.

## 8. Builder and strict database model

The builder receives the expanded tree before `data_entries` projection and local-variable collection. Inserted definitions and fields undergo existing conversion in their actual context. Template lookup and parameter discovery do not require the game command profile.

Introduce root-level `metadata.inline_scripts` in the database to preserve invocation history. Its common record fields match section 7. Replace the AST-only `insertion` field with `result_paths`, an array of JSON Pointers to generated values in the final database. One call may create several values or definitions; an empty insertion has `result_paths = []` while retaining its call site. Do not merge nested or repeated invocations.

Explicitly extend the provenance contract: `SourceLocation` contains `root`, `file`, `line`, `column`, and `inline_call_id`; `root` establishes the relative-path base. Replace the ambiguous standalone `line` in `ScriptEntry` with `source: SourceLocation`; also record local variable definition sources explicitly. A technology's definition location may differ from the origin of its inserted entries. Localization-source structures remain unchanged.

In `file_variables`, the key continues to identify the calling-context file; inserted variable definitions carry their separate origin. Global variable values from other directories do not begin resolving automatically.

Declare these changes in the database model and closed-schema generator; set `database.format_version = 2`. Keep metadata outside game `fields` and reject arbitrary new fields. Rebuild old databases without migrations or compatibility layers.

The structural parser does not acquire command-semantics validation. Existing database projection validation continues separately. If expansion exposes an unsupported game field or command, record the precise example and obstacle; do not automatically extend the registry or replace the result with the original invocation. Changes to model semantics or command rules outside this specification require separate approval.

The user separately approved five commands exposed by expansion: `is_preferred_weapons` and `is_councilor_type` as identifiers; `ai_armor_ratio` and `ai_shields_ratio` as numeric comparisons; `is_ai_ship_role` as a block requiring `ship_size` and `role`. This is a targeted profile addition; the remaining rules are unchanged.

## 9. Analysis and reports

Frequency, scalar-usage, and construct walkers read only working nodes in the expanded tree. Exclude `metadata`, original invocation strings, argument names, and template paths from counts. If an argument's value appears in expanded code, count it there normally, using existing filters for logical operators, `yes`/`no`, variables, and substitutions.

The same template called twice contributes twice to statistics. Do not additionally analyze its file as an independent expanded object. Physical template-file inspection and expanded-object analysis are separate report modes; their frequencies are not added together. Do not invent arguments to expand a parameterized template without a calling environment.

During a full-game pass, exclude the configured `INLINE_SCRIPTS_DIR` directory and all its subdirectories from the list of independent input files. Read its templates only through calls from processed objects, recursively including nested calls. This exclusion applies to initial traversal, not to the expansion loader. Unreachable templates are outside this pass; separately inspecting them is not a required part of verification.

Define `counts.inline_scripts` in expansion reports:

- `encountered`: all reached calls, including nested and failed calls;
- `expanded`: calls that completed insertion successfully, including empty ones;
- `failed`: calls with expansion errors; a child error also prevents its unfinished parent call from succeeding;
- `template_files`: number of unique files read;
- `max_depth`: maximum depth reached.

At the end of processing, `encountered = expanded + failed`. Track root files, successfully expanded documents, and primary diagnostic errors separately: these are not invocation counts. Remove the obsolete `skipped_inline_scripts` from expanded-mode contracts; missing insertions are no longer successful skips.

During implementation, adapt research passes to the new tree and verify them using separate output under `WORK_DIR/stage5/`. Do not overwrite the manually reduced `scalar_assignments.txt` or current working frequency lists without a separate user task.

## 10. Errors and reproducibility

Diagnostics must distinguish configuration errors, malformed calls, duplicate arguments, missing templates, invalid paths, missing parameters, unsupported substitution forms, cycles, depth-limit violations, reading/encoding failures, and syntax errors in expanded text. Each expansion error contains the root source and available call chain; do not print one nested failure repeatedly as independent root causes.

Do not replace an erroneous invocation with an empty result. A failed document cannot enter the build as a partial success. The builder may continue diagnosing other files, but must not publish a new database when errors exist; retain the previous successful database. Save the report independently of database publication.

A full corpus audit may finish with errors for individual files. In particular, missing templates referenced by reached calls and source syntax defects in processed files are reported as errors rather than hidden by exceptions to obtain a zero-error run. Do not import unreachable-template errors from a previous audit into the current pass report.

Source traversal order, invocation IDs, metadata, and output must be reproducible for identical file contents and settings; execution timestamps belong only in service reports. Include actually loaded templates among read sources and in integrity verification. Do not retain caches across runs, so the next build reads updated files.

## 11. Verification and acceptance criteria

Run existing useful checks, updating only expectations affected by the changed contract. Add behavior checks:

1. Short and block forms, quoted and unquoted paths, zero arguments, an empty template, preserved neighbors, and duplicate keys.
2. Substitution into a key, value, compound identifier, string, formula, and path; empty arguments, multiline code, and several commands from one argument.
3. An argument named after a logical operator does not become an operation; a real logical block in expanded text becomes `LogicalOperation`.
4. Nested argument forwarding, a dynamic path, and at least three nesting levels; two invocations of the same template with different values do not affect each other.
5. Independent repetition is allowed; direct and indirect cycles are rejected; test both the depth boundary and exceeding it.
6. Missing files/parameters, duplicates, malformed forms, paths outside the root, unsupported conditional/default forms, and post-substitution errors produce the expected diagnostics without publishing a partial database.
7. Metadata retains original and effective arguments, parents, empty results, and correct positions; an error following a multiline argument points to actual sources.
8. Direct manual inclusion of the same text and invocation expansion produce identical working trees and frequencies when provenance and metadata are excluded. Adding service records does not alter statistics.
9. Configuration changes take effect without Python edits. A subsequent build notices a modified template; invocation environments stay isolated within a run.
10. The current installation's technology build expands all its calls and validates the version-2 database. The previous audit suggests 301 direct calls and 10 templates; update baseline observations first if sources have changed. Verify, for example, `TECHNOLOGY` substitution in `rare_technologies_weight_modifiers` and the short `technology/archaeotech_weight` reference.
11. Domain data for objects without inclusions matches the previous database; differences for affected objects follow template contents. Verify `result_paths`, provenance, and the report schema.
12. Perform a separate audit of calls from `common/` and `events/`, excluding `INLINE_SCRIPTS_DIR` and its subdirectories as independent inputs. Verify that referenced templates and their nested calls still expand while unreachable templates are not read. Count physical files, invocations, and expanded nodes separately. List all failures from the current pass. Read game-file hashes before and after verification must match.

Running the game does not replace these checks and is not required for this stage: the product does not modify game files. A successful pass over one installed version does not establish support for unobserved language forms.

## 12. Deliverables

Following approval and implementation, deliver the expansion handler, its configuration, adapted tree consumers, updated schema generator and generated schemas, automated checks, and separate reports in the working directory.

Update the database model, backend guide, README, and changelog in Russian and English. User approval has been received. Actual results and limitations are recorded in the [stage guide](BACKEND_STAGE_5_EN.md).
