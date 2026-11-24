# PDE terraforming console description

## Contents

- [Main screen](#main-screen)
- [Target details and pagination](#target-details-and-pagination)
- [Section illustrations](#section-illustrations)
- [In-game checks](#in-game-checks)

## Main screen

In the planetary decisions list, the Effects text explains that the decision opens a menu for adding or removing deposits and blockers on the selected body. Changes take effect when the player selects an action in the editor.

In PDE 2.1.0 for Stellaris 4.6, the console greets the operator on every screen, including when opening a section or turning a page. The editor name comes from the decision localization. The example below shows the main screen for Earth. [Main specification](TZ_EN.md)

```text
Welcome to the Planetary Deposits Editor.
Circuit ready. Select a section, then a command.
Changes take effect immediately.

Celestial body: Continental World / Earth
Climate: Wet
System: Sol
```

## Target details and pagination

Leave one blank line after the greeting, then display the target details. Take the class, body name and system name from the editor's saved target. Show the climate line when the class specifies a planetary climate (dry, wet, cold or artificial). Evaluate `has_climate` on the target. For stars with a technical luminosity value and bodies without a climate, the system follows the body name directly.

In a submenu, leave exactly one blank line after the system. On the next line, display “Section” followed by the localized label of the menu item used to enter the current section. When two or more pages are available, display “Page S/N” immediately below the section. A single-page submenu reads as follows.

```text
Welcome to the Planetary Deposits Editor.
Circuit ready. Select a section, then a command.
Changes take effect immediately.

Celestial body: Gas Giant / Jupiter
System: Sol

Section: Orbital deposits
```

Example of a removal list with three pages after filtering.

```text
Welcome to the Planetary Deposits Editor.
Circuit ready. Select a section, then a command.
Changes take effect immediately.

Celestial body: Continental World / Earth
Climate: Wet
System: Sol

Section: Remove deposits
Page 2/3
```

On any screen, show the page line only when `cdpd_pages > 1` after filtering. If the main screen has multiple pages, leave one blank line between the system and the page line there as well. In an empty submenu, show the message about unavailable actions below the section name.

## Section illustrations

All 27 illustrations should look at home among Stellaris event pictures and evoke the same retrofuturistic terraforming console. Compose each scene from the outset as a horizontal **3:1** panorama (width to height). The final texture measures **450 × 150 pixels**, matching the vanilla `alien_planet.dds`. The silhouette and lighting should make the subject, terrain or phenomenon recognizable inside the standard event frame. Give each scene its own palette. Recurring instrument details tie the series together. One targeting mark, glowing oscilloscope trace or graduated scale is enough for a scene.

Vanilla references in the game's `gfx/event_pictures/` directory include the landscape depth in `alien_planet.dds`, the station silhouetted among asteroids in `mining_station.dds`, the glowing specimen in `crystal_mining.dds` and the instrument lighting in `worrying_signal.dds`. For example, the rare crystals scene could show glowing facets lighting the surrounding rock, with the measured spectrum at the edge of the frame.

The approved main menu illustration is **05 “Filling the Basin”**. In the shipboard observatory, a brass pointer touches the shore of a forming sea on an amber globe. This illustration sets a visual precedent for the series. The instrument and the selected terrain show what the operator is changing. [Approved original](artwork/cdpd_main_menu_basin.png) · [At game size, 450 × 150](artwork/cdpd_main_menu_basin_450x150.png)

The approved Planetary deposits illustration shows a probe touching an ore vein beneath a river valley. The approved Orbital deposits illustration shows an ore outcrop through a shipboard rangefinder. [Planetary deposits](artwork/cdpd_planetary_deposits.png) · [Orbital deposits](artwork/cdpd_orbital_deposits.png)

The approved Blockers illustration marks an impassable ridge with amber hatching on a relief map. In Remove deposits, a gripper lifts a turquoise deposit above its illuminated socket. [Blockers](artwork/cdpd_blockers.png) · [Remove deposits](artwork/cdpd_remove_deposits.png)

The approved district illustrations show a storm and an oscilloscope for generator districts, a drill in a copper vein for mining, and a floodplain survey for agriculture. Volcanic mining districts share the drill illustration. [Generator](artwork/cdpd_generator_districts.png) · [Mining](artwork/cdpd_mining_districts.png) · [Agriculture](artwork/cdpd_agriculture_districts.png)

The approved thermotechnic illustration shows a heat exchanger above a magma chamber. The mixed volcanic scene shows a probe examining a turquoise ore vein above a lava river. [Thermotechnic](artwork/cdpd_thermotechnic_districts.png) · [Mixed volcanic](artwork/cdpd_mixed_volcanic_districts.png)

The approved orbital illustrations show a collector satellite against a stellar plasma loop for energy credits, an ore seam measured on an asteroid for minerals, and an algae sample aboard a ship above an icy moon for food. [Energy credits](artwork/cdpd_orbital_energy.png) · [Minerals](artwork/cdpd_orbital_minerals.png) · [Food](artwork/cdpd_orbital_food.png)

The approved alloys illustration shows an asteroid metal sample under an assay probe. The trade illustration shows a tug moving a freight container at an orbital dock above a gas giant. [Alloys](artwork/cdpd_orbital_alloys.png) · [Trade](artwork/cdpd_orbital_trade.png)

The approved illustrations show a scoop collecting orange motes from an asteroid, green gas swirling in a glass sampling chamber, and a spectrograph illuminating golden crystals in an icy fissure. [Volatile motes](artwork/cdpd_orbital_volatile_motes.png) · [Exotic gases](artwork/cdpd_orbital_exotic_gases.png) · [Rare crystals](artwork/cdpd_orbital_rare_crystals.png)

The approved living metal illustration shows a sample healing between two clamps. Zro forms a wave of blue aerosol at a resonator. Distorted starlight near a black hole reveals dark matter. Under a lens, nanites assemble a cellular lattice. [Living metal](artwork/cdpd_orbital_living_metal.png) · [Zro](artwork/cdpd_orbital_zro.png) · [Dark matter](artwork/cdpd_orbital_dark_matter.png) · [Nanites](artwork/cdpd_orbital_nanites.png)

The approved research illustrations show a stellar spectrum for physics, a record of a flock's movement above a gas giant for society, and a landing leg undergoing a load test on an ice sample for engineering. [Physics research](artwork/cdpd_orbital_physics.png) · [Society research](artwork/cdpd_orbital_society.png) · [Engineering research](artwork/cdpd_orbital_engineering.png)

The minor artifacts scene shows two ancient fragments being fitted together. The astral threads scene shows luminous filaments extending from a tear in space. [Minor artifacts](artwork/cdpd_orbital_minor_artifacts.png) · [Astral threads](artwork/cdpd_orbital_astral_threads.png)

| Set | Count | Sections and subjects |
|---|---:|---|
| Main screens | 5 | Main menu — a globe in targeting rings. Planetary deposits — a geological cross section. Orbital deposits — a scan from orbit. Blockers — an obstacle on a topographic map. Remove deposits — a feature marked for removal. |
| Districts | 5 | Generator — a storm front and an oscilloscope trace. Mining — an ore vein and a probe. Agriculture — a surveyed floodplain. Thermotechnic — a magma chamber and heat channels. Mixed volcanic — an ore vein alongside a magma flow. |
| Orbital resources and research | 17 | One illustration each for energy credits, minerals, food, alloys, trade, volatile motes, exotic gases, rare crystals, living metal, zro, dark matter, nanites, physics research, society research, engineering research, minor artifacts and astral threads. |

A nested section inherits the illustration from its nearest parent with assigned artwork. Ordinary and volcanic mining districts share the mining picture. Resource yield and page changes preserve the selected image. Both minor artifact station branches use the artifact picture. Event and unique orbital deposits inherit the general orbital scanner scene. [Menu tree](MENU_STRUCTURE_EN.md)

## In-game checks

Check the class, name, system and climate visibility on an ordinary planet, a gas giant and a star. Check artificial climate on a habitat. From the main menu, open a single-page section and a multi-page list, advance a page and go back. At each step, compare the greeting, blank line after the system, section name and page indicator with the examples above. Check an empty list and confirm that the last line is readable with a long body or section name in Russian and English at the player's UI scale.

Compare the PDE banners with vanilla event pictures in the game window. Check that the subject and instrument details remain legible inside the standard frame, that entering a section changes the scene as specified and that turning the page preserves it. Check inheritance in the volcanic mining, minor artifact, event orbital and unique orbital branches.

[Русское ТЗ](TZ_EVENT_PANEL_RU.md).
