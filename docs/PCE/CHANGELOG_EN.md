# PCE changelog

## Contents

- [PCE 2.0.1](#pce-201)
- [PCE 2.0.0 for Stellaris v4.6.*](#pce-200-for-stellaris-v46)
- [2026-11-25 — Workshop cover and interface artwork](#2026-11-25--workshop-cover-and-interface-artwork)
- [2026-11-25 — Deposit types and interface for 2.0.0](#2026-11-25--deposit-types-and-interface-for-200)
- [2026-11-25 — District capacity icons](#2026-11-25--district-capacity-icons)
- [2026-11-24 — District capacity requirements](#2026-11-24--district-capacity-requirements)

## PCE 2.0.1

The decision description and the index shown in the planet and arkship menus now explain that the district limit takes a few in-game days to update.

The [Steam Workshop description](WORKSHOP_DESCRIPTION_EN.txt) explains that the cheat works on any player-owned colony and shows how to add and remove district slots.
The description now closes with a thank-you to players for their feedback and bug reports.

## PCE 2.0.0 for Stellaris v4.6.*

The decision opens the planning center on a player-owned colony or arkship. Both menus show the selected carrier’s index. Increase it by 1–10 at a time. A positive index unlocks the decrease menu, which offers the available amounts and Remove all. Tooltips show the district capacity bonus before and after the operation.

Each colony stores its own counter and one matching feature instance. The release contains 49 feature types, English and Russian cards and 48 icons. Changes to the world, owner, status or specialization preserve the bonus. Reaching zero removes the PCE feature and counter. The game manages its own features and districts. Migration of stacked features from earlier releases is outside this version’s scope.

The parser expanded the game-facing scripts. Synthetic checks exercised `0 → 10 → 13 → 10 → 0`, world conversion, restoration after vanilla feature cleanup and the end of a cruise. In-game checks cover the native feature card, actual district cap on a planet and arkship, tooltips, variant changes and save/load. [Requirements](REQUIREMENTS_EN.md) · [Vanilla functions](VANILLA_CHANGES_EN.md)

## 2026-11-25 — Workshop cover and interface artwork

Replaced the [Workshop cover](../../PCE/thumbnail.png), [decision icon](../../PCE/gfx/interface/icons/decisions/pce_extend_planetary_capacity.dds) and [menu illustration](../../PCE/gfx/event_pictures/pce_capacity_extension.dds). The icon has a transparent background. Both DDS textures were checked at their in-game dimensions. [Full-size source artwork](artwork/interface/)

## 2026-11-25 — Deposit types and interface for 2.0.0

The requirements specify 49 deposit types sharing a single variable on each colony or arkship. A change of variant replaces the deposit and preserves the capacity bonus. Updated the terraforming and vanilla deposit cleanup scenarios. Ocean, Gaia and Tomb Worlds use the owner's base variant. On resort worlds the game applies its vanilla modifiers to the cap. Agreed on the “District capacity bonus” label and new artwork for the Workshop thumbnail, decision icon and menu illustration. The menu design and the subjects of the three images remain open for discussion. [Requirements for 2.0.0](REQUIREMENTS_EN.md)

Clarified the dynamic menu rules. The decrease option is visible at a positive index. The amount buttons offer every value from 1 through 10 up to the current index. The final “Remove all” option removes the entire remaining bonus. Approved tooltips that display the district capacity bonus before and after the selected action.

Approved the planet and arkship main menu wording, the blank line before the current index and the three button labels. [Main menu wording](REQUIREMENTS_EN.md#main-menu-wording)

## 2026-11-25 — District capacity icons

All six special colony icons were approved, two each for resort worlds, penal colonies and thrall-worlds. The 49 cases described in the requirements use 48 distinct approved illustrations. An orbital habitat and an arkship with an active Order’s Hall share Galleries of the Order. The full-size PNG and the 98 × 75 pixel thumbnail were verified for each illustration. [Artwork and thumbnails](artwork/deposits/)

## 2026-11-24 — District capacity requirements

Recorded the requirements for one deposit with a cumulative bonus, partial and full removal of extra district capacity, and display of the current bonus in the menu. [Technical requirements](REQUIREMENTS_EN.md)

Agreed on a shared effect, an amount-button template, events for planets and arkships, a target check at the time of the click, and parameterized tooltips. Clarified that the full PCE bonus can be removed regardless of how many districts have been built. [Buttons and actions](REQUIREMENTS_EN.md#buttons-and-actions)

Added requirements for distinct Gaia World, Tomb World, and Wilderness colony descriptions. Dedicated Wilderness artwork and the presentation of ocean colonies remain open for discussion. [Colony types and wording](REQUIREMENTS_EN.md#colony-types-and-wording)

Agreed on a direction for Wilderness artwork, two Ocean World descriptions, and precedence for owner-specific wording over ordinary descriptions. Proposed a selection order with examples for an arkship and a mixed-species colony. [Description selection priorities](REQUIREMENTS_EN.md#description-selection-priorities)

Agreed to check the aquatic trait on the current owner’s primary species. Added the naming matrix and requirements for updating text and district names while preserving extra capacity after a colony changes. [Naming matrix](REQUIREMENTS_EN.md#combinations-for-feature-names) · [Colony changes](REQUIREMENTS_EN.md#updating-after-a-colony-changes)

Updated description selection to use ten vanilla district sets and five main civilization types. Documented shared districts across owners, different districts for the same owner, and the role of planet class and special colony conditions. [Description selection priorities](REQUIREMENTS_EN.md#description-selection-priorities) · [Combinations for feature names](REQUIREMENTS_EN.md#combinations-for-feature-names)

Removed wording selection by primary species and its aquatic trait from the requirements. Ordinary empires now share one Ocean World description. Updated the terraforming verification scenario. [Colony types and wording](REQUIREMENTS_EN.md#colony-types-and-wording)

Defined when the deposit type persists or changes. Started world-by-world planning with the Continental World, five draft descriptions, and terraforming and arcology scenarios. [Continental World](REQUIREMENTS_EN.md#continental-world)

Shortened the Multilevel Cities description to one sentence about new streets and squares rising above established neighborhoods. [Continental World](REQUIREMENTS_EN.md#continental-world)

Expanded the five draft descriptions for ordinary development on a Continental World. Each describes how that civilization builds or grows another layer. [Continental World](REQUIREMENTS_EN.md#continental-world)

Approved the five Continental World descriptions. Checked vanilla volcanic districts, Lithoid and Thermophile conditions, and the restriction on Wilderness pops. Added four proposed descriptions for volcanic colonies. [Continental World](REQUIREMENTS_EN.md#continental-world) · [Volcanic World](REQUIREMENTS_EN.md#volcanic-world)

Approved three descriptions of volcanic development. The revised ending for Multilevel Cities describes a square above the lava flow. [Volcanic World](REQUIREMENTS_EN.md#volcanic-world)

Revised the ending for Multilevel Cities on a Volcanic World. The bridges become streets that unite the neighborhoods on both slopes in a single work of architecture and engineering. [Volcanic World](REQUIREMENTS_EN.md#volcanic-world)

Approved the final Multilevel Cities wording for the Volcanic World. Checked ecumenopolis construction, restoration, use of existing arcologies, and the Rogue Servitor specialization. Added five proposed capacity descriptions. [Volcanic World](REQUIREMENTS_EN.md#volcanic-world) · [Ecumenopolis](REQUIREMENTS_EN.md#ecumenopolis)

Approved the five ecumenopolis descriptions. Proposed two Hive World descriptions based on resident species and disconnected drone rights in BioGenesis. Added a capacity check after vanilla terraforming removes deposits. [Ecumenopolis](REQUIREMENTS_EN.md#ecumenopolis) · [Hive World](REQUIREMENTS_EN.md#hive-world)

Approved both Hive World descriptions. Checked Machine World residence rules, owner-specific districts, the servitor specialization, and deposit cleanup during terraforming. Proposed five feature names and descriptions. [Hive World](REQUIREMENTS_EN.md#hive-world) · [Machine World](REQUIREMENTS_EN.md#machine-world)

Approved the five Machine World descriptions. Verified how the habitable Nanite World arises, its differences from Machine Worlds and uninhabitable L-Cluster planets, and the removal of the PCE deposit when subsumption finishes. [Machine World](REQUIREMENTS_EN.md#machine-world) · [Nanite World](REQUIREMENTS_EN.md#nanite-world)

Approved Nanite Tiers for every owner of a habitable Nanite World. Checked the shared Habitation District, origins and habitat specializations. Proposed five descriptions by owner and one for a habitat with an active Order’s Hall. [Nanite World](REQUIREMENTS_EN.md#nanite-world) · [Orbital Habitat](REQUIREMENTS_EN.md#orbital-habitat)

Approved the habitat entries for hive minds, machine intelligences, individualistic machines, servitors and knights. Proposed Modular Quarters for regular empires, describing a neighbourhood that grows as new modules dock to the station. [Orbital Habitat](REQUIREMENTS_EN.md#orbital-habitat)

Approved Modular Quarters and the use of existing deposits on unique habitats. Checked owner-specific districts, the servitor specialization and the vanilla repair decision for intact Ring Segments. Proposed five feature names and descriptions. [Orbital Habitat](REQUIREMENTS_EN.md#orbital-habitat) · [Intact Ring Segment](REQUIREMENTS_EN.md#intact-ring-segment)

Approved the five intact segment descriptions and the use of the existing capacity deposit on shattered segments. Checked all three Synaptic Lathe districts and proposed a single feature description, Pod Galleries. [Intact Ring Segment](REQUIREMENTS_EN.md#intact-ring-segment) · [Synaptic Lathe](REQUIREMENTS_EN.md#synaptic-lathe)

Approved Pod Galleries. Checked arkship districts, the cruise district change, local specializations and the vanilla deposit capacity bonus. Proposed eight new texts and reuse of Galleries of the Order. [Synaptic Lathe](REQUIREMENTS_EN.md#synaptic-lathe) · [Arkship](REQUIREMENTS_EN.md#arkship)

Approved arkship variants 1–6 and 8 and the use of Galleries of the Order. Checked shore excursions and the migration effect that brings residents aboard. Proposed Cabins with a Private Dawn for Hospitality Servitors. [Arkship](REQUIREMENTS_EN.md#arkship)

Approved Cabins with a Private Dawn for Hospitality Servitors. [Arkship](REQUIREMENTS_EN.md#arkship)

Checked eligibility, status removal, available districts and the resort capacity penalty for the three special colonies. Proposed a capacity feature description for each status. [Special worlds](REQUIREMENTS_EN.md#resort-worlds-penal-colonies-and-thrall-worlds)

Proposed separate feature names and descriptions for organic and synthetic owners of each special colony. Selection follows the owner’s civilization type on mixed colonies and accounts for synthetic ascension. [Special worlds](REQUIREMENTS_EN.md#resort-worlds-penal-colonies-and-thrall-worlds)

Proposed Subterranean Cell Blocks for a synthetic empire’s Penal Colony, with new text describing construction beneath the working prison. [Special worlds](REQUIREMENTS_EN.md#resort-worlds-penal-colonies-and-thrall-worlds)

Approved Subterranean Cell Blocks. Counted names and descriptions in both languages and recorded the reused texts and outstanding work for standard worlds. [Combinations for feature names](REQUIREMENTS_EN.md#combinations-for-feature-names)

Created the first two feature icon concepts for standard worlds. The source paintings are accompanied by 98 × 75 pixel previews for review at interface scale. [Multilevel Cities](artwork/deposits/pce_multilayered_cities_98x75.png) · [Biosphere Layers](artwork/deposits/pce_biosphere_layers_98x75.png)

Adopted the futuristic art direction of Stellaris for the feature icons. The revised Multilevel Cities concept shows a high-speed transit line above the residential tiers. In Biosphere Layers, root bridges link living terraces above the clouds. [Multilevel Cities](artwork/deposits/pce_multilayered_cities_v2_98x75.png) · [Biosphere Layers](artwork/deposits/pce_biosphere_layers_v2_98x75.png)

The second versions of Multilevel Cities and Biosphere Layers were approved as visual references. Added standard-world feature concepts for the three remaining civilization types, each with a source painting and a 98 × 75 pixel preview. [Tiered Nests](artwork/deposits/pce_tiered_nests_98x75.png) · [Modular Quarters](artwork/deposits/pce_modular_quarters_98x75.png) · [Distributed Nodes](artwork/deposits/pce_distributed_nodes_98x75.png)

Tiered Nests and Distributed Nodes were approved. Modular Quarters was redrawn from above to show a metropolis. Blocks stretch along a transit corridor while gantry arms dock a new section in the foreground. [Source painting](artwork/deposits/pce_modular_quarters_v2.png) · [Icon](artwork/deposits/pce_modular_quarters_v2_98x75.png)

The second version of Modular Quarters was approved for standard worlds. Created four Volcanic World concepts and saved each source painting with a 98 × 75 pixel preview. [Multilevel Cities](artwork/deposits/pce_volcanic_multilayered_cities_98x75.png) · [Tiered Nests](artwork/deposits/pce_volcanic_tiered_nests_98x75.png) · [Modular Quarters](artwork/deposits/pce_volcanic_modular_quarters_98x75.png) · [Distributed Nodes](artwork/deposits/pce_volcanic_distributed_nodes_98x75.png)

All four Volcanic World icons were approved. Created five Ecumenopolis concepts, each with a 98 × 75 pixel preview. [The Upper City](artwork/deposits/pce_ecumenopolis_upper_city_98x75.png) · [Modular Arcologies](artwork/deposits/pce_ecumenopolis_modular_arcologies_98x75.png) · [Nest Towers](artwork/deposits/pce_ecumenopolis_nest_towers_98x75.png) · [Assembly Towers](artwork/deposits/pce_ecumenopolis_assembly_towers_98x75.png) · [Garden Arcologies](artwork/deposits/pce_ecumenopolis_garden_arcologies_98x75.png)

All five Ecumenopolis icons were approved. Created two Hive World concepts and saved 98 × 75 pixel previews. In Deep Hive Cells, the Hive Mind grows a new tier. In Reclaimed Galleries, surviving drones reopen old chambers for freight traffic. [Deep Hive Cells](artwork/deposits/pce_hive_world_deep_hive_cells_98x75.png) · [Reclaimed Galleries](artwork/deposits/pce_hive_world_reclaimed_galleries_98x75.png)

Both Hive World icons were approved. Created five Machine World concepts and saved each source painting with a 98 × 75 pixel preview. [Layers of the Planetary Machine](artwork/deposits/pce_machine_world_layers_of_the_planetary_machine_98x75.png) · [Quiet Decks](artwork/deposits/pce_machine_world_quiet_decks_98x75.png) · [Artisans’ Quarters](artwork/deposits/pce_machine_world_artisans_quarters_98x75.png) · [Habitation Sections](artwork/deposits/pce_machine_world_habitation_sections_98x75.png) · [Heat Exchanger Nests](artwork/deposits/pce_machine_world_heat_exchanger_nests_98x75.png)

All five Machine World icons were approved. Created the Nanite Tiers concept for all owners of a habitable Nanite World. The silvery surface folds into a pillar from which nanites weave a new deck above the city. [Source painting](artwork/deposits/pce_nanite_tiers.png) · [98 × 75 preview](artwork/deposits/pce_nanite_tiers_98x75.png)

The Nanite Tiers icon was approved. Created six Orbital Habitat concepts with 98 × 75 pixel previews. Galleries of the Order uses an interior view suitable for an arkship with an active Order’s Hall. [Modular Quarters](artwork/deposits/pce_habitat_modular_quarters_98x75.png) · [Brood Compartments](artwork/deposits/pce_habitat_brood_compartments_98x75.png) · [Rack-Mounted Decks](artwork/deposits/pce_habitat_rack_mounted_decks_98x75.png) · [Airlock Workshops](artwork/deposits/pce_habitat_airlock_workshops_98x75.png) · [Starlight Cabins](artwork/deposits/pce_habitat_starlight_cabins_98x75.png) · [Galleries of the Order](artwork/deposits/pce_habitat_galleries_of_the_order_98x75.png)

Modular Quarters, Rack-Mounted Decks and Starlight Cabins were approved for the orbital habitat. The revised concepts show individual workshops docked externally to adjacent locks and brood chambers built on a new deck above a working freight passage. The knights’ gallery is an extension to the orbital keep, with expedition trophies drawn from its vanilla description. [Airlock Workshops](artwork/deposits/pce_habitat_airlock_workshops_v2_98x75.png) · [Brood Compartments](artwork/deposits/pce_habitat_brood_compartments_v2_98x75.png) · [Galleries of the Order](artwork/deposits/pce_habitat_galleries_of_the_order_v2_98x75.png) · [Order’s Keep](E:/SteamLibrary/steamapps/common/Stellaris/localisation/english/toxoids_l_english.yml:73)

The third revision of three concepts shows how much space the habitat gains. An industrial district lines the freight locks. Hive workers grow the ribs of a new vault above the occupied brood chambers. In the Order’s keep, builders add a gallery of cells above the working muster hall. [Airlock Workshops](artwork/deposits/pce_habitat_airlock_workshops_v3_98x75.png) · [Brood Compartments](artwork/deposits/pce_habitat_brood_compartments_v3_98x75.png) · [Galleries of the Order](artwork/deposits/pce_habitat_galleries_of_the_order_v3_98x75.png)

The third versions of Airlock Workshops, Brood Compartments and Galleries of the Order were approved, completing the six-icon orbital habitat set. Created five concepts for an intact habitable ring segment with 98 × 75 pixel previews. [Cities Above the Main Line](artwork/deposits/pce_ringworld_cities_above_the_main_line_98x75.png) · [Nests in the Ring Frame](artwork/deposits/pce_ringworld_nests_in_the_ring_frame_98x75.png) · [Maintenance Tiers](artwork/deposits/pce_ringworld_maintenance_tiers_98x75.png) · [Settlements on the Outer Rim](artwork/deposits/pce_ringworld_settlements_on_the_outer_rim_98x75.png) · [Garden Quays](artwork/deposits/pce_ringworld_garden_quays_98x75.png)

All five icons for the habitable ring segment were approved. Created the Pod Galleries concept for the Synaptic Lathe, shared by all owners. [Full artwork](artwork/deposits/pce_synaptic_lathe_pod_galleries.png) · [98 × 75 preview](artwork/deposits/pce_synaptic_lathe_pod_galleries_98x75.png)

The Pod Galleries icon for the Synaptic Lathe was approved.

Created eight arkship concepts and their 98 × 75 pixel previews. Arkships with an active Order’s Hall share the approved [Galleries of the Order](artwork/deposits/pce_habitat_galleries_of_the_order_v3_98x75.png) artwork. [Streets Between Decks](artwork/deposits/pce_arkship_streets_between_decks_98x75.png) · [Brood Nests Under Way](artwork/deposits/pce_arkship_brood_nests_under_way_98x75.png) · [Rotary Racks](artwork/deposits/pce_arkship_rotary_racks_98x75.png) · [Custom-Built Cabins](artwork/deposits/pce_arkship_custom_built_cabins_98x75.png) · [Family Decks](artwork/deposits/pce_arkship_family_decks_98x75.png) · [Promenade Decks](artwork/deposits/pce_arkship_promenade_decks_98x75.png) · [Cabins with a Private Dawn](artwork/deposits/pce_arkship_cabins_with_a_private_dawn_98x75.png) · [Pilgrims’ Courts](artwork/deposits/pce_arkship_pilgrims_courts_98x75.png)

All eight arkship icons were approved.

Created six concepts for resort worlds, penal colonies and thrall-worlds, with separate artwork for organic and synthetic owners. Checked all six 98 × 75 pixel previews. [Resort Terraces](artwork/deposits/pce_resort_terraces_98x75.png) · [Spectrum Galleries](artwork/deposits/pce_resort_spectrum_galleries_98x75.png) · [Tiered Prison Yards](artwork/deposits/pce_penal_tiered_prison_yards_98x75.png) · [Subterranean Cell Blocks](artwork/deposits/pce_penal_subterranean_cell_blocks_98x75.png) · [Barrack Tiers](artwork/deposits/pce_thrall_barrack_tiers_98x75.png) · [Numbered Barracks](artwork/deposits/pce_thrall_numbered_barracks_98x75.png)
