# Technology chains — anti-ship weaponry

## Contents

- [Status and purpose](#status-and-purpose)
- [Membership evidence](#membership-evidence)
- [Action and event relations](#action-and-event-relations)
- [Candidate selection](#candidate-selection)
- [Stellar Cannon](#stellar-cannon)
- [Impact comparison](#impact-comparison)
- [Review boundaries](#review-boundaries)
- [Related documents](#related-documents)

## Status and purpose

Approved on 2026-11-19. This document adds the “Anti-ship weaponry” group to the [functional group criterion](CHAIN_FUNCTIONAL_GROUPS_EN.md). It is a predecessor selection design rule; product implementation requires a separate specification. This iteration comprises research verification and documentation updates.

The criterion retains its position: after direct upgrades and matching availability conditions, before direct functional relations, empire filtering and seniority.

## Membership evidence

Either of these two confirmed grounds is sufficient:

1. The technology unlocks a weapon component. The verified form in the current database is an object of type `weapon_component_template`.
2. The technology unlocks an object with a user-accessible action that damages ships through explicitly linked events. In the current example the route ends at a `damage_ship` effect.

Technology-to-object relations come from game requirements. Conditions, alternatives and sources are retained; a reference under negation does not become a positive unlock. Membership represents a capability under its conditions, not guaranteed execution or current availability to a particular empire.

The group definition, accepted object types and field traversal routes belong in configuration. Names, description text, ID similarity, energy cost and AI weights do not replace functional evidence. No technology pairs are assigned manually for this group.

## Action and event relations

For the investigated route:

| Transition | Field and meaning |
| --- | --- |
| Unlocked object → action | `scripted_action` contains an action ID from the `scripted_actions` database. |
| Action → handler | `on_completed` references a definition in the `on_actions` database. |
| Handler → event | `events` contains event IDs; an event in the `events` database is found by its own `id` field. |
| Event → effect | Inspect effects in `immediate`, including already expanded scripted effect calls; `damage_ship` supplies the evidence. |

Retain the complete path, sources and surrounding action/effect conditions. Do not evaluate `amount`, `attacker` arguments or scopes against an invented game state. Stellar Cannon damage depends on variables, and different event branches handle targets differently.

A `damage_ship` occurrence in an arbitrary event without a confirmed route from the unlocked object does not assign the group to a technology. A textual reference in localization is not evidence either. More damage calls do not increase a candidate's weight.

This traverses relations between objects and events. It does not change the depth of [indirect affinity through technology prerequisites](CHAIN_INDIRECT_AFFINITY_EN.md) or require scripted effects to be expanded again: the checked database already contains their expansion inside the event. Other routes must be specified explicitly; no universal traversal of arbitrary references is introduced here.

## Candidate selection

Combine the new group with the technology's other confirmed groups. Then apply the general criterion: retain current candidates sharing at least one group. Keep the previous set if there are no matches; finish selection if one candidate remains. Matching groups and objects are not counted as votes.

Previously discarded candidates are not restored. Game prerequisites, their logic and tiers are retained; only the analytical placement anchor changes.

## Stellar Cannon

| Technology | Game tier | Group evidence |
| --- | ---: | --- |
| Stellar Cannon (`tech_dyson_gun`) | 3 | Megastructure → action → event → damage to ships. |
| UV Lasers (`tech_lasers_3`) | 2 | Unlocks weapon components, such as `SMALL_UV_LASER`. |
| Wormhole Stabilization (`tech_wormhole_stabilization`) | 3 | Membership is not confirmed by the checked routes. |

Confirmed evidence chain: `dyson_gun_1` → `dyson_shoot` → `on_dyson_shoot` → `nomads.8000` → `damage_ship`. The expansion includes scripted firing effects and their conditional branches.

Result: **UV Lasers → Stellar Cannon**, or `tech_dyson_gun.parent_tech = tech_lasers_3`. The tier criterion is no longer evaluated. Wormhole Stabilization remains a mandatory game requirement.

Sources: [technology](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_nomads_dlc_tech.txt:727), [weapon component](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_weapons_energy.txt:281), [megastructure action](E:/SteamLibrary/steamapps/common/Stellaris/common/megastructures/31_dyson_gun.txt:277), [action completion](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_actions/04_dyson_gun.txt:146), [handler](E:/SteamLibrary/steamapps/common/Stellaris/common/on_actions/02_component_on_actions.txt:403), [event](E:/SteamLibrary/steamapps/common/Stellaris/events/nomads_events_1.txt:17273), [damage effect](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/nomads_effects.txt:1251).

## Impact comparison

An isolated comparison was performed on 2026-11-19 using published set `8d7f30af6cc5a9504e6fbb0e2126edae8d18fe9a159f9969e574926ca62b5f01`. Functional groups were compared before and after adding weaponry, with identical first six criteria and unchanged later ordering. Existing mobile combat ship and planet class change groups were included on both sides.

| Measure | Result |
| --- | ---: |
| Base technologies | 679 |
| Have multiple direct prerequisites | 89 |
| Reach the functional group criterion with multiple candidates | 14 |
| Receive the new group through checked forms | 113 |
| Candidate set changes after the criterion | 1 |
| Candidate set stays unchanged after the criterion | 678 |

The only change is Stellar Cannon: previously both candidates remained after groups; now only UV Lasers remain. Later criteria cannot replace the sole candidate. Equal outgoing sets for other technologies imply equal results from unchanged subsequent criteria.

Mega-Engineering also receives the group because it appears in the requirements of higher or restored cannon stages. However, none of its remaining candidates shares this group, so the empty result is skipped. Selection proceeds through the remaining criteria, including the agreed affinity through starbase capacity.

Checked database sizes and SHA-256 values against research projections, common set identity, stopping at one candidate, skipping empty matches and never restoring discarded candidates. The new parent is an original direct prerequisite. Its original prerequisite graph has no path back to Stellar Cannon, so the new edge cannot create a cycle.

Artifacts: [all-technology comparison](../../data/chain_analysis/weapon_review/report.json), [evidence and the expanded linked event body](../../data/chain_analysis/weapon_review/evidence.json), [research calculation](../../data/chain_analysis/weapon_review/compare.py). For events, the set identity, size and SHA-256 of the actual input file are recorded; the entire large database was not loaded into a Python object.

## Review boundaries

- Base technology representations were considered; variant switching, inherited effects and other empire profiles were not checked separately.
- Checked weapon components and the explicit route through `scripted_action`, `on_completed`, `events`, `immediate`. Arbitrary event-to-event calls and other ways to provide actions were not traversed.
- Action routes were inspected in the component, building, hull, starbase module, starbase building and megastructure databases. Four objects with confirmed technology unlocks lead to the same firing event. Objects without such a relation were not assigned to technologies automatically.
- Execution conditions and dynamic damage amounts were not evaluated. Retaining conditional evidence does not prove that every event execution deals damage.
- This checks one group's impact; final totals were not recalculated at that stage. The subsequent [complete pass of all agreed criteria](CHAIN_RULES_FULL_REVIEW_EN.md) is documented separately and confirms Stellar Cannon's parent.
- Product code, published databases and card placement remain unchanged; tree rendering was not tested.

## Related documents

- [General chain rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [Functional groups](CHAIN_FUNCTIONAL_GROUPS_EN.md).
- [Previous criterion order comparison](CHAIN_CRITERIA_ORDER_REVIEW_EN.md).
- [Русская версия](CHAIN_WEAPONRY_RU.md).
