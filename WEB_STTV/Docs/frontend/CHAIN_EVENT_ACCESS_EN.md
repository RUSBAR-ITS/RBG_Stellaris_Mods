# Event-based technology access — preliminary analysis

## Contents

- [Task](#task)
- [Verified examples](#verified-examples)
- [Omega Theory — dependency through prerequisites](#omega-theory--dependency-through-prerequisites)
- [Proposed analysis](#proposed-analysis)
- [Result boundaries](#result-boundaries)

## Task

**Status:** the user deferred event dependency analysis. Current work moves to grid design. The material below is retained for revisiting this task; event links are not included in the layout calculation at this stage.

The user added technology access unlocked by event outcomes to dependency analysis, particularly technologies unavailable through the ordinary research draw. This document records preliminary source inspection and proposals for discussion; it is not an approved implementation specification.

Technology requirements in `prerequisites`, the method of obtaining research access and the placement anchor `parent_tech` must be distinguished. Event-based access can coexist with technology requirements. The proposal is to retain event links separately without replacing the technology parent ID.

## Verified examples

| Technology | Technology definition | Event outcome | Analytical implication |
| --- | --- | --- | --- |
| `tech_lgate_activation` | `weight = 0`, unconditional `weight_modifier.factor = 0`; `potential` excludes an already opened L-Cluster | The `GOOD` option of `distar.10904` executes `add_research_option` when `can_research_technology` passes | Direct research access with the ordinary draw disabled |
| `tech_repeatable_lcluster_clue` | `weight = 70`; `potential` requires `encountered_first_lgate` and the absence of chain completion and cluster opening flags | `distar.13080.immediate` sets `encountered_first_lgate` | An event removes an ordinary draw restriction through a flag; this is a different mechanism |
| `tech_psi_jump_drive_1` | The base definition contains `weight = 0` and `prerequisites = { tech_precognition_interface }` | An option of `utopia.3161` adds research access if neither the technology nor the research option exists; it also adds progress under `delving_ritual` | Event access does not imply an absence of technology prerequisites; access and progress are separate effects |

Sources inspected with read-only access:

- [Both L-Gate technology definitions](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_distant_stars_tech.txt:18).
- [Activation research access](E:/SteamLibrary/steamapps/common/Stellaris/events/distant_stars_events_3.txt:1280).
- [Setting the first encounter flag](E:/SteamLibrary/steamapps/common/Stellaris/events/distant_stars_events_3.txt:2365).
- [Psi drive definition](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:4283).
- [Psi drive research access and conditional progress](E:/SteamLibrary/steamapps/common/Stellaris/events/utopia_shroud_events.txt:3967).

An additional match, `graygoo.32`, also unlocks L-Gate activation but explicitly has `is_test_event = yes` and `trigger = { always = no }`. The mere presence of this effect cannot establish an ordinary gameplay route. [Test event source](E:/SteamLibrary/steamapps/common/Stellaris/events/gray_goo_events.txt:661).

## Omega Theory — dependency through prerequisites

Following the user's additional request, **Omega Theory**, ID `tech_akx_worm_3`, was inspected. It is a tier 3 physics technology: `@horizontechtier` is defined in the [static variables](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_variables/00_scripted_variables.txt:289).

It has `weight = 60` and two mandatory technology prerequisites connected by AND:

| Prerequisite | Ordinary draw | Example event access |
| --- | --- | --- |
| `tech_akx_worm_1` | Base weight 60 is zeroed by a modifier with `factor = 0`, `always = yes` | `akx.9095`, option `OK`: in the `owner` scope, adds 10% progress and the research option if absent and the technology has not been researched |
| `tech_akx_worm_2` | The same unconditional zeroing modifier | `akx.9101`, for example option `akx.9101.a.notspiritual`: in the `owner` scope, adds the research option and 20% progress under the applicable conditions |

The definition of `tech_akx_worm_3` itself has no such zeroing modifier. Its inline script adds a conditional federation multiplier equal to 2. Thus its definition permits ordinary drawing once both technology prerequisites and general research requirements are satisfied. Its event dependency is **indirect, through obtaining the prerequisites**, rather than these events directly unlocking Omega Theory itself.

Special projects were also checked for these routes: `HORIZON_DEBRIS_PROJECT.on_success` invokes `akx.9095`, while `LOOP_TEMPLE_PROJECT.on_success` invokes `akx.9101`. These are examples of existing routes, not an exhaustive list of rewards throughout the story chain.

Sources:

- [Definitions of all three technologies](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_horizonsignal_tech.txt:1).
- [Omega Theory definition](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_horizonsignal_tech.txt:59).
- [Rare technology modifier inline script](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/technologies/rare_technologies_weight_modifiers.txt:1); [federation multiplier](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_variables/00_scripted_variables.txt:382).
- [Debris research reward](E:/SteamLibrary/steamapps/common/Stellaris/events/horizonsignal_events.txt:459); [temple rewards](E:/SteamLibrary/steamapps/common/Stellaris/events/horizonsignal_events.txt:782).
- [Temple project](E:/SteamLibrary/steamapps/common/Stellaris/common/special_projects/00_projects_horizonsignal.txt:28); [debris project](E:/SteamLibrary/steamapps/common/Stellaris/common/special_projects/00_projects_horizonsignal.txt:316).

## Proposed analysis

1. Find research access effects `add_research_option`, technology grants `give_technology` and progress additions `add_tech_progress` in the existing events database. Preserve the distinction: progress alone does not establish either access or research completion.
2. For each effect, retain the event ID, outcome branch path (`immediate`, `option`, `after` and nested constructs), branch conditions, recipient scope and node provenance. An effect in one option or random branch is not an unconditional outcome of the whole event.
3. Match changes to flags and other supported state with checks in technology `potential` and `weight_modifier`. A matching flag name without a matching scope is insufficient; increasing weight is also not equivalent to unlocking access.
4. Determine ordinary draw eligibility separately using the technology definition. Account for the complete weight and condition structure; an event reference or an isolated `weight = 0` occurrence is insufficient to establish exclusively event-based acquisition.
5. Retain every discovered route. Establishing exclusivity requires checking alternative sources and event reachability; leave the conclusion unconfirmed when evidence is insufficient. Mark test events and unconfirmed routes separately.
6. Trace indirect dependencies through the full `prerequisites` graph, preserving AND/OR. AND requires all branches; an event route in only one OR alternative does not establish mandatory event access for the entire technology. Use all requirements rather than only the selected `parent_tech`; distinguish a discovered event route from established necessity of event access.
7. In subsequent chain analysis, consider event access alongside original technology requirements. Markers, separate card groups and layout changes require separate agreement.

The existing technology, event and `on_actions` databases provide starting inputs; expanded effect calls are already present in the tree. Fully tracing event activation may require other sources, such as special project or archaeology site definitions. This preliminary investigation does not establish their coverage.

## Result boundaries

Four examples (the last includes Omega Theory and both its prerequisites) and one test route were inspected in the installed sources. This is not a complete list of event-related technologies. A full database acquisition pass has not been performed, and exclusively event-based technologies have not been counted. In-game execution was not tested.

The previous [complete pass](CHAIN_RULES_FULL_REVIEW_EN.md) establishes unambiguous technology parents for base variants, not a complete analysis of technology acquisition. Event links extend the analytical model while preserving original prerequisites.

Code, databases, parent selection criteria and the frontend were not changed in this iteration.

[Chain rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md) · [Русская версия](CHAIN_EVENT_ACCESS_RU.md).
