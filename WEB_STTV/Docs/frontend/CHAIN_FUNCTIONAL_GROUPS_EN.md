# Technology chains — functional groups

## Contents

- [Status and purpose](#status-and-purpose)
- [Group definitions](#group-definitions)
- [Technology groups](#technology-groups)
- [Candidate selection](#candidate-selection)
- [Mobile combat ship](#mobile-combat-ship)
- [Planet class change](#planet-class-change)
- [Anti-ship weaponry](#anti-ship-weaponry)
- [Rule boundaries](#rule-boundaries)
- [Related documents](#related-documents)

## Status and purpose

Approved on 2026-11-18 for comparing technology functions without an explicit relation between their unlocked objects. This document continues `parent_tech` design; it does not replace an implementation specification. This iteration changes documentation only.

Following the [order comparison dated 2026-11-19](CHAIN_CRITERIA_ORDER_REVIEW_EN.md), the criterion runs **before direct functional object relations**, after direct upgrades and matching availability conditions if predecessor selection remains ambiguous. In the current database this changes only Juggernaut's anchor from Citadel to Battleships.

The additional “Planet class change” group was approved on 2026-11-19. It extends this criterion without changing its position in the selection order.

## Group definitions

A functional group is defined by rules over game data: object type, fields, values and their combinations. Group definitions and required value lists are configured separately. Rules do not contain predetermined pairs of technology IDs.

A group must have a clear meaning and verifiable assignment criteria. For example, belonging to `ship_sizes` or having a particular `class` alone does not establish membership in the mobile combat ship group.

## Technology groups

1. Find objects directly unlocked by a technology through game requirements, retaining access conditions and relation sources.
2. Check these objects against the configured functional group rules.
3. Obtain the technology's group set as the union of confirmed groups of its unlocked objects.

An object and a technology may belong to multiple groups. Repeated occurrences of a group across objects add no extra set members. Retain the objects and features establishing membership to explain the result.

Insufficient data or no matching rule means membership is unconfirmed. Function is not guessed from a technology's name or ID.

## Candidate selection

For current technology `T` and remaining candidate set `C`:

1. Selection is already complete if a single candidate remains.
2. Determine the functional group sets of `T` and each candidate.
3. Form set `M` of candidates sharing at least one confirmed group with `T`.
4. Select a sole candidate in `M` and finish selection. Pass multiple candidates in `M` to the next criterion.
5. If `M` is empty, skip the criterion and retain the previous set `C`.

The number of shared groups or unlocked objects is not used to pick a winner. Previously discarded candidates are not reintroduced. All original game prerequisites are retained regardless of the selected `parent_tech`.

## Mobile combat ship

The first approved group example uses this combination of features:

- the object belongs to `ship_sizes`;
- `max_speed > 0` after static variable substitution;
- `ship_roles` contains at least one combat role from a list supplied by configuration.

The checked example contains the roles `artillery`, `carrier`, `gunship`. This is not a claim to list all combat roles in the game; the list is a configurable part of the group definition.

| Object | Technology | Speed | `ship_roles` | Basis |
| --- | --- | --- | --- | --- |
| `battleship` | `tech_battleships` | Positive | `artillery`, `carrier`, `gunship` | Mobile hull with combat roles. |
| `juggernaut` | `tech_juggernaut` | Positive | `carrier`, `artillery` | The same combination of features. |
| `starbase_citadel` | `tech_starbase_5` | Zero | Not specified | This group's conditions are not met. |

Stellaris 4.5.4 sources: [battleship](E:/SteamLibrary/steamapps/common/Stellaris/common/ship_sizes/00_ship_sizes.txt:493), [juggernaut](E:/SteamLibrary/steamapps/common/Stellaris/common/ship_sizes/18_juggernauts.txt:1), [citadel](E:/SteamLibrary/steamapps/common/Stellaris/common/ship_sizes/00_starbases.txt:424), [speed value](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_variables/03_scripted_variables_ships.txt:10).

The juggernaut and citadel share `class = shipclass_starbase`, so comparing class alone is insufficient. The group establishes a shared function for the juggernaut and battleship while excluding the citadel from that group. This distinguishes this candidate pair but does not guarantee a unique candidate when other matching technologies are present.

## Planet class change

The group uses these features:

- the object has type `terraform_link` in the `terraform` database;
- its `from` and `to` fields specify different planet classes;
- the object is associated with its unlocking technology through `has_technology` in `condition`, preserving logic and access conditions.

A technology reference under negation does not become a positive unlock. Conditions and alternatives are retained, and sharing a group does not establish transition availability for a particular empire. References in AI weights or localization do not replace requirements in `condition`. The group definition and field paths belong in configuration alongside other groups.

Example checked against the current database and Stellaris 4.5.4 sources:

| Technology | Game tier | Directly unlocked capability | Group confirmed |
| --- | ---: | --- | --- |
| Volcanic Terraforming (`tech_volcanic_terraforming`) | 2 | Transitions from the volcanic planet class to other classes, such as `pc_volcanic` → `pc_tropical`. | Yes |
| Terrestrial Sculpting (`tech_terrestrial_sculpting`) | 2 | Transitions between ordinary classes, such as `pc_continental` → `pc_tropical`. | Yes |
| Deep Crust Engineering (`tech_volcano`) | 2 | Clearing blockers, including `d_active_volcano`; no transitions requiring this technology in `condition` were found. | No |

Comparing the two remaining candidates is expected to yield `tech_volcanic_terraforming.parent_tech = tech_terrestrial_sculpting`: **Terrestrial Sculpting → Volcanic Terraforming**. This follows from a general feature of unlocked objects, not a fixed ID pair in configuration. The number of transitions gives no additional votes.

Both original technology requirements remain mandatory. Selecting an anchor does not cancel the agreed placement of Volcanic Terraforming between the two branches: card positioning is considered separately from `parent_tech`.

Sources: [technology and both requirements](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:2161), [ordinary class transition and its condition](E:/SteamLibrary/steamapps/common/Stellaris/common/terraform/00_basic_terraform_links.txt:8), [transition from the volcanic class and its condition](E:/SteamLibrary/steamapps/common/Stellaris/common/terraform/01_advanced_terraform_links.txt:2224), [blocker and its clearing requirement](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:71). Transition fields are also described in the [object relation dictionary](../semantics/OBJECT_RELATIONS_EN.md#terraforming-transitions).

## Anti-ship weaponry

Approved on 2026-11-19, this group is established by an unlocked weapon component or an object with an action that damages ships through linked events. Its [rule, routes and impact comparison](CHAIN_WEAPONRY_EN.md) are documented separately.

It runs at the same functional group stage. Across the current 679 base technologies, the addition changes only Stellar Cannon: UV Lasers become its sole candidate. The other 678 candidate sets after the criterion stay unchanged. This is an isolated comparison of the addition, not a complete new calculation of all final parents.

## Rule boundaries

- A group is an analytical concept of the reference application, not a new game field or requirement.
- This criterion considers directly unlocked objects. Prerequisite groups are not inherited automatically; [indirect affinity](CHAIN_INDIRECT_AFFINITY_EN.md) is considered by a separate criterion.
- Conditional relations and features retain their conditions. Matching functions does not establish object availability for a particular empire.
- Rules for additional groups and the configuration format remain to be described in the specification. No configuration files are created in this iteration.
- Following the isolated [criterion order swap](CHAIN_CRITERIA_ORDER_REVIEW_EN.md) and [weaponry addition](CHAIN_WEAPONRY_EN.md#impact-comparison) checks, a [complete pass](CHAIN_RULES_FULL_REVIEW_EN.md) of all additions on base technologies found no ambiguities. This does not prove universal classification of every game object. Product code remains unchanged; research calculations are stored separately in the working directory.

## Related documents

- [General chain and sorting rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [Direct functional object relations](CHAIN_DIRECT_RELATIONS_EN.md).
- [Effect and function dictionary](../semantics/FUNCTIONAL_EFFECTS_EN.md).
- [Русская версия](CHAIN_FUNCTIONAL_GROUPS_RU.md).
