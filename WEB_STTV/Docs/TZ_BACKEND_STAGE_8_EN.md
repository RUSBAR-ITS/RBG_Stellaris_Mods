# Stellaris Technological Tree View — stage eight specification: effect and trigger expansion

## Contents

- [1. Status and goal](#1-status-and-goal)
- [2. Inspected sources](#2-inspected-sources)
- [3. Stage boundaries](#3-stage-boundaries)
- [4. Sources and configuration](#4-sources-and-configuration)
- [5. Definition indexes and call recognition](#5-definition-indexes-and-call-recognition)
- [6. Arguments and conditional fragments](#6-arguments-and-conditional-fragments)
- [7. Effect expansion](#7-effect-expansion)
- [8. Trigger expansion](#8-trigger-expansion)
- [9. Static-variable environments](#9-static-variable-environments)
- [10. Nesting and processing order](#10-nesting-and-processing-order)
- [11. Tree and expansion history](#11-tree-and-expansion-history)
- [12. Modules and schemas](#12-modules-and-schemas)
- [13. Diagnostics and publication](#13-diagnostics-and-publication)
- [14. Validation and acceptance criteria](#14-validation-and-acceptance-criteria)
- [15. Stage deliverables](#15-stage-deliverables)

## 1. Status and goal

**Approved by the user. Implementation and verification results are documented in the [stage-eight guide](BACKEND_STAGE_8_EN.md).**

Basis: the [previous-stage backend](BACKEND_STAGE_7_EN.md), [static-variable specification](TZ_BACKEND_STAGE_7_EN.md), [syntax reference](SCRIPT_SYNTAX_EN.md), and [shared coding principles](TZ_EN.md#2-project-structure-and-coding-principles). The user agreed to a separate expander for `scripted_effects` and `scripted_triggers`; the existing `inline_script` expander remains.

The goal is to substitute bodies of reached named effects and triggers while preserving order, logical boundaries, arguments, and provenance. JSON remains a database of parsing results, without a technology domain model, an allowed-command registry, or execution of game state.

Additional design proposals in this specification are a separate node for a trigger result test that cannot be reduced to `yes`/`no`, unified mixed-call history, and extended parameter processing. They are included in the approved stage scope.

## 2. Inspected sources

On 2026-11-15, both libraries and 35 technology files were parsed without expansion. Materials and the repeatable research script are `data/stage8/specification_research/inventory.py` and `inventory.json`. This is a structural inventory, not engine-equivalence validation.

| Observation | Result |
|---|---|
| `scripted_effects` | 43 TXT files, 1,691 block definitions, 24 local declarations |
| `scripted_triggers` | 37 TXT files, 1,692 block definitions, 12 local declarations |
| Duplicate names and names shared between libraries | None found in the current installation |
| Default parameters / conditional fragments | 53 occurrences / 50 fragments in library bodies |
| `optimize_memory` | 97 standalone occurrences |
| Direct names in technologies / names reachable through known names | 96 / 129; inline insertions and dynamic names are not included |
| Cycles of statically recognized named calls | None found; this does not verify mixed chains |

Supporting sources relative to `STELLARIS_ROOT`:

- `common/scripted_effects/99_advanced_documentation.txt:13–64`: call forms, parameters, defaults, and conditional fragments; `:68–84`: `optimize_memory`.
- `common/scripted_triggers/00_scripted_triggers.txt:46–67`: positive and negative tests of one trigger; `:1250–1252`: `crisis_stage_$STAGE|1$`.
- `common/scripted_triggers/00_scripted_triggers_pop.txt:59–73`: `pop_amount`, `sapient_pop_amount`, and `psionic_pop_amount`; for example, `common/scripted_effects/00_scripted_effects.txt:1638` contains `pop_amount > 200`.
- `common/scripted_effects/first_contact_effects.txt:1219–1226`: a formula passed as an argument; `common/scripted_triggers/01_scripted_triggers_refugees.txt:51–56`: conditional forwarding of arguments to a nested call.
- `common/scripted_triggers/02_scripted_triggers_marauders.txt:5–17`: library-local static variables; `common/scripted_triggers/03_scripted_triggers_cosmic_storms.txt:5`: the file-level `namespace = cstorms` field.

Ambiguous source locations include `is_arkship_fleet = ye` in `common/scripted_effects/grand_archive_effects.txt:1916` and `$HIDEAGE|IMMORTAL$` with a fallback comment in `paragon_effects.txt:419`. Do not correct them by guessing. A comment alone does not establish that a default is looked up again as another parameter name. The rules below explicitly separate structural preservation from command evaluation.

## 3. Stage boundaries

Included: two library indexes, a dedicated expander, mixed nesting with inline insertions, parameter binding, defaults, conditional fragments, static environments, history, schemas, database building, and corpus analytics.

Excluded: executing effects, evaluating game-state conditions, numeric results of game triggers, formulas `@[ ... ]` / `@\[ ... ]`, `script_values`, expanding `trigger:...` inside scalars, localization, mods, the UI, and fixes to vanilla files. References such as `root`, `prev`, `from`, and `event_target:...` remain unevaluated without rewriting game scopes.

Ordinary unknown command names and arbitrary fields are preserved. Do not reintroduce a closed command profile or game-semantic validation. Existing `CLASS`, `RELIC`, and `@max_unlocked_council_positions` failures are not bypassed automatically.

## 4. Sources and configuration

During implementation, add `SCRIPTED_TRIGGERS_DIR = common/scripted_triggers` to `global_variables.json`. `SCRIPTED_EFFECTS_DIR = common/scripted_effects` already exists. Both paths are relative to `STELLARIS_ROOT` and read-only; directories are required, while existing empty directories are allowed.

The shared independent-source filter must exclude four libraries and their descendants: `INLINE_SCRIPTS_DIR`, `SCRIPTED_EFFECTS_DIR`, `SCRIPTED_TRIGGERS_DIR`, and `SCRIPTED_VARIABLES_DIR`. Libraries are read separately rather than ignored entirely. The current general selection decreases by 37 trigger files: 1,541 → 1,504 independent files before handling the two documentation TXT files.

The seventh selector, `backend.json → parser.scripted_calls`, uses the existing `product` / `work` bases, defaulting to `config/parser/scripted_calls.json`:

```json
{
  "format_version": 1,
  "pattern": "*.txt",
  "recursive": true,
  "encoding": "utf-8-sig",
  "name_case_sensitive": false,
  "parameter_case_sensitive": true,
  "max_call_depth": 64,
  "max_expanded_nodes": 1000000,
  "root_definition_files": ["common/game_rules/*.txt"],
  "file_fields": ["namespace"],
  "definition_directives": ["optimize_memory"]
}
```

Call names follow `name_case_sensitive`; this is a configurable backend contract, not proof that the entire language is case-insensitive. Normalized-name collisions are errors. `file_fields` permits service scalar assignments at file level; `definition_directives` permits standalone markers immediately inside a definition body. Neither list enumerates game commands. Markers inside strings and values are not removed.

`max_call_depth` limits the complete active mixed chain; the existing inline-expander limit also remains applicable. `max_expanded_nodes` limits syntax nodes created per independent document, including all three kinds of calls. Count intermediate node creation as well, stopping explosive growth before serialization. Limits are positive and configurable, not claimed as engine limits.

Parameter/formula delimiters, syntactic operators, and logical names come from existing configurations. Read in stable order with physical deduplication, link/root confinement, encoding checks, and SHA-256 hashes. Caches last for one operation only. Inline path exceptions do not become arbitrary file access.

## 5. Definition indexes and call recognition

Index both libraries completely before expanding calls. A definition is a top-level assignment `name = { ... }`; retain library kind, name, body, coordinates, source text, and the file-local environment. `@name` declarations, comments, and permitted file fields are not definitions. Other top-level forms require diagnostics rather than silent loss. Keep file fields in the index/report, without inserting them into every body.

Expand root inline insertions that introduce definitions or declarations while preparing that file. Do not execute definition bodies or substitute their `$PARAM$` without a call. Loading a library must not require arguments for every unused definition.

Reject identical normalized names within a library or between the libraries, reporting both definition locations. Do not choose a winner by file order. Also diagnose names conflicting with configured built-in parser constructs.

A call candidate is an assignment in the working tree whose unquoted key fully matches an indexed name. A standalone scalar, a string, a name on the right-hand side, `trigger:name`, or a fragment of a composite identifier is not a call. Ordinary unknown keys remain unchanged.

After recognizing a call, process its form and arguments first. Do not traverse its argument block as an executable body: an argument named after an effect, trigger, or logical operation remains an argument. Metadata and library file fields do not participate in recognition. If the corpus reveals a definition name used as an independent data field outside these contexts, report the collision and agree on a narrow context rule; do not introduce a broad heuristic or game-field registry.

**Addendum approved by the user during validation:** `root_definition_files` contains path patterns relative to `STELLARIS_ROOT`. In matching files, root assignments with block values are definitions even when their keys match library names. The default is `common/game_rules/*.txt`. Their bodies are traversed normally and inner named calls expand. Root inline insertions inherit this context; nested blocks do not. Call recognition in other files is unchanged. This is a narrow definition-location rule, not an allowed-command registry.

## 6. Arguments and conditional fragments

Input forms are `effect_name = yes`, `trigger_name = yes/no`, and `name = { PARAM = value ... }`; other scalar trigger tests are covered in section 8. A call block contains named assignments using `=`. Support scalars, formulas, and balanced blocks as textual arguments; do not expand a block argument before its actual insertion. Remove outer string quotes using existing inline decoding rules while preserving provenance and escaping. Duplicate arguments are errors; unused arguments produce warnings.

Argument environments are isolated per call. A nested call receives only explicitly forwarded values, not undeclared parameters inherited from its parent. Support substitution in keys, values, strings, formulas, and arguments of nested calls. Do not evaluate formulas. An inserted value is not reinterpreted as a new parameter of the same call.

Text selection rules:

1. `$PARAM$`: use the supplied argument; absence in retained text is an error.
2. `$PARAM|fallback$`: use the supplied argument, including explicit `no` and an empty string; only when absent, use the literal `fallback` text, including an empty fallback. Do not automatically interpret it as another parameter name. Without `HIDEAGE`, `$HIDEAGE|IMMORTAL$` retains `IMMORTAL`; the comment's implied additional semantics remain unverified.
3. `[[PARAM] ... ]`: retain the body if the argument is present and its decoded value is not `no`, case-insensitively. `[[!PARAM] ... ]` makes the opposite selection. Argument presence differs from a default in an individual substitution: a default does not add the parameter to the environment.
4. Conditional fragments may nest within the depth limit. Select branches before binding parameters in retained parts. Do not require parameters, open inline files, or expand calls in discarded branches. Outer delimiters must still be structurally balanced.
5. Comments do not participate in substitution; conditional-looking syntax inside an ordinary string remains string text. Unresolved substitutions in a reached expansion produce diagnostics rather than empty text.

The new module uses this processing; a shared parameter helper may also serve the inline expander while preserving its existing path and invocation rules. Do not create divergent algorithms for identical parameter notation. Conditional fragments outside a call context remain structural nodes as before this stage.

## 7. Effect expansion

`effect_name = yes` calls without arguments; the block form supplies arguments. Other scalar values, `no`, and comparisons for an effect receive no invented semantics at this stage: a reached call produces `unsupported_scripted_call`.

After argument binding, splice the body elements at the call position without adding a game-state scope. Preserve neighbor order, repeated keys, and empty expansions. Do not execute `if`, `limit`, loops, random selection, or state-changing commands. Calls inside their bodies are expanded structurally regardless of whether the game will execute that branch.

A standalone `optimize_memory` directly in a definition is a template-storage directive: remove it from the inserted body and record it in the call history. Do not remove same-named scalars in other positions or present the directive as a game effect.

## 8. Trigger expansion

The positive boolean form and a block call with arguments become one `AND = { expanded body }`. `= no` becomes `NOT = { AND = { expanded body } }`. Preserve these wrappers even with one or zero children: they bound the call result rather than request logical simplification. Use configured logical operations; missing required operators make the configuration incompatible with this transformation.

For example, after expanding a call inside `OR`:

```text
OR = {
    AND = {
        condition_a = yes
        condition_b = yes
    }
    condition_c = yes
}
```

Do not insert `condition_a` and `condition_b` directly into `OR`, which would lose the original trigger result. Do not add `owner`, `root`, or other scope transitions.

For calls such as `pop_amount > 200`, `sapient_pop_amount >= @threshold`, and other nonboolean scalar tests, a new structural node, `scripted_trigger_test`, is proposed:

| Field | Value |
|---|---|
| `kind` | `scripted_trigger_test` |
| `operator` | Original comparison operator |
| `value` | Original right-hand side, a `scalar` or `formula` node; static references are resolved later |
| `body` | A `block` node containing the fully expanded definition body |
| `span`, `origin` | Original test location and link to call history |

The definition name is stored in call history. The node means “test the result of this expanded definition using the specified operator and value”; it neither evaluates the result nor converts the body to `AND`. For example, the `pop_amount` body remains `count_owned_pop_amount = { }`; do not invent a replacement command or move the right-hand side into it.

This rule also preserves the unusual `is_arkship_fleet = ye` without correcting it to `yes`. Such a record is not declared a valid game command or a number. Count preserved nonboolean tests separately in the report and identify questionable source locations in research. Preserve `!= yes/no`, if encountered, with this same node instead of introducing additional logical reductions.

## 9. Static-variable environments

Do not merge all library-local declarations with those of the calling document. Each physical library file has its own table; a definition body uses that table and shared scripted variables. Calling a definition from another file switches the environment of its own text rather than inheriting the previous definition's locals.

An argument retains its passing-site environment: `@cost` passed by an independent document uses that document's local value. A default uses the definition environment. An inline insertion inherits its insertion-site environment as in stage 7; its template path does not establish a separate variable scope. Cached results must not leak between environments of repeated calls.

Required example: the caller has `@cost = 10` and the definition file has `@cost = 20`; the body contains `first = @cost` and `second = $AMOUNT$`, with the call passing `AMOUNT = @cost`. The result is `first = 20`, `second = 10`.

Tables and their reference chains may be prepared beforehand. **The bulk substitution of working values takes place after complete mixed expansion.** When choosing a call form or conditional fragment, an argument consisting entirely of a static reference is resolved on demand through its environment: this is a table lookup controlling expansion, not a general substitution pass over the tree. An unknown reference is an error and cannot be treated as true merely because its text starts with `@`.

Account for declarations introduced by root inline insertions before using the file environment. Declarations inside an effect/trigger body do not become caller variables: nested declarations remain forbidden. Tables and environment references are internal processing data, not new JSON history.

If an entire static reference came from an argument, use the argument environment. If multiple text fragments compose a reference whose environment cannot be determined unambiguously, report `ambiguous_static_environment` rather than choosing the first file containing the name. Quoted strings, formulas, keys, and composite non-reference values retain stage-seven restrictions. Do not introduce per-substitution `@name` history.

## 10. Nesting and processing order

Proposed pipeline: settings and shared variables → library/root-insertion reading and indexing → independent source → binding and recursive mixed-call expansion → working static-reference substitution → serialization, structural validation, and publication.

The inline and named expanders cooperate through a small shared coordinator and one call stack. Inserted text undergoes recognition again: effect → inline → trigger → another trigger and reverse combinations must work. Two independent one-off passes cannot provide this behavior.

An active named call is identified by library kind and definition identity; an inline call by file identity. A repeated definition in the active chain is diagnosed as a cycle, including mutual recursion and mixed cycles. Repeated independent calls are allowed. This stage does not execute recursive game programs with changing arguments: even a potentially terminating game call is not expanded indefinitely.

Deferred `country_event`, `on_action`, `script_values`, and similar references are not expanded or added to this mechanism's call stack. Cache source text, structural templates, and indexes where useful; never share a mutable expanded result between calls.

## 11. Tree and expansion history

Database: `sttv.parse_database`, `format_version: 2`, containing the previous seven node kinds plus `scripted_trigger_test`. The schema remains structural and does not restrict game-field names. Reading the completed database requires no game; rebuild old databases rather than adding a compatibility layer.

Replace `metadata.inline_scripts` with one `metadata.expansions` array. A record has common fields `id`, `parent_id`, `kind` (`inline_script`, `scripted_effect`, `scripted_trigger`), `call_site`, `target`, `invocation`, `arguments`, `directives`, and `insertion`:

- `target`: for inline, the relative path of the template actually read; for a named call, the definition name, file, and span. The schema distinguishes these variants by `kind`.
- `invocation`: the original operator, form (`reference`, `boolean`, `arguments`, `test`), and original value text. Allowed forms depend on call kind.
- `arguments`: an ordered array of explicitly passed arguments with `name`, `raw`, and `value`. `value` is text after parent-parameter binding and string decoding; defaults must not appear as explicitly supplied arguments.
- `directives`: removed definition markers; empty for inline calls.
- `insertion`: the final `items` container path, first-element index, and inserted-element count, including zero. A boolean trigger or `scripted_trigger_test` inserts one node.

`parent_id` spans any combination of call kinds. Rename provenance field `inline_call_id` to `expansion_id`, preserving fragments/placeholder chains. Mark introduced logical wrappers and test nodes with `synthetic: true` in origin and use call-site coordinates; do not present wrappers as literal source text. Original nodes retain real definition/argument coordinates.

Compute `insertion` ranges and provenance links against the final tree after all nested replacements and removal of conditional wrappers. Validate parents, acyclic history, unique IDs, valid ranges, and references from every node. Metadata neither duplicates expanded bodies nor logs individual static substitutions.

Analytics traverses working values and bodies, including the new node's `value` and `body`, but not metadata, library tables, or directives. Synthetic operators do not become text terms; existing filters for variables, parameters, logical names, `yes`/`no`, and singleton occurrences remain. Each actually inserted body instance is counted separately.

## 12. Modules and schemas

Proposed code boundaries:

| Area | Responsibility |
|---|---|
| `sources/` | Two-library reading, configuration, hashes, traversal exclusions |
| `script/scripted/` | Definition index, call recognition, distinct effect and trigger expansion |
| Small shared helpers | Parameters, conditional text selection, provenance, history, and stack |
| `script/inlining/` | Existing inline expander, paths, and file exceptions |
| `script/variables/` | Environment tables and final substitution |
| Building, schemas, and analytics | One shared transformation pipeline and structural validation |

Do not turn the inline expander into a monolith or write another syntactic parser. The base parser must still parse text without library access; the new node is introduced during transformation. Moving shared helpers is allowed only within this stage's scope. Follow DRY and a target of at most 200 lines per file; split files over 300 lines except for justified indivisible blocks.

Add the `parser_scripted_calls.schema.json` declaration, update backend/database/report declarations, and use the regular generator. Ten schemas are expected in total. Do not unnecessarily duplicate existing inline configuration parameters; shared lexical notation stays in its existing configurations.

## 13. Diagnostics and publication

Report version is 4. Retain hashes of independent sources, inline files, and the shared-variable library; add separate manifests for effect and trigger files. Count read files, definitions, local declarations, calls by kind, successful/failed expansions, nonboolean tests, used defaults, retained/discarded fragments, and maximum mixed depth. State counter units clearly: a library file once, an expansion per invocation.

Principal errors include invalid configuration/path, read or syntax failure, ambiguous definition, unsupported call form, duplicate/missing parameter, unresolved static reference, ambiguous environment, cycle, depth, expansion size, and invalid history. Diagnostics include the independent input, definition/argument location, and complete mixed call chain. Preserve nested causes instead of hiding them behind a generic expansion message.

Do not require errors for ordinary unknown keys: without a command registry, a misspelled call name cannot reliably be distinguished from an engine command. Do not use fallback values to hide source failures. Unused arguments produce warnings; unused definitions are not expanded.

Do not publish a partial working database after a failure; preserve the previous file. A corpus audit may continue with independent files and emit a partial report with precise causes. Detect files changing during the build using control hashes and do not label a result combining multiple source versions as reproducible.

## 14. Validation and acceptance criteria

Required synthetic scenarios:

1. Two indexes, multiple definitions per file, file order, duplicate/case/cross-library collisions, `namespace`, `optimize_memory`, empty libraries, read failures, and links escaping allowed directories.
2. Effects with and without arguments; several/zero result elements; neighbor order, repeated fields, and no runtime-branch evaluation.
3. Trigger `yes`/block/`no` inside `OR`, `NOT`, and `NAND`; an independent truth table for a two-condition body confirms preservation of grouping and negation.
4. `pop_amount > 200`, equality to a number, a formula on the right, `!= yes`, and `= ye`: preserve the operator, value, and expanded body without numeric evaluation.
5. String/empty/block/formula arguments, defaults for absence, explicit `no`, an empty default, a parameter in a command name, and no repeated reinterpretation of inserted text.
6. Positive/negative/nested conditional fragments; a discarded branch with a missing argument and inline file; comments and strings with similar symbols; conditional forwarding to a nested call.
7. Mixed chains of all kinds; direct, indirect, and mixed cycles; independent repetitions; depth/size boundaries. An argument named after a known call is not expanded before insertion.
8. Caller and definition both declaring `@cost`; nested switching between libraries; inline environment inheritance; arguments/defaults from distinct environments; a static argument controlling a conditional; no cache leakage or extra substitution history.
9. Correct final insertion paths, empty expansion, provenance after multiline substitution, mixed parent links, and synthetic wrappers; reject invalid history when reading without the game.
10. Analytics excludes directives, library templates, and history; all four libraries are excluded from independent traversal. Preserve previous filters and manually curated lists.
11. Failures preserve the previous database; another operation notices source changes; byte-identical rebuilding; adapt previous tests to format 2 without a compatibility layer.

Real implementation checks: first the 35 technology files with independent comparison of selected chains, then the general `common/` and `events/` corpus excluding four libraries and the two previous documentation TXT files. Compare failures with stage 7 by file and cause, separating new failures, expanded-library failures, and cases removed by excluding independent templates. Do not promise zero vanilla-corpus errors or equate successful parsing with proof of correct game sources.

Verify before/after source SHA-256 hashes, database format, all node kinds, history, statistics, memory limits, and rebuilding. Send reports, the new database, and lists to `WORK_DIR/stage8/`; the validation run must not replace the previous standard database or manually curated research lists. Tests and research do not write to the game. Structural acceptance requires no game launch; synthetic tests do not establish equivalence to every edge case of the closed engine.

## 15. Stage deliverables

Implementation deliverables: the dedicated expander, trigger variable and exclusion, configuration, shared parameter helper and coordinator, updated schemas/tree consumers, tests, validation database, and reports. Prepare a bilingual stage-eight guide and update README and changelog with actual results.

Implementation is in the codebase; configuration, schemas, and tree consumers have been updated. Actual results and limitations are in the [guide](BACKEND_STAGE_8_EN.md); verification artifacts are under `data/stage8/`.
