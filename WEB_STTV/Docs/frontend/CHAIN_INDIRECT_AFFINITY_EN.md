# Technology chains — indirect functional affinity

## Contents

- [Status and purpose](#status-and-purpose)
- [Search direction and depth](#search-direction-and-depth)
- [Affinity evidence](#affinity-evidence)
- [Candidate selection](#candidate-selection)
- [Armor hardening example](#armor-hardening-example)
- [Rule boundaries](#rule-boundaries)
- [Related documents](#related-documents)

## Status and purpose

Approved on 2026-11-18 as the next criterion after direct functional evidence and groups if no predecessor has been selected. This document records a decision for a future specification; code, configuration, databases and layout are unchanged in this iteration.

The criterion seeks evidence of a candidate's function through its technology prerequisites. A discovered ancestor technology provides evidence; the candidate itself is selected, not that ancestor.

## Search direction and depth

Inputs are the current technology `T`, remaining candidate set `C` and the full original technology requirement graph with its logical structure retained.

For each candidate `P`, search proceeds backward from it to its prerequisites. Depth is configurable; the initial value is **one transition**. A prerequisite `A` in the requirements of `P` is at depth 1. The edge from `T` to candidate `P` itself is not counted in that depth.

The first pass compares objects directly unlocked by `T` with objects directly unlocked by the discovered ancestor `A`. This rule does not introduce an additional traversal of the prerequisites of `T` itself.

Search uses game `prerequisites`, not previously selected `parent_tech` links. Evidence therefore does not depend on current card placement or the candidate's previously selected anchor.

## Affinity evidence

Look for a confirmed match in the specific function or effect of unlocked objects. Interpretation accounts for application context, conditions and effect sign; an identical field name in different contexts is insufficient. Function is not guessed from a technology's name.

Evidence contains:

- candidate `P` and the discovered ancestor `A`;
- the path through original technology requirements and its depth;
- objects confirming the function or effect and their technology links;
- conditional branches and source references.

Logical alternatives and negations are retained. A reference in an `OR` branch does not become a mandatory requirement. Conditional evidence is not declared unconditional. The criterion neither evaluates a particular empire's state nor rewrites original requirements.

## Candidate selection

1. If `C` already contains one candidate, selection is complete.
2. Search for each remaining candidate within the configured depth.
3. Collect set `M` of candidates with a confirmed functional match through an ancestor.
4. Select a sole candidate in `M` and finish selection. Pass multiple candidates in `M` to the next criterion.
5. If `M` is empty, skip the criterion and retain the previous set `C`.

Previously discarded candidates are not reintroduced. The ancestor is not added to the candidate set and does not become `parent_tech` in place of the original candidate. The retained explanation shows the path supporting the selection.

## Armor hardening example

Checked against local Stellaris 4.5.4 files:

| Role | Data |
| --- | --- |
| Current technology `T` | `tech_armor_hardeners_1` unlocks `ARMOR_HARDENER_1`. |
| Effect of the object unlocked by `T` | `ship_modifier.ship_armor_hardening_add = 0.15`. |
| Candidate `P` | `tech_advanced_metallurgy_1` requires `tech_alloys_1` and `tech_ship_armor_2`. |
| Ancestor `A` at depth 1 | `tech_ship_armor_2` unlocks, among other objects, `SMALL_ARMOR_2`. |
| Effect of the object unlocked by `A` | `ship_modifier.ship_armor_hardening_add = 0.01`. |

Both effects are positive and concern the same ship modifier. Their magnitudes differ: functional comparison does not require equal numerical bonuses. This establishes affinity through `tech_ship_armor_2` in support of candidate `tech_advanced_metallurgy_1`.

This path remains in the original requirements even when `tech_alloys_1` is selected as the layout anchor for Ceramo-Metal Alloys itself. Traversing only `parent_tech` would lose the relevant evidence.

Sources: [current technology and its candidates](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2036), [alloy requirements](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:2853), [hardening component](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:250), [armor component](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities.txt:147), [modifier values](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_variables/02_scripted_variables_component_cost.txt:408).

The example explains one piece of evidence; no new full database run or count of remaining ambiguities was performed in this iteration.

## Rule boundaries

- Depth 1 limits the initial search to a candidate's immediate prerequisites. It does not mean automatically inheriting function from every ancestor.
- If there is no evidence within the configured depth, skip the criterion. Search does not deepen automatically to force a unique candidate.
- This traverses technology requirements. Sequential traversal of intermediate objects, actions and events is not automatically covered by this depth limit and requires a separate definition.
- The depth configuration format and supported function and effect comparison rules remain to be specified. No configuration files are created in this iteration.

## Related documents

- [General chain and sorting rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [Functional groups](CHAIN_FUNCTIONAL_GROUPS_EN.md).
- [Direct functional object relations](CHAIN_DIRECT_RELATIONS_EN.md).
- [Effect and function dictionary](../semantics/FUNCTIONAL_EFFECTS_EN.md).
- [Русская версия](CHAIN_INDIRECT_AFFINITY_RU.md).
