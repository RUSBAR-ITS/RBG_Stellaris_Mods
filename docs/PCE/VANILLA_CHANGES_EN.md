# PCE 2.0.0 — vanilla files and functions

## Contents

- [Decision and capacity bonus](#decision-and-capacity-bonus)
- [Feature selection](#feature-selection)
- [Refresh events](#refresh-events)

## Decision and capacity bonus

The target is Stellaris `v4.6.*`. PCE adds its own decision, events and features. Vanilla arkship decisions use `owned_planets_only`. A `carrier_event` accepts a planet or ship. A variable written in colony scope belongs to its carrier. [Arkship decisions](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/15_nomads_dlc_decisions.txt)

The `mult` field in `triggered_planet_modifier` follows `d_cd_ancient_tunnels`. The vanilla arkship feature `d_compact_modules` also applies a local `planet_max_districts_add`. Both features belong to the game. PCE uses `every_deposit` and `remove_deposit = yes` to remove its own instances. [Ancient Tunnels](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/15_infernals_deposits.txt) · [Arkship features](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/17_nomads_deposits.txt)

## Feature selection

When updating for a new game version, check the district sets, the `pc_nanotech` class, the three special colony modifiers and the civic conditions. Knights and pilgrims require the local zone on the arkship or habitat. The Hospitality Servitor condition includes the state of the cruise. The [requirements](REQUIREMENTS_EN.md) give the per-world conditions and references for districts, zones and origins. [Empire types](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt) · [Hospitality Servitors](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/09_scripted_triggers_nomads.txt) · [Special colonies and ecumenopolis conversion](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/02_special_decisions.txt)

## Refresh events

For a colony or its carrier PCE subscribes to `on_planet_class_changed`, `on_terraforming_complete`, `on_decision_enacted`, `on_colony_transfer`, `on_colonized`, `on_zone_complete`, `on_district_demolished`, `on_arkship_encamped`, `on_arkship_mobile`. A second check on the next game day handles vanilla feature cleanup at the end of a conversion. [Game hooks](E:/SteamLibrary/steamapps/common/Stellaris/common/on_actions/00_on_actions.txt)

For country changes PCE uses `on_post_government_changed`, `on_modification_completion`, `on_policy_changed`. It refreshes that country's colonies with a positive index. A daily check tied to each installed PCE feature catches changes in story flags, including the end of the cruise. Removing the bonus retires that instance's check.
