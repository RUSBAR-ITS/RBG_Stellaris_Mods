# RB_SDM vanilla files and functions affected

## Contents

- [Project status](#project-status)
- [Design references](#design-references)

## Project status

Version 0.0.1 has an empty list of vanilla overrides. The decision, events, triggers, effects, templates and localization entries use their own names. The mod references the following base-game resources.

| Resource | Use |
|---|---|
| `gfx/interface/icons/decisions/decision_resources.dds`, `event_administrative_work` | Planetary decision icon and sound. |
| `interface/eventpictures.gfx` | Menu windows display `GFX_evt_alien_planet`. |
| `localisation/english/main_1_l_english.yml`, `localisation/russian/main_1_l_russian.yml` | Navigation labels reference `PREV`, `NEXT`, `BACK` and `CLOSE`. Russian terms were checked against the repository's translation priorities. |

## Design references

Paths are relative to the Stellaris v4.5.4 installation. These files were consulted for syntax.

| Vanilla file | Subject |
|---|---|
| `common/decisions/example.txt` | Planetary decision blocks for visibility, eligibility, execution and AI weight. |
| `common/decisions/03_crime_decisions.txt` | Conditions on an owned colony and adjustments to AI decision weight based on planet state. |
| `common/inline_scripts/grand_archive/collection/stage_3_reward_option.txt` | Template for an entire `option` block with parameters and a display condition. |
| `common/inline_scripts/grand_archive/collection/stage_3_reward_options_by_category.txt` | Repeated inclusion with different parameters in declaration order. |
| `common/inline_scripts/grand_archive/mutations/camouflage/camouflage_mutation.txt` | A parameter in the path of a nested `inline_script`. |
| `events/000_how_to_use_variables_in_script.txt` | Variable scopes, counters, rounding and displaying a variable in localization. |
