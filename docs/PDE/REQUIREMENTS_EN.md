# PDE deposit editor requirements

## Contents

- [Project status](#project-status)
- [Manual placement rules](#manual-placement-rules)
- [Effects of placement and removal](#effects-of-placement-and-removal)
  - [Required planet modifiers](#required-planet-modifiers)
- [Remove deposits](#remove-deposits)
  - [Direct blocker removal](#direct-blocker-removal)
- [Quest warnings](#quest-warnings)
- [Section visibility and pagination](#section-visibility-and-pagination)
- [Verification examples](#verification-examples)

## Project status

Agreed requirements for rewriting Planetary Deposits Editor (PDE) using RB_SDM. The catalog was checked against vanilla Stellaris 4.5.4. Of 593 unique IDs, the planetary decision offers 529 for placement, another 63 are removal-only, and the `d_null_deposit` placeholder is counted separately. The register records the categories, exclusions and vanilla placement sources. [Deposit classification](DEPOSIT_CLASSIFICATION_EN.md) · [2.0.0 specification](TZ_EN.md)

The PDE 2.0.0 planetary decision is available only to a player-controlled empire. It checks the initiating country (`from = { is_ai = no }`) and sets the AI weight to zero.

The editor uses standard Stellaris decisions on owned colonies and uncolonized bodies within the acting empire’s borders. The decision saves the selected body and opens the menu for the country that enacted it. Vanilla restricts access through the standard window on a foreign colony, including a pre-FTL planet in owned space. [Vanilla rule](E:/SteamLibrary/steamapps/common/Stellaris/common/game_rules/00_rules.txt:4698) · [PDE 2.0.0 layout](PROJECT_LAYOUT_EN.md)

## Manual placement rules

For a generic colonizable-world requirement, `cdpd_is_colonizable_or_colonized` tests `is_colonizable = yes` or `is_colony = yes`. Orbital resource targets must fail both tests. Individual class and climate restrictions still apply.

| Condition | PDE menu rule |
| --- | --- |
| Object type, celestial body class and climate | Preserve the eligible object types and body classes for each ID. Preserve climate restrictions on planets. If climate only increases the generation weight, other eligible classes remain available. If a vanilla script changes the body's class, use its class at the moment the script places the deposit. |
| Orbital deposits | Prohibit placement of every ID in the Orbital branch on a colonizable world, including uncolonized worlds and worlds where a vanilla script can place the same ID. On non-colonizable bodies, the deposit's individual class restrictions still apply. |
| Amounts of a basic orbital resource | Use one eligible body list per resource. On a body eligible for one energy amount, offer every approved `d_energy_*`. Physics has its own list shared by all `d_physics_*` amounts, including +25. Apply the same rule to the other basic orbital series. Use the regular vanilla targets of the resource for manual placement. Record scripted exceptions as source notes without extending the body list. |
| Nebula | A system's position inside or outside a nebula has no bearing on manual placement. |
| Named worlds and systems | Offer the feature on any object of an eligible type, class and climate. A name, a specific system or a flag used solely to identify a unique world does not restrict placement. The register retains the vanilla location. |
| Empire origin and type | On the same eligible body, players see the same deposits for every empire type and origin, including regular empires, hive minds and machine intelligences. After placement, vanilla conditions determine jobs, output and bonuses. |
| Repeated placement | For each of the 529 placeable IDs, the add button remains visible when the eligible body already has instances. Each click adds one instance. The removal menu lists the ID once and removes one instance per click. |
| Empire technologies and events | On an eligible body the placement button is visible and usable regardless of researched technologies or the stage of the associated event or quest, including before it starts. After placement, vanilla determines when the resource can be extracted and when bonuses apply. |
| Irradiated planet | `d_irradiated_ruins` requires a colonizable world with an existing `irradiated_planet` modifier, except `pc_ark`. `d_ancient_battlefield` and `d_ancient_bombardment_craters` accept the same targets or any class in `is_starting_planet_type`. Adding or removing any of the three preserves the original modifier state. |

## Effects of placement and removal

This rule applies to every deposit, including blockers. Placement must activate all effects of the instance that apply under current vanilla conditions. These include output and upkeep, changes to district capacity, jobs and modifiers, including effects defined elsewhere in the game through a deposit presence check. A conditional effect becomes active when its condition is met. The editor must account for effects already applied by the game exactly once.

Placing a deposit through PDE does not start or advance its associated quest, event, anomaly or special project. Independent outcomes of the source script, including story progression flags, rewards, companion deposits and incidental modifiers, fall outside the placement action.

Removal must eliminate the removed instance's entire contribution regardless of how it was placed. Reconcile any modifiers, flags and counters that maintain the deposit's own effects with the remaining instances and other active sources. Removal does not reverse independent outcomes of earlier events. Starting on a body without the deposit or its effects, placing and then removing it restores the active bonuses, penalties and bookkeeping to their starting state if external conditions stay the same.

### Required planet modifiers

For a deposit tied to a specific planet modifier in vanilla, record both IDs and the script that establishes the dependency. Manual placement through PDE applies both the deposit and its required modifier to the planet. If the modifier is already present, reuse the existing instance.

When the last dependent deposit is removed, PDE also removes the modifier, including for pairs originally placed by vanilla. Keep one instance of the modifier while another deposit instance, a different dependent deposit or an independent active source on the planet still sustains it. An event granting both a deposit and a modifier does not by itself establish a dependency.

One verified pair is the Titanic Lifeforms deposit (`d_titanic_life_blocker`) and planet modifier (`titanic_life`). The vanilla script selects planets with the modifier and adds the deposit to them. The deposit grants 8 society research per month and reduces total district capacity by 1. The modifier grants +25% society research from jobs. PDE applies the pair directly. One year after colonization, the game can check this modifier when selecting a colony event. [Placement](E:/SteamLibrary/steamapps/common/Stellaris/events/colony_events_3.txt:909) · [Deposit](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:879) · [Modifier](E:/SteamLibrary/steamapps/common/Stellaris/common/static_modifiers/00_static_modifiers.txt:499) · [Modifier check](E:/SteamLibrary/steamapps/common/Stellaris/events/colony_events_3.txt:980) · [One year after colonization](E:/SteamLibrary/steamapps/common/Stellaris/common/on_actions/00_on_actions.txt:3721)

## Remove deposits

“Remove deposits” is a top-level menu entry. It opens a flat list without categories or subcategories. The list draws on the full catalog of known IDs, including deposits and blockers excluded from manual placement. [Stellaris 4.5.4 catalog](../../TMP/PDE/v4.5.4/deposits.json)

Show an ID in this list if and only if at least one instance is present on the selected celestial body. This covers deposits placed by the vanilla game and by PDE alike. Placement restrictions on object type, class and climate do not apply to removal.

Hide “Remove deposits” when the body has no known deposits. Refresh the list and its pages after removal. Once the last instance of a given ID is gone, its entry disappears. When the list is empty, hide the top-level entry as well.

### Direct blocker removal

PDE removes the selected blocker directly, including blockers that cannot be cleared normally. Removal does not queue a clearing action, start its timer, charge its cost or invoke `on_cleared`. Rewards, new deposits, pops and events granted by clearing do not result from PDE removal.

If the blocker restricted access to an existing feature, verify that its own restriction is lifted. Inspect `on_cleared` for operations that maintain the blocker's own state. For example, removing a blocker with a shared counter must preserve the contribution of other blocker types. Removal when the counter is absent must not create a negative balance.

## Quest warnings

If the deposit ID is listed for the selected action, start the button tooltip with the red warning. Leave a blank line, then show the deposit name with its full description below. For other IDs, start with the deposit name. Placement and removal use separate lists. The warning is keyed to the ID, requires no quest log lookup and leaves the action available. [ID lists and vanilla evidence](QUEST_TOOLTIP_WARNINGS_EN.md)

- **Placement.** “WARNING!!! Adding this deposit will not start its associated quest!”
- **Removal.** “WARNING!!! Removing this deposit may disrupt a quest already in progress!”

Apply `§R…§!` only to the warning. The preferred size for this phrase is 200% of normal tooltip text. Use the normal size unless scaling an individual span in the standard RB_SDM tooltip is verified. [Formatting and verification](QUEST_TOOLTIP_WARNINGS_EN.md#display-rules)

## Section visibility and pagination

The main menu lists Planetary deposits, Orbital deposits, Blockers and Remove deposits in that order. Each section contains either subfolders or deposit actions. [PDE menu structure](MENU_STRUCTURE_EN.md)

Determine availability for the selected object. In placement branches, show a deposit if it can be placed on that object. In the removal menu, availability depends on its presence. Show a section or subcategory if **any of its descendants** is an available deposit. This applies at every depth. A single available deposit keeps its entire path visible. When the last deposit becomes unavailable, hide the entire empty branch.

Paginate each level after filtering. Preserve the author's order among visible entries in the current section. A visible subcategory takes one slot on its parent's page regardless of how many deposits it contains. Hidden entries use no slots and produce no empty pages. [RB_SDM dynamic menu](../../RB_SDM/README_EN.md#what-the-template-does)

## Verification examples

| Scenario | Expected result |
| --- | --- |
| Check the same eligible body and empire under player control and under AI control | The player can take the decision and open the menu. The AI cannot take the decision or start an editor session. |
| Place two instances of Project Cornucopia (`d_project_cornucopia`) on an eligible world, then remove both, one at a time | The instance count follows 0 → 1 → 2 → 1 → 0. Placement stays available at every step. A single removal entry is visible at counts 1 and 2. |
| Arid Highlands (`d_arid_highlands`) on a desert world and an ocean world | The highlands are available on the desert world and hidden on the ocean world. For Dust Caverns (`d_dust_caverns`), dry climate increases generation weight, so climate alone does not disqualify an ocean world. |
| Check `pc_continental` and `pc_nuked` with and without `irradiated_planet`, then `pc_ark` with the modifier | The continental world always offers the battlefield and craters. It offers the ruins only when irradiated. The tomb world offers all three only when irradiated. The arkship hides all three. Adding and removing each deposit preserves the irradiation state. |
| Compare amounts on a G-class star and on a frozen world without the `can_have_physics_deposits` flag. | The star offers all energy and physics amounts, including +10 energy and +25 physics. The frozen world offers all food amounts, including +10. Energy and physics are hidden even though a vanilla script can place +10 energy on a frozen world. |
| Food +3 (`d_food_3`) on a frozen world inside and outside a nebula | The deposit is available in both cases. Ice asteroids and gas giants also qualify. |
| Valley of Zanaam (`d_valley_of_zanaam`) and dark matter +10 (`d_dark_matter_deposit_10`) | The valley can be placed on any Gaia world (`pc_gaia`) and the dark matter deposit on any black hole (`pc_black_hole`), including targets outside their respective named systems. |
| Treasure Vault (`d_treasure_planet`) on eligible colonies belonging to two empires | Both empires see the entry. After placement, vanilla grants 500 jobs to an owner with the Treasure Hunters origin. An owner with another origin receives none of those jobs. |
| Place `d_titanic_life_blocker` on an eligible planet without `titanic_life` and remove it. Separately remove the last instance from a planet where vanilla placed the pair. | Placement applies both IDs and all three effects. In both removal cases, the modifier and all contributions of the pair disappear once the last instance is removed and no other source remains. PDE does not trigger the titan investigation chain. |
| Place a dependent deposit on a planet that already has its required modifier. Remove the deposit while another source still requires that modifier. | The modifier grants its bonus once after placement. It remains active for the other source after removal. |
| Place and then remove Savage Wildlands (`d_savage_wildlands`) on a regular empire's colony. Also remove it from a colony where the Single-Minded anomaly placed it. | Placement grants 200 Biologist jobs and +10% society research from jobs. It does not add the Dangerous Wildlife blocker or the `dangerous_wildlife` modifier. Both removals eliminate the deposit's contribution. On the second colony, the blocker and modifier placed separately by the anomaly remain. [Deposit](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/02_event_planetary_deposits.txt:636) · [Anomaly actions](E:/SteamLibrary/steamapps/common/Stellaris/events/distant_stars_events_2.txt:3677) |
| Place Dust Caverns (`d_dust_caverns`) before researching volatile mote harvesting. Research the technology, then remove the deposit. | Generator district capacity immediately rises by 3. Technicians gain extra mote output once the technology is researched. Removal takes away both contributions of the instance. The empire retains the technology. [Cavern conditions and effects](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_planetary_deposits.txt:1138) |
| Open the menu on a continental world before, during and after the mining automata special project. | The menu offers `d_ancient_mining_site` in all three cases. Its tooltip displays the quest warning. Manual placement preserves the current state of the project. |
| Orbital branch on a colonizable world | The entire branch is hidden both before and after colonization. |
| The body contains only `d_arc_furnace_1`, which is excluded from placement. A neighboring body has `d_minerals_2`. | “Remove deposits” opens a list containing only `d_arc_furnace_1`. Once its last instance is removed, the top-level entry disappears. |
| A colonizable world already has the orbital deposit `d_energy_3`. | “Remove deposits” lists `d_energy_3` even though the Orbital placement branch is hidden. |
| Remove the ruined promenade (`d_star_mall_promenade_blocker`). | The −2 total district cap penalty disappears. The usable promenade (`d_star_mall_promenade`) awarded by normal clearing is not created. [Blocker definition](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/02_event_planetary_deposits.txt:2114) |
| A planet has one fungoid and one plantoid seed bombardment blocker, with the shared `seed_bomb_blockers` counter at 2. Remove the fungoid blocker, then the plantoid blocker. | After the first removal the counter is 1 and the plantoid blocker's contribution remains. After the second, the variable is unset. Neither removal grants clearing rewards or creates pops. [Placement and counter](E:/SteamLibrary/steamapps/common/Stellaris/events/origin_events_5.txt:145) · [Fungoid blocker](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:1817) · [Plantoid blocker](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:1934) |
| Remove `d_spawning_complex_blocker` from a subject planet with an active Splinter Hive holding. | The blocker's −1 total district cap penalty disappears. The holding still supplies its jobs and its link to the overlord's capital. [Blocker](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/08_overlord_deposits.txt:222) · [Holding](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/15_overlord_holdings.txt:584) |
| Two sibling subcategories with just one available deposit, on the third level inside the first subcategory | The deposit and its entire path are visible. The other subcategory is hidden. If that deposit also becomes unavailable, the parent section disappears. |
| At one level, 89 of 200 entries are available with 10 entries per page | The menu shows 9 pages in the original order. The first eight contain 10 entries each and the final page contains 9. |
