# Specification. Event technology acquisition and participants in game conditions

## Contents

- [Scope](#scope)
- [When a technology qualifies](#when-a-technology-qualifies)
- [Distinguishing acquisition paths](#distinguishing-acquisition-paths)
- [Acceptance technologies](#acceptance-technologies)
- [Readable conditions and rewards](#readable-conditions-and-rewards)
- [Acceptance](#acceptance)

## Scope

Approved on 22 November 2026. Two server changes use the same imported Stellaris snapshot. The first refines `event_only` in the reference tree. The second addresses condition and reward wording in the shared technology page and tooltip content. The following rules qualify item 3 of “Events and debris” in the earlier specification. [Tree modes](TZ_REFERENCE_TREE_MODES_EN.md) · [Condition text](TZ_CONDITION_TEXT_EN.md) · [Русская версия](TZ_EVENT_TECHNOLOGIES_AND_SCOPE_TEXT_RU.md)

## When a technology qualifies

The server sets `event_only = true` when all three conditions hold.

1. The base technology has an explicit, unambiguous research `weight = 0`. Its applicable game weight modifiers contain no positive additive term, including conditional terms and terms hidden in the tooltip. Multiplication preserves zero weight. `ai_weight` controls AI choice and is outside this check.
2. At least one path in the full snapshot lets a playable empire unlock **this** research option, receive the researched technology or gain positive research progress. A random reward needs evidence that this technology is eligible. A debris reward requires a confirmed carrier capable of leaving researchable debris.
3. Every independent path to such a reward qualifies as an event, first contact, an anomaly, excavation, rift, situation or special project outcome, or researchable debris, subject to the rules below. A single independent acquisition path in another category keeps the technology visible under this filter.

An ambiguous weight, an unresolved additive term or a material path with unknown acquisition method, recipient or sign of the progress amount keeps the technology visible under this filter and produces a diagnostic. The absence of any confirmed reward also requires a diagnostic. Classify against the full snapshot before applying the user's DLC selection. Evaluate DLC availability separately. [Acquisition audit](TECHNOLOGY_ACQUISITION_RESULTS_EN.md)

## Distinguishing acquisition paths

For each executable reward command, trace its callers backwards. Record **what initiated the chain**, **which action or outcome made the reward available**, and **what the player received**. A single command can have multiple callers. Traverse all reachable branches with their conditions, handle cycles and retain a game source address for each distinct basis. A shared event handler can serve different game mechanics.

| Evidence in the game script | Treatment |
|---|---|
| An empire receives the technology, option or progress as part of its starting setup. The starting effect may delegate the grant to a helper event. | Starting reward. An origin or civic requirement is compatible with this classification. |
| Setup only schedules a future contact, enables a project or starts a situation. The reward requires a separate gameplay outcome such as completing the project, choosing a response or reaching a particular situation outcome. | Event path. Preserve the origin and game start as context for the trigger. |
| An artifact action opens a project. The project outcome awards progress or another research reward. | Event path through the project. If the action also independently awards the technology, include a separate artifact-action path. |
| The reward belongs to another independent mechanic, including a dedicated ascension perk reward chain such as the Colossus Project. | Retain the mechanic's category, including when an event executes the grant. |
| The only evidence is a timer, filename, terminal event type or invocation at game start. | This is insufficient to distinguish a gameplay outcome from delivery of an already assigned reward. Trace the executable conditions and commands. Report material uncertainty. |

Successive stages of a single chain count as one path. When an action has multiple effects, assess each reward separately. For example, a starting effect that both grants progress immediately and starts a project with a future reward for the same technology supplies an independent starting path. A delivery delay alone does not change the category. Exclude branches proven to be exclusive to a non-playable recipient. A variable progress amount is sufficient when every possible value is positive.

Use game definitions and the server's existing reward indexes for classification. The technology IDs below are acceptance examples. Rendered tooltip text, event names and manually tagged technology lists are outside the classifier inputs. [Current classifier](../sttv_server/tree/event_technologies.py)

## Acceptance technologies

| Technology | Expected outcome when available under the DLC selection |
|---|---|
| Materiality Engine (`tech_materiality_engine`) | Event technology. For the Shroud-Forged origin, a situation outcome leads to the Reintegration project. After project success, an event opens the research option. [Project](E:/SteamLibrary/steamapps/common/Stellaris/common/special_projects/00_projects_origins.txt:13) · [Reward](E:/SteamLibrary/steamapps/common/Stellaris/events/shroud_forged_events.txt:214) |
| Frequency Tuning (`tech_space_whale_weapon_1`) | Both paths qualify. Check first contact with the Tiyanki and the Fruitful Partnership origin project separately. The project outcome grants the option and 20% progress, or 60% if the option is already open. [Contact](E:/SteamLibrary/steamapps/common/Stellaris/common/first_contact/01_first_contact_space_fauna_and_NPCs.txt:66) · [Project reward](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_5.txt:78) |
| Irassian Naval Yards (`tech_secrets_irassian`) and the other six precursor secrets technologies | Event technologies. Verify each artifact action, project and positive progress award from the outcome. The Irassian award is 10%. [All seven chains and grant sites](TZ_TECHNOLOGY_ACQUISITION_FIXES_1_EN.md) |
| Mining Drone Lasers | Qualifies under the filter through researchable debris. [Debris audit](TECHNOLOGY_DEBRIS_AUDIT_EN.md) |
| `tech_subspace_drive`, `tech_thrusters_bio_integration`, `tech_colossus` | Visible when allowed by DLC. Verify a conditional starting grant, a starting and later reward for the same technology, and a dedicated ascension perk chain, respectively. [Tree rules](TZ_REFERENCE_TREE_MODES_EN.md) · [Colossus grant](E:/SteamLibrary/steamapps/common/Stellaris/events/apocalypse_events.txt:581) |
| `tech_xeno_linguistics`, `tech_crystal_armor_1` | Visible because the research weight can increase through `add = 100` and `add = 5`, respectively. This includes a modifier hidden in the card text. [Weight controls](TZ_REFERENCE_TREE_MODES_EN.md) |

## Readable conditions and rewards

The server resolves a participant's role at the point of use. Consider the source object type, transitions into nested scopes, explicitly passed targets and the call stack. Apply the same rules to nested conditions, both operands of comparisons, dotted paths, reward recipients and source summaries. For a shared fragment, resolve the participants in each caller's context. The frontend uses the server's wording and RU/EN localization.

| Family from the audit | Requirement and example |
|---|---|
| Existence of `this` | Elide the guard only when that particular participant is known to exist. For the Paradox Titan's `potential`, show “The Machine Age is enabled” and “The empire does not use biological ships”. For a positive call, show “The empire uses biological ships”. Preserve the existence test and the scope of negation for an optional target. [Technology](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_machine_age_tech.txt:250) · [Trigger](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/07_scripted_triggers_ships.txt:33) |
| “Root object of this call”, “Object supplied by the calling script”, “Previous scope object” (`root`, `from`, `prev`), including literal “Root” and “From” | Name the participants. For example, `marauder.101` checks the raiding empire's relations with the empire receiving the event. Distinguish a previous scope inside an expression from an object passed by another event. [Relation check](E:/SteamLibrary/steamapps/common/Stellaris/events/marauder_events.txt:4390) |
| Existence checks for “Leader associated with the object” or “Owner” | Identify who the leader is assigned to or which object must have an owner. For the `site_something_waiting` excavation, leader existence and `scientist` class together mean “An assigned scientist is conducting the excavation”. Retain an explicit check when possession of a leader or owner is itself a condition. [Excavation](E:/SteamLibrary/steamapps/common/Stellaris/common/archaeological_site_types/03_federations_arc_sites.txt:139) |
| “Reward recipient — the empire applying the effect” | Identify who receives the reward in the selected branch, including grants to a different empire. For the Paradox reward, this is the empire reaching Cosmogenesis level four. The summary and expanded details must identify the same recipient for that branch. [Crisis level](E:/SteamLibrary/steamapps/common/Stellaris/common/crisis_levels/00_crisis_levels.txt:455) |
| “Additional condition” heading from `hidden_trigger` | Render its checks under the applicable logical operator. Preserve grouping and negation, including multiple conditions under `OR` or `NOT`. |
| “In-game name” or “in-game value” anywhere in a phrase | Check headings, descriptions, conditions, response options, reward labels and summaries. When the script identifies a participant, use its name or role, for example “First contact with the Tiyanki”. When a name or quantity depends on the campaign, rewrite the whole phrase around the known subject of the action. For a numerical condition, preserve the meaning of the quantity, the operator and the threshold wherever known. [Contact stage](E:/SteamLibrary/steamapps/common/Stellaris/common/first_contact/01_first_contact_space_fauna_and_NPCs.txt:66) |
| “A marker … is still active on the object” | Where setters, checks and any clearers establish the meaning, describe the game state, e.g. “The Irassian homeworld has been found”. Keep the setters accessible in details. For an unresolved case, state what is known about the participant or condition and record the uncertainty with its ID and source address in diagnostics. [Action condition](E:/SteamLibrary/steamapps/common/Stellaris/common/artifact_actions/artifact_actions.txt:568) |

Owner, controller and explorer can be different participants. An unresolved role cannot justify dropping a condition or substituting the player's empire. Transformations preserve the truth of each branch and the sign of a modifier. Group headings take a trailing colon. Game terms use their localized names and existing styles. [Condition simplification](TZ_TOOLTIP_CONDITION_SIMPLIFICATION_EN.md)

## Acceptance

For placeholders embedded in phrases, check the response options on `tech_afterburners_2` and `tech_alien_topography`. In the baseline RU text, the former inserts a generic campaign name into an offer about a star system. The latter uses the generic campaign value twice within one response. Verify that the whole response reads naturally and retains the meaning of the choice. Check RU and EN independently.

1. **Classification.** Compare every technology in the snapshot before and after. Report the IDs that changed with weights, additive terms, paths and reward addresses. For zero-weight technologies, verify conservative handling of unknown paths and distinguish alternatives from stages of one chain. Reproduce the acceptance table. Use fixtures for a shared callee with two sources, a cycle with an exit to a reward, and conditional progress whose sign is unknown.
2. **Tree.** For both all DLC and no DLC, check the four switch combinations and reopen them. The complete settings identify each collection. A rule revision rebuilds stale results for the same settings. Stripes and branch order apply independently of the switch. Between trees differing only in this filter, a DLC-eligible event technology switches `availability` from `true` to `false`. Compare parents, children and RU/EN coordinates in the pair. An ordinary child of a hidden technology retains its position. With Grand Archive enabled, verify the Gravity Snares → Artificial Breeding edge in mixed mode and the separate science areas in ordinary mode. [Display contract](TZ_REFERENCE_TREE_MODES_EN.md)
3. **Text.** Audit every page in both languages, including summaries and expanded sections. The baseline has 679 technologies and 1,358 presentations. Check `exists = this` (125 technologies, including the exact bioship pair on 106), relative scope labels (611), raw quoted roles (107), leader existence (144) and owner existence (282), generic reward actor (117), generic `hidden_trigger` heading (166), campaign name/value placeholders (512 RU and 511 EN), and flags described through a list of setters (638). These groups overlap. For each family, record before/after results, affected IDs and the justification for remaining matches. Resolvable cases must receive meaningful wording in both languages. Repeat earlier checks for missing names, raw keys, empty groups and leaked localization markup.
4. **Semantics and cache.** Compare the original and transformed conditions for positive and negative bioship checks, present and absent optional participants, nested groups and a shared fragment called with two different participants. Verify the sample wording in both the page and card tooltip. Check revision-based refresh of derived tooltips and trees, reopening a ready result and the existing collection reset. Use the same import for comparison.
