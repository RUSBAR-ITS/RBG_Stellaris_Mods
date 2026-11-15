# Stellaris Technological Tree View — stage nine specification: script value expansion

## Contents

- [1. Status and goal](#1-status-and-goal)
- [2. Inspected sources](#2-inspected-sources)
- [3. Stage boundaries](#3-stage-boundaries)
- [4. Sources and configuration](#4-sources-and-configuration)
- [5. Definition index](#5-definition-index)
- [6. Reference recognition and arguments](#6-reference-recognition-and-arguments)
- [7. Calculation representation in JSON](#7-calculation-representation-in-json)
- [8. Expansion order and static environments](#8-expansion-order-and-static-environments)
- [9. History and analysis](#9-history-and-analysis)
- [10. Diagnostics and publication](#10-diagnostics-and-publication)
- [11. Modules and schemas](#11-modules-and-schemas)
- [12. Checks and acceptance criteria](#12-checks-and-acceptance-criteria)
- [13. Deliverables](#13-deliverables)

## 1. Status and goal

**Approved by the user; stage nine is implemented.** Date: 2026-11-15. Results and limitations are in the [stage-nine guide](BACKEND_STAGE_9_EN.md).

This stage builds on the [implemented eighth stage](BACKEND_STAGE_8_EN.md), [its specification](TZ_BACKEND_STAGE_8_EN.md), [static variables](TZ_BACKEND_STAGE_7_EN.md), and [shared development principles](TZ_EN.md#2-project-structure-and-coding-principles).

The goal is to expand references to `common/script_values` into dedicated value nodes containing a calculation body, bound parameters, and the preserved evaluation scope. The result remains a structural JSON database without executing the game or calculating final numbers. Conditions and operation order must remain available for subsequent enrichment.

The following sections specify the approved configuration, node and history representations, format versions, and verification requirements.

## 2. Inspected sources

Structural parsing of the installed vanilla game on 2026-11-15 found:

| Observation | Result |
|---|---|
| `common/script_values` library | 15 TXT files, 674 definitions; all definitions are blocks |
| Duplicate exact names | None found |
| Definitions containing parameters | 106, including parameters with defaults |
| Definitions containing conditional fragments | 3 |
| References inside the library | 246 scalar occurrences of `value:` before expansion |
| References in source trees under `common/` and `events/` | 2,621 scalar occurrences, all unquoted and in value positions |
| Arguments / scope prefixes among those occurrences | 666 / 282 |
| Multiple `value:` occurrences in one scalar | 4; a nested reference is passed as an argument |

The last sample parsed 293 TXT files containing the text `value:`. Comments were excluded, and opaque `inline_script` payloads were not expanded. This is source-syntax research, not a count of future expansions or proof of engine behavior.

Evidence relative to `STELLARIS_ROOT`:

- `common/script_values/00_script_values.txt:2–55`: bundled documentation of reference forms, operations, and parameters; compared with actual definitions below.
- `common/script_values/00_script_values.txt:524`: `tech_weight_likelihood = { base = 1.25 }`; used in `common/technology/00_first_contact_tech.txt:40`.
- `common/script_values/00_script_values.txt:528`: `leader_cost` references two other calculations that use `trigger:has_base_skill`.
- `common/script_values/00_script_values.txt:572` and `common/script_values/04_script_values_machine_age.txt:38`: definition and invocation of `num_active_buildings` with the `BUILDING` parameter.
- `common/script_values/04_script_values_machine_age.txt:80`: `owner.value:num_active_technophant` reference.
- `events/paragon_events_2.txt:40`: `value:trait_kill_naval_cap_scaling|MULT|value:hells_heart_effect|`.
- `common/script_values/01_script_values_paragon.txt:310`: `$BONUS|0$`; `common/script_values/00_script_values.txt:74`: a conditional fragment.

The known unresolved reference `@max_unlocked_council_positions` is in `common/script_values/01_script_values_paragon.txt:365`. Excluding the library from independent traversal does not fix this reference: reaching the corresponding body must still allow the error to be diagnosed.

## 3. Stage boundaries

Included: library loading, indexing, parsing `value:...` references, parameter binding, nested and mixed expansion, a new value node, history, static environments, schemas, the builder, and existing tree consumers.

Arithmetic, `modifier` conditions, `complex_trigger_modifier`, `trigger:...`, `modifier:...`, game variables, and state scopes remain structural data. Do not evaluate even simple constant calculations such as `{ base = 1.25 }`: the uniform stage result is an expanded body. Do not introduce a registry of permitted mathematical or game commands.

Excluded: evaluating `@[ ... ]` / `@\[ ... ]` formulas, expanding references inside formulas or strings, executing effects, reading saves, localization, UI, mods, and vanilla fixes. Internal service metadata is not executed. Existing stage-eight limitations must not be bypassed with fallback values.

## 4. Sources and configuration

During implementation, add `SCRIPT_VALUES_DIR = common/script_values` to `global_variables.json`, relative to `STELLARIS_ROOT`. The directory is required; an existing empty directory is valid. Reading does not modify game files; permitted paths, physical deduplication, and source protection follow the existing loader.

The shared independent-source filter excludes five libraries and their subdirectories: `INLINE_SCRIPTS_DIR`, `SCRIPTED_EFFECTS_DIR`, `SCRIPTED_TRIGGERS_DIR`, `SCRIPTED_VARIABLES_DIR`, and `SCRIPT_VALUES_DIR`. The last is read separately for indexing and invocations. With unchanged installed sources, the independent sample decreases by 15 files: 1,504 → 1,489 before excluding the two TXT documentation files.

Add the eighth selector, `backend.json → parser.script_values`, with the existing `product` / `work` bases and default `config/parser/script_values.json`:

```json
{
  "format_version": 1,
  "reference_prefix": "value:",
  "scope_separator": ".",
  "argument_separator": "|"
}
```

This configures the reference form. Reuse reading order, `pattern`, `recursive`, `encoding`, `name_case_sensitive`, `parameter_case_sensitive`, and mixed-expansion limits from `parser.scripted_calls`; do not duplicate shared rules. `$...$` delimiters, defaults, and conditional fragments remain in the constructs configuration. A `|` inside `$PARAM|default$` is not a reference-argument separator.

Validate nonempty markers, distinguishability, and compatibility with lexical parsing; configuration must not allow ambiguous token splitting. Protect the new configuration path from output overwrites. Do not move definition names into configuration.

## 5. Definition index

Build a separate script value index before processing independent sources. A definition is a root assignment `name = { ... }`; retain its name, original body, coordinates, file, and that file's static environment. Handle top-level `@name` declarations and permitted file fields through the existing library contract. Prepare root inline insertions that produce definitions through the existing mechanism.

Do not expand bodies or require their arguments while indexing. Validate syntax and root form when loading; substitution errors inside an unused body must not occur solely because the library was read. The index does not enter `documents` and is not counted as independent objects in analysis.

Name collisions within this library under configured case rules are errors identifying both definitions. Sharing a name with an effect or trigger is allowed: `value:...` selects a separate library. Diagnose other root forms; do not infer definitions from similar names or file order.

## 6. Reference recognition and arguments

Support these forms of an entire unquoted scalar value:

```text
value:tech_weight_likelihood
owner.value:num_active_technophant
event_target:paragon_destroyed_ship.value:ship_naval_cap
value:num_active_buildings|BUILDING|building_augmentation_center|
value:trait_kill_naval_cap_scaling|MULT|value:hells_heart_effect|
```

A reference consists of an optional scope prefix ending in `scope_separator`, `reference_prefix`, a definition name, and an optional sequence of `|NAME|VALUE|` pairs. The argument form requires the trailing separator. Empty names, unpaired elements, duplicate parameter names, and empty scope segments are errors. An empty argument value is valid and differs from an absent argument.

Find the reference prefix only in the head before the arguments: `value:` inside an argument does not change the outer target. The name and scope can be formed by parent-call parameter substitution. Parse the token using known substitution boundaries instead of unconditional `split('|')`.

In the observed nested form, `MULT` receives the text `value:hells_heart_effect`. It expands at the position where the parameter is actually inserted. This stage does not invent escaping for `|` or an unconfirmed syntax for nested argument lists inside one value. Diagnose ambiguous and unsupported forms; new rules require investigation and agreement.

Recognition applies to working-tree value positions, including assignment values, `scripted_trigger_test` comparison values, and standalone scalar items. Do not process assignment keys, logical-operation or tag names, strings, formulas, comments, metadata, or raw arguments before actual insertion. `value = ...` without the prefix remains an ordinary field. A complete reference form whose name is absent from the index is an error.

Bind parameters using the shared mechanism: configured case sensitivity, defaults only for missing arguments, preservation of explicit `no` and empty values; select conditional fragments before binding inactive text. Nested calls receive only explicitly passed arguments; unused arguments produce warnings. Do not expand argument contents eagerly when they are never inserted or occur only in a discarded conditional fragment. Runtime `modifier` conditions are not evaluated or discarded.

## 7. Calculation representation in JSON

The new database format is `sttv.parse_database`, `format_version: 3`. Add a ninth node kind, `script_value`:

| Field | Type and purpose |
|---|---|
| `kind` | The string `script_value` |
| `scope` | Scope-prefix string without the trailing separator, or `null` if no prefix exists |
| `body` | A `block` node with the expanded calculation body, retaining order and repetitions |
| `span` | Coordinates of the replaced reference under the shared contract |
| `origin` | Invocation provenance with its `expansion_id`; the synthetic wrapper has `synthetic: true` |

The following example shows only the semantic portion of the node; required `span` and `origin` fields are omitted for readability:

```json
{
  "kind": "script_value",
  "scope": null,
  "body": {
    "kind": "block",
    "items": [
      {
        "kind": "assignment",
        "key": { "kind": "scalar", "raw": "base", "text": "base", "quoted": false, "parameters": [] },
        "operator": "=",
        "value": { "kind": "scalar", "raw": "1.25", "text": "1.25", "quoted": false, "parameters": [] }
      }
    ]
  }
}
```

For `factor = value:tech_weight_likelihood`, this node occupies `assignment.value`; `factor`, the operator, and adjacent entries remain intact. The body is neither spliced as a list into the parent block nor converted into a number. A nested reference creates a nested value node with its own calculation boundary.

`scope` stores the original chain after parameter substitution, such as `owner` or `event_target:paragon_destroyed_ship`. Do not replace an absent scope with an invented object; preserve explicit `this` as a string. Do not merge nested calculation scopes or rewrite `root` / `prev` / `from`. Original child nodes retain definition and argument coordinates. Store the definition name and original reference form in history without duplicating the expanded body.

Update all permitted value positions, serialization, reading, structural validation, and node traversal. Reading a finished database requires neither the game nor repeated expansion. Rebuild older databases; do not add a compatibility layer.

## 8. Expansion order and static environments

Pipeline: load configurations and shared variables → prepare library environments and indexes → parse an independent source → recursively expand mixed calls → finish static-variable substitution → serialize and validate → publish.

Connect the new expander to the shared coordinator. References introduced by an inline insertion, effect, trigger, another script value, or parameter are processed within the same operation. Bind recognized-call arguments before traversing the inserted body. Also expand named calls inside calculation conditions, retaining their existing logical grouping.

Reuse current static environments: local declarations belong to the definition file, explicit arguments to their call site, defaults to the definition; inline insertions inherit their insertion environment. Final substitution covers the new node's body and nested comparison values. Do not create a separate history of static replacements.

Retain the existing limited static-resolution mechanism for control arguments. If an entire scalar `@name` resolves to a `value:...` reference, recognize it through that mechanism before expansion completes, retaining provenance; do not leave the introduced call as an unprocessed string. This does not evaluate a script value or game variable. Continue diagnosing ambiguous composite environments.

Script values share the active mixed stack and limits on depth and created nodes. Invocation identity consists of the library kind and normalized definition name. Direct, indirect, and mixed cycles are forbidden; independent repeated calls are allowed. Changing arguments does not permit infinite recursive-program expansion. Cache sources and templates, but do not reuse mutable expanded bodies between invocations.

## 9. History and analysis

Add `kind: script_value` to `metadata.expansions`. Retain shared fields `id`, `parent_id`, `call_site`, `target`, `invocation`, `arguments`, `directives`, and `insertion`:

- `target` contains the definition name, file, and span; `arguments` retains explicitly passed pairs in order under the previous contract. Defaults are not presented as explicit arguments.
- `invocation.form` is `reference` or `arguments`, and `raw` is the complete reference text after parent-parameter binding; `operator: null` because the reference itself has no assignment operator. The surrounding entry's operator remains in the tree.
- `directives` is an empty array; mathematical commands and ordinary body elements are not removable directives.
- For the new kind, `insertion` is `{ "node": "/items/0/value" }`: a JSON Pointer to the single final `script_value` node relative to its document.
- For the three existing kinds, retain `{ "container": "...", "index": 0, "count": 1 }`: a range in an array. Expansions inside the new value's body use regular addresses through `body`.

Compute all addresses against the final tree. Validate the addressed node kind, matching `origin.expansion_id`, parent relationships, unique IDs, absence of history cycles, and valid ranges. Nested references retain their parent regardless of the outer invocation kind. Reject invalid pointers when reading the database without the game.

Analysis traverses each instance's expanded `body` exactly once. History, library templates, service node-kind names, and original reference strings are not added to frequency lists. `scope` remains a calculation attribute rather than a separate game command. Retain existing filters for variables, parameters, logical operators, `yes`/`no`, and single occurrences. Verification runs must not overwrite manually curated lists.

## 10. Diagnostics and publication

Report version is 5. Add a `script_value_sources` manifest with SHA-256 hashes of files read and separate script value counts: files, definitions, local declarations, encountered, successful, and failed references. Shared counts for defaults, conditional fragments, and maximum mixed depth include the new kind. Corpus reports separately count excluded library files.

Configuration, reading, syntax, duplicate-definition, reference-form, unknown-target, parameter, static-reference, cycle, limit, and history errors are automatically recorded in the JSON report. Retain the independent input, physical coordinates, definition, and mixed call chain; preserve the original cause. Unsupported or ambiguous forms must not become silently skipped scalars.

On build failure, preserve the previous database and do not publish a partial database. Audits continue independent files and report each file's first blocking error under the existing contract. The current-run report is overwritten; no cumulative log is added. The shared `TO_DO` is not populated automatically.

Before publication, recheck hashes of all consumed sources, including the new library. Changes between operations must be picked up through a fresh load. Do not substitute zero or other guesses to bypass vanilla errors.

## 11. Modules and schemas

- `sources/`: configuration, library reading, environments, manifest, and traversal exclusion.
- `script/values/`: reference parsing and dedicated calculation expansion. Share indexing and parameter binding through existing small helpers.
- Shared coordinator: replacement of a scalar position with a value node, mixed stack, limits, and final history addresses.
- Serialization, structural validation, static variables, and analysis: support for the ninth node kind.

The base syntax parser remains independent of library files. The new node appears during expansion; ordinary context-free parsing still returns the original scalar. Only changes to shared helpers needed by this stage are permitted; avoid unrelated refactoring and do not restore a command profile. Follow DRY, configuration, and agreed file-size constraints.

Add the `parser_script_values.schema.json` declaration; update backend/database/report and history declarations, then generate schemas through the standard generator. Eleven schemas are expected. Do not edit generated schemas as an independent source of rules. The node format remains structural and does not enumerate permitted game fields.

## 12. Checks and acceptance criteria

Required synthetic checks:

1. Multiple indexed files/definitions, an empty library, local declarations, root inline preparation, duplicate and case-colliding names, permitted name sharing with an effect/trigger, invalid paths and definition forms.
2. Plain, parameterized, and scoped forms; `event_target:` in a scope; empty arguments, incorrect element counts, duplicate parameters, unknown targets, and ambiguous separators. Changed marker settings must actually take effect.
3. Keys, strings, formulas, metadata, and unused arguments stay outside expansion. Inserted working arguments, including another `value:...`, expand. `$PARAM|default$` does not break `|NAME|VALUE|` parsing.
4. Defaults, explicit `no`/empty values, positive/negative conditional fragments, no requirements for discarded-branch parameters, and independent nested-call arguments.
5. Exactly one value position is replaced; operators, neighbors, repetitions, and operation order are preserved; nested nodes have separate bodies and scopes. The `base = 1.25` example does not substitute a number for the node.
6. Mixed chains of four invocation kinds, references in `scripted_trigger_test.value`, triggers inside calculations, repeated calls, direct/mutual/mixed cycles, and depth/size boundaries.
7. Different static values in caller and definition files, argument/default/inline environments, a static reference alias, no cache leakage, and no separate replacement history.
8. JSON round trip, reading without the game, all nine node kinds, both `insertion` forms, nested pointers after insertions/removals, provenance, and rejection of corrupted history.
9. Analysis counts each expanded body once, ignores history and the separate library, and preserves existing filters and previous lists.
10. An error does not replace the previous database; source changes are detected; repeated builds with unchanged inputs are byte-identical; all existing tests are adapted without a compatibility layer.

Real-source checks during implementation: build the 35 technology files with independent comparison of selected expansions and all unchanged surroundings, then run one full `common/` and `events/` audit excluding five libraries and the two existing TXT documentation files. Check the nested argument from `paragon_events_2`, scoped references, parameters/defaults, and preservation of calculation blocks. The comparison must not simply call the same new expander again as its oracle.

The error baseline is `data/stage8/verification_report.json → current_corpus_coverage.remaining_failures` (20 files after the game-rule context fix), not the outdated full report with 21 failures. Separately identify previous failures, new failures, and inputs removed from independent traversal. An old error disappearing because its library is excluded does not fix the source. Full expansion can reveal further errors; record and investigate them without promising zero vanilla failures.

Direct verification output to `WORK_DIR/stage9/`, including the new verification database, reports, and separate frequency lists. Preserve previous standard outputs, sources, and research lists; verify their hashes. Check schemas through the standard generator, history structure, output size/memory, and technology-build repeatability. Repeat the corpus run only when changes affect previously checked behavior.

Structural acceptance does not require launching the game. These checks do not prove numerical equivalence with the engine: arithmetic and game state are not evaluated.

## 13. Deliverables

Implementation deliverables: a source variable and filter, configuration, script value index and expander, new node, shared history, updated schemas/consumers, tests, verification database, and reports. Prepare a bilingual stage-nine guide and update README, concept, and changelog with actual results.

Implementation, a separate verification database, and reports are available; actual checks and known failing inputs are documented in the [guide](BACKEND_STAGE_9_EN.md). Sources and previous outputs are preserved.