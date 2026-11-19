# Frontend stage 5 — tree grid from a prepared combination

## Contents

- [1. Status and scope](#1-status-and-scope)
- [2. Data and combination](#2-data-and-combination)
- [3. Configuration and modules](#3-configuration-and-modules)
- [4. Trees within areas](#4-trees-within-areas)
- [5. Tree and branch ordering](#5-tree-and-branch-ordering)
- [6. Row and height calculation](#6-row-and-height-calculation)
- [7. Rendering and interaction](#7-rendering-and-interaction)
- [8. Input checks and diagnostics](#8-input-checks-and-diagnostics)
- [9. Synthetic checks](#9-synthetic-checks)
- [10. Real set and acceptance](#10-real-set-and-acceptance)
- [11. Deliverables](#11-deliverables)

## 1. Status and scope

**Approved by the user and implemented on 2026-11-19, frontend 0.0.5.** Agreed decisions are collected in the [chain and sorting rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md). Actual results and limitations are in the [implementation guide](FRONTEND_STAGE_5_EN.md).

Replace independent column sorting with a tree grid using stored `parent_tech` and `children`. Use a prepared [stage 17](../TZ_BACKEND_STAGE_17_EN.md) set and [stage 16](../TZ_BACKEND_STAGE_16_EN.md) results. Python selects parents; the frontend only determines card order and coordinates.

The user chose a first stage for a **prepared combination**. Variants come from its parameters. Interactive variant changes, calling Python from the browser, an HTTP API and new parent calculations are excluded. Automatic database generation, writing to the source set, persisting coordinates between sessions and portable packaging are also excluded.

Areas run from top to bottom: physics, society, engineering. Keep the simple design: existing title-only cards, title/description tooltips, RU/EN, themes, menu, status panel and scrolling. Connection lines, additional prerequisites and special acquisition methods are not displayed yet.

## 2. Data and combination

Preserve explicit directory opening and the stage 4 streaming reader. Initial opening reads the manifest and technology documents; the other 14 kinds are unnecessary for placement and must not be loaded to repeat parent selection.

Extend the compact adapter projection without transferring the full AST to the main thread:

| Source | Required data |
| --- | --- |
| Technology definition | Base ID, `tier`, `start_tech`, `levels`, technology requirements and `NodeRef` |
| Representation | `base` / `swap:N` ID, effective area, name and description references |
| `node.enrichments.technology_tree[combination_id]` | `parent_tech`, `children`, `status` |
| `manifest.technology_tree` | Enrichment version, selected combination, its parameters, input and result revisions |

Missing `start_tech` means `false`. Missing `levels` does not imply infinite repetition. Read `start_tech` and `levels` from the base definition, not from a number in its ID. Keep game `tier` separate from display tier.

Identical repeated `start_tech = yes` entries, previously recorded for three technologies in the [starting technology study](STARTING_TECHNOLOGIES_EN.md), produce one flag value. Conflicting values stop opening with an error.

Select the combination through configuration; initially use `reference_default`. Open that specific combination rather than the first available one. Select every representation from its stored, fully normalized `parameters.variants`. Do not display a changed variant with parents from the base combination.

A missing combination, unsupported version, incomplete records or input revisions that do not match the manifest must stop opening with diagnostics. Do not automatically run the backend, substitute another combination or fall back to the old sorting. Following external enrichment, the user explicitly opens the set again.

## 3. Configuration and modules

Proposed separate configuration: `config/frontend/tree_layout.json`. It defines the combination ID, starting-root priority, digits `0–9` removed when comparing IDs, RU/EN sort locales and the repeatable technology rule: `levels = -1`, game `tier = 5` and at least one technology prerequisite → display tier 6. Do not restrict that prerequisite's research area.

Add extracted game field names to the existing adapter configuration. Obtain area order from the existing setting; card dimensions, gaps, headings and padding from `config/frontend/interface.json`; colors and fonts from the styling dictionary. Do not duplicate numeric values between coordinate calculations and CSS.

Separate enrichment extraction, tree preparation, name comparison, geometry and React rendering. Proposed location for pure geometry modules: `src/frontend/data/tree/`. Remove the former independent column ordering and its adapter validation call; do not retain it as a fallback mode.

Reuse common helpers. Aim for at most 200 code lines per file; review splitting above 200 and extract independent parts above 300. Do not introduce an automatic graph layout library or another Worker pool. Extraction stays in the existing Worker; a pure frontend module calculates compact geometry.

## 4. Trees within areas

Use the selected representation's area for placement. An independent tree within an area starts with a technology that has:

- stored `status = root` and `parent_tech = null`;
- `status = ambiguous` and `parent_tech = null`: keep the card and report its state;
- a confirmed parent in another research area.

In the last case, retain the original link but exclude it from cross-area geometry. Do not modify `parent_tech`, remove the child from stored `children` or find a replacement parent. Traverse only children with the same effective area when preparing a tree; each area transition starts another tree. A descendant returning to the original area also starts a separate tree there.

Place every technology exactly once. Having one or several prerequisites does not exclude a card. `weight = 0` and special acquisition conditions do not currently change field membership, ordering or styling. Additional prerequisites do not impose vertical constraints between selected branches.

## 5. Tree and branch ordering

First place whole trees whose initial technology has `start_tech = yes`, then other trees. A starting descendant does not change its tree's group or move separately. This replaces the former requirement to place all starting cards above all non-starting cards.

Within each group, compare initial technologies' displayed names in the current language. Use the same localization resolver as the card, including existing missing-text behavior. Use language-aware ordering with an explicit locale; break equal results with stable base ID comparison. Ordering must not depend on file reading order or JSON property enumeration.

For each parent, place a child whose ID exactly matches the parent's after removing digits `0–9` first; preserve other characters. Its descendants occupy their branch before the next child. Sort other children by name in the current language, then ID. If no ID matches, apply that order to all children.

**Approved technical addition:** if multiple IDs match, place the entire matching group first, ordering its members by name and ID. This neither chooses a new parent nor makes a game alternative mandatory. The current set has no such cases; verify this behavior synthetically.

## 6. Row and height calculation

A card's layout coordinate is `(area, column, row)`. `column` is its display tier; `row` is a nonnegative integer within the area. Columns share row indices, preserving empty positions. Tree depth does not determine the column.

Proposed algorithm: sequential top-down traversal accounting for occupied cells:

1. Start the first tree at row 0. Place its root in its own column.
2. Order children according to section 5. The first child tries its parent's row when its column differs; for the same column, start at the next row.
3. If the target cell is occupied, including by an ancestor, find the first free row below while respecting the branch's lower starting bound. Then calculate descendants relative to that position. Do not move ancestors or previously placed sibling branches.
4. Place that child's entire branch. Start the next child below its lowest occupied row, even if earlier rows have vacant cells.
5. A tree/branch's bottom boundary is the maximum row of its root and descendants. Its height in rows is `bottom_row - root_row + 1`, including empty rows. A leaf has height 1.
6. Start the next whole tree at `bottom_row + 1` of the previous tree. Do not pack it into the previous tree's gaps. Adjacent rows use the normal card gap.

The downward shift applies to the corresponding child branch's start and subsequent construction, not its parent. If a deeper descendant encounters a conflict, shift that descendant's branch; an already placed intermediate ancestor retains its row.

Agreed example: `A1 → A2 → A3 → A4`, while `B1 → B2` is another child branch of `A1`. Direct-continuation priority preserves the space to the right of `A1`:

```text
Tier 1      Tier 2      Tier 3
   A1
   A2           A3          A4
                B1          B2
```

Agreed example `A → B → C`: tiers 3 → 4 → 3. Ancestor `A` occupies `C`'s target cell in its parent's row, so only the `C` branch starts lower:

```text
Tier 3      Tier 4
   A            B
   C
```

Transitions spanning multiple tiers leave intermediate columns empty. A lower-tier transition occupies a column to the parent's left; retain the row if the cell is free. Do not correct a tier number to match the link's direction.

## 7. Rendering and interaction

Convert columns and rows to pixels using existing dimensions and gaps. Area height is headings plus `row_count × cardHeight + max(0, row_count − 1) × cardGap`. An empty area has `row_count = 0`. Preserve existing `areaGap` between areas. Overall width includes columns from 0 to the maximum display tier, including empty intermediate columns.

Do not reserve an artificial column before tier 0; retain only normal field padding. Empty rows do not stretch cards. CSS Grid or explicit positioning is acceptable, but DOM and keyboard traversal order must follow visible area, tree and branch order rather than the former independent column lists.

Changing the language recalculates names, tree/child order and geometry from prepared data. It does not change parents or combination parameters, reread documents or call the backend. Theme changes, tooltips and menu collapse do not change grid coordinates. Geometry depends on the snapshot, selected combination, language and placement settings; in-memory reuse requires all these inputs to match.

Cards display representations from the combination. Hide the manual variant selector at this stage; changing only text or area while retaining old parents is prohibited. Do not add a combination selector to the menu: another prepared combination can be configured and the set explicitly reopened.

Recalculation preserves scroll position as far as the new bounds allow, then clamps it to the field's dimensions. Overlays continue to position relative to their cards. Page reload and application startup do not open databases or trigger generation.

## 8. Input checks and diagnostics

Do not duplicate full AST JSON Schema validation, semantic parent selection or analysis of all 15 object kinds. Preserve stage 17 document hashing and format checks. Additional checks cover only the contract required by the new grid.

Compare the combination's `source_set_id` with the manifest's `set_id`, and stored `inputs[].hash` values with `datasets[kind].source_revision`. This compares prepared metadata rather than reading every dataset or recalculating Python revisions. Record `calculation_revision` and `result_revision` without presenting this as a new audit of all inputs.

During extraction and traversal, check that every technology has a record for the selected combination, a valid status, an existing selected variant and parent, no repeated children, consistent parent/child references used by the layout, no cycle, complete card coverage and no overlap. A missing enrichment record is not a `root`. An invalid graph stops field preparation with diagnostics; do not repair it automatically or invent a parent.

`ambiguous` is a valid stored state resulting in a warning and independent tree start, not a format error. Its log includes ID, `NodeRef`, combination parameters/revisions, language and field settings. Do not invent selection traces; detailed decisions remain in the backend report.

Extend the existing frontend report with the combination ID, selected variants, revisions, language, layout settings, technology/tree counts per area, hidden cross-area parent link count, grid dimensions and geometry preparation time. Distinguish missing/stale combinations, incomplete enrichment and placement failures; RU/EN messages use existing dictionaries and the status panel.

## 9. Synthetic checks

| Scenario | Expected result |
| --- | --- |
| Leaf, linear chain, skipped tiers | Own columns; continuations share a row when free |
| Parent and child in the same tier | Child below; no shared cell |
| Branch with a direct ID continuation | Entire main branch first; side branch does not fill a gap above it |
| Transition 3 → 4 → 3 | Section 6 example: `A` and `B` share a row, `C` below |
| Multiple backward transitions and nested branches | No overlap; bottom boundaries include all descendants |
| Multiple trees | Whole trees stay separate; each starts after the previous one |
| Starting root and starting descendant | Priority only for the tree with a starting root; descendant stays in its branch |
| Cross-area parent and descendant returning to the original area | Independent starts in the respective areas; original links retained |
| Infinite repetition | Only `levels = -1`, `tier = 5` and a technology prerequisite produce column 6; game `tier` remains 5 |
| RU/EN, equal names, multiple matching IDs | Reproducible language/ID ordering without parent changes |
| Different document and `children` array orders | Identical coordinates for otherwise identical inputs |
| Missing/stale combination, unknown variant, cycle, invalid references | Specific diagnostics without old sorting or automatic recalculation |
| Stored ambiguity | Card and descendants placed; warning includes field context |

Geometry checks must compare expected positions and invariants rather than mirror the algorithm. Verify both agreed examples separately, including a free target cell that requires no shift.

## 10. Real set and acceptance

Use the prepared `data/stage17/database_set/manifest.json` set without rebuilding game data for interface testing. For `reference_default`, show all 679 technologies exactly once; preserve the stored 178 roots and 501 selected parents. Count layout trees separately because they also include branches with cross-area parents.

Check lasers, the five tier-3 mutations with a tier-4 parent, `tech_arkship_exodus_jump`, `tech_mine_dark_matter` and physics technologies `tech_encryption_1` and `tech_decryption_1` with a society parent. These are test cases, not hardcoded exceptions. Zero-weight technologies remain ordinary cards.

Separately open another prepared combination through configuration and confirm its variants, areas and links are used; the reference set includes `reference_variants`. Viewing does not change set files or their hashes. Language changes do not reread files; the other 14 kinds remain unloaded.

Run relevant TypeScript unit tests, typecheck, build and browser scenarios: explicit opening, combination errors, field placement without overlaps, RU/EN, themes, menu, scrolling, tooltips, absence of manual variant selection and report export. Update former sorting and variant-switching tests to the agreed stage scope.

Visually check both themes and languages. Record opening and geometry recalculation time, documents actually read and responsiveness without promising an unmeasured speedup. User review is needed for real-field usability; this is a web interface, so Stellaris execution is not required for stage acceptance.

## 11. Deliverables

Expected results: updated adapter projection, layout configuration, independent tree/geometry modules, field integration, localized messages, report and checks. A bilingual implementation guide records actual verification and limitations. Update README and changelog; increment frontend patch version from 0.0.4 to 0.0.5 during implementation.

Publishing `location` in the database, a persistent coordinate cache, manual variant selection with recalculation, all-prerequisite lines and special-acquisition markers remain separate stages. Database storage format and parent-selection rules do not change in this stage.

[Placement rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md) · [Previous stage](TZ_FRONTEND_STAGE_4_EN.md) · [Русская версия](TZ_FRONTEND_STAGE_5_RU.md).
