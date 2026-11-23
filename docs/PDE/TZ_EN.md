# PDE 2.0.0 technical specification

## Contents

- [Release scope](#release-scope)
- [Access and target selection](#access-and-target-selection)
- [Catalog and menu](#catalog-and-menu)
- [Instances and planet state](#instances-and-planet-state)
- [Acceptance](#acceptance)

## Release scope

**Approved by the user on 23 November 2026.** Rewrite Planetary Deposits Editor as a standalone cheat editor for vanilla Stellaris 4.5.4. Ship the mod from `PDE/` with version `2.0.0` and `supported_version="v4.5.*"`. Adapt the RB_SDM dynamic menu under PDE names. Game identifiers use the `cdpd_` prefix and events use the `CDPD` namespace. Ship Russian and English localization. [File layout](PROJECT_LAYOUT_EN.md) · [Vanilla dependencies](VANILLA_CHANGES_EN.md)

## Access and target selection

The planetary decision opens the editor **for players only**. Check the initiating country in `from`, set the AI weight to zero and open sessions only for player-controlled empires. Use the standard decisions window within the empire’s borders on an owned colony or an uncolonized body. The vanilla access rule governs foreign colonies, including pre-FTL colonies. Save the target for the acting country’s session. Recheck the target and access before each action. Close the session if the target is lost. [Entry requirements](REQUIREMENTS_EN.md#project-status)

Use the register’s **Where to add** column for placement. On the same eligible body, players see the same IDs regardless of empire type, origin, technology or quest state. Target-specific conditions still apply. For example, `d_irradiated_ruins` requires an existing `irradiated_planet` modifier on a colonizable world other than `pc_ark`. [Per-ID rules and exceptions](DEPOSIT_CLASSIFICATION_EN.md#placement-by-id)

## Catalog and menu

- Provide **529 IDs for placement and 592 for removal**, including 63 removal-only IDs. Treat `d_null_deposit` as a placeholder. Each ID has one catalog entry and appears once per applicable list.
- Use the approved PDE 2.0.3 menu tree. [PDE menu structure](MENU_STRUCTURE_EN.md) Hide a section at any depth when none of its descendants is available. The top-level “Remove deposits” entry opens a flat list of IDs present on the selected body, including vanilla instances and placement exclusions. Hide an empty removal entry.
- Count eligible entries first, then display them in the same order, ten per page. A subsection occupies one slot. Navigation controls sit outside the limit. Recount the list and its ancestors after every action. If the current page disappears, use the last available page. If the section becomes empty, return to an available parent.
- The button references the localized name and full description. For a flagged action, place the red warning first, followed by a blank line, the name and the description. Use separate placement and removal lists and the standard tooltip font size. [Warning register](QUEST_TOOLTIP_WARNINGS_EN.md) · [Button fields](PROJECT_LAYOUT_EN.md#parts-of-a-deposit-button)

## Instances and planet state

**Every one of the 529 placeable IDs supports repeated placement**, including story and unique features. Existing instances on the body do not hide the add button. One click creates one additional instance. The first placement makes one removal entry available for that ID. One removal click selects one instance on the saved body by `is_deposit_type` and applies `remove_deposit = yes` to it. The entry disappears after the last instance. Remove blockers directly, preserving other features on the body and lifting the restriction imposed by the removed instance. [Vanilla single-instance removal](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/07_overlord_decisions.txt:44)

Vanilla determines each instance’s production, jobs, districts, upkeep and conditional bonuses. Some effects depend on the presence of an ID regardless of its instance count. Check effects defined outside the deposit definition as well. Editor actions do not start clearance, special projects or quests, or grant their rewards.

| State | PDE behavior |
| --- | --- |
| `d_titanic_life_blocker` and `titanic_life` | Keep one modifier for any positive number of instances. After removal check surviving instances and other active sources. Remove the modifier with the final dependency, including a vanilla-created pair. On the first placement on a body without dependent deposits, record whether the modifier was already independently active. Before removing it, check whether an independent source still applies. Clear PDE’s tracking after the final instance. Use deposits and verified sources on the body to establish which dependencies remain. The presence of the modifier alone does not identify its source. |
| `seed_bomb_blockers` | Shared by `d_seed_bombing_fungoid_blocker` and `d_seed_bombing_plantoid_blocker`. Account for one contribution per instance across both IDs. |
| `seismic_bombing_var` | Account for one contribution per instance of `d_seismic_bombing_crater`. |
| `pyrolatry_var` | Account for `d_large_volcano`, `d_ash_storms`, `d_charged_atmosphere`, `d_lava_flooding` and `d_toxic_atmosphere` together, including repeated instances of the same ID. |
| Quest progress or state of an independent object | Direct removal of `d_stasis_pods` preserves `cd_pods_var`. Removing `d_spawning_complex_blocker` preserves the overlord holding. Both operations on irradiated ruins preserve the existing irradiation. |

For the three maintenance counters, change only the contribution of the current operation. Unset the variable after its last counted contribution disappears. Direct removal with an initially absent counter must not create a negative value. Isolate the bookkeeping portion of vanilla actions when placing or removing deposits. See [planet state sources](VANILLA_CHANGES_EN.md#planet-state) for grants and clearance callbacks.

## Acceptance

| Check | Expected result |
| --- | --- |
| Catalog and scripts | Compare the implemented catalog IDs with the 4.5.4 snapshot. Verify totals of 529 and 592, matching count and display passes, both action bindings, event paths, RU/EN keys and the warning sets (205 for placement, 84 for removal). |
| Access and empire type | For the same eligible target, a player sees the same list as a regular empire, a hive mind or a machine intelligence. An AI-controlled empire cannot take the decision. |
| Repeat placement | Exercise 0 → 1 → 2 → 1 → 0 with `d_energy_3` on an eligible star and with Project Cornucopia (`d_project_cornucopia`) on an eligible planet. Placement remains available throughout. Check the single removal entry, instance count and effects after each click. |
| Shared effects | Test two Titanic Lifeforms instances, a vanilla pair and a separately active modifier source. For shared counters test duplicate instances, mixed IDs and direct removal when the variable is initially absent. Check that direct removal lifts the selected blocker’s effects without awarding clearance rewards. |
| Menu and tooltips | With 89 eligible entries out of 200 there are nine pages (10 × 8 + 9). Check a deep branch becoming empty, removal of the last ID on the last page and the tooltip text order in both languages. |

Run synthetic checks against the implemented game files. The user verifies decision access in the interface, actual instance counts, bonus recalculation, navigation and tooltips in game. [Detailed verification scenarios](REQUIREMENTS_EN.md#verification-examples)
