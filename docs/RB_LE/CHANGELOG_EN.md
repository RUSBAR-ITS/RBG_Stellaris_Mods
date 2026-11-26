# Leader Editor — changelog

## Contents

- [Version 0.0.5](#version-005)
- [Version 0.0.4](#version-004)
- [Version 0.0.3](#version-003)
- [Version 0.0.2](#version-002)
- [Version 0.0.1](#version-001)
- [Vanilla research](#vanilla-research)

## Version 0.0.5

In the 0.0.4 in-game test, the selected ruler's personal ethic, homeworld, world type and former occupation were blank. Opening the dossier logged seven `Unknown promotion` and four `Unknown property` messages. The Russian and English dossiers now request the species, ethic, homeworld, occupation and specialization lines directly on the selected leader. Leaders from an ark use the name of their saved home colony. [Dossier scope bindings](VANILLA_CHANGES_EN.md#leader-details)

## Version 0.0.4

The Personnel Department dossier shows age, years of service, species and species class, type used by trait conditions, personal ethic, home colony, and former occupation. Training lists the class, chosen specialization, level, and experience. An extra line shows effective skill when a bonus changes it. At the level cap the dossier displays the game's standard message. Updated the English and Russian text. [Specification and in-game checks](REQUIREMENTS_0_0_4_EN.md)

## Version 0.0.3

Set the display name to **Leader Editor** in the package and launcher descriptors. The internal identifier is `RB_LE`. Removed the empty `interface` and `common/button_effects` directories left by the card button prototype.

During the 0.0.2 in-game test on Stellaris 4.6.0, the log recorded a dossier opening in each of the four sections, navigation back to the lists, and exit from the main menu. The session recorded no errors for Leader Editor.

## Version 0.0.2

The in-game 0.0.1 test showed that the card button received the player country. Removed the interface override, button handler and UI Overhaul Dynamic dependency. The Personnel Department planetary decision opens registers for the ruler, commanders, officials and scientists. Empty sections are hidden, lists show ten names per page, and Back from a dossier returns to its originating page. Added a vanilla event illustration and updated both localisations. [Specification and in-game checks](REQUIREMENTS_0_0_2_EN.md)

## Version 0.0.1

Moved the documentation and trait tables to `docs/RB_LE`. Updated links to game files and the paths used by the table scripts. Added a local Stellaris launcher descriptor, `RB_LE.mod`, pointing to `RB_LE/mod`.

Added Edit Dossier to the UI Overhaul Dynamic leader card. When the engine passes a leader to the button, an event shows that leader’s name and a single Exit option. Other cases write a diagnostic to `game.log`. The package includes English and Russian localisation. Verifying which character the engine supplies requires an in-game test. [Specification and acceptance tests](REQUIREMENTS_0_0_1_EN.md) · [Affected files and functions](VANILLA_CHANGES_EN.md)

## Vanilla research

Documented leader classes and properties, traits and ranks, assignments, the council, lifecycle events and character selection in the Stellaris 4.6.0 interface. The study identifies vanilla sources and in-game checks for future feature selection. [Research overview](VANILLA_LEADERS_4_6_0_EN.md)

Recorded the decisions to preserve class and grant traits. Added vanilla examples for discussing XP, subclasses, background, age, gender and portrait editing. [Editor scope and character background](VANILLA_LEADERS_4_6_0_EN.md#editor-scope-and-character-background)

Marked editing a leader's personal ethic as required. Compared the starting ruler's biography input, the character card's background display and the effect that sets an existing leader's description. Recorded the acceptance check for free text entry.

Counted forward and reverse conflict declarations across all 797 trait IDs. Documented the categories of acquisition conditions and technology prerequisites, including compound conditions and exclusions outside `opposites`. [Opposites and acquisition requirements](VANILLA_LEADERS_4_6_0_EN.md#opposites-and-acquisition-requirements)

Counted the five gameplay trait types and checked examples distinguishing type, rank and display rarity. [Traits and progression](VANILLA_LEADERS_4_6_0_EN.md#traits-and-progression)

Compiled a Russian-language table of all 254 basic traits with names, descriptions, forward and reverse opposites, and acquisition requirements. [Stellaris 4.6.0 basic traits workbook](BASIC_LEADER_TRAITS_4_6_0_RU.xlsx)

Added a Russian CSV covering all 254 basic traits in the 16 agreed columns. Rank, replaced traits, direct opposites, classes, gestalt eligibility, species type, personal ethic and selection flags have dedicated fields for filtering. [Basic traits CSV](BASIC_LEADER_TRAITS_4_6_0_RU.csv)

Expanded the CSV to 22 columns. Six traits require the leader to be in the recruitment pool when choosing the trait, including when spending an earned level-up. Added separate country filters for crisis factions, Wilderness, machine intelligence, nomads and gestalt consciousness. The leader gestalt column now describes the character's own requirements. [Final table](BASIC_LEADER_TRAITS_4_6_0_RU.csv)

Assigned all 254 basic traits to eight menu sections in the final CSV. Added columns for the section, subsection, vanilla acquisition method and references to trait definitions or grants in game scripts. The starting-ruler-only section contains the first ranks of Buccaneer, Trailblazer and Treasure Hoarder. Six traits are marked as having an unconfirmed acquisition method. [Basic traits and menu sections](BASIC_LEADER_TRAITS_4_6_0_RU.csv)

All ranks of a basic trait now share the menu folder of its first rank. Buccaneer, Trailblazer and Treasure Hoarder ranks II and III moved to the starting-ruler-only section. Gifted II moved to the recruitment pool section. The table lists the acquisition conditions for each rank separately.

Documented trait visibility filters for the selected leader and their empire, hiding empty branches at every depth and paginating the available entries. [Add Traits menu visibility](VANILLA_LEADERS_4_6_0_EN.md#add-traits-menu-visibility)

Catalogued button eligibility for all 254 basic traits across eight menu sections. Listed the exact predecessor IDs for 36 promotions in 32 chains, documented story states, and recorded direct opposites for each rank that declares them. [Requirements for adding basic traits](BASIC_TRAIT_MENU_REQUIREMENTS_4_6_0_EN.md)

Confirmed the visibility rule for direct opposites. An add or upgrade button is hidden whenever the leader holds any trait in the target rank’s list.

Drafted the 0.0.1 specification for Edit Dossier on the UI Overhaul Dynamic leader card. It defines an event with a one-line description containing the selected leader’s name, a single Exit option and an in-game check of the character passed by the button. [Specification for 0.0.1](REQUIREMENTS_0_0_1_EN.md)
