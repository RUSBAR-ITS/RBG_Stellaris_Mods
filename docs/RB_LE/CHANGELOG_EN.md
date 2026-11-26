# Leader Editor — changelog

## Contents

- [Dossier menu design](#dossier-menu-design)
- [Version 0.1.0](#version-010)
- [Version 0.0.19](#version-0019)
- [Version 0.0.18](#version-0018)
- [Version 0.0.17](#version-0017)
- [Version 0.0.16](#version-0016)
- [Version 0.0.15](#version-0015)
- [Version 0.0.14](#version-0014)
- [Version 0.0.13](#version-0013)
- [Version 0.0.12](#version-0012)
- [Version 0.0.11](#version-0011)
- [Version 0.0.10](#version-0010)
- [Version 0.0.9](#version-009)
- [Version 0.0.8](#version-008)
- [Version 0.0.7](#version-007)
- [Version 0.0.6](#version-006)
- [Version 0.0.5](#version-005)
- [Version 0.0.4](#version-004)
- [Version 0.0.3](#version-003)
- [Version 0.0.2](#version-002)
- [Version 0.0.1](#version-001)
- [Vanilla research](#vanilla-research)

## Dossier menu design

Clarified portrait selection. Every visit starts on the first option for each control. Cancel preserves the original appearance and Accept saves the displayed preview. Added counts from the vanilla 4.6.0 files for all five appearance controls. [Parameters and checks](DOSSIER_MENU_REQUIREMENTS_EN.md#portrait-editor-prototype)

The portrait editor specification now proposes a test for choosing phenotype, texture, hairstyle and clothing separately. It covers both first-time editing of a vanilla leader and reopening a previously chosen combination. [Portrait editor prototype](DOSSIER_MENU_REQUIREMENTS_EN.md#portrait-editor-prototype)

Added Change portrait to the Personal details menu structure. The prototype specification now defines command visibility and how to verify preview, cancellation and application of a single appearance change. [Portrait editor prototype](DOSSIER_MENU_REQUIREMENTS_EN.md#portrait-editor-prototype)

Refined the portrait preview design for Personal details. The controls cycle through variants in the leader's current portrait set. Unique appearances cannot be edited. The specification records outstanding technical questions and verification scenarios. [Personal details](DOSSIER_MENU_REQUIREMENTS_EN.md#personal-details)

Added Change gender to the dossier specification for every selected leader. The screen offers the other two vanilla values regardless of species, empire or unique character status. [Personal details](DOSSIER_MENU_REQUIREMENTS_EN.md#personal-details)

Confirmed the Change personal ethic command. The specification gives Rejuvenate and Age up steps of 1, 5, 10, 50 and 100 years. Rejuvenation can bring organic leaders down to age 16 and synthetic leaders down to age 0. [Personal details](DOSSIER_MENU_REQUIREMENTS_EN.md#personal-details)

Updated the labels to Add Traits and Remove Traits. The first-stage specification gives both catalogs only Back and Exit. Future removal covers every trait held by the selected leader, including traits outside the Add Traits catalog.

The specification records four dossier sections, a shared menu for adding and removing traits, and separate XP and level actions. Changes to personal ethics and age are proposed for discussion. [Menu structure and personal details proposal](DOSSIER_MENU_REQUIREMENTS_EN.md)

## Version 0.1.0

Removed the 103 diagnostic entries written to `error.log` when the former occupation catalogue opened. The in-game test of 0.0.19 covered all 101 occupations and three page changes without an `Invalid context switch` error. The release includes the verified branch office checks. [Occupation visibility](DOSSIER_MENU_REQUIREMENTS_EN.md#occupation-visibility-in-460)

## Version 0.0.19

Fixed the branch office owner check in the former occupation catalogue. On colonies without a branch office, the editor skips that check for `criminal`, `dystopian_enforcer`, `enforcer` and `healthcare`. Existing jobs and other sources remain eligible. The diagnostic markers are still enabled for in-game verification. [Occupation visibility](DOSSIER_MENU_REQUIREMENTS_EN.md#occupation-visibility-in-460)

## Version 0.0.18

Opening the former occupation catalogue writes the start and end of the scan to `error.log`, along with each occupation ID immediately before its availability check. Paging does not repeat the trace. The order of the entries shows which occupation the editor was checking when an error occurred. [Catalogue diagnostics](DOSSIER_MENU_REQUIREMENTS_EN.md#occupation-visibility-in-460)

## Version 0.0.17

Fixed two formulas the former occupation catalogue uses to determine whether a subject can host another overlord holding. In 0.0.16 Stellaris rejected dynamic expressions in the `base` field. The generator now starts with a numeric base and adds the empire modifiers and calculated quota through `add`.

A regression check detects the previous error in the generated game files. Nine synthetic cases covered the overlord bonus, the four-holding cap and buildings spread across several colonies. The game log confirmed that both parsing errors were gone. A separate `Invalid context switch` error recurred when the catalogue opened. [Requirements and checks](DOSSIER_MENU_REQUIREMENTS_EN.md#occupation-visibility-in-460)

## Version 0.0.16

Leader registers and the occupation catalogue show Next, Previous, Back and Exit in that order. Both page controls appear when the list has at least two pages. Paging wraps in either direction between the first and last pages.

Back opens the parent of each submenu. Exit closes the entire department. The portrait preview uses the full labels Next variant and Previous variant. Returning from an individual feature keeps the working preview. Returning from the feature list discards it. [Navigation rules](DOSSIER_MENU_REQUIREMENTS_EN.md#navigation-across-all-menus)

## Version 0.0.15

In-game testing confirmed that the selected leader's former occupation changes successfully.

The dossier now includes Background. Players can view the selected leader's former occupation and choose another available to the leader's current empire. The list checks the leader's personal ethic, vanilla scripted assignments and conditions on owned colonies, including inhabited arks. Leaders with the Gestalt Consciousness personal ethic have no Background command.

The catalogue contains 101 occupations and shows up to ten eligible choices per page. Selecting one returns the player to the same leader's updated dossier. Added Russian and English menu text, a rule generator and a check that each button assigns the occupation it displays. [Visibility rules and in-game checks](DOSSIER_MENU_REQUIREMENTS_EN.md#occupation-visibility-in-460)

## Version 0.0.14

Personal details now includes Change gender. The screen shows the selected leader’s portrait, name and current gender. Choosing either of the other two values refreshes the screen. Robots and unique leaders can also use this command.

`game.log` records the leader’s gender after a change, the saved RB_LE appearance number when inspecting Personal details, and the catalogue opened by the portrait editor. The catalogue entry includes the phenotype count and the number of attachment or hairstyle choices for its first phenotype.

In-game testing confirmed that selecting Male switched a vanilla human portrait and opened the male portrait catalogue. [Test result](VANILLA_LEADERS_4_6_0_EN.md#editor-scope-and-character-background)

## Version 0.0.13

Each combination of phenotype, texture, stage, attachment and clothing has its own portrait key. Accept assigns the preview key to the selected leader and reads it back before returning to Personal details. A change to the hairstyle or clothing alone now selects a distinct portrait.

Each control displays Next above Previous. Both directions wrap between the first and last choices, including transitions between phenotypes with different sets of appearance details.

## Version 0.0.12

Accept now applies the displayed portrait key and the chosen attachment and clothing to the selected leader. Before returning to the dossier, the editor reads the portrait key back from the leader. If the game fails to confirm the change, the editor displays a message and restores the previous layer indices. Each application records its result in `game.log`. [Portrait effects](../../RB_LE/mod/common/scripted_effects/rb_le_portrait.txt)

## Version 0.0.11

Fixed the portrait effect chain that reached the Stellaris 4.6.0 nesting limit during startup. Opening the editor, stepping through options and accepting now share one hidden event. It selects the phenotype, checks the control ranges and prepares the preview. The build check follows scripted effects from each menu button. [Editor events](../../RB_LE/mod/events/rb_le_portrait_events.txt)

## Version 0.0.10

Personal details now offers a portrait editor for ordinary leaders across species. It recognises the current appearance and offers the available phenotypes, colours, hairstyles or attachments, clothes and evolution stages. Each visit starts on the first choices. Players can accept the preview or cancel to keep the original appearance. A separate sample species supplies the preview. [Editor behaviour and in-game checks](DOSSIER_MENU_REQUIREMENTS_EN.md#portrait-editor-prototype)

Added a vanilla catalogue generator and a graphics resource check. Five vanilla attachment selectors lack definitions and two stages of `bio7` lack mask textures. The editor offers the remaining available choices for those portraits. [Build and verify the catalogue](../../Instruments/RB_LE_Portraits/README_EN.md)

## Version 0.0.9

Selecting phenotype 2 repeatedly generated a fresh portrait each time. The editor now creates one preview for the selected scientist and reuses it when the player returns to that phenotype. Apply takes the appearance from the displayed preview. The reverse arrow shows the scientist's original portrait for comparison. Matching hair, clothes and colours after application requires an in-game check. [Portrait preview test](DOSSIER_MENU_REQUIREMENTS_EN.md#portrait-editor-prototype)

## Version 0.0.8

Personal details displays the selected leader in the vanilla communication window. In a separate test game, `event rb_le.90` sets up a trial with two human phenotypes. Preview and Apply are available only for the test scientist when the current phenotype is recognized. Recognition and preservation of hairstyle and clothing require in-game verification. [Test procedure](DOSSIER_MENU_REQUIREMENTS_EN.md#portrait-editor-prototype)

## Version 0.0.7

The dossier lets the player change the selected leader’s personal ethic and age, grant or remove XP, and lower their base level. Each age step displays the resulting age. Traits opens two catalogs with Back and Exit. Returning from the dossier restores the originating register page. [Menu rules and in-game checks](DOSSIER_MENU_REQUIREMENTS_EN.md)

## Version 0.0.6

The dossier shows the selected leader's gender immediately after their name. The English and Russian screens use the game's own labels. [Dossier fields](REQUIREMENTS_0_0_4_EN.md#dossier-fields)

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

Prepared visibility rules for the 102 original candidates and a register of vanilla job providers. There are 101 conditional choices. The only slot grant for `sand_caretaker` requires a Machine Intelligence without the gestalt ethic. Corrected its catalogue verdict and the totals. [Specification and tables](DOSSIER_MENU_REQUIREMENTS_EN.md#occupation-visibility-in-460)

Clarified former occupation eligibility for playable empires in the dossier requirements. Overseer is excluded from selection. Confirmed vanilla assigns it to the leader gifted to a Scion. [Selection rule](DOSSIER_MENU_REQUIREMENTS_EN.md#former-occupation)

The dossier requirements now filter former occupations by the leader's personal ethic, an overall Yes in the catalogue and availability in the current empire. [Selection rules](DOSSIER_MENU_REQUIREMENTS_EN.md#former-occupation)

The former occupation catalogue now shows an overall answer for each ID, pop-based generation, its basis and an example source of job slots. The direct assignment columns explicitly identify their script commands. Civilian is marked as available through pop-based generation. [Reading the result](BACKGROUND_JOBS_4_6_0_EN.md#which-jobs-can-be-a-former-occupation)

Surveyed 369 job definitions and their contextual names for the Background menu. The CSV records display name relationships, explicit leader assignments, predicates and generation weights. [Findings and menu proposal](BACKGROUND_JOBS_4_6_0_EN.md)

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
