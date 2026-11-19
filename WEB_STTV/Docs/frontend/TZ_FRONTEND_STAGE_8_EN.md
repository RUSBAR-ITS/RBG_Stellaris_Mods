# Frontend stage 8 — expanded technology card

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Card contents](#2-card-contents)
- [3. Value rules](#3-value-rules)
- [4. Representations and localization](#4-representations-and-localization)
- [5. Colors and states](#5-colors-and-states)
- [6. Dimensions and geometry](#6-dimensions-and-geometry)
- [7. Resources and UI elements](#7-resources-and-ui-elements)
- [8. Validation and acceptance](#8-validation-and-acceptance)

## 1. Status and scope

**Approved by the user and implemented on 2026-11-19.** Startup and results: [0.0.9 guide](FRONTEND_STAGE_8_EN.md). The user clarified that missing cost and weight are not displayed, including their row labels.

The basis is the user's diagram, the [technology card](elements/TZ_TECHNOLOGY_CARD_EN.md), [styling dictionary](TZ_STYLING_DICTIONARY_EN.md) and [stage 7 connections](TZ_FRONTEND_STAGE_7_EN.md). [Backend stage 18](../TZ_BACKEND_STAGE_18_EN.md) defines image and category name preparation.

This stage replaces the previous name-only restriction, two-line name truncation and card dimensions. Opening a prepared directory remains explicit. Preserve parent selection, logical tree order, the current combination and connections within research areas only. Interactive variant switching, additional connections, empire filters and game description formatting are outside scope.

## 2. Card contents

A square game icon area sits on the left; text sits on the right. Preserve image aspect ratio and fit the entire image into its area. The card has an inner surface and an outer frame matching the user's diagram.

| Element | Display |
| --- | --- |
| Name | Full text; wrapping is allowed, ellipsis and line count limits are prohibited |
| Information line | Localized research category — “Level N” — “Starting” only for `start_tech = yes` |
| Cost | “Cost:” + effective area research resource icon + base number |
| Weight | “Weight:” + base number |
| Limited repetitions | “Levels: N” only for a finite number of levels greater than one |

For multiple categories, display all in source order with a localized separator. Wrap long information lines. A hidden optional row leaves no label, icon, dash or dedicated blank row; the common card height remains unchanged.

The tooltip on hover and keyboard focus contains the selected representation's name and description. A full card name does not replace the tooltip. Preserve highlighting of immediate parent and child connections.

## 3. Value rules

| Field | Rule |
| --- | --- |
| Card level | Original game `tier`, not the layout column number |
| Starting technology | Base `start_tech = yes`; omit the marker when absent |
| Scalar `cost` | Source numeric value after backend static variable substitution |
| Block `cost` | Base numeric `factor`, without conditional modifiers |
| `weight` | Base numeric field of the main technology; selection weight, not a percentage probability |
| Missing `cost` or `weight` | Hide the complete corresponding row |
| Numeric `0` cost or weight | Keep the row visible and display `0` |
| `levels > 1` | Display the finite repetition count |
| Missing `levels`, `levels = 1` or `levels = -1` | Hide the level count row |

Repeatable technology cost is shown for its initial level: do not add `cost_per_level` without a specified research count. Do not evaluate `weight_modifier`, conditional cost modifiers or weight multipliers inside `technology_swap`. The card keeps the base technology weight; a variant weight block is not treated as a replacement scalar value.

A game tier 5 technology placed in the sixth column by tree rules displays “Level 5”. Column headings and card labels serve different purposes.

Do not treat explicitly malformed values as missing. Never render `NaN` or substitute zero: report technology ID, representation and field address, and hide the affected optional row. Missing mandatory layout data follows existing opening error handling.

## 4. Representations and localization

Use the representation selected by the prepared tree combination. Take its name, description, effective area/categories and prepared image reference. Inherit area and categories from the base technology when not overridden; a variant category list fully replaces the base list.

Take cost, base weight, `tier`, `start_tech`, `levels`, `is_rare` and `is_dangerous` from the base technology. Do not introduce arbitrary inheritance for all game fields: these explicit rules are this stage's contract. Do not select representations through empire condition evaluation in the frontend.

Pass interface labels to the shared text element using built-in RU/EN string IDs. Resolve technology/category names from the database through the existing localization source mechanism. Preserve agreed “Variant N” suffixes for duplicate names. Format numbers using a shared current-language formatter without invented units or a percentage sign for weight.

Changing language updates text, alphabetical order under existing rules and required dimensions. It does not reread game sources or launch the backend.

## 5. Colors and states

| Property | Appearance |
| --- | --- |
| Physics | Blue background |
| Society | Green background |
| Engineering | Yellow background |
| Ordinary technology | Outer frame matching the card background |
| `is_rare = yes` | Purple frame with a soft glow |
| `is_dangerous = yes` | Red frame with a soft glow |
| Both flags | Dangerous red styling takes precedence |

Rarity/danger styling is persistent, not hover-only. The glow is static. Background follows the representation's effective area. Day/night themes preserve these color meanings while adjusting surface brightness and text contrast.

User clarification after review: the frame is the entire band between the inner surface and outer card boundary. Fill that band with the rarity/danger colour, not only the outer outline.

Specify every color, font, frame and glow parameter through unambiguous element variables in the separate styling dictionary, using shared tokens where useful. Components contain no private color literals. Dimensions and spacing come from configuration.

Hover and keyboard focus remain distinguishable without replacing rarity/danger color. Their styling does not resize the card or move neighbors. Parent/child connection highlighting retains its own stage 7 colors.

## 6. Dimensions and geometry

Use one configured card width across the field and one calculated height sufficient for the tallest content in the current language and combination. A configured minimum height is allowed; a maximum that clips text is not. Reserve icon dimensions before image loading.

Order: prepare text/data → determine common dimensions using actual fonts and wrapping → calculate pixel layout/routes → show a consistent field. Measurement must not create infinite recalculation or estimate wrapping from string length alone. Session measurement caching may account for language, width and typography.

Keep existing rules for logical `(area, column, row)`. Account for new dimensions, padding and glow space when calculating gaps, connection ports, bridges, field bounds and scrolling. Lines do not pass through cards; arrowheads meet the outer boundary, not the inner text/icon region. Junction dots remain on actual corners without offsets.

Language or typography changes affecting dimensions update cards and SVG in one consistent geometry. Completing image loading does not resize cards. Theme changes require recalculation only when layout-affecting parameters change.

## 7. Resources and UI elements

Extend the compact catalog, adapter and Worker contract only with card data. Do not transfer the entire AST to the UI for a few additional fields. Apply stage 18 manifest/enrichment schemas; for an old set, report the need for explicit resource preparation without launching it automatically.

Load images from the selected directory through the manifest registry, with verification on read. Read and decode each resource once within the opened set. Do not preload unselected variant images. Repeated requests use the cache; closing/replacing the set releases object URLs and related resources.

A missing image displays a neutral placeholder in the same slot with a diagnostic. A damaged declared file is also diagnosed rather than silently substituted. Do not access absolute game installation paths from the browser. Decorative images beside already announced names should not duplicate screen-reader text; the cost icon must retain an understandable research area meaning.

Follow atomic UI structure: shared image element, existing text element, attribute row element, card composition and shared tooltip. Reuse existing state/reporting mechanisms. New module/public entity names follow project conventions; keep files compact.

## 8. Validation and acceptance

1. Verify hidden missing cost/weight, visible explicit zero, base `factor`, source weight and finite/infinite repetitions.
2. Verify all three areas, ordinary/rare/dangerous cards and dangerous precedence with both flags in both themes.
3. Check full long names, category wrapping and common dimensions in RU/EN; text and images must not overlap.
4. Check inherited icons, variant-specific images and effective area/category changes in a prepared combination.
5. Verify image caching, cleanup on set replacement, no game access and no automatic generation.
6. Test tooltips, focus, parent/child highlighting, corner dots, bridges, scrolling, resizing and menu collapse after enlarging cards.
7. On real `reference_default` and `reference_variants` combinations in RU/EN, confirm all 679 technologies and logical ordering under existing rules. Local connection counts must remain unchanged; pixel coordinates and bridge counts may change.
8. Run TypeScript checking, production build and relevant unit/browser checks; save card/field screenshots for user visual review.

Deliver the extended interface/configs, prepared working set, reports and bilingual stage 8 guide. Update affected UI element references, current instructions and both changelogs. In-game testing is unnecessary; synthetic checks do not replace the user's browser readability assessment.
