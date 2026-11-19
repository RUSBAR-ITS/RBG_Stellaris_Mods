# Dictionary — tooltips and conditions

## Contents

- [Constructs](#constructs)
- [Text parameters](#text-parameters)
- [Examples and analysis](#examples-and-analysis)
- [Sources](#sources)

## Constructs

| Keyword | Context and form | Meaning | Analytical use | Sources |
| --- | --- | --- | --- | --- |
| `hidden_trigger` | Conditions; check block | Conditions still apply, but their automatically generated tooltip is hidden. | Preserve and account for nested checks. Hiding text neither cancels a condition nor changes scope. | H1, H3 |
| `custom_tooltip` | Conditions; block with text parameters and checks | Replaces the display of nested checks with a specified message. Checks still determine the result. | Distinguish actual child conditions from text parameters. | H2, H3 |
| `custom_tooltip` | Scalar localization key in conditions, effects or a supporting object | Supplies tooltip text. This form has no nested checks. | The string key is not a technology requirement or game-object reference. | H1, H2, H4 |

## Text parameters

This table describes a `custom_tooltip` block in conditions. It does not define identically named fields in arbitrary other objects.

| Keyword | Value | Meaning | Sources |
| --- | --- | --- | --- |
| `text` | Localization string key | Shared message when a separate success or failure message is absent. | H3 |
| `fail_text` | String key or supported `default` / `none` modes | Failed-check presentation: specified text, standard display or no text. The mode does not replace the logical result. | H2, H3 |
| `success_text` | String key or supported `default` / `none` modes | Corresponding presentation control for a successful check. | H3 |

## Examples and analysis

`entertainer_job_check_trigger` specifies text followed by hidden checks (H1). An abbreviated illustration of that separation:

```text
custom_tooltip = SPECIALIST_JOB_TRIGGER
hidden_trigger = {
    exists = owner
    is_being_purged = no
}
```

This illustration retains only two of the source's actual checks. `SPECIALIST_JOB_TRIGGER` is a localization key; restrictions reside inside `hidden_trigger` and remain effective.

Within `dark_matter_detector`, `possible.custom_tooltip` contains `fail_text = "requires_detection_array"` and an `OR` block: the detection module is already installed or is earlier in the construction queue (H2). Analysis must retain the alternative and treat `requires_detection_array` as a text reference.

The same object separately specifies `custom_tooltip = sm_dark_matter_detector_desc_modifier`. This describes an effect, not an additional construction condition. Consequently, **form and tree location are required for interpretation**: requirements cannot be extracted from all occurrences of `custom_tooltip` in the same way.

The dictionary records the separation of logic and presentation. Rendering game tooltip formatting in WEB_STTV or evaluating tooltip state is outside its scope.

## Sources

- [H1 — entertainer job text and hidden checks](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/01_scripted_triggers_jobs.txt:15).
- [H2 — detector conditions and separate tooltip](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_buildings/00_starbase_buildings.txt:2353).
- [H3 — v4.3.1 trigger documentation](https://raw.githubusercontent.com/OldEnt/stellaris-triggers-modifiers-effects-list/master/4.3.1_game_triggers.log): `custom_tooltip`, `hidden_trigger` and text parameters. Forms were compared with v4.5.4 examples H1 and H2; `default` / `none` modes follow documentation without a separate game test.
- [H4 — v4.3.1 effect documentation](https://raw.githubusercontent.com/OldEnt/stellaris-triggers-modifiers-effects-list/master/4.3.1_game_effects.log): scalar `custom_tooltip` displays a localization string. This is distinct from `hidden_effect`, which hides the display of executed effects.

[Dictionary index](README_EN.md) · [Русская версия](TOOLTIPS_RU.md).
