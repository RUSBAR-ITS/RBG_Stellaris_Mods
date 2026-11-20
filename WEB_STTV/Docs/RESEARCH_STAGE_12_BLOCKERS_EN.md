# WEB_STTV — stage 12 blocker recheck

## Contents

- [Result and scope](#result-and-scope)
- [Confirmed cases](#confirmed-cases)
- [Causes in source constructs](#causes-in-source-constructs)
- [Mixed Shroud variable context](#mixed-shroud-variable-context)
- [Artifacts and next actions](#artifacts-and-next-actions)

## Result and scope

On 2026-11-18, seven complete files from the historical stage-nine list were rechecked. **All seven failed again with the same errors. There are six distinct causes: two event files use the same problematic `RELIC` template.**

The run used current product code, active configuration and installed-game libraries: `parse_text` with shared expansion context, followed by normal static substitution and serialization if preceding stages succeed. All seven stopped during expansion; no new successful database result was produced. The main run took 53.944 seconds.

This check covers only those seven documents. Each stops at its first error, so additional errors may appear after fixing the first cause. It was not a new full expansion pass over the 332 TXT files of the added sources.

Hashes of all consumed game sources were verified after the run. Backend code, configuration, global variables and published databases were also checked by hash and remained unchanged. No fixes were applied. Stellaris engine behavior was not tested: reproducing a tool error alone does not prove an execution bug in the game.

## Confirmed cases

| Source document | Error | Cause |
| --- | --- | --- |
| `common/pop_jobs/06_event_jobs.txt` | `invalid_script_value_arguments` | Double trailing delimiter `||` in a script-value reference |
| `events/ancient_relics_arcsite_events_2.txt` | `unsupported_scripted_call` | `small_artifact_reward = no`; the effect expander permits `yes` or an argument block |
| `events/first_contact_dlc_operations_events.txt` | `missing_inline_parameter` | `BONUS` is supplied but the selected fragment requests `$bonus$` |
| `events/grand_archive_events.txt` | `missing_inline_parameter` | A nested template requests unsupplied `RELIC` |
| `events/leviathans_events_1.txt` | `missing_inline_parameter` | The same `RELIC` template cause |
| `events/nomads_origin_events.txt` | `missing_inline_parameter` | The call supplies `PERCENTAGE` but not `RANDOM`, which the selected fragment uses |
| `events/shroud_events.txt` | `ambiguous_static_environment` | A static name combines pieces from two environments; the resolver rejects them without checking identical resolution |

## Causes in source constructs

1. [06_event_jobs.txt:2188](/E:/SteamLibrary/steamapps/common/Stellaris/common/pop_jobs/06_event_jobs.txt:2188) contains `value:scripted_modifier_mult|MODIFIER|pop_job_amenities_mult||`. The additional final `|` violates the parser's accepted closed name/value pairs. This is a confirmed mismatch with the current grammar; engine tolerance of that ending was not tested.
2. [ancient_relics_arcsite_events_2.txt:9884](/E:/SteamLibrary/steamapps/common/Stellaris/events/ancient_relics_arcsite_events_2.txt:9884) calls `small_artifact_reward = no`. Its definition is a [scripted effect](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/archaeology_event_effects.txt:117). [Our expander](/D:/Repos/RBG_Stellaris_Mods/Instruments/Stellaris_Parser/stellaris_parser/script/scripted/expansion.py:49) explicitly prohibits this. Without separate investigation, `no` must not become a skipped call, `yes`, or effect negation.
3. The chain from [first_contact_dlc_operations_events.txt:330](/E:/SteamLibrary/steamapps/common/Stellaris/events/first_contact_dlc_operations_events.txt:330) to [first_contact_dlc_effects.txt:2478](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/first_contact_dlc_effects.txt:2478) passes `BONUS`. In [00_script_values.txt:1804](/E:/SteamLibrary/steamapps/common/Stellaris/common/script_values/00_script_values.txt:1804), `[[BONUS]` selects a fragment containing `add = $bonus$`. Active `parameter_case_sensitive = true` makes these names different. This is a case mismatch, not a wholly absent argument. The example does not establish general parameter case insensitivity.
4. [stage_3_reward_option.txt:15](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/grand_archive/collection/stage_3_reward_option.txt:15) uses `gave_relic_$RELIC$`. Its [calling template](/E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/grand_archive/collection/stage_3_reward_options_by_category.txt:1) passes `SELECTED_RELIC` and `OTHER_RELIC_1`–`OTHER_RELIC_4`, but not `RELIC`. Nearby checks and reward effects use `SELECTED_RELIC`. The failure was reached through `grand_archive_events.txt:4811` and `leviathans_events_1.txt:7577`; `VANILLA-002` already tracks this case.
5. [nomads_origin_events.txt:795](/E:/SteamLibrary/steamapps/common/Stellaris/events/nomads_origin_events.txt:795) calls `pop_group_add_ethic_effect` with `POP_GROUP`, `ETHOS` and `PERCENTAGE = 0.3`. The selected branch in [00_scripted_effects.txt:9030](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:9030) requires `$RANDOM$`, with neither an argument nor a default. An arbitrary zero must not be supplied just to pass validation.

## Mixed Shroud variable context

[shroud_events.txt:17815](/E:/SteamLibrary/steamapps/common/Stellaris/events/shroud_events.txt:17815) calls `apply_pop_template_pop_check` with `TIER = 1`, followed by calls with 2 and 3. The [trigger:639](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/08_scripted_triggers_shroud.txt:639) constructs `@po_apply_pop_template_tier$TIER$_nb_pop`.

Three minimal calls to the real trigger were also run against unchanged libraries. Diagnostic observation resolved the name independently in each discovered environment, then passed original arguments to the normal resolver, which produced the same error. Its result was not substituted.

| `TIER` | Constructed name | Template environment | Argument environment |
| ---: | --- | ---: | ---: |
| 1 | `@po_apply_pop_template_tier1_nb_pop` | 1500 | 1500 |
| 2 | `@po_apply_pop_template_tier2_nb_pop` | 3000 | 3000 |
| 3 | `@po_apply_pop_template_tier3_nb_pop` | 5000 | 5000 |

There are no local overrides in these cases. Both environments point to the same global definition in [09_scripted_variables_shroud.txt:194](/E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_variables/09_scripted_variables_shroud.txt:194).

The cause is in our code: [MappedSource.environment_at](/D:/Repos/RBG_Stellaris_Mods/Instruments/Stellaris_Parser/stellaris_parser/script/inlining/text.py:26) retains multiple environments for a composed token, while [Processor.resolve](/D:/Repos/RBG_Stellaris_Mods/Instruments/Stellaris_Parser/stellaris_parser/script/variables/processor.py:47) immediately rejects an environment tuple. It never looks up the existing variable. This is a confirmed parser limitation for this case; selection rules for genuinely different local definitions still need design.

## Artifacts and next actions

- [Seven-file results](../data/stage12/problem_recheck/results.json): codes, coordinates, call chains and tracebacks.
- [Current pipeline report](../data/stage12/problem_recheck/pipeline_report.json): warnings and hashes of consumed sources.
- [Shroud diagnostic calls](../data/stage12/problem_recheck/shroud_environment_probe.json).
- Reproduction scripts: `data/stage12/problem_recheck/recheck.py` and `inspect_shroud.py`; use the existing Python environment with `-B`.
- [Stage 12 specification](TZ_BACKEND_STAGE_12_EN.md) remains a draft. Confirming errors does not approve their fixes.

After this recheck, the user agreed to case-insensitive parameters, conditional exceptions for four sources and `RANDOM = 0`. Subsequent decisions, concrete rules and proposals for the `no` effect and composed variable are recorded in the [import addendum](SOURCE_IMPORT_EXCEPTIONS_EN.md). They do not change the unmodified-run results above. After implementation, rerun complete files and then the new full set to reveal failures beyond the first stopping point.

[Русская версия](RESEARCH_STAGE_12_BLOCKERS_RU.md).
