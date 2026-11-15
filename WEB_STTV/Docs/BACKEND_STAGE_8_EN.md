# Stellaris Technological Tree View — stage eight backend

## Contents

- [Pipeline and invocation](#pipeline-and-invocation)
- [Libraries and configuration](#libraries-and-configuration)
- [Expansion rules](#expansion-rules)
- [Arguments and variables](#arguments-and-variables)
- [Database format and history](#database-format-and-history)
- [Code and schemas](#code-and-schemas)
- [Validation](#validation)
- [General audit and failing inputs](#general-audit-and-failing-inputs)
- [Limitations](#limitations)

## Pipeline and invocation

This document preserves stage-eight results. The current implementation is described in the [stage-nine guide](BACKEND_STAGE_9_EN.md).

Implementation follows the approved [stage-eight specification](TZ_BACKEND_STAGE_8_EN.md). Sources are read without modification. The backend indexes libraries, parses independent documents, expands mixed calls, substitutes static values, and saves structural JSON. The [stage-seven guide](BACKEND_STAGE_7_EN.md) describes the previous format.

Standard invocation from the repository root:

```powershell
& WEB_STTV/data/.venv/Scripts/python.exe -B WEB_STTV/src/backend/main.py
```

The `--variables` and `--config` options and Python functions `sttv.builder.build` and `sttv.database.storage.read_database` remain. There is no interactive console dialog. Standard paths are `data/database.json` and `data/reports/build_report.json`. Stage checks write separately under `data/stage8/`, preserving the standard database and manually curated frequency lists.

## Libraries and configuration

Four directories relative to `STELLARIS_ROOT` are read separately and excluded from independent traversal:

| Variable | Default value |
|---|---|
| `INLINE_SCRIPTS_DIR` | `common/inline_scripts` |
| `SCRIPTED_EFFECTS_DIR` | `common/scripted_effects` |
| `SCRIPTED_TRIGGERS_DIR` | `common/scripted_triggers` |
| `SCRIPTED_VARIABLES_DIR` | `common/scripted_variables` |

The seventh selector, `parser.scripted_calls`, selects [scripted_calls.json](../config/parser/scripted_calls.json). Filename pattern, recursion, encoding, name/parameter case rules, depth, node budget, and service fields are configurable. Defaults are `*.txt`, `utf-8-sig`, recursive traversal, case-insensitive names, case-sensitive parameters, mixed depth 64, and at most 1,000,000 created nodes per document. The separate inline-depth limit also applies.

Indexes are built from the game on every operation. Duplicate normalized names, including cross-library collisions, are errors. `namespace` is retained as a file field in the report; `optimize_memory` is excluded from working commands and recorded in history. Caches do not transfer processed bodies between calls or builds. All consumed source hashes are verified again before publication.

## Expansion rules

- `root_definition_files = ["common/game_rules/*.txt"]`: the approved rule retains root game-rule block definitions while expanding inner calls. Root inline insertions inherit the context; other files are unaffected. Patterns are relative to `STELLARIS_ROOT`.
- An effect using `= yes` or an argument block is replaced by its body elements. Neighbor order and repeated keys are preserved; expansion can be empty.
- A trigger using `= yes` or arguments becomes `AND = { ... }`; `= no` becomes `NOT = { AND = { ... } }`. Wrappers preserve a whole result, for example inside `OR`.
- Other scalar or formula trigger tests become `scripted_trigger_test`: the original operator, right-hand side, and expanded body. Its numeric result is not evaluated.
- Expanders cooperate through a coordinator: effect → inline → trigger and other combinations expand recursively. Active-chain repetition, depth overflow, and node-budget overflow produce diagnostics.
- Known-call arguments are bound as data first. An argument sharing a name with a known call or logical operation does not become a command.

## Arguments and variables

Named calls support textual scalars, strings, blocks, and formulas as arguments. `$PARAM|fallback$` uses the fallback only if the argument is absent; explicit `no` and empty strings are not replaced with defaults. A fallback is literal text without another parameter-name lookup. `[[PARAM] ... ]` is retained for a present argument different from `no`; `[[!PARAM] ... ]` makes the opposite selection.

Discarded branches do not require their parameters or files. Nested calls receive only explicitly passed arguments. Formulas remain formulas: their parameters are substituted, but mathematical expressions are not evaluated. The inline expander uses the shared helper as well.

Each library file has a separate local `@name` environment. A definition's own text uses that environment, an argument uses its passing-site environment, a default uses the definition environment, and inline text uses its insertion-site environment. For example, with `@cost=20` in the library and `@cost=10` in the caller, the definition's own `value=@cost` becomes 20 while passed `AMOUNT=@cost` becomes 10.

Bulk working-scalar substitution follows mixed expansion. If a static argument controls a conditional fragment or call form, its table value is read earlier on demand. A reference composed from multiple sources with an ambiguous environment is an error. Environments are not serialized, and individual variable substitutions do not get separate history.

## Database format and history

Database format is `sttv.parse_database`, version 2. The previous seven node kinds are joined by `scripted_trigger_test` with `operator`, `value`, `body`, `span`, and `origin`. The schema does not contain a closed list of game commands or fields.

One `metadata.expansions` array holds inline calls, effects, and triggers. Records retain kind and target, original form, explicit arguments, removed directives, parent ID, and the insertion range in the final tree. `origin.expansion_id` connects nodes to history; synthetic wrappers have `synthetic: true`. Original body and argument provenance is preserved.

History is validated when loading without the game: unique IDs, parents, cycles, ranges, and node references. Metadata, library templates, and variable declarations do not contribute to frequency statistics. The new node's statistics traverse only its value and body.

Report version 4 separately stores effect/trigger manifests, definition and local-declaration counts, call/default/conditional counters, and maximum depth. Library locals are counted in `scripted_calls`, while independent-document locals are counted in `static_variables`. Reading an old database requires old code or rebuilding; no compatibility layer was added.

## Code and schemas

`script/scripted/` handles indexes, argument binding, and named-body expansion; `script/coordination.py` handles mixed chains, limits, and insertion addresses; `script/inlining/` retains inline-file processing. Conditional text selection is in `script/parameters/`. Source reading and verification are in `sources/`; environments and final substitution are in `script/variables/`.

Ten schemas are generated from declarations in `schema_generation/`:

```powershell
$env:PYTHONPATH = "$PWD/WEB_STTV/src/backend"
& WEB_STTV/data/.venv/Scripts/python.exe -B -m sttv.schema_generation
```

## Validation

Commands from the repository root:

```powershell
$env:PYTHONPATH = "$PWD/WEB_STTV/src/backend;$PWD/WEB_STTV/src/backend/tests"
& WEB_STTV/data/.venv/Scripts/python.exe -B -m unittest discover -s WEB_STTV/src/backend/tests
& WEB_STTV/data/.venv/Scripts/python.exe -B WEB_STTV/src/backend/tests/database/audit_build.py
& WEB_STTV/data/.venv/Scripts/python.exe -B WEB_STTV/src/backend/tests/script/audit_corpus.py
```

All 128 tests passed, including 24 new tests. They cover grouping using an independent truth table, mixed history, environments, parameters, conditional fragments, cycles, node budgets, previous-database preservation, and sources changing during a build.

Real build: 35 files, 81,502 nodes, 1,776 expanded triggers, 32 nonboolean tests, 301 inline insertions, and 1,929 static-reference substitutions; no errors or warnings. Files are `data/stage8/database.json` and `build_report.json`. Independent comparison of every tree field and static value passed; rebuilding produced identical bytes. JSON size: 135,690,539 bytes. All consumed sources, templates, libraries, and previous standard outputs were preserved. Details are in `real_validation_report.json`; the general audit is recorded in `corpus_report.json`.

## General audit and failing inputs

First full audit of the current installation: 2,238 TXT files, including 631 inline templates, 43 effect files, 37 trigger files, and 23 static-variable files read separately. Of 1,504 independent inputs, 1,481 succeeded, the two previous documentation TXT files were skipped, and 21 failed. JSON and history checks covered 7,177,784 nodes. The report status is `partial`, not complete success.

The run expanded 40,174 effect calls, 130,762 trigger calls, and 13,317 inline insertions, retaining 928 nonboolean tests. It used 1,132 defaults, retained 1,081 conditional fragments, discarded 939, and reached mixed depth 8. Counters include processed portions of failed files. New lists contain 53,279 frequency entries, 34,405 scalar values, and 3,569 scalar constructs. Metadata, variable declarations, and previously agreed exclusions are not counted in those lists.

All previous 17 failures remain: 14 inputs with `CLASS`, two with `RELIC`, and one unknown `@max_unlocked_council_positions`. Four additional cases require distinct decisions:

| Independent input | Cause and evidence |
|---|---|
| `common/game_rules/00_rules.txt:4677` | False `NOMAD` diagnostic caused by the outer `benefits_from_waystation_network` definition sharing a trigger name. The actual inner call at line 4678 supplies both arguments. After separate approval, `root_definition_files` was added to preserve the outer definition. The correction is checked separately against both files in this directory. |
| `events/ancient_relics_arcsite_events_2.txt:9884` | `small_artifact_reward = no` is outside the approved effect contract (`yes` or arguments). It is not automatically treated as a skip or positive invocation; this audit does not establish engine behavior. |
| `events/nomads_origin_events.txt:795` | `pop_group_add_ethic_effect` receives `POP_GROUP`, `ETHOS`, and `PERCENTAGE`, but no `RANDOM`. Its reached definition branch requires `$RANDOM$` at `common/scripted_effects/00_scripted_effects.txt:9030`, without a default. |
| `events/shroud_events.txt:17815` | `apply_pop_template_pop_check` receives `TIER = 1`; its body constructs `@po_apply_pop_template_tier$TIER$_nb_pop` (`08_scripted_triggers_shroud.txt:639`). Part of the name comes from the library and part from an argument. Shared tier1/2/3 variables exist in `09_scripted_variables_shroud.txt:194–196`; the current contract diagnoses mixed environments instead of guessing one. |

Game files are unchanged. Analytical lists cover successful inputs only and do not represent the complete corpus. Detailed diagnostics include coordinates and call history. A reached library failure fails its independent caller; libraries themselves do not increase the independent-input count.

After the approved `game_rules` context correction, both directory files were rebuilt separately: 14,709 nodes, 364 trigger calls, 10 nonboolean tests, and one inline insertion, without errors or warnings. Independent name comparison confirmed all 218 outer definitions in `00_rules.txt` and five in `01_gui_rules.txt`; the inner call at line 4678 is the one expanded. Sources are unchanged. Report: `data/stage8/game_rules_validation_report.json`; separate database: `data/stage8/game_rules/database.json`.

Combined full-audit and targeted-recheck coverage: 1,482 successful inputs, two documentation exclusions, and 20 failures. Of the three additional remaining cases, one lacks `RANDOM`; two reflect approved-contract limitations (`effect = no` and a composite reference with mixed environments). Vanilla repairs or new interpretations of these constructs were not applied.

The repeat after the directive fix confirmed original corpus counts, diagnostics, and byte-identical contents of all three text lists. It preceded the `game_rules` rule; after changing that sole context, both affected files were checked without repeating the full traversal again. Lists in `data/stage8/text_frequency/` and `repeated_text_frequency/` retain original full-run results. Summary: `verification_report.json`; stage-seven comparison: `corpus_comparison.json`; repeated-run comparison: `repeat_comparison.json`.

## Limitations

Expansion does not execute the game: game conditions, loops, random choices, event references, script values, state scopes, and formulas are not evaluated. Ordinary unknown keys are retained because no command registry is used. Unsupported forms of known effects receive no invented semantics.

`is_arkship_fleet = ye` is retained as a nonboolean test; `$HIDEAGE|IMMORTAL$` without `HIDEAGE` produces literal `IMMORTAL`. This preserves structure under the contract rather than confirming the original command's validity in the engine. Known vanilla failures are not repaired with fallback values.

A complete-corpus check may be partial because of source failures or expansion limits; causes must be listed in its report. Synthetic checks establish the backend contract, not every edge case of the closed game engine.
