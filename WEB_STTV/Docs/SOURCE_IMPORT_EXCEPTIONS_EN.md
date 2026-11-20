# WEB_STTV — import exceptions and expander refinements

## Contents

- [Status](#status)
- [Conditional exceptions](#conditional-exceptions)
- [Application and reporting](#application-and-reporting)
- [Parameter case](#parameter-case)
- [Scalar effect invocation](#scalar-effect-invocation)
- [Composed static variable](#composed-static-variable)
- [Verification](#verification)

## Status

The user approved these rules with stage 12 on 2026-11-18; they are implemented. [source_exceptions.json](../config/parser/source_exceptions.json) is loaded through `parser.source_exceptions`, with every application recorded in the report. Case-insensitive parameter names, structural expansion of `effect = no`, and mixed-environment resolution for one shared variable declaration are implemented.

This transformation neither evaluates nor confirms engine behavior for `effect = no`. Original causes are documented in the [investigation](RESEARCH_STAGE_12_BLOCKERS_EN.md); all seven files passed the full run, with results in the [stage 12 guide](BACKEND_STAGE_12_EN.md#verification).

## Conditional exceptions

The rules below use paths relative to `STELLARIS_ROOT`.

| Rule | Conditions | In-memory transformation |
| --- | --- | --- |
| `sttv_event_job_amenities_separator` | Both root document and immediate source are `common/pop_jobs/06_event_jobs.txt`; the scalar reference exactly equals `value:scripted_modifier_mult\|MODIFIER\|pop_job_amenities_mult\|\|` | Remove only the last `\|`, then parse the corrected reference with the normal handler |
| `sttv_archive_selected_relic` | Root document is `events/grand_archive_events.txt` or `events/leviathans_events_1.txt`; expansion uses `common/inline_scripts/grand_archive/collection/stage_3_reward_option.txt`; `gave_relic_$RELIC$` is reached; `RELIC` is absent and `SELECTED_RELIC` was supplied | Bind `RELIC` to the supplied `SELECTED_RELIC` for this invocation, preserving its value provenance |
| `sttv_nomads_ethic_random` | Root document is `events/nomads_origin_events.txt`; invocation is `pop_group_add_ethic_effect` from `common/scripted_effects/00_scripted_effects.txt`; `$RANDOM$` is reached but its argument is absent; `POP_GROUP`, `ETHOS`, `PERCENTAGE` were supplied | Add `RANDOM = 0` to this invocation as the explicitly agreed temporary value |
| `sttv_dlc_metadata_store_separator` | Only `dlc_metadata/dlc_info.txt`, direct contents of `dlcs/dlc002`, token sequence `paradoxplaza_store_url ""` | Insert `=` in memory. Comments, string literals, other objects and corrected assignments do not match; multiple matches fail |

A reached reference means a lookup after conditional template fragments are selected. Matching text in a comment or discarded fragment does not activate a rule. The root document remains available through nested expansions. `required_parameters` checks presence, including explicitly supplied values; original arguments are not overwritten.

A `||` suffix alone does not justify a correction: it can represent an empty argument value in a different valid reference. Removing a character is therefore restricted to the specified complete reference. Reapplying the rule to an already corrected reference changes nothing.

`RELIC` does not become a global parameter alias. `RANDOM` does not gain a default across the entire effect or game. Multiple matching invocations inside the allowed root documents are handled individually.

## Application and reporting

Stage 19 approves `sttv_trait_icon_class` and `sttv_trait_council_icon_class`: a reached missing CLASS only in `trait/icon.txt` and `trait/icon_element/council_no.txt`, within the configured root trait files. Derive it from the enclosing root trait's immediate leader_class. A sole allowed class retains its original coordinates; multiple distinct classes use approved leader with configuration provenance. Explicit arguments are preserved. Missing fields, invalid shapes, unknown classes or unresolved owners fail. Nested calls use the original call chain, not neighboring objects or filenames. Reports identify the object/field in value_source and retain the call chain. Allowed values and the neutral value belong to parameter_from_object configuration, not expander code.

If an intermediate template dropped an explicitly supplied CLASS, the same scoped exceptions first use the nearest explicit argument in the invocation chain, then consult leader_class. This does not introduce general argument inheritance between templates.

`source_exceptions.json` is separate from [exceptions.json](../config/parser/exceptions.json), which already allows an inline template filename without an extension. The new file describes import transformations; its paths match sources already being read and do not authorize opening arbitrary files.

The implementation loads the file through `parser.source_exceptions`, validates its format and records it among configuration inputs. Applied transformations affect set contents and identity. Conditions within one rule use AND; `root_files` entries use OR. Parameter names follow the shared case policy; argument values are not lowercased. Complete scalar reference values match exactly.

Apply transformations in memory before the operation that would otherwise raise the corresponding error. Preserve original text, coordinates and provenance; do not imply that corrected content was read from the game. Neither game files nor the shared source-template cache are changed. Unmatched conditions retain normal handling; errors elsewhere remain visible.

Log every application: rule ID, root document, immediate source and coordinates, call chain, original value or absent-argument state, applied value and its source. For `RANDOM` the source is the exception rule; for `RELIC` it is the `SELECTED_RELIC` argument. A complete run records application counts for every rule, including zero; no matches alone do not fail a partial build.

Two matching rules changing the same value produce a diagnostic conflict; file order does not select a winner. Repeating the same inputs and configuration must produce the same result. A rule that no longer matches after a game update is not automatically widened.

## Parameter case

Parameter names will match without case sensitivity: `BONUS`, `bonus` and `Bonus` identify the same supplied argument. During implementation, set `parameter_case_sensitive = false` consistently for inline and named calls; script values follow the same binding policy.

This covers supplied argument names, `$PARAM$` lookup, `[[PARAM]` / `[[!PARAM]` selection, missing-argument checks before defaults, and duplicate detection. Argument values, literal default text and strings remain unchanged. Supplying both `BONUS` and `bonus` in one invocation is a duplicate, not a reason to silently select the last entry.

This resolves the `BONUS` / `$bonus$` mismatch reached from `first_contact_dlc_operations_events.txt`; no per-file exception is needed. It is the agreed tool contract, not a conclusion about case handling throughout the game language.

## Scalar effect invocation

The restriction has a confirmed origin: [section 7 of stage 8](TZ_BACKEND_STAGE_8_EN.md#7-effect-expansion) separately limited scalar effect invocation to `yes`. The check lives in `expand_named` in `script/scripted/expansion.py`. It survived removal of the allowed-command registry independently: it restricts transformation of a known invocation rather than validating an unknown command.

Vanilla `common/scripted_effects/99_advanced_documentation.txt:13` describes normal invocation with `yes` and block arguments; it does not explain `effect = no`. That documentation cannot establish whether the engine executes this form.

**Proposal:** for `effect_name = no`, expand the located definition without arguments for structural analysis, retaining the original `no` in the existing invocation record (`invocation.raw`). Do not convert it to trigger negation, remove the body, or rewrite the original invocation to `yes`. Such expansion exposes definition contents but does not claim engine execution for `no`. This proposal does not redefine other scalar invocation forms.

## Composed static variable

`shroud_events.txt` needs no source-data exception. The trigger contains `@po_apply_pop_template_tier$TIER$_nb_pop`. Substituting `TIER = 1` produces `@po_apply_pop_template_tier1_nb_pop`, whose existing global declaration equals `1500`. Values 2 and 3 similarly resolve to `3000` and `5000`.

Name fragments originate from the template and the calling event argument. Our handler retains both environments but currently rejects them before variable lookup. The investigation confirmed that both environments resolve all three calls to the same global declaration without a local override.

**Proposal:** assemble the full name first, then resolve it in each retained environment using the existing local/global rules. Substitute when all environments lead to the same declaration and resolution chain. Compare declaration provenance, not just numeric equality: two distinct local declarations with equal values do not establish a shared environment.

If any environment cannot resolve the name or definitions differ, retain a diagnostic error with lookup results rather than choosing the first environment. Preserve fragment provenance. For this case, the rule imports the real `1500`, `3000`, `5000` without Shroud-specific constant exceptions.

## Verification

The prepared file was checked against current sources: one exact reference has the extra separator, and the corrected reference is accepted by the existing script-value reader. The calling template contains five invocations supplying `SELECTED_RELIC` without `RELIC`; the nomad file contains nine matching invocations without `RANDOM`. JSON, contents and links were checked; hashes confirmed 151 existing code, configuration and database files unchanged. The verification report (`data/stage12/source_exceptions_review.json`) covers condition matching, not execution of the exceptions that are not yet wired.

During implementation, test every rule and nearby nonmatching cases: a different file, template or reference, an already supplied `RELIC`/`RANDOM`, a comment, and a discarded branch. Check a valid empty script-value argument, repeated application, conflicting rules, and complete reporting.

For case handling, test nested calls of all three kinds, conditionals, defaults, unchanged values and normalized-name duplicates. For mixed environments, test the three real `TIER` values, a single environment, a shared global origin, distinct local declarations and an unknown name. For the proposed `effect = no`, test expansion without negation and preservation of the original invocation.

After implementation, rerun the seven full files and the complete stage 12 set. Validating the prepared JSON and matching its conditions against sources does not replace that run.

[Русская версия](SOURCE_IMPORT_EXCEPTIONS_RU.md).
