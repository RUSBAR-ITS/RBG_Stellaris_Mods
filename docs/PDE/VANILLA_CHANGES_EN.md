# PDE 2.0.4 vanilla files and functions

## Contents

- [Scope](#scope)
- [Decision and deposits](#decision-and-deposits)
- [Planet state](#planet-state)

## Scope

The release dependencies were checked against the installed Stellaris 4.6.0. Version 2.0.4 uses PDE-owned scripts and keys and relies on the vanilla decision interface, deposit definitions and events without overriding vanilla files. Review these dependencies when updating the game version. [Specification](TZ_EN.md)

## Decision and deposits

| Mechanism | Use and source |
| --- | --- |
| Access to planetary decisions | Vanilla access for owned colonies and uncolonized bodies. PDE checks the system owner (`space_owner`), the acting player (`from`) and, for a colony, `colony.owner`. It checks the carrier type with `carrier_is_type`. [Source](E:/SteamLibrary/steamapps/common/Stellaris/common/game_rules/00_rules.txt:4779) |
| Adding one instance | PDE calls `add_deposit` for a regular feature and `add_blocker = { type = … blocked_deposit = none }` for a blocker. This prevents creation of a random feature beneath the blocker. [PDE effects](../../PDE/common/scripted_effects/cdpd_deposit_effects.txt) |
| Selecting one instance | On the selected body, `random_deposit` and `is_deposit_type` restrict the choice to instances of one ID. [Source](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/01_start_of_game_effects.txt:3323) |
| Direct removal | The `remove_deposit = yes` effect acts on the selected instance in deposit scope. [Source](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/07_overlord_decisions.txt:44) |
| ID and class register | The per-ID register links the `common/deposits/` definitions, classes and vanilla grants. Manual placement applies the deposit to the selected body. [Register](DEPOSIT_CLASSIFICATION_EN.md) |
| Tooltip | The vanilla tooltip window sets the font. Localization uses `§R` and `§!` for the red warning. [Source](E:/SteamLibrary/steamapps/common/Stellaris/interface/core.gui:40) |
| Ghostly Canyon stability | The +10% stability modifier checks `is_spiritualist` on the owner. The add and remove tooltips use the vanilla names for the three eligible ethics from `ethic_spiritualist`, `ethic_fanatic_spiritualist` and `ethic_absolute_spiritualist`. [Deposit](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/12_cosmic_storms_deposits.txt:53) · [Triggers](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:1723) |
| Effect preview | All placement options use the actual `add_deposit` or `add_blocker` operation within a target-scoped `tooltip`. [Menu template](../../PDE/common/inline_scripts/cdpd/menu/cdpd_option_preview.txt) |
| Property data | Read production, upkeep and modifiers from `common/deposits/`, included job and blocker scripts, scripted variables and script values. Cross-check feature-specific building, district and specialization unlocks against `common/buildings/`, `common/districts/`, `common/zones/` and `common/zone_slots/`. [Deposit register](DEPOSIT_CLASSIFICATION_EN.md) |
| Colony status | For a generic colonizable-world requirement, `cdpd_is_colonizable_or_colonized` tests `is_colonizable = yes` or `is_colony = yes`. Orbital resource targets must fail both tests. Individual class and climate restrictions still apply. |
| Feature properties | The [three-deposit table](TZ_TOOLTIP_EFFECTS_EN.md#first-verification) links the constants for the plains (+1), the sinkhole (−1), Titanic Lifeforms (+8 and −1) and its shared modifier (+25%). Sinkhole energy output uses the global `@ranger_small_production`. Its included script sets job output (−10%), founder species growth (−10%) and pop upkeep (+15%). [Lodge condition](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/01_scripted_triggers_jobs.txt:434) · [Variable](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_variables/00_scripted_variables.txt:488) · [Penalties](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/deposits/environmental_architects_natural_blocker_modifier.txt) · [Civic group](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:5337) |

## Planet state

In the 4.5.4 snapshot, 58 definitions have an `on_cleared` handler. Direct removal requires distinguishing instance bookkeeping from vanilla clearance rewards. The table records the required pair and the variables identified during the callback review. [Definition snapshot](../../TMP/PDE/v4.5.4/deposits.json)

| State | Vanilla behavior and sources |
| --- | --- |
| `d_titanic_life_blocker` / `titanic_life` | At setup, vanilla places the deposit on planets with the modifier. The deposit and the modifier supply separate bonuses. An origin event can also grant the modifier independently. PDE records any independent modifier present before the first instance is added. If `grand_archive.1015` grants the same modifier again while it is already active, the event leaves no source marker on the planet. Removing the last instance can then remove that grant as well. [Pair setup](E:/SteamLibrary/steamapps/common/Stellaris/events/colony_events_3.txt:909) · [Deposit](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:879) · [Modifier](E:/SteamLibrary/steamapps/common/Stellaris/common/static_modifiers/00_static_modifiers.txt:500) · [Independent grant](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_grand_archive.txt:608) |
| `seed_bomb_blockers` | Bombardment increments the variable and places a fungoid or plantoid blocker. Clearing either decrements the same variable and handles rewards separately. [Placement](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_5.txt:145) · [Fungoid](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:1821) · [Plantoid](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:1938) |
| `seismic_bombing_var` | Seismic bombardment increments the variable and adds a crater. Vanilla subtracts one when the crater is cleared. [Placement](E:/SteamLibrary/steamapps/common/Stellaris/events/infernals_1_events.txt:200) · [Clearance](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/15_infernals_deposits.txt:192) |
| `pyrolatry_var` | The decision increments the variable and selects one of five blockers. Each clearance handler subtracts one. A separate terraforming event can unset the variable. [Five types](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/14_infernal_decisions.txt:35) · [Blocker definitions](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/15_infernals_deposits.txt:208) · [Reset](E:/SteamLibrary/steamapps/common/Stellaris/events/infernals_1_events.txt:6096) |
| `cd_pods_var` | Normal clearance of the stasis pods advances the separate ancient tunnels feature. Direct removal of the pods preserves this variable. [Pods and tunnels](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/15_infernals_deposits.txt:96) |
