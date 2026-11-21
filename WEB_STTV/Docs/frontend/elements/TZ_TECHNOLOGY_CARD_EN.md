# Stellaris Technological Tree View — Technology card specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Composition and input data](#composition-and-input-data)
- [Dimensions and placement](#dimensions-and-placement)
- [Name display](#name-display)
- [Name and description in the tooltip](#name-and-description-in-the-tooltip)
- [Manual variant selection](#manual-variant-selection)
- [Variant labels](#variant-labels)
- [Variant list interaction](#variant-list-interaction)
- [Selection state and placement](#selection-state-and-placement)
- [States and styling](#states-and-styling)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

Implemented the [stage 8 redesign](../TZ_FRONTEND_STAGE_8_EN.md): game icon, full name, attributes and area/rarity/danger styling. It replaces the earlier content and size restrictions below. This document retains design history; current behavior and verified scenarios are described in the [0.0.8 guide](../FRONTEND_STAGE_8_EN.md). Interactive variant switching remains deferred.

This document records the technology card requirements agreed by the user on 2026-11-16: the tooltip contains both the name and description, and technology variants are selected manually through a dropdown with mouse and keyboard support. The element has not been implemented yet; remaining details are listed in the final section for further design.

The basis is the [interface concept](../CONCEPT_EN.md) and [UI element list](../UI_ELEMENTS_EN.md). A card represents a technology in the technology field; its visible content in the first stage is limited to the name.

## Composition and input data

The card consists of a container, the shared [Text](TZ_TEXT_EN.md) element for the name, and a bound shared [Tooltip](TZ_TOOLTIP_EN.md) for the name and description. For a technology with `technology_swap` blocks, the card allows opening manual representation selection.

| Data or setting | Purpose |
| --- | --- |
| Source | Application database |
| Base technology | Original technology identifier associated with the card, links, and representation selection |
| Representation set | Base version and `technology_swap` variants with distinct database record references, string IDs, and research area information |
| Current representation | Base version or a specific variant of this technology |
| Selection handling | Reporting the selected representation to the consuming component |
| Name string ID | For example, `tech_titans`; used in the card and tooltip heading |
| Description string ID | For example, `tech_titans_desc`; used in the tooltip body |
| System-provided language | Current `ru` or `en` localization from application state |
| Dimensions and padding | Shared card geometry settings |
| Styling roles | Named variables for the card, its name, and tooltip |

The table describes the required information, rather than final API parameter names or the mechanism used to pass it. Name and description identifiers correspond to the selected representation and come from the consuming component. The shared localization mechanism receives the source, string ID, and system language and applies source configuration under the Text specification. Selected object identity and localization string ID are different data.

The catalog and `representations` array follow the [Database adapter specification](../TZ_DATABASE_ADAPTER_EN.md). Each representation contains its own ID, effective area, `nameId`, `descriptionId`, and `sourceRef`; variants additionally have `variantNumber`. The base version comes first, followed by variant blocks in database order. Representation identity refers to the loaded database; matching after a rebuild is considered alongside state persistence.

## Dimensions and placement

All cards have the same width and height. Dimensions and padding are defined in settings. Changing the window, language, hover state, or selected representation does not change card dimensions.

The technology field assigns the research area, column, and vertical position. The card displays supplied data at the assigned position; grouping and ordering within a column belong to the technology field. Selecting a variant with a different research area is reported to the field for placement changes.

## Name display

The name is centered horizontally and vertically. The shared Text element wraps at word boundaries with a two-line limit.

If the name does not fit, an ellipsis appears at the end of the visible portion under the Text rules. Names that fit do not receive an ellipsis. Display restrictions do not modify the original localization string.

## Name and description in the tooltip

For a base technology in the reference tree, the description is followed by its required technologies, availability conditions and draw weight modifiers when present. [Extended tooltip content](../TZ_TECHNOLOGY_TOOLTIP_CONTENT_EN.md)

Hovering over any part of the card, including its padding, shows the shared tooltip. Moving the pointer away from the card hides it. The entire card is the anchor element. Opening the variant list hides the card tooltip; that card's tooltip is not shown while the list is open.

The tooltip contains:

- The full technology name as its heading.
- The technology description below the heading.

Both strings come from the selected representation's prepared database localization in the current system language. The heading uses the same name ID as the card; the body uses the description ID. For a variant, this includes an inherited base description already prepared in the database. The card's two-line name limit and ellipsis do not apply to the tooltip: its text wraps at word boundaries while retaining the full content.

Placement beside the card, overlay display without moving other elements, visible boundary handling, and styling follow the shared Tooltip specification. Changing the language updates the card name and both tooltip strings.

## Manual variant selection

When no selection is set, the base technology version is displayed. Clicking a card that has variants opens a choice of the base version and its `technology_swap` blocks from the database. This selection is not offered for technologies without variants.

One representation of the base technology is displayed at a time. Selecting it updates the card name, tooltip heading, and description. The base version remains available for switching back. Other technologies retain their own selections.

This is manual representation browsing in the reference tool. Evaluating a variant's `trigger` for a particular empire and automatic selection based on game conditions belong to later stages.

Different `technology_swap` blocks can share a `name` and localized title. They remain separate variants: the selected value must distinguish the base technology and specific variant block, rather than just its title or localization key. Labels follow the rules in the next section.

The list uses the shared [Selection control](TZ_SELECT_EN.md) from the UI kit. The card itself opens the list and retains its agreed name display while the list is closed.

## Variant labels

If a variant's localized title matches the base version or another variant in the same technology's selection list, append ` (Вариант N)` in Russian or ` (Variant N)` in English to that variant's label. The base version retains its title without a suffix. A variant with a unique title in the current language is displayed without a suffix.

`N` is the position of the `technology_swap` block within the base technology in the database, starting at 1. The base version is not numbered. The number does not depend on language, title collisions, or list display order; changing language retains the selected block. For example: “Titans”, “Titans (Variant 1)”, “Titans (Variant 2)”; in Russian: “Титаны”, “Титаны (Вариант 1)”, “Титаны (Вариант 2)”.

The suffix template is stored separately for RU and EN in built-in interface localization; the title comes from the database. The suffix is composed for the selection list label and does not change database strings, localization keys, or object identifiers. Selection remains associated with a specific variant block; its label and number do not replace its identifier.

## Variant list interaction

- Clicking a card with variants opens the dropdown.
- The base version is listed first, followed by variants in database `technology_swap` block order. The currently selected option is visually marked.
- Choosing an option applies its representation and closes the list.
- Clicking outside the list or pressing `Escape` closes it without changing the selected representation.
- The card tooltip remains hidden while the list is open.
- When the card has focus, `Enter` or `Space` opens the list. In the open list, the up and down arrow keys move focus between options; `Enter` confirms the selection and closes the list. Moving focus alone does not apply a variant.

The selected option marker and navigation focus remain distinct under the shared Selection control rules. Cancelling after moving focus retains the previously selected representation.

## Selection state and placement

Selection is held in application state separately for each base technology. The card receives the current representation and reports changes to the consuming component. Changing language or theme, or moving the card to another research area, retains the selected representation.

The base identifier and technology dependencies are retained. In the current data, `technology_swap` does not override `tier` or `prerequisites`; selecting a variant creates no additional independent technology or separate links.

The research area comes from the selected variant when it specifies one, otherwise from the base technology. If the area changes, the field moves the card to the corresponding region, retaining its `tier` column and applying vertical ordering rules. For example, selecting `tech_biogenesis_titans` moves the `tech_titans` card from Engineering to Society. Switching back to the base version restores its research area.

Persistence of selected variants across launches is considered separately within the [shared state mechanism](../CONCEPT_EN.md#settings-and-state-persistence). The card introduces no persistent storage of its own.

## States and styling

Addition dated 2026-11-19: hovering over a card also highlights its displayed immediate parent connection in one color and its immediate child connections in another, following the [connection element specification](TZ_CONNECTION_EN.md#highlighting-on-card-hover). Moving the pointer away clears the highlight. Connection highlighting preserves card and route geometry and does not suppress the tooltip. This requirement belongs to the planned connection stage and has not yet been implemented.

Default and hover states are supported, together with keyboard focus for a card offering variant selection. Hover and focus visually highlight the card while retaining its dimensions and assigned position. List option states follow the shared Selection control specification.

Background, border, and text colors, together with typography properties, use named variables in the [color and typography dictionary](../CONCEPT_EN.md#color-and-typography-dictionary) for both themes and the corresponding state. The card name, tooltip heading, and tooltip description use their respective styling roles of the shared Text element.

## Acceptance criteria

Checks are performed after implementation:

- The card contains only the name, displayed through shared Text from the database source in the system language.
- All cards use the same configured width and height; dimensions remain stable when the window, language, or selected representation changes and on hover.
- A short name is centered on both axes; a long name wraps at word boundaries to at most two lines and receives an ellipsis only on overflow.
- With the variant list closed, hovering over the name or padding shows a tooltip with the full name and description; moving the pointer away hides it.
- A name shortened in the card remains fully available in the tooltip heading; the description appears separately below it.
- Switching RU/EN updates the card name, tooltip heading, and description through shared localization.
- Showing the tooltip does not change card geometry; placement near edges follows the shared Tooltip specification.
- Default, hover, and keyboard focus states use dictionary variables in both themes; hover and focus are distinguishable.
- Without a selection, the base version is displayed; cards with variants open a choice of the base version and its variants. No selection is offered for technologies without variants.
- The list uses the shared Selection control: the base version appears first, variants follow database order, and the current selection is marked.
- Choosing an option applies its representation and closes the list; clicking outside or pressing `Escape` closes it without changing the selection, including after moving focus.
- `Enter` and `Space` open the list from a focused card; arrow keys move focus, and `Enter` confirms a variant. Navigation does not apply a variant before confirmation.
- Opening the list hides the card tooltip; it remains hidden throughout interaction with the open list.
- Selection updates the name and both tooltip strings using prepared database localization; checks include a variant with an inherited description and returning to the base version.
- Distinct blocks with identical titles remain different selection values and receive “(Вариант N)” / “(Variant N)” suffixes in the list; checks cover collisions with the base version and between variants. The base version and variants with unique titles receive no suffix.
- The number follows the order of `technology_swap` blocks in the database and remains stable across language changes; checks include titles that collide in only one language. Labels do not modify original database localization.
- Changing one technology's selection does not change other selections; switching RU/EN or theme retains the selected representation.
- A variant's research area change moves the card under the field rules while retaining card size, `tier`, base ID, and dependencies; switching back restores the base area.
- The card follows the position assigned by the technology field, including area changes on variant selection.

## Subsequent implementation details

Concrete dimensions, spacing, parameter and styling variable names, and technology field integration are determined during implementation design. Lookup and missing-string behavior are established in the [Localization specification](../TZ_LOCALIZATION_EN.md); arranging tooltip content that exceeds the available area belongs to the shared Tooltip specification.

Implementation design still needs to define variant availability indication, list geometry and placement near window boundaries, and initial and restored focus, including when a card moves between research areas. The program representation of variant identifiers and references is refined in adapter implementation; restoring selections after database rebuilds belongs to the state mechanism. These details are not considered approved by this document.

[Русская версия](TZ_TECHNOLOGY_CARD_RU.md) · [UI element list](../UI_ELEMENTS_EN.md).
