# Technology chains — direct functional object relations

## Contents

- [Status and purpose](#status-and-purpose)
- [Relation evidence](#relation-evidence)
- [Conditions and context](#conditions-and-context)
- [Candidate selection](#candidate-selection)
- [Detector example](#detector-example)
- [Boundaries and further design](#boundaries-and-further-design)
- [Related documents](#related-documents)

## Status and purpose

Approved on 2026-11-18 as a kind of functional affinity evidence for selecting `parent_tech`. This records a rule for a future specification; product code, configuration and current layout remain unchanged.

The criterion uses an explicit relation where an object requires or enhances another object. Following the [review dated 2026-11-19](CHAIN_CRITERIA_ORDER_REVIEW_EN.md), it runs **after functional groups** and before indirect affinity. Direct upgrades and matching availability conditions retain higher priority. This refines the initial order: Juggernaut's ship group now selects Battleships before the construction infrastructure relation could select Citadel.

## Relation evidence

For current technology `T` and candidate `P`, evidence consists of three links:

1. `T` unlocks object `B`.
2. Operational use or bonus conditions of object `B` establish that it requires or enhances object `A`.
3. Technology `P` unlocks object `A`.

Object-to-technology links are established by game requirements, such as `prerequisites` or `has_technology` in the relevant access conditions. Displaying an object among technology unlocks alone does not establish a game requirement.

Retain object identifiers, relation type, applicable conditions and references to supporting sources. This explains the selected anchor; it does not add a dependency to game `prerequisites`.

## Conditions and context

- Consider actual construction, access, use and bonus conditions in the context of the relevant object type.
- Preserve alternatives and negations. Conditional evidence is not declared an unconditional requirement. An object prohibition does not become a positive required-object relation.
- Nested checks inside `custom_tooltip` and `hidden_trigger` retain their meaning. Tooltip text parameters and the scalar tooltip form are not required-object references; see the [tooltip dictionary](../semantics/TOOLTIPS_EN.md).
- Resource consumption, costs and mentions in AI weights do not establish this functional relation.
- A matching modifier may explain the function of a discovered relation. It does not by itself replace an explicit object relation under this criterion.

## Candidate selection

Only candidates in the current set `C` are considered. Selection is already complete if a single candidate remains.

Collect set `M` of candidates with a confirmed relation following the scheme above:

| Result | Action |
| --- | --- |
| One candidate in `M` | Select it and finish selection. |
| Multiple candidates in `M` | Pass `M` to the next criterion. |
| Empty `M` | Skip the criterion and retain the previous set `C`. |

Previously discarded candidates are not reintroduced. Original technology requirements and the logical structure of conditions remain unchanged.

## Detector example

Checked against local Stellaris 4.5.4 files:

| Link | Evidence |
| --- | --- |
| `T = tech_dark_matter_detection` unlocks `B = dark_matter_detector` | In `B.potential`, the owner must have `tech_dark_matter_detection`. |
| `B` requires `A = detection_array` or its earlier placement in the construction queue | `B.possible.custom_tooltip` contains an `OR` with `has_starbase_module` and `starbase_buildable_is_in_queue_before`. |
| The detection bonus of `B` applies when `A` is present | `B.triggered_station_modifier.potential` checks `has_starbase_module = detection_array`; the bonus uses `ship_cloaking_detection_add`. |
| `P = tech_detection_array` unlocks `A` | In `A.potential`, the owner must have `tech_detection_array`. |

Sources: [building](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_buildings/00_starbase_buildings.txt:2353), [module](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_modules/00_starbase_modules.txt:282), [technology prerequisites](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_first_contact_tech.txt:340).

The technology also requires `tech_mine_dark_matter`. The building's consumption of `sr_dark_matter` is not an equivalent relation using or enhancing an unlocked object. The prohibition of `dark_matter_listening_post` in the same `possible` block does not mean that the detector requires that building.

The example explains evidence supporting `tech_detection_array`. If an earlier criterion already left one candidate, this step is not run. No new full database run was performed while documenting the rule.

## Boundaries and further design

This criterion describes one explicit relation between unlocked objects. Identifying function without such a link and traversing intermediate object chains are considered separately.

The implementation specification must list supported relation forms and their contexts based on game data. Searching for arbitrary matching IDs inside a tree does not replace that description. An unknown construct does not by itself establish a relation.

## Related documents

- [General chain and sorting rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [Direct object upgrades](CHAIN_DIRECT_UPGRADES_EN.md).
- [Matching availability conditions](CHAIN_AVAILABILITY_EN.md).
- [Object relation dictionary](../semantics/OBJECT_RELATIONS_EN.md).
- [Effect and function dictionary](../semantics/FUNCTIONAL_EFFECTS_EN.md).
- [Русская версия](CHAIN_DIRECT_RELATIONS_RU.md).
