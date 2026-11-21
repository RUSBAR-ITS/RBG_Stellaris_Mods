# Specification. Technology page

## Contents

- [Purpose and contents](#purpose-and-contents)
- [Navigation](#navigation)
- [Acceptance](#acceptance)

## Purpose and contents

The technology page is a standalone view in `views/` for reading the details of one base technology. Use its full localized name as the heading, followed by its description. Then show research prerequisites, availability conditions, draw weight modifiers and acquisition sections with confirmed sources. Follow the order and display rules in the [stage specification](../TZ_TECHNOLOGY_PAGE_AND_ACQUISITION_EN.md#three-acquisition-sections).

The page and tooltip use the same API response and shared detail components. With the same language and DLC selection, both show the same wording, condition groups, colors, game icons, percentages and formulas. Long content scrolls with the page.

## Navigation

Give the page its own address containing the game ID. The proposed address for the test deployment is `/#/technology/tech_ordered_retreat`. The card context menu opens the page in the current tab. Middle click opens it in a new tab. A link from the tree carries the language and applied DLC selection, including an explicitly empty set. A link without these settings uses the reference defaults.

On direct navigation or browser refresh, request details by ID. Opening the page requires neither loading the tree nor calculating coordinates. After navigating from the tree in the same tab, browser Back restores the previous tree position. An unknown ID shows a localized message and a link to the tree.

## Acceptance

Compare the page and tooltip for the same technology in RU and EN with matching DLC selections. Check long descriptions, compound conditions and technologies with and without acquisition sources. Test navigation from the card, browser Back, a new tab, direct link refresh and an unknown ID. Verify the DLC labels on a link with default settings and a link with all DLCs explicitly disabled.
