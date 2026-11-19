# Dictionary — empire conditions

## Contents

- [Checks](#checks)
- [Named functions](#named-functions)
- [Use in chains](#use-in-chains)
- [Sources](#sources)

## Checks

The table covers contexts needed for current analysis. It does not enumerate every engine-supported scope.

| Keyword | Context and value | Game meaning | Use and boundaries | Sources |
| --- | --- | --- | --- | --- |
| `is_nomadic` | Country; `yes` / `no` | Checks whether the empire is nomadic. | Distinguishes nomadic and ordinary technology paths. Preserve complete negations and alternatives. | C1 |
| `uses_ship_category` | Country; ship category ID | Checks the ship category in use, such as `bio_ship`. | Distinguishes biological and conventional ship branches. A ship category is not a scientific `category`. | C2 |
| `has_ethic` | Country here; ethic ID | Checks for a specific ethic. | Compares restrictions; `ethic_gestalt_consciousness` is relevant to the agreed profile. Other ethics are not assigned automatically. | C3, C7 |
| `has_authority` | Country; authority ID | Checks the authority, such as `auth_hive_mind`. | Clarifies country conditions. Do not substitute a species category for an authority. | C4 |
| `is_archetype` | Species; archetype ID | Checks the species archetype, such as `MACHINE` or `BIOLOGICAL`. | In country conditions, first account for the transition to a species, such as `founder_species`. | C5, C7 |
| `has_origin` | Country; origin ID | Checks the empire origin. | Compares special conditions. An unspecified origin leaves the result unknown. | C6 |
| `has_valid_civic` | Country; civic ID | Checks civic possession and validity. | Do not reduce it to the presence of a civic ID: validity is part of the check. | C6, C7 |

## Named functions

`country_uses_bio_ships` is a **scripted trigger** defined in game files, not a separate built-in technology field. Its body in the current installation is:

```text
country_uses_bio_ships = {
    exists = this
    uses_ship_category = bio_ship
}
```

Source: C2. Analysis of the expanded database should use the resulting body and call context. It should not introduce an independent fact that could contradict `uses_ship_category`. This exemplifies the distinction between a named function and a built-in check; name prefixes are not a universal classifier.

## Use in chains

- Agreed reference profile: non-nomadic, non-gestalt empire with biological population and conventional ships. Ethics beyond this restriction, origin and development paths remain unspecified.
- An unknown profile parameter does not prove technology unavailability. A special condition in one `OR` branch does not exclude another available alternative.
- Matching special conditions must preserve operators, values and scope. Generic checks such as `exists = this` do not by themselves establish meaningful technological affinity.
- Availability conditions are interpreted at their structural location. Research-draw or AI weight conditions do not become availability restrictions.
- [Complete comparison of nonempty `potential` blocks](../frontend/CHAIN_AVAILABILITY_EN.md) after expansion is approved for predecessor selection. Entire blocks are matched, not individual shared checks.
- These entries explain condition meaning. They do not implement a complete empire evaluator or the new predecessor selector.

## Sources

- [C1 — nomadic titan variant](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:269).
- [C2 — country_uses_bio_ships definition](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/07_scripted_triggers_ships.txt:33).
- [C3 — special conditions of religious technologies](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:5803); [ethic check definition](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:1674); [federation conditions used](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/02_scripted_triggers_federations.txt:111).
- [C4 — authority checks](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:1781).
- [C5 — founding-species archetype](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/02_scripted_triggers_machine_age.txt:63); [biological archetype](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/01_scripted_triggers_jobs.txt:241).
- [C6 — origin and valid civic examples](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:195).
- [C7 — v4.3.1 trigger documentation dump](https://raw.githubusercontent.com/OldEnt/stellaris-triggers-modifiers-effects-list/master/4.3.1_game_triggers.log): meanings of `has_valid_civic`, `has_ethic` and `is_archetype`. Older than the installation; C1–C6 examples come from v4.5.4.

[Dictionary index](README_EN.md) · [Русская версия](EMPIRE_CONDITIONS_RU.md).
