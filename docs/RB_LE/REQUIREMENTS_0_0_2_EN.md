# RB_LE 0.0.2 — Personnel Department

## Contents

- [First test](#first-test)
- [Screens and navigation](#screens-and-navigation)
- [Acceptance](#acceptance)

## First test

The agreed workflow replaces the leader card button with a Personnel Department planetary decision. Taking it on an owned colony opens the player’s empire-wide register in the standard Stellaris `v4.6.*` interface. The package includes English and Russian. Viewing a dossier preserves the character’s attributes.

## Screens and navigation

| Screen | Text | Options |
|---|---|---|
| Personnel Department decision | The personnel register holds the dossiers of the ruler and all leaders in the service of the empire. The effect tooltip reads “Opens the empire’s personnel register.” | Enact decision |
| Personnel Department | Empire: ‹name›. After a blank line, “Select a section of the personnel register.” | Ruler, Commanders, Officials, Scientists, Exit |
| Ruler’s Dossier | This register holds the current ruler’s dossier. Select the name to open it. | Ruler’s name |
| Commander Register | Select a commander to open their dossier. | Commander names |
| Official Register | Select an official to open their dossier. | Official names |
| Scientist Register | Select a scientist to open their dossier. | Scientist names |
| Dossier | Name: ‹selected leader’s name› | Back, Exit |

The main menu hides empty sections. Class registers include both assigned and unassigned leaders in service. The ruler also appears under their class. Recruitment candidates enter the register once hired.

Each register shows up to ten names per page. When there are multiple pages, “Page S/N” appears after a blank line in the description. Navigation to available adjacent pages follows the names. Back and Exit appear below each list. Back from a dossier returns to the original section and page. Back from a list returns to the main menu. Exit ends the session.

## Acceptance

Verify the decision on an owned colony, section order, hidden empty lists, both routes to the same ruler, the presence of an unassigned hired leader and exclusion of recruitment candidates. With eleven leaders of one class, open the last name, return to page two, then exit. Reopening the decision starts at the main menu. Compare names with the Leaders window and inspect the game log.
