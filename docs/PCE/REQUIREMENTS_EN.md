# PCE district capacity requirements

## Contents

- [Counter and deposit](#counter-and-deposit)
- [Main menu wording](#main-menu-wording)
- [Removal submenu and current value](#removal-submenu-and-current-value)
- [Buttons and actions](#buttons-and-actions)
- [Colony types and wording](#colony-types-and-wording)
- [Description selection priorities](#description-selection-priorities)
- [Combinations for feature names](#combinations-for-feature-names)
- [Continental World](#continental-world)
- [Volcanic World](#volcanic-world)
- [Ecumenopolis](#ecumenopolis)
- [Hive World](#hive-world)
- [Machine World](#machine-world)
- [Nanite World](#nanite-world)
- [Orbital Habitat](#orbital-habitat)
- [Intact Ring Segment](#intact-ring-segment)
- [Synaptic Lathe](#synaptic-lathe)
- [Arkship](#arkship)
- [Resort Worlds, Penal Colonies and Thrall-Worlds](#resort-worlds-penal-colonies-and-thrall-worlds)
- [Updating after a colony changes](#updating-after-a-colony-changes)
- [Verification example](#verification-example)

## Counter and deposit

PCE stores a separate integer counter, `pce_extra_districts`, on each planet or arkship. It records how much PCE adds to that body's district limit. PCE 2.0.0 defines one deposit type for each of the 49 agreed variants. All types read the same variable on the selected body. The first expansion creates one instance of the applicable type. Subsequent expansions add the selected amount to the counter on the same body.

The deposit grants `planet_max_districts_add = 1`, scaled by `mult = pce_extra_districts` in a `triggered_planet_modifier` block. The Ancient Tunnels deposit uses this pattern in Stellaris 4.6.0. [Vanilla example](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/15_infernals_deposits.txt:123)

## Main menu wording

`X` stands for the current `pce_extra_districts` value on the selected body. The examples show a positive index. At zero, each menu shows only the increase button and Exit.

**Planet**

```text
Welcome to the Planetary Infrastructure Planning Center.
The colony master plan is open for revision.

Current planetary capacity index: X
The index changes immediately. The new district limit takes effect within a few in-game days.

Increase planetary capacity index
Decrease planetary capacity index
Exit
```

**Arkship**

```text
Welcome to the Arkship Infrastructure Planning Center.
The deck plan is on screen.

Current arkship capacity index: X
The index changes immediately. The new district limit takes effect within a few in-game days.

Increase arkship capacity index
Decrease arkship capacity index
Exit
```

## Removal submenu and current value

A dedicated submenu lets the player choose how much extra district capacity to remove. The maximum removable amount equals the selected body's current `pce_extra_districts`, regardless of how many districts have been built. Partial removal keeps the deposit and reduces its bonus by the chosen amount. The last option removes the entire bonus remaining at the time of the click. When the amount reaches zero, PCE removes its deposit from the selected body and clears the counter.

When opened and after each operation, the menu shows the selected body's current capacity index (`pce_extra_districts`), including zero. The action tooltips refer to its gameplay effect as the “District capacity bonus”.

The main menu is built dynamically for the selected planet or arkship. Increase capacity index and Exit are available at every index value. The decrease option appears when `pce_extra_districts > 0`. Its submenu lists all integer amounts from 1 through `min(10, pce_extra_districts)` in ascending order, followed by “Remove all”. For example, an index of 3 offers 1, 2, 3 and “Remove all”. An index of 12 offers 1–10 and “Remove all”, which removes all 12. After an operation, the menu determines the available options from the updated value.

## Buttons and actions

1. Define the amount buttons with an `inline_script` template. Each button passes its selected quantity as the `AMOUNT` parameter. A shared `scripted_effect` applies the increase or reduction to the selected body.
2. Use `carrier_event` screens for planets and arkships. The current screen determines the menu section, and the button supplies the requested amount. The deposit and its capacity counter are sufficient persistent state.
3. At the time of the click, check that the player who opened the editor still owns the colony. For removal, read the current counter and check the available amount. “Remove all” uses the entire current balance.
4. Use one parameterized tooltip per operation and language for the amount buttons. The tooltip and the action read the same amount parameter. The tooltip shows the current and resulting bonus. At an index of 10, the `+3` tooltip reads “District capacity bonus will increase from 10 to 13”. For `−3` it reads “District capacity bonus will decrease from 10 to 7”. For “Remove all”, the resulting bonus is 0. The values in these tooltips are filled in for the selected body.

## Colony types and wording

PCE feature icons follow the science-fiction art direction of Stellaris and may depict far-future technology. For the Wilderness, the biosphere itself conveys the scale of development. Each feature should have a recognizable silhouette when its 98 × 75 pixel texture is scaled down in the planet's feature list. [Scale in the planet interface](E:/SteamLibrary/steamapps/common/Stellaris/interface/planet_view.gui:5976)

All three interface illustrations for version 2.0.0 show an icy blue outline of a planned tier above the warm lights of occupied levels.

- **New Tier decision icon, 45 × 45.** Two occupied floors with amber window bands share a foundation. The blue outline of the third floor appears above them. The silhouette should read against the game interface. [Source artwork](artwork/interface/pce_decision_new_tier.png)
- **City Above the City Workshop cover, 1254 × 1254.** Two construction arms lower a span onto piers marked by the blue outline. A train passes underneath the inhabited upper street. The title Planetary Capacity Extender occupies the upper quarter. [Source artwork](artwork/interface/pce_workshop_city_above_the_city.png)
- **Planning Center menu illustration, 450 × 150.** A long table holds a scale model in section. A blue projection of the new district rises above occupied tiers and an illuminated transit line. The enclosed hall suits both a planet and an arkship. [Source artwork](artwork/interface/pce_menu_planning_center.png)

Ocean (`pc_ocean`), Gaia (`pc_gaia`) and Tomb (`pc_nuked`) Worlds with the `standard` district set use the base deposit and description for their owner’s civilization type. For example, a regular empire with no special colony status gets Multilevel Cities on all three.

Wilderness colonies have their own wording about the growth of a single organism. The agreed direction for a dedicated illustration is a cross section of the living biosphere. An empire with this origin can colonize different planet classes. [Wilderness districts](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/05_wilderness_districts.txt:21)

## Description selection priorities

PCE selects the capacity feature name and description using the colony's **district set** (`district_set`) and the **civilization type of its current owner**. The set determines which infrastructure can be expanded. The civilization type determines who uses it and can change which districts are available within the set. Use these properties together with the world class and special colony conditions to select the deposit type to place. Each type specifies its name, description and icon. All variants use the same calculation for the overall district limit.

Use the following working order for civilizations. The third column gives the base housing district on an ordinary Ocean World colony with the `standard` set and no special conditions. The in-game name of a district can vary with capital status and zones.

| Priority | Civilization type | Base housing district on an Ocean World |
|---|---|---|
| 1 | Wilderness (`is_wilderness_empire`) | Communal Biome (`district_craglands`). The PCE text describes a single organism growing new layers. |
| 2 | Hive Mind (`is_hive_empire` after checking the origin) | Hive Cluster (`district_hive`). The hive fits drone chambers and passages closer together. |
| 3 | Machine Intelligence (`is_machine_empire`) | Central Nexus (`district_nexus`). The intelligence reorganizes drone servicing nodes. |
| 4 | Individualistic machines (`is_individual_machine`) | City District (`district_city`). The text describes machine inhabitants and their infrastructure. |
| 5 | Ordinary empire | City District (`district_city`). The text reflects the environment on the planet. |

Wilderness also passes the vanilla Hive Mind check. Individualistic machines pass the ordinary non-gestalt empire check for the City District. For a non-gestalt empire that has undergone synthetic ascension, retain the proposed machine wording. After the three specialized owners and individualistic machines have been checked, `is_synthetic_empire` can select this wording. Use the synthetic variant listed for the applicable world. [Authority and origin](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:1859) · [Individualistic machines](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/02_scripted_triggers_machine_age.txt:63) · [Synthetic empires](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:1335) · [City District](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:32)

World class refines the selection where a distinct deposit type applies. For example, a habitable Nanite World and a Machine World share the `machine_world` district set and use different PCE features. With all other conditions equal, the colony’s species mix has no bearing on this choice.

## Combinations for feature names

The 24 classes with `colonizable = yes` in Stellaris 4.6.0 have ten district sets. Cross each row with the civilization types in the preceding table.

| District set | Where it occurs |
|---|---|
| `standard` | Nine basic climate classes including Ocean, plus Gaia, Tomb, and Relic Worlds |
| `volcanic_world` | Volcanic World |
| `city_world` | Ecumenopolis |
| `hive_world` | Hive World |
| `machine_world` | Machine World and colonizable Nanite World (`pc_nanotech`) |
| `habitat` | Orbital Habitat and classes `pc_crystal_habitat`, `pc_warden_guardian` |
| `ring_world` | Intact habitable ring segment |
| `shattered_ring_world` | Shattered habitable ring segment |
| `nomad` | Arkship |
| `cosmogenesis_world` | Synaptic Lathe |

The set can change the base district for the same owner. An intact ring segment offers `district_rw_hive` to a Hive Mind. On a shattered segment the hive can use `district_hive`. Different owners can also share a district. An arkship has `district_ark_city`, and the capacity text can describe the decks in terms appropriate to their owner. [Intact segment](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/04_ringworld_districts.txt:216) · [Shattered segment](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:1055) · [Arkship](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/07_ark_districts.txt:26)

Account for a colony's special status when it changes the districts mentioned. A continental resort keeps the `standard` set, while the `resort_colony` modifier enables resort districts. Penal and thrall colonies also warrant this check. An origin can matter within a specific set. On an arkship, `origin_forever_cruise` enables a special district while the owner lacks the `forever_cruise_over` flag. [Special colonies](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:3238) · [Resort district](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:376) · [Special arkship district](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/07_ark_districts.txt:609)

The ten district sets and three special colony statuses are covered by 49 deposit types. They use 48 approved illustrations, 48 distinct descriptions and 43 distinct names per language. Galleries of the Order has separate habitat and arkship deposit types that share a name, description and icon. Four Continental World names recur on Volcanic Worlds with different descriptions. Modular Quarters also appears on Orbital Habitats.

For colonies with the `standard` set, the Continental World table gives the base deposit for each owner. An active special colony status takes precedence. [Climate world requirements](#colony-types-and-wording) · [Continental World texts](#continental-world)

## Continental World

The five names and descriptions below are approved for a colonized `pc_continental` with the `standard` district set, before any special colony status applies. Every variant adds the selected amount to the overall district limit. The vanilla housing district provides a reference for the description. [Planet class](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt:233)

| Owner civilization | Base housing district | PCE feature name | How space is made for additional districts |
|---|---|---|---|
| Ordinary empire | `district_city` | Multilevel Cities | New tiers rise above the rooftops of established neighborhoods, each with streets and squares of its own. Homes and workshops line the elevated roads, with lifts connecting them to the neighborhoods below. |
| Hive Mind | `district_hive` | Tiered Nests | Above the vaulted nest, drones build another tier of storerooms and brood chambers. Wide passages connect it to the heart of the hive. Workers are already carrying food up for the first brood. |
| Individualistic machines | `district_city` | Modular Quarters | Residents add modules above their workshops to recharge, make repairs, and store spare chassis. Standard fittings let neighbors link their buildings with walkways. Gradually, another neighborhood takes shape overhead. |
| Machine Intelligence | `district_nexus` | Distributed Nodes | Drones assemble new floors of production lines and repair bays around the coordination nodes. As each floor comes online, the machine intelligence routes parts to it and assigns drones to their stations. |
| Wilderness | `district_craglands` | Biosphere Layers | In the canopy of mature groves, branches intertwine and soil collects. New gardens take root high above the ground. Symbionts cross living bridges to colonize them, while the spreading roots nourish both layers. |

Start with a regular empire, one feature on a Continental World and `pce_extra_districts = 10`. Terraforming to an Ocean World retains the same Multilevel Cities type. A transition to a Volcanic World selects the volcanic type with the same name and its own description and icon. Completing the Arcology Project selects the ecumenopolis type. After each transition, the colony should have one matching deposit granting +10. [Ocean World](E:/SteamLibrary/steamapps/common/Stellaris/common/terraform/00_basic_terraform_links.txt:47) · [Volcanic World](E:/SteamLibrary/steamapps/common/Stellaris/common/terraform/01_advanced_terraform_links.txt:2611) · [Arcology Project](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/02_special_decisions.txt:1019)

For a Continental World with a special status, see the selection rules for [Resort Worlds, Penal Colonies and Thrall-Worlds](#resort-worlds-penal-colonies-and-thrall-worlds).

## Volcanic World

In Stellaris 4.6.0 the habitable Volcanic World (`pc_volcanic`) uses the `volcanic_world` district set. Its three characteristic districts are the Geothermal Power Plant, Magma Conduit, and Thermotechnic Forum. In all three definitions, `potential` checks the district set. The forum takes its display name from its owner. Ordinary empires and individualistic machines see Auxiliary Centers, Hive Minds see Synaptic Clusters, and Machine Intelligences see Auxiliary Hubs. [Planet class](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt:430) · [Geothermal Power Plant](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/02_rural_districts.txt:445) · [Magma Conduit](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/02_rural_districts.txt:544) · [Forum and display names](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/02_rural_districts.txt:665) · [English names](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/infernals_l_english.yml:47)

In empire creation, the `INF` species class unlocks the Volcanic World homeworld choice. The Thermophile trait adds 20 percentage points to volcanic habitability and raises the habitability floor on such worlds by 50 percentage points. Lithoids receive a general 50-point habitability bonus. Their archetype is eligible for Volcanic Preference. For example, the `origin_red_giant` origin assigns a volcanic starting world and allows Lithoids. On an established colony, each civilization type has its own description. [Infernal species class](E:/SteamLibrary/steamapps/common/Stellaris/common/species_classes/01_base_species_classes.txt:350) · [Thermophile trait](E:/SteamLibrary/steamapps/common/Stellaris/common/traits/16_infernals_traits.txt:62) · [Lithoid trait](E:/SteamLibrary/steamapps/common/Stellaris/common/traits/02_species_traits_basic_characteristics.txt:335) · [Volcanic Preference](E:/SteamLibrary/steamapps/common/Stellaris/common/traits/01_species_traits_habitability.txt:281) · [Origin conditions](E:/SteamLibrary/steamapps/common/Stellaris/common/governments/civics/00_origins.txt:327)

For Wilderness pops, `species_can_live_on_planet` requires a suitable world, and `is_habitable_for_wilderness` explicitly excludes `pc_volcanic`. The Communal Biome requires the `standard` set. This leaves four variants for ordinary volcanic colonies. The habitability rule applies to Wilderness pops. An ordinary Hive Mind can build Hive Clusters on this world. [Population rule](E:/SteamLibrary/steamapps/common/Stellaris/common/game_rules/00_rules.txt:287) · [Wilderness habitability](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/05_scripted_triggers_biogenesis.txt:709) · [Communal Biome](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/05_wilderness_districts.txt:20) · [Hive Cluster](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:1055)

When a colony becomes a Volcanic World, select the volcanic deposit type with the same name and its own description and icon. All four names and descriptions in the table are approved.

| Owner civilization | PCE feature name | Description |
|---|---|---|
| Ordinary empire | Multilevel Cities | Houses rise in terraces on either side of a lava channel. Builders span the gap with broad bridges above the rooftops. In time the bridges become streets, uniting the neighborhoods on both slopes in a single intricate work of architecture and engineering. |
| Hive Mind | Tiered Nests | Scout drones find another tier of lava tubes above the nest. Builders follow, shoring up the vaults, lining warm niches for the brood, and cutting passages to the chambers below. |
| Individualistic machines | Modular Quarters | Workshop owners assemble new living modules on their upper decks. Neighbors link them with walkways and run a shared power cable from the nearest geothermal plant. Soon the new tier has workshops of its own. |
| Machine Intelligence | Distributed Nodes | Above the geothermal wells, drones stack assembly floors and connect each one to the power grid. While production runs on one floor, a lift in the next shaft is already hauling deck sections up for the next. |

## Ecumenopolis

The Ecumenopolis (`pc_city`) uses the `city_world` district set. In Stellaris 4.6.0 ordinary non-gestalt empires, including individualistic machines, and Machine Intelligences with the Rogue Servitor civic can qualify for the Arcology Project. The usual route requires MegaCorp. The `civic_megacity_architects` and `civic_megacity_architects_corporate` civics open another route to the perk. Restoring an ecumenopolis on a Relic World has its own decision. It checks the owner (a non-gestalt empire or a Rogue Servitor), `tech_housing_2`, and blocker clearance. Restoration does not require the ascension perk. [Planet class](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/02_planet_classes_megacorp.txt:40) · [Ascension perk](E:/SteamLibrary/steamapps/common/Stellaris/common/ascension_perks/00_ascension_perks.txt:2538) · [Eligible civics](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/10_scripted_triggers_forceofwill.txt:33) · [Restoration decision](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/02_special_decisions.txt:1084)

PCE uses the current owner of the established colony. An ordinary Hive Mind or a Machine Intelligence without the servitor civic can acquire an existing ecumenopolis, for example by conquest. The Residential Arcology and the three towers available for specialization check the colony's district set. The Residential Arcology has an exception for a capital with `menp_behemoth_mind_meld`. Wilderness is outside the ordinary set of owners. For its pops, `species_can_live_on_planet` checks a habitability trigger that explicitly excludes `pc_city`. [Existing Fallen Empire ecumenopolis](E:/SteamLibrary/steamapps/common/Stellaris/common/solar_system_initializers/fallen_empire_initializers.txt:36) · [Residential Arcology](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/01_arcology_districts.txt:19) · [Towers](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/01_arcology_districts.txt:163) · [Population rule](E:/SteamLibrary/steamapps/common/Stellaris/common/game_rules/00_rules.txt:287) · [Wilderness habitability](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/05_scripted_triggers_biogenesis.txt:709)

All five feature names and descriptions are approved, including the Rogue Servitor variant for Machine Intelligence. A Rogue Servitor can choose the Organic Habitation specialization. The active servitor civic selects the PCE text. The player chooses the actual tower specializations. When the colony becomes an ecumenopolis, use the PCE deposit type for an ecumenopolis and carry over its existing capacity bonus. [Arcology specialization](E:/SteamLibrary/steamapps/common/Stellaris/common/zones/04_secondary_zones.txt:256) · [Civic requirement](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/zones/shared_unity_bio_trophy_zone.txt:3) · [English name](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/main_3_l_english.yml:5459)

| Owner | PCE feature name | Description |
|---|---|---|
| Ordinary empire | The Upper City | The roofs of old arcologies become the foundations of new neighborhoods. Express trains run between the tower tops. Homes, shops, and small parks spring up around their stations, high above the streets of the old city. |
| Individualistic machines | Modular Arcologies | On the upper floors of the arcologies, each machine fits out a workshop to suit its own chassis. Behind one door there is room to swing a heavy manipulator. Behind another, the owner assembles delicate components under a magnifying lens. A common freight gallery serves the workshops along the entire tier. |
| Hive Mind | Nest Towers | Drones build vaulted brood chambers above the arcology rooftops. In the old lift shafts they fashion spiral passages and carry the brood up from the depths of the towers to the new nests. |
| Machine Intelligence | Assembly Towers | Drones anchor new assembly floors to the load-bearing columns of the arcologies. Each chassis travels upward as it takes shape. The finished machine rolls off the topmost line straight onto a transit platform. |
| Rogue Servitor | Garden Arcologies | On the tower roofs, servitors lay out gardens and build homes for their wards. An entire service tier runs beneath the promenades. Long before dawn, drones travel its corridors to deliver everything the residents have ordered for the morning. |

In the game, compare the same ecumenopolis before and after a transfer to an ordinary Hive Mind or a Machine Intelligence. Also compare a Rogue Servitor colony with and without an Organic Habitation zone. With an initial +10 capacity, every ownership transfer should leave one deposit worth +10 with the current owner's text.

## Hive World

In Stellaris 4.6.0 the Hive World (`pc_hive`) uses the `hive_world` district set. Its usual owner is a Hive Mind. The Hive Worlds perk requires Climate Restoration and excludes Wilderness, nomads, and Lithoid Devouring Swarms. These conditions govern the perk. A hive can also acquire an existing Hive World through conquest. Other creation paths include the mutation event for an Evolutionary Predators hive. How the hive obtained the world does not affect the PCE description. [Planet class](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt:729) · [Ascension perk](E:/SteamLibrary/steamapps/common/Stellaris/common/ascension_perks/00_ascension_perks.txt:2495) · [Existing Hive World](E:/SteamLibrary/steamapps/common/Stellaris/common/solar_system_initializers/fallen_empire_initializers.txt:4180) · [Mutation choice](E:/SteamLibrary/steamapps/common/Stellaris/events/biogenesis_events.txt:3566) · [Terraforming event](E:/SteamLibrary/steamapps/common/Stellaris/events/biogenesis_origin_events.txt:1690)

Vanilla allows pops with `trait_hive_mind` to live on `pc_hive`. For a Necrophage Hive Mind it also admits species eligible for conversion. Wilderness pops face a separate check that explicitly excludes `pc_hive`. A Machine Intelligence's own drones do not qualify by virtue of being machines. The usual housing district for a hive colony is the Hive Cluster. The `hive_world` set also has three clusters available for specialization (`district_hive_1/2/3`). [Population rule](E:/SteamLibrary/steamapps/common/Stellaris/common/game_rules/00_rules.txt:254) · [Wilderness](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/05_scripted_triggers_biogenesis.txt:709) · [Housing district](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:1055) · [Specializable clusters](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:1176)

An acquired, inhabited colony supports another case. With BioGenesis, a playable non-gestalt empire, including individualistic machines, can retain local disconnected drones under suitable species rights. Those drones retain the trait that allows them to live on a Hive World. Vanilla excludes them from the species their new owner can grant colonization rights. Both descriptions in the table are approved. Non-gestalt owners share the Reclaimed Galleries description while the resident drones remain. [Disconnected drone trigger](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:1063) · [Species rights](E:/SteamLibrary/steamapps/common/Stellaris/common/species_rights/citizenship_types/00_citizenship_types_biogenesis.txt:1) · [Colonization restriction](E:/SteamLibrary/steamapps/common/Stellaris/common/species_rights/colonization_controls/00_species_controls_colonization.txt:79)

| Owner | PCE feature name | Description |
|---|---|---|
| Hive Mind | Deep Hive Cells | Beneath the inhabited nests, layers of living tissue slowly draw apart. While the walls are still soft, drones widen the cavities and cut passages between neighboring chambers. By the time the vaults harden, vessels pulse within them, nourishing an entire tier. |
| Non-gestalt empire with surviving drones | Reclaimed Galleries | Deep in the old nest, sealed chambers survive. Doors in the living walls still open at a drone's touch. Freight tracks follow the newly opened passages as another tier comes back into use. |

After terraforming a colony into `pc_hive`, check the result after vanilla event `action.68` has run. It removes deposits outside the Hive World exception list. With the same owner and an initial +10, the colony should retain one deposit of the appropriate Hive World type granting +10. A zero counter needs no restoration. A second in-game scenario is the transfer of an inhabited world to a non-gestalt empire with BioGenesis and suitable rights for its surviving drones. Check that the colony persists, the second description appears, and the capacity bonus survives. [Terraforming completion](E:/SteamLibrary/steamapps/common/Stellaris/common/on_actions/00_on_actions.txt:2173) · [Hive World deposit cleanup](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:6942)

## Machine World

In Stellaris 4.6.0 the Machine World (`pc_machine`) uses the `machine_world` district set. The habitable Nanite World (`pc_nanotech`) shares the set and has its own planet class. The descriptions below are approved for `pc_machine`. A Machine Intelligence can terraform a suitable planet with the Machine Worlds perk or start on one with the Resource Consolidation origin. The perk requires a non-nomadic Machine Intelligence. The origin has additional restrictions and excludes Rogue Servitors. [Planet class](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt:773) · [Nanite World](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt:1030) · [Ascension perk](E:/SteamLibrary/steamapps/common/Stellaris/common/ascension_perks/00_ascension_perks.txt:2460) · [Origin](E:/SteamLibrary/steamapps/common/Stellaris/common/governments/civics/00_origins.txt:2650)

For an established colony, use the current owner. Machines, robots, cyborgs, and species with one of the three positive cybernetic traits from Hard Reset pass the Machine World residence check. Possible owners therefore include ordinary empires with suitable residents, individualistic machines, and Hive Minds with suitable drones, such as cyborgs. A separate rule excludes Wilderness pops. Depending on the owner, the usual housing district is the City District, Hive Cluster, or Central Nexus. The district set supplies the three additional nexuses available for specialization (`district_nexus_1`, `district_nexus_2`, `district_nexus_3`). [Residence rule](E:/SteamLibrary/steamapps/common/Stellaris/common/game_rules/00_rules.txt:240) · [Hard Reset traits](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/05_scripted_triggers_traits.txt:557) · [Cybernetic hive path](E:/SteamLibrary/steamapps/common/Stellaris/common/ascension_perks/00_ascension_paths.txt:226) · [Wilderness](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/05_scripted_triggers_biogenesis.txt:709) · [City District](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:32) · [Hive Cluster](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:1055) · [Central and specialized nexuses](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:1479)

All five names and descriptions are approved. Within Machine Intelligence, the active Rogue Servitor civic selects a dedicated text. Vanilla gives this owner the Organic Habitation specialization. The text also fits a colony where the servitor is still preparing the quarters. The player chooses the specialization, and bio-trophies must meet the usual residence rule. A Driven Assimilator uses the general Machine Intelligence text. A non-gestalt empire that has undergone synthetic ascension uses the individualistic machine text under the existing selection priorities. [Nexus specialization](E:/SteamLibrary/steamapps/common/Stellaris/common/zones/04_secondary_zones.txt:820) · [Servitor civic check](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/zones/shared_unity_bio_trophy_zone.txt:3) · [Bio-trophy rights](E:/SteamLibrary/steamapps/common/Stellaris/common/species_rights/citizenship_types/00_citizenship_types.txt:548)

| Owner | PCE feature name | Description |
|---|---|---|
| Machine Intelligence | Layers of the Planetary Machine | Beneath the freight main line, drones assemble a new belt of workshops. Lifts link it to the foundries on the surface. A casting can now descend for machining and return to the assembly yards thousands of kilometers from the furnace that poured it. |
| Rogue Servitor | Quiet Decks | Above the freight tracks, servitors suspend residential decks on shock absorbers. Before signing off on a deck, a drone places a glass of water on a bedside table and waits for a heavy train to pass below. If the water stays still, the rooms are ready for their occupants. |
| Individualistic machines | Artisans’ Quarters | On either side of the freight line, machines cut workshop doors into the planet’s outer shell. One owner needs a tall bay for a bridge crane. The neighbor fits three working floors into the same height. Both loading platforms meet the same track. |
| Ordinary non-gestalt empire with suitable residents | Habitation Sections | The old cable galleries beneath the surface are wide enough to carry a passenger line. Homes occupy the upper decks of the adjoining machine halls. The old freight platforms serve as stations for the new neighborhoods. |
| Hive Mind with suitable drones | Heat Exchanger Nests | The hive spreads into deep shafts that carry heat away from the planetary machinery. Drones fasten brood chambers along the warm pipes. Wide passages between tiers let them carry the brood to the temperatures it needs as it grows. |

After terraforming a Continental World with +10 capacity under the same owner, expect one deposit of the applicable `pc_machine` type granting +10. Check after `action.68` runs. The Machine World branch respects the `keep_deposit_on_terraform` deposit flag. Its population cleanup checks three traits (`trait_machine_unit`, `trait_mechanical`, `trait_cybernetic`). The Hard Reset exception is part of the residence rule for an existing world. In game, also check an ownership transfer and a Rogue Servitor with and without Organic Habitation. [Continental World conversion](E:/SteamLibrary/steamapps/common/Stellaris/common/terraform/02_special_terraform_links.txt:2136) · [Deposit cleanup](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:6856) · [Population cleanup](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:6892)

## Nanite World

In Stellaris 4.6.0 a habitable `pc_nanotech` world can arise when an empire subsumes a suitable colony. The class has `spawn_odds = 0`, and no direct placement of this class was found in vanilla system initializers. Nanite planets in the L-Cluster use `pc_gray_goo`, which has `colonizable = no`. Both display the name “Nanite World” because the `pc_nanotech` localization key references `pc_gray_goo`. The habitable class has its own description of a sea of nanites in constant flux. [Habitable class](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt:1030) · [Uninhabitable class](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes_distant_stars.txt:2) · [L-Cluster planet](E:/SteamLibrary/steamapps/common/Stellaris/common/solar_system_initializers/distant_stars_initializers.txt:4207) · [English localization](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/machine_age_l_english.yml:3189)

In The Machine Age, Machine Intelligences and individualistic machines can pursue Nanotech if they meet the tradition tree requirements. Unbridled Consumption unlocks the Subsume World planetary decision. The owner can use it on a suitable non-capital colony, such as a Continental World. When the situation finishes, event `colony.200` changes the target to `pc_nanotech` and calls `action.68`. [Tradition tree](E:/SteamLibrary/steamapps/common/Stellaris/common/tradition_categories/01_nanotech.txt:6) · [Decision](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/12_machine_age_decisions.txt:160) · [Situation completion](E:/SteamLibrary/steamapps/common/Stellaris/common/situations/08_machine_age_situations.txt:2020) · [Class change](E:/SteamLibrary/steamapps/common/Stellaris/events/colony_events_1.txt:4670)

The district set is shared with Machine Worlds (`machine_world`). The `pc_machine` class grants +10% resources from jobs and −10% housing usage. The `pc_nanotech` class lacks these intrinsic modifiers, and the rule for pop growth explicitly excludes it. Subsumption creates Nanite Harvest Basins. Each produces 0.5 nanites per month. For an owner without `tr_nanotech_adopt`, each basin also removes one district slot and lowers the habitability ceiling by five percentage points. An owner with active `tr_nanotech_3` can use the Nanotech World designation, which increases nanite production from miners and farmers by 35%, among other effects. [Machine World class](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt:773) · [Pop growth rule](E:/SteamLibrary/steamapps/common/Stellaris/common/game_rules/00_rules.txt:1953) · [Basin creation](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt:8855) · [Basin effects](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/01_blocker_deposits.txt:2067) · [Designation](E:/SteamLibrary/steamapps/common/Stellaris/common/colony_types/02_special_planet_colony_types.txt:637)

One feature name and description are approved for every owner of a habitable Nanite World. The feature is called **Nanite Tiers**.

> At the foot of the settled platforms, the silvery surface gathers into folds. Pillars rise from them, and nanites weave floor after floor between the supports. The first transit lines take shape along their edges as a new tier rises above the old districts.

A test case is a colony with a PCE bonus of +10 that its owner subsumes. The `pc_nanotech` branch of event `action.68` preserves only `d_nanotech_devastation`. After cleanup, expect exactly one PCE deposit with the original +10 counter. At zero, expect no deposit. The basins’ effects on total district capacity are counted separately. [Deposit cleanup](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:6924)

## Orbital Habitat

A regular `pc_habitat` uses the `habitat` district set and starts with a Habitation District (`district_hab_housing`). Owners share this district, except on a capital with `menp_behemoth_mind_meld`. Energy, mining and research districts have individual caps. PCE raises the habitat’s total district capacity. Void Dwellers and Voidforged start on a habitat and use the same district set. We propose selecting their text by owner. The Wilderness residence rule excludes artificial worlds. [Class and starting district](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt:1584) · [Habitat districts](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/03_habitat_districts.txt:10) · [Origins](E:/SteamLibrary/steamapps/common/Stellaris/common/governments/civics/00_origins.txt:2069) · [Residence rule](E:/SteamLibrary/steamapps/common/Stellaris/common/game_rules/00_rules.txt:287) · [Artificial world check](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/05_scripted_triggers_biogenesis.txt:709)

All six names and descriptions are approved, including Modular Quarters. Unique habitat classes with the `habitat` district set use the existing capacity deposit under the usual selection rules. The local Order’s Hall specialization selects the habitat’s Galleries of the Order deposit type when the order is active.

| Owner or habitat condition | PCE feature name | Description |
|---|---|---|
| Regular empire | Modular Quarters | Crews dock new modules to the station hull one by one. The first families are settling into one, the smell of fresh bread drifts from another each morning, and beyond the next bulkhead the fitters are still running cable. A corridor that once ended at an airlock becomes the main street of a new neighbourhood. |
| Hive Mind | Brood Compartments | Drones build brood chambers around warm pipes, leaving narrow passages between the clutches. When the time comes to move the brood, a steady rustle fills the new deck. It carries clear through the bulkhead. |
| Machine Intelligence | Rack-Mounted Decks | Manipulator arms slide a prefabricated deck along guides in the hull. As it locks into place, the power contacts engage. The first shift of drones rides the rails down to the deck while its lights are still dark. |
| Individualistic machines and non-gestalt synthetics | Airlock Workshops | Workshop owners attach modules of their own design to the freight locks. One has fitted an entire foundry behind the doors. Another has barely enough bench space to lay out a clockwork movement. Each workshop still gives the old airlock number as its address. |
| Rogue Servitor | Starlight Cabins | Servitors reserve the outer hull of each new deck for cabins and run pipes and freight lines along the inner side. Before the residents arrive, drones visit every cabin and shift the bed until the stars are visible from the pillow. |
| Knightly habitat with an active Order’s Hall | Galleries of the Order | Squires extend covered galleries from the Order’s Hall to new cells and armouries. On the inner plating of each passage they engrave the names of the knights who stood the first watch there. |

Rogue Servitors can build a Sanctuary Enclave in the Habitation District. We propose selecting their description by active civic. For knights, the local condition should take priority over the owner’s regular text. A habitat of an owner with an active order must have the Order’s Hall specialization installed, which changes the district to the Order’s Demesne. A second habitat of the same empire uses the ordinary text in the absence of the hall. Compare both habitats in game and verify that transferring a habitat with +10 capacity updates its text and preserves its bonus. [Sanctuary Enclave](E:/SteamLibrary/steamapps/common/Stellaris/common/zones/00_zones.txt:381) · [Servitor conditions](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/zones/shared_unity_bio_trophy_zone.txt:3) · [Order’s Hall](E:/SteamLibrary/steamapps/common/Stellaris/common/zones/01_habitat_zones.txt:2) · [Installed specialization check](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/01_scripted_triggers_buildings.txt:1148)

## Intact Ring Segment

The habitable `pc_ringworld_habitable` uses the `ring_world` district set. PCE raises the total district capacity of the selected colony on the ring. The basic district is the City Segment for non-gestalts, the Hive Segment for hive minds, and the Nexus Segment for machine intelligences. All three have an exception for a capital with `menp_behemoth_mind_meld`. Three further segments (`district_rw_urban_1`, `district_rw_urban_2`, `district_rw_urban_3`) take specializations. Rogue Servitors can build a Sanctuary Enclave, turning such a district into a Sanctuary Segment. The residence rule for Wilderness pops excludes artificial worlds. [Planet class](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt:1374) · [City Segment](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/04_ringworld_districts.txt:27) · [Hive Segment](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/04_ringworld_districts.txt:216) · [Nexus Segment](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/04_ringworld_districts.txt:332) · [Specializable segments](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/04_ringworld_districts.txt:849) · [Sanctuary Segment](E:/SteamLibrary/steamapps/common/Stellaris/common/zones/04_secondary_zones.txt:524) · [Wilderness habitability](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/05_scripted_triggers_biogenesis.txt:709)

All five feature names and descriptions for an intact segment are approved. The servitor text follows its active civic and also fits a colony still preparing homes for its wards. An inhabited shattered segment (`pc_shattered_ring_habitable`) uses the existing capacity deposit for the owner's civilization type. District references follow the segment's current district set.

| Owner | PCE feature name | Description |
|---|---|---|
| Regular empire | Cities Above the Main Line | Long-distance trains follow the curve of the ring. Builders span the tracks with broad vaults, and whole neighbourhoods rise above them. Where passengers once stepped out onto a lonely platform, stairs now lead straight from the train to a city square. |
| Hive Mind | Nests in the Ring Frame | Between the ribs of the ring, the hive grows sleeping chambers in tiers. A trough of warm nutrient broth runs the length of each tier. Sated after their shift, the drones settle beneath the vaults, where they can hear the whole nest breathing through the walls. |
| Machine Intelligence | Maintenance Tiers | Assembly units suspend rows of repair cradles beneath the tracks that bring drones back from their shifts. A lift takes a drone off the line, lowers it into an empty cradle and brings a serviced unit back up. Traffic keeps its pace along the entire arc. |
| Individualistic machines and non-gestalt synthetics | Settlements on the Outer Rim | A power bus and a freight rail run along the outer skin of the ring. At each stop, machines assemble homes of their own design. A strip of steel runs past their front doors for those who like to walk home on magnetic soles. |
| Rogue Servitor | Garden Quays | Servitors raise broad terraces above the inhabited belt of the ring. They lay out houses and gardens on each and carry a river along the terraces on an aqueduct. From the quays, the future residents will see treetops on the tier below and the distant arc of the ring overhead. |

In game, repair an inhabited shattered segment with a PCE bonus of +10. The vanilla decision saves deposits from its own list, clears deposits and changes the class to `pc_ringworld_habitable`. Expect the repaired colony to show one deposit with the original +10 and the intact segment description for its current owner. An adjacent segment should retain its own value. [Repair decision](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/02_special_decisions.txt:1979) · [Saved deposits](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/02_machine_age_effects.txt:4345)

## Synaptic Lathe

One capacity feature name and description are approved for every owner of `pc_cosmogenesis_world`. Regular empires, hive minds and machine intelligences can take Cosmogenesis if they meet its other requirements. All three Lathe districts check the same `cosmogenesis_world` district set and the owner's `ap_cosmogenesis` perk. The class provides capacity for one Synaptic Processing Unit. The other two districts are the Neural Gate for research and the Ampliative Speculator for Advanced Logic. Organic and synthetic minds share the Lathe's infrastructure. [Ascension perk](E:/SteamLibrary/steamapps/common/Stellaris/common/ascension_perks/00_ascension_perks.txt:507) · [Districts and effects](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_special_districts.txt:10) · [Class and unit limit](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt:1649) · [Lathe description](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/machine_age_l_english.yml:194)

**Pod Galleries**

> A new tier rises above the Lathe’s working halls. Rows of pods line the aisle, and coolant murmurs beneath the floor. At the head of each pod, a small display glows with the network address of its future occupant.

In game, record an operating Lathe's total district capacity. Adding +1 should open one more slot for either working district while the Synaptic Processing Unit remains capped at one. Before building a district, remove the bonus and verify that capacity returns to its original value. The class disables inheritance of country district modifiers, so this check specifically exercises the PCE deposit's local modifier. [Class properties](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/00_planet_classes.txt:1659)

## Arkship

Civilian, science and military arkships share the `pc_ark` class and the `nomad` district set. Their base districts are Habitation Decks, Reactor Arrays, Arkship Deck and Ordnance Engineering. An empire with Forever Cruise and no `forever_cruise_over` flag uses the Service District in the fourth slot. Habitation Decks have a separate exception for a capital with `menp_behemoth_mind_meld`. The Wilderness origin requires a settled empire. [Class and hulls](E:/SteamLibrary/steamapps/common/Stellaris/common/planet_classes/06_planet_classes_nomads.txt:1) · [Habitation Decks](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/07_ark_districts.txt:26) · [Ordnance Engineering](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/07_ark_districts.txt:406) · [Service District](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/07_ark_districts.txt:609) · [Wilderness origin](E:/SteamLibrary/steamapps/common/Stellaris/common/governments/civics/00_origins.txt:741)

All eight arkship descriptions are approved, including Cabins with a Private Dawn for Hospitality Servitors. An arkship with an active Order’s Hall uses Galleries of the Order. Each uses the capacity counter of the individual ship. Hull role and upgrade tier alone do not require separate texts.

| Owner or condition | PCE feature name | Description |
|---|---|---|
| Regular empire | Streets Between Decks | Shipwrights lay an extra deck across the tall bays of the hull. Cabin doors open onto a common gallery and shops spring up at the foot of the companionway. The ship’s register still gives the new street a number. Its residents already have a name for it. |
| Hive Mind | Brood Nests Under Way | Drones sling new brood chambers between the ribs of the hull on springy fibres. The chambers sway gently when the arkship changes course. The drones feel each fibre to check its tension before returning to the brood. |
| Machine Intelligence | Rotary Racks | Deep in the hull, assembly drones fit tiers of racks around a common shaft. At the end of its watch a drone locks into an empty berth. The rack turns, bringing its relief to the very same companionway. |
| Individualistic machines and non-gestalt synthetics | Custom-Built Cabins | Machines build cabins to their own designs and slide them along guide rails into the new residential tiers. The power couplings are standard. When two friends decide to live next door, a crane simply moves their homes at the next port of call. |
| Rogue Servitor | Family Decks | Servitors fit out cabins on the new deck for families who have outgrown their old ones. Before the move, a drone measures the old doorframe. On the new one it carefully copies every pencil mark where the family recorded a child’s height. |
| Active Forever Cruise | Promenade Decks | A new promenade follows the curve of the liner’s hull, with cabins and an observation lounge. A service corridor runs beneath the floor. While the guests admire an unfamiliar star, the crew delivers luggage to the doors of those who came aboard at the last stop. |
| Hospitality Servitor on an active cruise | Cabins with a Private Dawn | Servitors add another tier of cabins along the observation gallery. Each has its own lighting and climate. While the bridge keeps the night watch, dawn is already breaking in one cabin. Next door, a passenger sleeps on to the soft sound of rain. |
| Arkship with a Consecrated Community and The Sacred Path | Pilgrims’ Courts | The new tier is divided into courts with cells around common refectories. Beside each companionway the pilgrims set a stone from a shrine they have visited into the bulkhead. On the way to table the elders trace the arkship’s journey for the newcomers. |
| Arkship with an active Order’s Hall | Galleries of the Order | Uses the approved habitat description. [Orbital Habitat](#orbital-habitat) |

Forever Cruise passengers can go ashore on excursions such as the Port of Call contract. Population exchanges can also bring new residents aboard. Hospitality Servitors give eligible migrant species bio-trophy rights. The PCE text describes extra cabins tailored to the people who live aboard. [Port of Call](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/nomads_1_l_english.yml:625) · [Population exchange](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/nomads_effects.txt:7088) · [Hospitality Servitor species rights](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_effects/nomads_effects.txt:7165)

Proposed selection starts with an Order’s Hall (`zone_ark_knights`) or Consecrated Community (`zone_ark_sacred_path_pilgrims`) installed on this ship, with the matching origin. The knights must still have an active order. Next check Hospitality Servitor (`is_hospitality_servitor_empire`), followed by the general active cruise. Otherwise use the current owner's text. Once the cruise ends, both cruise variants give way to the applicable owner text. [Order’s Hall](E:/SteamLibrary/steamapps/common/Stellaris/common/zones/05_arkship_zones.txt:1057) · [Community conditions](E:/SteamLibrary/steamapps/common/Stellaris/common/inline_scripts/zones/shared_ark_pilgrim_zone.txt:3) · [Arkship specialization](E:/SteamLibrary/steamapps/common/Stellaris/common/zones/05_arkship_zones.txt:1024) · [Hospitality Servitor](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/09_scripted_triggers_nomads.txt:1418)

Vanilla event `nomads.6015` adds `d_compact_modules` to the selected arkship colony, granting a local `planet_max_districts_add = 1`. In game, add +10 to one of two arkships of the same empire, move to another system and check both counters. Ending a cruise with a positive capacity bonus should update the text and preserve the bonus. Removing all PCE capacity should preserve the vanilla deposit’s own bonus. [Arkship event target](E:/SteamLibrary/steamapps/common/Stellaris/events/nomads_events_1.txt:16379) · [Deposit modifier](E:/SteamLibrary/steamapps/common/Stellaris/common/deposits/17_nomads_deposits.txt:112)

## Resort Worlds, Penal Colonies and Thrall-Worlds

Each of the three mutually exclusive statuses has two capacity feature names and descriptions. Select the active colony modifier first, then the civilization type of the current owner. Among non-gestalt empires, individualistic machines and synthetically ascended empires take the synthetic text. Other owners, including cybernetically ascended empires, take the organic text. The same rule applies to mixed populations. The decision preserves the planet class and district set. Granting a status selects its corresponding deposit type. Revoking the status restores the type for the current world and owner. A colony with a positive counter retains one capacity deposit with its existing value. In normal play the technologies for all three decisions are available to settled non-gestalt empires. The decisions exclude the capital, artificial worlds, ecumenopolises and Nanite Worlds. [Special colony check](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:3238) · [Technologies](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_soc_tech.txt:6216) · [Decisions](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/02_special_decisions.txt:129) · [Synthetic empire check](E:/SteamLibrary/steamapps/common/Stellaris/common/scripted_triggers/00_scripted_triggers.txt:1335)

| Status | Requirements and available districts in Stellaris 4.6.0 |
|---|---|
| Resort World (`resort_colony`) | One per empire, including a queued resort decision. The six listed basic and volcanic production districts must be absent and no building may be under construction. A Relic World requires a Memorialist empire. Tomb Worlds have special eligibility conditions. The status opens the Accommodation District and three specializable attraction districts. The Pleasure World designation (`col_pleasure`) uses the same resort modifier and districts. It uses the resort text for the current owner. [Decision conditions](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/02_special_decisions.txt:318) · [Resort districts](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:361) · [Pleasure World](E:/SteamLibrary/steamapps/common/Stellaris/common/colony_types/00_colony_types.txt:1521) |
| Penal Colony (`penal_colony`) | One per empire. The Prison District provides housing and enforcement jobs. The Prison Industrial District is disabled by `potential = { always = no }`. The Experimental Sentencing civic grants an additional empire effect and both PCE descriptions refer to the same vanilla residential district. [Decision](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/02_special_decisions.txt:144) · [Prison District](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:779) · [Industrial district](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:1912) |
| Thrall-World (`slave_colony`) | An empire can establish several. The target needs a pop group with slavery citizenship and may already have at most one district and one building. The Slave Domicile District provides housing and has provisions for overseer jobs. The Battle Thrall District is disabled by `potential = { always = no }`. [Decision requirements](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/02_special_decisions.txt:235) · [Slave Domicile District](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:900) · [Battle Thrall District](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/00_urban_districts.txt:1978) |

The synthetic Penal Colony name, Subterranean Cell Blocks, and its description of new cells built beneath a working prison are approved.

| Status | Owner | PCE feature name | Description |
|---|---|---|---|
| Resort World | Organic | Resort Terraces | Guest pavilions rise in tiers around the square. Each roof serves as a promenade for the tier above. Towards evening, guests draw their chairs up to the rail to watch the lights come on for the performance in the square below. |
| Resort World | Synthetic | Spectrum Galleries | Tiers of viewing galleries rise above the resort pavilions. On one level the optics reveal the heat patterns of the landscape. On another they show the sky in ultraviolet. Towards evening, guests make their way from floor to floor, debating which part of the spectrum best suits tonight’s sunset. |
| Penal Colony | Organic | Tiered Prison Yards | Several new storeys rise above the old cell blocks. Each tier has an exercise yard on the roof of the neighbouring wing. In the cells below, prisoners tell the time by the footsteps overhead. |
| Penal Colony | Synthetic | Subterranean Cell Blocks | Beneath the working prison, tunnelling machines cut new halls out of the bedrock. Assembly units follow, fitting rows of cells with lighting and ventilation. By the time the lift brings down the first prisoners, the drills are already at work one floor below. |
| Thrall-World | Organic | Barrack Tiers | The barracks rise storey by storey. Doors open onto shared galleries linked by flights of outside stairs. When the shift begins, an overseer is already waiting on each landing with the gang roster. |
| Thrall-World | Synthetic | Numbered Barracks | A crane sets a new dormitory block on top of the barracks. While welding units fasten it to the tier below, the mechanical overseer assigns bunks by work shift. The first gang arrives to find the bunks already marked with the numbers on their passes. |

For each status, compare colonies of organic and synthetic owners with mixed populations and the same capacity bonus. Check that the feature name and description change when the same empire completes synthetic ascension while the corresponding status is active.

On a resort world, PCE applies the same flat district capacity bonus as on any other colony. The game calculates the final cap with the vanilla −25% modifier (`planet_max_districts_mult = -0.25`). The change in the final cap may therefore differ from the PCE bonus. Compare the same world's starting cap, cap with +10, cap on granting the status and cap after revocation. Also remove the capacity bonus while the resort is active. On colony transfer, event `action.89` clears all three statuses. Outlawing slavery clears `slave_colony` on every owned world. Check the text, deposit count and counter after each transition. [Resort modifier](E:/SteamLibrary/steamapps/common/Stellaris/common/static_modifiers/08_static_modifiers_megacorp.txt:482) · [Colony transfer](E:/SteamLibrary/steamapps/common/Stellaris/common/on_actions/00_on_actions.txt:3479) · [Modifier cleanup](E:/SteamLibrary/steamapps/common/Stellaris/events/on_action_events_1.txt:7587) · [Slavery policy](E:/SteamLibrary/steamapps/common/Stellaris/common/policies/00_policies.txt:4937)

## Updating after a colony changes

After terraforming, a change of owner or civilization type, a special status being granted or revoked, or a change of local specialization, determine which deposit type applies. When the variant changes, replace the old deposit while preserving `pce_extra_districts` on the body. Keep the deposit when its type still matches. If vanilla clears deposits and the counter is positive, restore exactly one instance of the applicable type. At zero the body has no PCE deposit.

Select the feature name, description, district references, menu text, and tooltips from the current body class, available districts, and current owner. When next displayed after terraforming, a change of class or ownership, or a change that alters the available districts, these surfaces must agree. Use the vanilla localization of a specific district when that district applies. Examples include the housing decks on an arkship and the Wilderness urban district on a world with the standard district set. PCE adds to the overall district limit. [Arkship district](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/07_ark_districts.txt:27) · [Wilderness district](E:/SteamLibrary/steamapps/common/Stellaris/common/districts/05_wilderness_districts.txt:20)

Test an ordinary empire on a Tomb World with +10 capacity. Once terraformed into an Ocean World, it has one PCE deposit granting +10, and its menu and feature card still show the base Multilevel Cities variant. Two ordinary empires with different primary species should see the same result under otherwise identical conditions. A second case is converting a Relic World into an ecumenopolis. The vanilla decision clears deposits and restores a predefined list. If the PCE counter is positive and the feature has disappeared after the class change, restore exactly one deposit with the existing bonus. A zero counter must leave the feature absent. Vanilla restores Ancient Tunnels in a similar way through `on_planet_class_changed`. [Relic World conversion](E:/SteamLibrary/steamapps/common/Stellaris/common/decisions/02_special_decisions.txt:1122) · [Restoring Ancient Tunnels](E:/SteamLibrary/steamapps/common/Stellaris/events/infernals_1_events.txt:3954)

On both a planet and an arkship, verify that the standard feature card shows the installed type’s name, description and icon after replacement, reopening the view and reloading a save. Compare the capacity bonus against the selected body’s variable.

## Verification example

On one body, selecting `+10` and then `+3` makes the menu show 13 and a single deposit grant +13 to the district limit. Removing 3 keeps that deposit, reduces its bonus to +10 and makes the menu show 10. The last option removes the remaining 10 and the deposit. Reopening the menu shows 0. The counter on a second body retains its value. This scenario is to be checked on both a planet and an arkship.
