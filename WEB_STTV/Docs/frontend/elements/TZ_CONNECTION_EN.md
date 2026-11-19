# Stellaris Technological Tree View — connection element specification

## Contents

- [Status and purpose](#status-and-purpose)
- [Crossings and corner junctions](#crossings-and-corner-junctions)
- [Responsibilities](#responsibilities)
- [Attachment points](#attachment-points)
- [Attachment rules](#attachment-rules)
- [Mixed branch with a free left side](#mixed-branch-with-a-free-left-side)
- [Incoming connection on the parent's left](#incoming-connection-on-the-parents-left)
- [Branches and constraints](#branches-and-constraints)
- [Rendering and styling](#rendering-and-styling)
- [Gap expansion](#gap-expansion)
- [Highlighting on card hover](#highlighting-on-card-hover)
- [Planned checks](#planned-checks)
- [Implementation details](#implementation-details)

## Status and purpose

Implemented under approved [stage 6](../TZ_FRONTEND_STAGE_6_EN.md) and [stage 7](../TZ_FRONTEND_STAGE_7_EN.md). Current routing, bridges and check results are described in the [0.0.7 guide](../FRONTEND_STAGE_7_EN.md).

The element extends the [stage 5 grid](../TZ_FRONTEND_STAGE_5_EN.md) and belongs to the [UI element list](../UI_ELEMENTS_EN.md). Display only selected `parent_tech` connections to children in the same effective area of the prepared combination. Additional prerequisites and cross-area connections remain undrawn.

## Crossings and corner junctions

The approved [stage 7 rules](../TZ_FRONTEND_STAGE_7_EN.md) apply: simple paths may cross; the horizontal line receives a continuous upward bridge while the vertical stays straight. The arc has a field-colored underlay. A crossing is not a junction and receives no dot.

A branch dot sits at the corner vertex without a separate offset. Children sharing an exit use one exit corner, including different child entry sides. An ordinary unbranched turn is unmarked. The bridge always remains above the vertical; hover only changes color. Implemented in [0.0.7](../FRONTEND_STAGE_7_EN.md).

## Responsibilities

1. Attachment selects the sides and points where a connection leaves the parent and enters the child.
2. Routing determines the path between these points, accounting for cards and other branches.
3. The UI element renders the prepared path with the assigned styling.

A connection is identified by its endpoint card IDs and selected attachment sides. Coordinates are calculated from the current layout and card dimensions. Parent selection remains the responsibility of the existing database enrichment; the connection element does not select parents.

Programming contract: a logical route contains parent and child IDs, attachment sides and points. A unique segment contains its parent ID and the child routes using it; the UI element receives an SVG path with arcs and a styling role.

## Attachment points

A card provides four points: the centers of its left, right, top and bottom borders. The UI element supports attachment to any of these points. The connection direction is from parent to child.

Points belong to card borders, rather than the text inside. Their coordinates update with card placement.

## Attachment rules

| Situation | Parent exit and child entry |
| --- | --- |
| Child in a column to the right of the parent | Right → left |
| Child in a column to the left of the parent | Left → right |
| Only child immediately below in the same column | Bottom → top |
| Multiple children in the parent's column | Side attachments through a shared vertical trunk |
| Multiple children in one other column | Shared trunk between columns with branches to the children |

Basic side attachment uses the right sides of the parent and children for a right trunk, and their left sides for a left trunk. The parent's exit may differ from the children's entry side: the agreed bottom-exit case is described below. Own-column children use a left trunk; an occupied incoming port moves the exit to the bottom. Stage 7 rules refine routing.

Example of a trunk on the right; arrows point toward the children:

```text
[Parent]  --+
           |
[Child 1] <+
           |
[Child 2] <+
```

Skipping tiers does not change the applicable attachment sides. The route between them must stay outside other cards. The table does not define a complete obstacle routing algorithm; the agreed refinement for a mixed group follows below.

## Mixed branch with a free left side

When a root has children in its own column and to its right, and the left side is free for routing, place the trunk serving its own-column children on the left. Its exit and child entries use the left card sides. Rightward continuations use the parent's right side and the corresponding children's left sides.

```text
+-- [A] --> [B]
|
+-> [C] --> [D]
|
+-> [E]
```

Here, `B`, `C`, `E` are children of `A`, while `D` is a child of `C`. The left trunk belongs to `A`; the `C → D` connection runs to the right of `C` without crossing it.

The rule is agreed for a free left side. The incoming connection from the left is covered next. Children on lower tiers and occupied gaps are handled by routing in [stage 7](../TZ_FRONTEND_STAGE_7_EN.md#3-route-shape).

## Incoming connection on the parent's left

If a connection from `P` enters `A` from the left, `A`'s own left trunk serving its same-column children leaves through `A`'s bottom point. In the gap beneath the card, the route turns left, then continues down and enters the children from the left.

```text
[P] --> [A] --> [B]
         |
      +--+
      +>[C] --> [D]
      |
      +>[E]
```

Here, `B`, `C`, `E` are children of `A`, while `D` is a child of `C`. The incoming `P → A` connection stays above the turn and separate from `A`'s trunk. The `A → B` and `C → D` continuations use their parents' right sides.

The parent's exit and child entries of a shared trunk may belong to different card sides. Perpendicular crossings with foreign branches are permitted here with stage 7 bridges; merging and corner contacts are prohibited.

## Branches and constraints

Perpendicular crossings of straight sections owned by different parents are permitted with bridges. A shared section of one parent is drawn once; an actual fork has a dot at its exact junction. Coincident foreign sections and contacts with foreign endpoints, corners or junctions are prohibited.

Lines do not cross cards; contact is allowed at designated attachments. Arc and underlay clearances from arrows, cards, corners and other connections are validated. Simple-shape selection and gap expansion are bounded; failure produces diagnostics.

## Rendering and styling

A route consists of horizontal and vertical segments joined at right angles. A small arrow is displayed at the child endpoint.

Connections occupy a shared layer beneath the cards inside the scrolling field. Cards and lines move together when scrolling. Layout changes, including language changes, update the points and routes.

Line colors use named variables in the [styling dictionary](../TZ_STYLING_DICTIONARY_EN.md). Line thickness, arrow size and junction radius are named values in `config/frontend/connections.json`; thickness also reaches CSS through `--sttv-connection-stroke-width`. Both day and night themes are supported.

## Gap expansion

Grid gaps may expand when there is insufficient room for lines. Preserve tiers, logical rows and technology order, card dimensions and branch membership. Gaps also account for arcs, underlays and clearance.

Expand only gaps requiring additional room. Before Level-0, retain minimum necessary padding without a reserved column. Cross-area sizing coordination and impossible-route handling are defined in the [stage 7 specification](../TZ_FRONTEND_STAGE_7_EN.md#6-space-and-coordinates).

## Highlighting on card hover

Hovering over a technology card highlights the following simultaneously:

- The connection from its immediate parent to this card, using the parent connection color.
- Connections from this card to its immediate children, using a different color shared by child connections.

Highlighting applies to connections already displayed within the research area for the selected combination. A root has no parent connection to highlight; a leaf has no child connections. Other generations of the tree are not highlighted automatically.

Highlight the entire route of each applicable connection, including participating shared trunk segments, its arrow and junction dots along the route. Hovering over one child highlights the shared path from its parent to that child, while branches to its siblings keep their default color. A shared trunk continuation beyond the selected path also keeps its default color.

Moving the pointer away clears the highlight; moving to another card selects that card's connections. Highlighting changes existing route styling while preserving route geometry and card positions. The card tooltip continues to follow its own specification.

Provide separate styling dictionary variables:

| Variable | Purpose |
| --- | --- |
| `--sttv-connection-color-default` | Default connection color |
| `--sttv-connection-color-parent` | Connection to the hovered card's parent |
| `--sttv-connection-color-children` | Connections to the hovered card's children |

Parent and child connection colors are distinct in both themes; dictionary values are listed in the [guide](../FRONTEND_STAGE_7_EN.md#configuration-and-styling). Keyboard focus highlighting is not enabled.

## Planned checks

- Direction and attachments for rightward, leftward and immediately downward transitions.
- Shared trunks for multiple children in the parent's column and in another column.
- A left trunk for a mixed branch with a free left side and an independent rightward continuation from its child.
- A bottom exit to a left trunk when an incoming connection occupies the left side, without merging into that incoming connection.
- Expanding required gaps without changing logical card positions; minimum padding before Level-0.
- One bridge per crossing; no card penetration or merged foreign connections. Branch corner dots have no offset.
- Arrows and branches match the actual parent relationships of the prepared combination.
- No additional prerequisite or cross-area connections.
- Attachment points match card borders after scrolling and language changes.
- Styling in both themes through dictionary variables.
- Distinct incoming and outgoing connection colors on hover, clearing and transferring the highlight between cards without changing geometry.
- Root, leaf and intermediate card highlighting; shared trunks are highlighted only along applicable routes, leaving neighboring branches in their default state.

Completed checks and limitations are listed in the stage 7 guide.

## Implementation details

The [stage 7 specification](../TZ_FRONTEND_STAGE_7_EN.md) defines simple shapes, bridges, gap expansion and checks. Bounded lane selection, trunk merging, SVG rendering and highlighting are implemented; old A* search was removed. See the [guide](../FRONTEND_STAGE_7_EN.md).

