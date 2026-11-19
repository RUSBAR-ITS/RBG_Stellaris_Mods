# Frontend stage 6 — tree connections and highlighting

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Connection source](#2-connection-source)
- [3. Element and modules](#3-element-and-modules)
- [4. Attachments and routing](#4-attachments-and-routing)
- [5. Gaps and coordinates](#5-gaps-and-coordinates)
- [6. Shared trunk geometry](#6-shared-trunk-geometry)
- [7. Rendering and highlighting](#7-rendering-and-highlighting)
- [8. Configuration and diagnostics](#8-configuration-and-diagnostics)
- [9. Synthetic checks](#9-synthetic-checks)
- [10. Real dataset and acceptance](#10-real-dataset-and-acceptance)
- [11. Deliverables](#11-deliverables)

## 1. Status and scope

**Approved by the user and implemented on 2026-11-19, frontend 0.0.6.** This document combines the agreed attachments, prohibition of crossings, highlighting and gap expansion. Implementation details and checks are in the [stage guide](FRONTEND_STAGE_6_EN.md).

Build on the implemented [stage 5 grid](TZ_FRONTEND_STAGE_5_EN.md) and the [connection element specification](elements/TZ_CONNECTION_EN.md). Add parent connection rendering within each research area of the prepared combination. Tiers, parents, branch membership and ordering follow existing data and stage 5 rules.

Additional prerequisites, cross-area lines, variant changes involving backend calls, event markers, persistent geometry storage and database changes are outside this stage. Opening a dataset remains an explicit user action; data generation is not triggered.

## 2. Connection source

Use the already loaded `tree.parent_tech`, `tree.children` and selected representations from the prepared combination parameters. No further reading of the other 14 database kinds or repeated parent selection is required.

Create one logical connection for each selected parent → child pair whose cards belong to the same effective research area. Pairs are identified by technology IDs, not coordinates or localized names. Existing graph consistency checks remain in place.

Cards with `parent_tech = null` have no incoming connection. A parent in another area remains in the data, but its line is not rendered. That child may have its own displayed connections to children within its area.

## 3. Element and modules

Separate logical connection preparation, attachment selection, routing, gap sizing, geometry validation and rendering. Place pure preparation functions in a dedicated module such as `src/frontend/data/connections/`, the shared UI element in `ui/base/`, and the field connection layer in `ui/layout/`.

The shared element receives prepared geometry and a styling role. It does not read the database, select parents or order cards. The field view associates it with technology IDs and hover state.

Maintain modularity and DRY. Aim for at most 200 code lines per file; above 200, consider splitting, and above 300, extract independent parts. An external graph layout library and a new Worker pool are not required. Existing module changes are limited to connection and variable-gap integration.

## 4. Attachments and routing

Use the centers of the four card sides and the [connection specification rules](elements/TZ_CONNECTION_EN.md#attachment-rules). Main cases:

| Situation | Basic solution |
| --- | --- |
| Child to the right | Parent right → child left |
| Child to the left | Parent left → child right |
| Only child immediately below in the same column | Bottom → top |
| Multiple children in the parent's column | Side vertical trunk with branches |
| Multiple children in one other column | Shared trunk in the gap between columns |
| Mixed root branch: own-column and rightward children, left side free | Left trunk for own-column children, separate rightward continuations |
| Parent's left point occupied by an incoming connection | Bottom exit, left turn beneath the card, child entries from the left |

For other mixed and backward transitions, account for occupied points and gaps. A basic side pair does not permit merging incoming and outgoing connections from different parents. Technical generalization of the agreed case: resolve such a conflict with a separate bottom exit turning toward the required trunk; use mirrored routing when the free space is on the right. Child entry retains the direction of the applicable side branch.

Route orthogonal paths through free gaps between cards. A route may use multiple gaps. A straight segment across skipped tiers is permitted only if the path is clear. Nested trunks belonging to different parents occupy separate lanes with configured spacing.

Crossings, overlaps or merging routes from different parents are prohibited. Shared segments are permitted only for connections from the same parent. Lines must not pass through cards; arrows end at the assigned border. Preserve visual clearances accounting for stroke width, arrows and junction dots.

Traversal and selection among equivalent routes must be reproducible using tree order, child order and stable IDs. Do not introduce technology-specific exceptions. Select the exact search and lane allocation algorithm during implementation within these constraints, and verify it on synthetic and actual trees.

## 5. Gaps and coordinates

First obtain the stage 5 logical layout: `(area, column, row)`. Then calculate routes and required space before converting the layout to pixels. Logical rows and columns, traversal order, card dimensions and tree membership remain unchanged.

Column and row gaps may increase only where routes require additional space. Existing `columnGap`, `cardGap` and `fieldPadding` settings serve as baseline minimum spacing. Automatic expansion does not mean increasing all gaps to one maximum size.

Tier columns stay aligned across research areas. For each column boundary, use a width sufficient for all areas; other boundaries retain their individual sizes. Vertical gaps are calculated separately for each area's rows. Tier headings and cards use the same column coordinates.

Before Level-0, allow only the minimum spacing needed for its side trunks; there is no reserved column. If an external route needs room at another field boundary, account only for the required padding. Keep research area headings outside routes.

Cards, the connection layer, area dimensions and scrollbars receive one final geometry. Implementation may use explicit positions or variable CSS Grid gaps; do not duplicate coordinate formulas independently in CSS and routing.

Expansion provides room for separate lanes but cannot by itself eliminate an incorrectly routed crossing. If no valid route is found, use section 8 diagnostics; silently hiding a connection or changing its parent is prohibited.

## 6. Shared trunk geometry

The prepared result must contain:

- Logical connections: parent and child IDs, area, selected attachments and ordered route.
- Card rectangles, column and row positions, final gaps and field dimensions.
- Render segments: endpoints, owning parent and membership in logical connections.
- Child entry arrows and actual branch junction dots.

These are frontend memory data requirements, not a new database format. Select exact programming field names during implementation.

Split shared trunks into segments at branch points. Render each shared segment once while retaining the logical connections using it. This supports highlighting one child's path without coloring neighboring branches. Ordinary bends do not receive junction dots.

## 7. Rendering and highlighting

Use an SVG layer beneath the cards within the same scrolling field. Shared trunks, branches and arrows move with the cards; geometry does not need recalculation on every scroll event. The layer does not intercept the pointer, wheel or keyboard focus.

Hovering over a card highlights the full path from its immediate parent in one color and the paths to its immediate children in another. Highlight applicable trunk segments, arrows and dots. Other branches retain their default color. Leaving clears the highlight; moving to another card changes the highlighted set.

Handle roots, leaves, cross-area parents and missing children without inventing connections. Do not highlight other generations. Hovering does not recalculate routes, read the database or resize the field; the existing tooltip continues to work. This stage does not add connection highlighting on keyboard focus.

RU/EN recalculates ordering and geometry from loaded data. Theme changes styling; menu collapse and window resizing change the viewport. These actions do not change routes relative to cards. Clamp scrolling to updated field bounds.

## 8. Configuration and diagnostics

Provide a separate extensible configuration such as `config/frontend/connections.json` for routing geometry settings: card clearance, lane spacing and attachment exit length. Arrow sizes, junction sizes and stroke width must have a single source for occupied-space calculation and named styling variables.

Both theme dictionaries assign `--sttv-connection-color-default`, `--sttv-connection-color-parent` and `--sttv-connection-color-children`. Parent and child colors must differ. Choose exact numeric values and colors during implementation and verify them visually. No additional menu settings are introduced.

After preparation, check the geometry being used: pair coverage, endpoint attachments, absence of card intersections, prohibited route crossings and overlaps. Do not repeat full database validation or semantic parent selection.

If correct connections cannot be prepared, fail field preparation through the existing error mechanism with a localized message. Include conflicting technology/connection IDs, area, attachments, coordinates, routing parameters, combination and language in the report. Do not show a successful field with silently omitted connections or retry gap expansion indefinitely.

Add displayed logical connection counts, shared segment/junction counts, expanded gaps, final dimensions, settings and routing time to successful reports. Distinguish logical connections from their rendering segments.

## 9. Synthetic checks

| Scenario | Expected result |
| --- | --- |
| Leaf, root, empty area | Correct absence of the applicable connections |
| Rightward, leftward and multi-tier transitions | Correct endpoint cards, arrows and obstacle routing |
| Only child immediately below | Bottom → top attachment |
| Multiple own-column or other-column children | Their parent's trunk and individual branches |
| Agreed `A → B/C/E`, `C → D` examples, with and without incoming `P → A` | Left trunk; bottom exit when the incoming point is occupied |
| Backward tier chain `3 → 4 → 3` | Preserved rows/columns and separate incoming/outgoing connections |
| Nested trunks and occupied intermediate cells | Separate lanes, no crossings or paths through cards |
| Insufficient gap width/height | Local expansion without changing logical card positions |
| Level-0 side trunk | Minimum necessary padding without a reserved column |
| Cross-area connection and returning descendant | No cross-area lines, internal connections retained |
| Hovering over a child on a shared trunk | Full child path highlighted, neighboring branches remain default |
| Hovering over an intermediate card | Distinct parent/child path colors, unchanged geometry |
| Repeated calculation with identical inputs | Identical attachments, routes and gaps |
| Invalid geometry or impossible route | Contextual diagnostics, no partial successful result |

Browser checks: hover and leave, moving between cards, both themes, RU/EN, scrolling, menu collapse, resizing, tooltips, report export and line endpoints matching card borders.

## 10. Real dataset and acceptance

Use the existing `data/stage17/database_set/manifest.json` without rebuilding. Check `reference_default` and `reference_variants`, each in RU and EN. Reference counts from [stage 5](FRONTEND_STAGE_5_EN.md#checks-and-measurements) are calculated from 501 saved parent relationships excluding cross-area links:

| Combination | Cards | Cross-area relationships without lines | Displayed logical connections |
| --- | --- | --- | --- |
| `reference_default` | 679 | 37 | 464 |
| `reference_variants` | 679 | 38 | 463 |

Stage 6 implementation confirmed these reference values in RU and EN. If the source dataset changes, explain the discrepancy before proceeding rather than adjusting data to match.

Automatically verify all routes for prohibited crossings/overlaps and paths through cards. Visually check linear chains, forks, nested trunks, backward transitions and Level-0 in both themes. Check shared trunk highlighting separately.

Logical card positions must match stage 5 for identical inputs; pixel dimensions may increase to accommodate connections. Verify that language changes do not reread the database and hovering does not run layout. Measure geometry preparation time and record measurement conditions. Dataset files remain unchanged.

## 11. Deliverables

Deliver the connection UI element, routing and variable-gap module, field and hover integration, configuration and styling variables, diagnostics and checks. Keep working reports and screenshots in `data/frontend-stage6/`.

The bilingual stage guide, changelog and current frontend links have been updated. Implementation patch version: `0.0.6`.

Stellaris does not need to be launched for verification. User checks concern tree readability, distinguishable highlighting and browser viewing usability.
