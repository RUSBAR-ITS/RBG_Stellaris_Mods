# Stellaris Technological Tree View — stage-nine backend

## Contents

- [Pipeline and invocation](#pipeline-and-invocation)
- [Sources and configuration](#sources-and-configuration)
- [Value expansion](#value-expansion)
- [Database format and history](#database-format-and-history)
- [Diagnostics and analysis](#diagnostics-and-analysis)
- [Verification](#verification)
- [Limitations](#limitations)

## Pipeline and invocation

**Historical stage-nine guide.** Current database format 4 and localization are documented in the [stage-ten guide](BACKEND_STAGE_10_EN.md). Counts and formats below describe stage-nine verification.

Implementation follows the approved [stage-nine specification](TZ_BACKEND_STAGE_9_EN.md). After preparing libraries, the shared coordinator expands inline insertions, effects, triggers, and script values. Final static-variable substitution precedes structural validation and JSON publication. Game sources remain read-only; no technology domain model or game-command profile is used.

Verification build from the repository root:

```powershell
& WEB_STTV/data/.venv/Scripts/python.exe -B WEB_STTV/src/backend/main.py --config WEB_STTV/data/stage9/backend.json
```

Without `--config`, the standard `config/backend.json`, `data/database.json`, and `data/reports/build_report.json` apply. `--variables`, `sttv.builder.build`, and `sttv.database.storage.read_database` remain available. Stage checks write a separate database to `data/stage9/database.json`; previous standard outputs and curated lists are preserved. Reading a finished database does not require installed sources.

## Sources and configuration

The new variable `SCRIPT_VALUES_DIR = common/script_values` selects the library relative to `STELLARIS_ROOT`. It is read separately and excluded from independent traversal together with inline, scripted effect, scripted trigger, and scripted variable directories. An existing directory is required; an empty library is valid.

The eighth selector, `parser.script_values`, points to [script_values.json](../../Instruments/Stellaris_Parser/stellaris_parser/config/script_values.json): `reference_prefix = value:`, `scope_separator = .`, and `argument_separator = |`. Ambiguous and conflicting markers are rejected. File patterns, recursion, encoding, case rules, and shared limits come from [scripted_calls.json](../../Instruments/Stellaris_Parser/stellaris_parser/config/scripted_calls.json), without duplicating loading settings.

Defaults are `*.txt`, recursive traversal, `utf-8-sig`, case-insensitive names, case-sensitive parameters, mixed depth up to 64, and a budget of 1,000,000 created nodes per document. The separate inline-depth limit still applies. Configurations and libraries are protected from output overwrites.

The installed library contains 15 indexed files, 674 calculations, and one local declaration. Script value names use a separate namespace from effects/triggers; within-library collisions are diagnosed. Indexing does not expand bodies or require arguments for unused definitions.

## Value expansion

Entire unquoted scalars are supported:

```text
value:tech_weight_likelihood
owner.value:num_active_technophant
value:num_active_buildings|BUILDING|building_augmentation_center|
value:trait_kill_naval_cap_scaling|MULT|value:hells_heart_effect|
```

A calculation remains one value at its reference position. For example, `factor = value:tech_weight_likelihood` preserves the key and operator while its right-hand side becomes a node containing `base = 1.25`. No number is evaluated or substituted for the body. Operation order, repeated fields, and conditions remain intact.

Arguments are bound before traversing inserted bodies. Nested `value:...` references expand after the argument is actually inserted; unused arguments do not expand. Defaults, explicit `no`/empty values, and conditional fragments share the previous stage's rules. Discarded parameter fragments do not require their arguments; runtime conditions remain in the tree.

Scopes such as `owner` or `event_target:paragon_destroyed_ship` are preserved separately. Nested scopes are not merged, and `root`/`prev`/`from` are not rewritten. Definition, argument, and default static variables retain their own environments; inline inherits its insertion environment. A whole static alias resolving to `value:...` is recognized before expansion finishes, without separate static replacement history.

Strings, formulas, keys, logical-operation/tag names, and metadata are not expanded as references. The syntax parser without library context still preserves the original scalar. Protective limits and the stack are shared across four invocation kinds; independent repeated calls are not cycles.

## Database format and history

The database format is `sttv.parse_database`, version **3**. The ninth node kind, `script_value`, contains `scope` (string or `null`), `body` (block), `span`, and `origin`. The wrapper has `synthetic: true`; child entries retain physical definition and argument provenance. Older databases require rebuilding.

The new `kind: script_value` in `metadata.expansions` contains the target, call coordinates, arguments, original reference, and parent. Its `invocation.operator` is `null`: the outer assignment operator belongs to the surrounding entry. `directives` is empty; ordinary calculation operations are not removed.

For script values, `insertion = { "node": "/items/0/value" }` addresses one final node. Other invocations retain `container` / `index` / `count` ranges. Addresses are resolved against the final tree and validated alongside provenance; corrupted history is rejected even when reading without the game.

All schemas are generated from declarations under `src/backend/sttv/schema_generation/`. Added `parser_script_values.schema.json`, bringing the total to 11 schemas. The closed JSON structure defines node kinds and service fields without restricting game-command names.

## Diagnostics and analysis

Report version **5** includes `script_value_sources` with file hashes and `counts.scripted_calls.script_value`: files, definitions, local declarations, encountered, successful, and failed references. The shared `tests` field remains zero for this kind; triggers use it for nonboolean comparisons. Defaults, conditional fragments, and depth contribute to shared counters.

Errors are recorded automatically: unknown targets, malformed argument pairs, missing parameters, static references, cycles, limits, and other causes. Diagnostics preserve locations and mixed call chains. On failure, the database is not replaced; the current-run report is overwritten. Corpus audits continue independent files and record each file's first blocking error. The shared `TO_DO` is not changed automatically.

Analysis traverses each expanded body once; history, library templates, and service wrappers are not counted as game terms. Existing frequency filters remain. New verification lists go to `data/stage9/text_frequency/`.

## Verification

- All **154 tests** passed, including 26 new tests; report: `data/stage9/unit_tests.json`.
- Technologies: **35 files, 82,246 nodes, 36 expanded script values**, 1,776 triggers, 301 inline insertions, and 1,929 static substitutions. No errors or warnings occurred. Verification database size: **138,156,360 bytes**.
- Independent comparison of every serialized field and static value, comparison of surroundings with script value expansion disabled, direct comparison of 16 constant bodies against the game definition, and byte-identical rebuilding passed. Report: `data/stage9/real_validation_report.json`.
- Three real source fragments and four synthetic invocations of vanilla definitions also passed: the nested Paragons argument, scoped references, `BUILDING`, defaults, and conditional fragments. This covers 7 trees / 300 nodes; reports: `value_examples.json` and `value_examples_report.json` in the stage directory.

The full `common/` and `events/` audit completed: 2,238 TXT files yielded 1,489 independent inputs after excluding five libraries. **1,466 succeeded, two documentation files were skipped, and 21 inputs stopped with diagnostics.** JSON round trips and history were checked for 7,464,925 serialized nodes; the sum of checked document sizes was 4,839,643,282 bytes, without publishing one corpus database. The run took 1,379.79 seconds. It encountered 11,676 script value references, expanded 11,674, and failed two; counters include invocations in inputs that later stopped.

`data/stage9/corpus_report.json` contains locations, call chains, and 642 warnings about unused inline arguments. Separate lists cover successful inputs: 52,604 frequency entries, 33,805 scalar values, and 3,545 scalar assignments. Hash checks passed for independent sources, templates, all libraries, and previous lists.

Compared with the previous 20 failures: **19 matched exactly, two inputs newly failed, and one library input was excluded from independent traversal**. The previous 19 concern `CLASS` (14 files), `RELIC` (two), an effect called with `no`, missing `RANDOM`, and an ambiguous static environment in Shroud. Their causes remain documented in the [stage-eight guide](BACKEND_STAGE_8_EN.md#general-audit-and-failing-inputs).

| Newly failing input | Confirmed cause |
|---|---|
| `common/pop_jobs/06_event_jobs.txt:2188` | `value:scripted_modifier_mult\|MODIFIER\|pop_job_amenities_mult\|\|`: an extra trailing delimiter violates the agreed argument-pair form. Diagnostic: `invalid_script_value_arguments`. |
| `events/first_contact_dlc_operations_events.txt:330` | The effect chain reaches `common/scripted_effects/first_contact_dlc_effects.txt:2478`, which supplies `BONUS`. In `common/script_values/00_script_values.txt:1804–1805`, the `[[BONUS]]` fragment requests `$bonus$`. With the active `parameter_case_sensitive = true`, these are different parameters; diagnostic: `missing_inline_parameter`. Engine behavior at this location was not tested. |

`common/script_values/01_script_values_paragon.txt` is no longer an independent input. Its previous `@max_unlocked_council_positions` reference at line 365 remains unfixed: this audit does not establish successful reachability of that body. Reaching its error must still produce a diagnostic.

All 102 Python files passed checks; maximum length is 160 lines. All 11 schemas match the generator. Contents, links, and JSON examples were checked across 60 documents, along with seven changed bilingual pairs and matching stage-nine examples. Summary: `data/stage9/verification_report.json`; investigation of the two new failures: `corpus_findings.json` in the same directory.

A process peak working set of 4,329,783,296 bytes (about 4.03 GiB) was observed during the corpus run. This is an intermediate observation, not a final maximum measurement; the original sample is in `corpus_memory_sample.json`.

## Limitations

Expansion does not evaluate arithmetic, game conditions, building/population counts, trigger results, modifiers, or game variables. It does not replace the game engine or claim numerical equivalence without game execution.

Argument `|` delimiters follow the agreed pair syntax; unverified nested argument-list syntax and escaping are not invented. Unknown ordinary commands remain; unknown explicit `value:...` targets are diagnosed. Removing a library file from independent traversal does not fix it: an error in its reached body still stops the corresponding input.

Sources, previous standard outputs, and old lists are preserved. Large expanded trees require memory; the corpus checks individual documents without publishing one partially successful database of the entire game.
