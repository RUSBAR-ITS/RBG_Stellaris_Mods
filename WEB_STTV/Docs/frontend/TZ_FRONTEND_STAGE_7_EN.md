# Frontend stage 7 — simple routes and crossing bridges

## Contents

- [1. Status and objective](#1-status-and-objective)
- [2. Preserved behavior](#2-preserved-behavior)
- [3. Route shape](#3-route-shape)
- [4. Crossings and junctions](#4-crossings-and-junctions)
- [5. Horizontal bridge](#5-horizontal-bridge)
- [6. Space and coordinates](#6-space-and-coordinates)
- [7. Modules and configuration](#7-modules-and-configuration)
- [8. Validation and diagnostics](#8-validation-and-diagnostics)
- [9. Real-data acceptance](#9-real-data-acceptance)
- [10. Deliverables](#10-deliverables)

## 1. Status and objective

**Approved by the user and implemented on 2026-11-19 in frontend 0.0.7.** Results are in the [guide](FRONTEND_STAGE_7_EN.md).

Reason for the change: the crossing prohibition in [stage 6](TZ_FRONTEND_STAGE_6_EN.md) forces connections to detour around each other, creating a maze. The objective is understandable paths. Field compactness is not a goal; cards may be spaced farther apart for readability.

This stage replaces stage 6's crossing prohibition and corresponding routing method. Changes are limited to routes, their geometry, SVG rendering, related settings and checks. Backend, databases, parent selection rules and technology ordering remain unchanged.

## 2. Preserved behavior

- Display only `parent_tech → child` within one effective research area of the prepared combination.
- Preserve logical `(area, column, row)`, card sizes, DOM order and keyboard traversal. Pixel gaps may change.
- Preserve attachment sides and incoming/outgoing port conflict handling from the [connection specification](elements/TZ_CONNECTION_EN.md), particularly a bottom exit toward a side trunk when the side input is occupied.
- Draw each parent's shared trunk once, retaining segment membership in child routes. Arrows remain at child inputs.
- Preserve distinct colors for the immediate parent path and immediate child paths, highlight reset and tooltips.
- Opening a set remains explicit. Do not add loading of other database kinds, variant recalculation, cross-area or additional connections, or geometry persistence between launches.

## 3. Route shape

Choose a simple shape for a connection or a group of connections belonging to one parent, then allocate space. A foreign perpendicular line is not an obstacle requiring a detour. Merely disabling the crossing prohibition in the current search is insufficient: path shape must no longer be dictated by detours around previously drawn lines.

Technical proposal: generate a small set of orthogonal alternatives — a straight segment, a path through a side trunk, or a bottom exit turning toward a trunk. Group children by exit side and direction; plan shared portions at group level. Preserve an unobstructed straight path when attachments permit it. Detours are required for cards, prohibited overlaps and attachment conflicts.

When choosing between valid alternatives:

1. Prefer simple topology with fewer bends and no unnecessary reversals.
2. Preserve a readable shared trunk for children of one parent; do not follow unrelated branches to obtain a cheap path section.
3. For comparable shapes, prefer shorter length and fewer crossings. Reducing crossings does not justify extra detour loops.
4. Resolve equivalent choices deterministically using branch order and stable IDs.

Where several corridors are possible, trunks may move and gaps may grow. Alternative search and gap adjustments must be bounded. Return diagnostics if no valid path can be prepared. Do not hide connections or silently revert to the previous maze.

Exact algorithm structures can be refined during implementation within these constraints. No technology-ID exceptions or new graph layout library are required.

## 4. Crossings and junctions

| Situation | Behavior |
| --- | --- |
| Straight horizontal and vertical sections of different connections | Permitted crossing with a horizontal bridge |
| Actual fork in one parent's shared trunk | Shared section and junction dot |
| Bend without a fork | Normal corner, no dot |
| Coincident sections belonging to different parents | Prohibited; place them in separate parallel lanes |
| Contact with a foreign endpoint, bend or junction | Not a valid crossing; move the corridor or allocate space |
| Path through a card | Prohibited except for its designated endpoint attachment |

Crossings must lie inside straight sections, not at their endpoints, arrows, bends or junctions. Actual connections are determined by logical route membership, not accidental coordinate equality. Do not create false junctions or extra cycles within a shared trunk.

Merge shared sections first: a vertical line crossing a horizontal trunk used by several children creates one bridge, not one bridge per child.

User addition: when a branch meets a corner, place the dot at the corner vertex without a separate offset. Children sharing an exit side use a common exit corner even when their entry sides differ. An ordinary unbranched corner receives no dot.

## 5. Horizontal bridge

At a crossing, the horizontal line smoothly curves upward, passes over the vertical line and returns to its original height. The bump always points upward on screen, including for connections traveling right to left. The vertical route stays straight. There is no junction dot at the crossing.

The horizontal stroke must be continuous: straight section before the arc → arc → straight section after it. Do not retain a straight horizontal section under its own arc or replace the bridge with an empty gap.

To distinguish the arc in SVG, use a narrow field-background underlay beneath its stroke. The underlay covers only the local overlap with the vertical line: the vertical route does not bend and receives no separate empty gap in place of a bridge. Confine the underlay to the bridge so it does not erase neighboring connections. This is the technical rendering of one line passing over another, not a separate logical connection.

Arc width, height and surrounding clearance participate in geometry calculations. Multiple crossings on one horizontal line receive individual bridges with distinguishable straight sections between them. If space is insufficient, separate vertical lanes or enlarge the gap; do not turn adjacent bridges into a continuous wave.

On hover, the bridge changes color with its horizontal segment, including the shared path to a selected child. The vertical line highlights independently. The horizontal line remains the bridge even when the vertical line is highlighted: layering and shape do not change. The earlier suggestion to dynamically raise any highlighted line above others does not apply here.

## 6. Space and coordinates

Cards may be spaced farther apart horizontally and vertically. Expansion should accommodate readable trunks, parallel lines, arcs and clearances. A smaller field is not an acceptance criterion.

Calculation proceeds through logical card positions → route shapes and trunks → required gaps → pixel coordinates → crossings and bridges → validation. An arc conflict may trigger bounded reconsideration of a gap or routing lane.

Tier columns remain aligned between research areas. Cards, headings, lines, bridges, field dimensions and scrolling use one final geometry. There is no reserved column before Level-0; external padding accommodates actually needed trunks and arcs.

Neither arc strokes nor their underlays may touch cards, arrows, neighboring bridges, bends or junctions. Account for full styling dimensions, not just the centerline intersection point.

## 7. Modules and configuration

Extend the existing separation between `data/connections/`, `ui/base/Connection.tsx` and `ui/layout/Connections.tsx`. Separate route shape, lane allocation, crossing classification, bridge geometry, validation and rendering. Keep files compact and use shared geometric helpers. Do not retain the old algorithm as a separate compatibility mode.

Prepared data must distinguish:

- Logical parent/child pairs and the orthogonal route backbone.
- Unique sections with child route membership and actual junctions.
- Crossings with horizontal/vertical segment IDs, owners and coordinates.
- Bridges with arc bounds, underlay geometry and a reference to the horizontal section.

These are transient frontend data, not a new database format. Exact field names are chosen during implementation.

Extend `config/frontend/connections.json` with bridge width and height, clearance from endpoints/corners/arrows/junctions, bridge spacing, underlay thickness and adjustment limits. Choose numeric values on test diagrams. Dimensions must share one source between geometry and SVG. Remove old search settings if no longer used.

Keep connection colors in both theme dictionaries. The underlay uses the field color through a named variable rather than hardcoded white/black. Do not add menu controls.

## 8. Validation and diagnostics

Validate final geometry without repeating whole-database validation. Retain parent-pair coverage and endpoint checks. Replace the blanket crossing prohibition with a requirement that every permitted crossing has exactly one bridge; junctions must not receive bridges. Check forbidden overlaps, contacts and the full arc/underlay footprint.

Add crossing/bridge counts, logical route bend count, maximum bends per path, final gaps, field size and preparation time to reports. Count bends on the orthogonal backbone; an arc is not an additional routing bend. Total length across logical routes may count shared trunks more than once — explicitly document the counting method.

Retain `tree_connections_failed` with combination, language, settings, area and conflicting technology context. Add route or bridge conflict details. Errors must not publish a partially successful field.

| Scenario | Check |
| --- | --- |
| Simple connection with a foreign vertical line in its path | Straight route with a bridge, no vertical-line detour |
| Horizontal travel in both directions | Both arcs point upward |
| Several nearby vertical lines | Separate bridges with sufficient clearance |
| Shared trunk used by several children | One rendered bridge with correct highlight membership |
| Actual junction and ordinary corner | Dot only at the junction; neither gets a bridge |
| Arrow, corner, card or junction near a crossing | Clearance or gap/lane adjustment without overlap |
| Parallel sections from different parents | Separate lanes without merging |
| Occupied input, mixed branch, nested trunks, `3 → 4 → 3` | Simple paths preserving attachments and logical positions |
| Hover on horizontal and vertical connections | Independent colors with unchanged bridge shape and layering |
| No valid path or exhausted attempts | Diagnostics without silently losing connections |

Browser checks: RU/EN, both themes, tooltips, scrolling, window resize, menu collapse, arrow-to-card alignment and no geometry recalculation on hover. Save screenshots of nearby crossings and highlighted paths through bridges. Numerical checks alone cannot establish readability.

## 9. Real-data acceptance

Use the existing `data/stage17/database_set/manifest.json` without rebuilding, testing `reference_default` and `reference_variants` in RU and EN. Expect 679 cards and respectively 464/463 local logical connections. Cross-area links remain undrawn.

Before changes, preserve stage 6 geometry and screenshots for comparison of identical branches. After implementation, confirm unchanged logical positions for all cards and complete connections. Compare bend counts and path lengths, showing eliminated foreign-line detours separately. Do not introduce an unverified requirement that every route or the entire field must become shorter.

Visually compare forks, nested trunks, reverse transitions and dense crossings at the same language and scale. A control diagram whose only obstacle is a foreign vertical line must show a straight path with a bridge instead of a detour. Success means traceable paths without unnecessary loops, not minimum field size.

Language changes do not reread databases, hover does not run layout, and dataset files stay unchanged. Record preparation time and measurement conditions. Repeating a full load of all 15 database kinds is unnecessary for this change.

## 10. Deliverables

Implemented revised routing, crossing classification, bridges, required gaps, configuration, diagnostics and checks. Updated bilingual guides, the connection element specification, changelog and current implementation links. Working artifacts are in `data/frontend-stage7/`.

The implementation version is `0.0.7`. Stellaris testing is unnecessary. The user reviews connection appearance and readability in the browser.
