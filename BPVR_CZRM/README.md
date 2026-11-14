# BPV Reborn - Configure Zone Rows Mode

Configurable Planet View layout framework for Stellaris, built as a submod for **UI Overhaul Dynamic**.

This mod changes the **interface layout only**. It gives Planet View enough UI space to display larger BPV-style zone and building-slot layouts, but it does not add districts, zones, buildings, or building slots by itself. Game data and other mods still decide what actually exists.

## Table of contents

- [Requirements and load order](#requirements-and-load-order)
- [Files](#files)
- [Variable reference and default values](#variable-reference-and-default-values)
  - [UOD / Planet View base values](#uod--planet-view-base-values)
  - [Building slot and grid values](#building-slot-and-grid-values)
  - [District area geometry](#district-area-geometry)
  - [Main city zone and secondary zone geometry](#main-city-zone-and-secondary-zone-geometry)
  - [Lower district card geometry](#lower-district-card-geometry)
  - [Planetary resources geometry](#planetary-resources-geometry)
  - [Build queue geometry](#build-queue-geometry)
  - [Default value map](#default-value-map)
- [Current default preset](#current-default-preset)
- [Layout safety rule: scale only vertically](#layout-safety-rule-scale-only-vertically)
- [Configuration presets](#configuration-presets)
  - [Vanilla preset](#vanilla-preset)
  - [Expanded preset](#expanded-preset)
  - [Huge preset](#huge-preset)
- [Configuration workflow](#configuration-workflow)
- [Active user-tuned grid values](#active-user-tuned-grid-values)
- [Manual calculation guide](#manual-calculation-guide)
- [What to recalculate when changing common values](#what-to-recalculate-when-changing-common-values)
- [Testing checklist](#testing-checklist)
- [PIF gameplay preset compatibility](#pif-gameplay-preset-compatibility)
- [Credits](#credits)

## Requirements and load order

Required:

1. Stellaris `4.3.*`
2. UI Overhaul Dynamic for Stellaris `4.3.*`
3. This mod loaded after UI Overhaul Dynamic

Recommended load order:

```text
UI Overhaul Dynamic
BPV Reborn - Configure Zone Rows Mode
```

This mod overrides part of `planet_view.gui`, so other UI mods that also override Planet View may need a compatibility patch.

## Files

```text
descriptor.mod
interface/zz_bpv_planet_view.gui
README.md
CHANGELOG.md
```

The main layout file is:

```text
interface/zz_bpv_planet_view.gui
```

It intentionally overrides only the GUI types required by the current BPV layout path:

```text
planet_view
planet_district_entry_width_1
planet_district_entry_width_2
zone_entry
```

`planet_district_entry_width_3` is intentionally not overridden because the current BPV layout path does not use it.


## Variable reference and default values

This section is the detailed reference for the preset values. It intentionally lives in `README.md` instead of the `.gui` file, so the layout code stays readable while the configuration meaning is still documented.

There are two kinds of values here:

```text
Active GUI value       = assigned in zz_bpv_planet_view.gui and used by the UI layout.
Calculation helper     = used only by this guide when recalculating active values by hand.
```

### UOD / Planet View base values

| Variable | Default | Kind | Meaning |
|---|---:|---|---|
| `@planet_pop_category_width` | `1177` | Active GUI value | Width of a population category entry in the population tab. |
| `@planet_sidebar_width` | `450` | Active GUI value | Width of right-side Planet View panels and sidebar windows. |
| `@planet_sidebar_list_height` | `830` | Active GUI value | Base height of scroll lists inside Planet View sidebars. |
| `@planet_portrait_window_width` | `890` | Active GUI value | Width of the planet portrait window. |
| `@planet_portrait_window_height_900` | `236` | Active GUI value | Planet portrait window height for the base 900px Planet View layout. |
| `@planet_portrait_window_height_1200` | `336` | Active GUI value | Planet portrait window height for scaled layouts with `min_height = 1200`. |
| `@planet_portrait_window_height_1440` | `376` | Active GUI value | Planet portrait window height for scaled layouts with `min_height = 1440`. |

### Building slot and grid values

| Variable | Default | Kind | Meaning |
|---|---:|---|---|
| `@BPV_BUILDING_SLOT_SIZE` | `52` | Active GUI value | Width and height of one building slot cell. |
| `@BPV_CITY_ZONE_BUILDING_SLOT_COLUMNS` | `6` | Active GUI value | Number of building slot columns shown in the main city zone grid. Treat as a layout-safe constant for normal presets. |
| `@BPV_CITY_ZONE_BUILDING_SLOT_ROWS` | `8` | Active GUI value | Number of building slot rows shown in the main city zone grid. |
| `@BPV_SECONDARY_ZONE_ENTRY_COUNT` | `2` | Active GUI value | Number of secondary zone entries reserved inside the main district card. |
| `@BPV_SECONDARY_ZONE_BUILDING_SLOT_COLUMNS` | `6` | Active GUI value | Number of building slot columns shown in each secondary zone entry. Treat as a layout-safe constant for normal presets. |
| `@BPV_SECONDARY_ZONE_BUILDING_SLOT_ROWS` | `8` | Active GUI value | Number of building slot rows shown in each secondary zone entry. |
| `@BPV_LOWER_DISTRICT_BUILDING_SLOT_COLUMNS` | `3` | Active GUI value | Number of building slot columns shown inside each lower district card. Treat as a layout-safe constant for normal presets. |
| `@BPV_LOWER_DISTRICT_BUILDING_SLOT_ROWS` | `16` | Active GUI value | Number of building slot rows shown inside each lower district card. |
| `@BPV_CITY_ZONE_BUILDING_SLOT_TARGET_COUNT` | `48` | Calculation helper | Target number of city zone building slots. Use it only to calculate city zone rows manually. |
| `@BPV_SECONDARY_ZONE_BUILDING_SLOT_TARGET_COUNT` | `48` | Calculation helper | Target number of secondary zone building slots. Use it only to calculate secondary zone rows manually. |
| `@BPV_LOWER_DISTRICT_BUILDING_SLOT_TARGET_COUNT` | `48` | Calculation helper | Target number of lower district building slots. Use it only to calculate lower district rows manually. |

### District area geometry

| Variable | Default | Kind | Meaning |
|---|---:|---|---|
| `@BPV_DISTRICTS_AREA_BASE_WIDTH` | `570` | Active GUI value | Base UIOD districts area width before BPV extra width is added. |
| `@BPV_DISTRICTS_AREA_EXTRA_WIDTH` | `310` | Active GUI value | Extra width added to the BPV districts area and main district cards over the base width. |
| `@BPV_MAIN_DISTRICT_ZONES_TOP_Y` | `35` | Active GUI value | Y-position where city and secondary zone blocks start inside the main district card. |
| `@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT` | `264` | Active GUI value | Visible height of the main districts scroll viewport. |
| `@BPV_MAIN_DISTRICT_CARD_HEIGHT` | `891` | Active GUI value | Actual height of one main district card. Recalculate when city or secondary zone height changes. |
| `@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT` | `891` | Active GUI value | Full scroll-content height for the main districts scroll area. |
| `@BPV_MAIN_TO_LOWER_DISTRICTS_GAP` | `10` | Active GUI value | Vertical gap between the main districts viewport and the lower districts viewport. |
| `@BPV_MAIN_DISTRICT_CARD_REQUIRED_BOTTOM_PADDING` | `10` | Calculation helper | Bottom padding used when manually calculating required main district card height. |
| `@BPV_MAIN_DISTRICTS_SCROLL_TRAILING_PADDING` | `0` | Calculation helper | Extra scroll-content height after the main district card. |
| `@BPV_MAIN_DISTRICT_CARD_MIN_HEIGHT` | `264` | Calculation helper | Minimum allowed main district card height used when manually choosing the final card height. |

### Main city zone and secondary zone geometry

| Variable | Default | Kind | Meaning |
|---|---:|---|---|
| `@BPV_BUILDING_GRID_FRAME_EXTRA_WIDTH` | `8` | Active GUI value | Extra width added to building grid frames around city and lower district slot grids. |
| `@BPV_CITY_ZONE_X` | `95` | Active GUI value | X-position of the primary city zone frame inside the main district card. |
| `@BPV_CITY_ZONE_BUILDING_GRID_X` | `5` | Active GUI value | X-offset where the building slot grid starts inside the primary city zone frame. |
| `@BPV_SECONDARY_ZONES_LIST_X` | `420` | Active GUI value | X-position of the secondary zones list inside the main district card. |
| `@BPV_SECONDARY_ZONE_ENTRY_WIDTH` | `450` | Active GUI value | Width of one secondary zone entry. |
| `@BPV_SECONDARY_ZONE_BUILDING_GRID_X` | `136` | Active GUI value | X-offset where the building slot grid starts inside a secondary zone entry. |
| `@BPV_SECONDARY_ZONE_ENTRY_BOTTOM_PADDING` | `2` | Active GUI value | Bottom padding inside each secondary zone entry. |
| `@BPV_SECONDARY_ZONE_ENTRY_VERTICAL_GAP` | `10` | Active GUI value | Vertical gap between secondary zone entries. |

### Lower district card geometry

| Variable | Default | Kind | Meaning |
|---|---:|---|---|
| `@BPV_LOWER_DISTRICT_CARD_WIDTH` | `285` | Active GUI value | Width of one lower district card. |
| `@BPV_LOWER_DISTRICT_CARD_HEIGHT` | `897` | Active GUI value | Actual height of one lower district card. Recalculate when lower district slot rows change. |
| `@BPV_LOWER_DISTRICTS_GRID_ROW_SLOT_WIDTH` | `288` | Active GUI value | Horizontal step used by the lower districts grid for one card slot. |
| `@BPV_LOWER_DISTRICT_CARDS_PER_ROW` | `3` | Active GUI value | Number of lower district cards placed in one row of the lower districts grid. |
| `@BPV_LOWER_DISTRICTS_GRID_BOX_WIDTH` | `870` | Active GUI value | Width of the gridBox that contains lower district cards. |
| `@BPV_LOWER_DISTRICT_TOP_ROW_HEIGHT` | `35` | Active GUI value | Height of the top row area in a lower district card. |
| `@BPV_LOWER_DISTRICT_HEADER_EXTRA_Y` | `20` | Active GUI value | Additional vertical offset applied to lower district card contents below the top row. |
| `@BPV_LOWER_DISTRICT_ZONE_X` | `110` | Active GUI value | X-position of the building zone frame inside a lower district card. |
| `@BPV_LOWER_DISTRICT_BUILDING_GRID_X` | `5` | Active GUI value | X-offset where the building slot grid starts inside a lower district zone frame. |
| `@BPV_LOWER_DISTRICTS_VIEWPORT_HEIGHT` | `284` | Active GUI value | Visible height of the lower districts scroll viewport. Current preset uses 284 because 285+ clips in the tested layout. |
| `@BPV_LOWER_DISTRICTS_GRID_ROW_HEIGHT` | `907` | Active GUI value | Height of one lower-district grid row: lower district card height plus row trailing padding. |
| `@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT` | `907` | Active GUI value | Full scroll-content height for the lower districts grid. |
| `@BPV_LOWER_DISTRICT_CARD_MIN_HEIGHT` | `280` | Calculation helper | Minimum allowed lower district card height used when manually choosing the final card height. |
| `@BPV_LOWER_DISTRICT_CARD_INNER_BOTTOM_PADDING` | `10` | Calculation helper | Inner bottom padding used when manually calculating required lower district card height. |
| `@BPV_LOWER_DISTRICTS_CONTENT_ROWS` | `1` | Calculation helper | Number of vertical rows of lower district cards used for manual scroll-content height calculation. |
| `@BPV_LOWER_DISTRICTS_ROW_TRAILING_PADDING` | `10` | Calculation helper | Padding after each lower district row, including the trailing padding after the last row. |

### Planetary resources geometry

| Variable | Default | Kind | Meaning |
|---|---:|---|---|
| `@BPV_PLANETARY_RESOURCES_BASE_X` | `-10` | Active GUI value | Base X-position of the planetary resources block before BPV offsets. |
| `@BPV_PLANETARY_RESOURCES_OFFSET_X` | `315` | Active GUI value | Horizontal offset applied to the planetary resources block from its original UIOD position. |
| `@BPV_PLANETARY_RESOURCES_BASE_Y_900` | `247` | Active GUI value | Base Y-position of the planetary resources block in the base scaled-height layout before BPV offsets. |
| `@BPV_PLANETARY_RESOURCES_BASE_Y_1200` | `147` | Active GUI value | Base Y-position of the planetary resources block for `min_height = 1200` before BPV offsets. |
| `@BPV_PLANETARY_RESOURCES_BASE_Y_1440` | `107` | Active GUI value | Base Y-position of the planetary resources block for `min_height = 1440` before BPV offsets. |
| `@BPV_PLANETARY_RESOURCES_OFFSET_Y` | `-190` | Active GUI value | Vertical offset applied to the planetary resources block from its original UIOD position. |
| `@BPV_PLANETARY_RESOURCES_WIDTH` | `300` | Active GUI value | Width of the planetary resources block. |
| `@BPV_PLANETARY_RESOURCES_HEIGHT` | `178` | Active GUI value | Height of the planetary resources block. |

### Build queue geometry

| Variable | Default | Kind | Meaning |
|---|---:|---|---|
| `@BPV_BUILD_QUEUE_WINDOW_BASE_Y` | `236` | Active GUI value | Base Y-position of the build queue window before BPV vertical shift. |
| `@BPV_BUILD_QUEUE_Y_SHIFT` | `185` | Active GUI value | Moves the build queue window down from its base Y-position. |
| `@BPV_BUILD_QUEUE_LIST_WIDTH` | `300` | Active GUI value | Width of the internal build queue list. |
| `@BPV_BUILD_QUEUE_LIST_BASE_HEIGHT_900` | `558` | Active GUI value | Base height of the internal build queue list in the base scaled-height layout before BPV height reduction. |
| `@BPV_BUILD_QUEUE_LIST_BASE_HEIGHT_1200` | `658` | Active GUI value | Base height of the internal build queue list for `min_height = 1200` before BPV height reduction. |
| `@BPV_BUILD_QUEUE_LIST_BASE_HEIGHT_1440` | `698` | Active GUI value | Base height of the internal build queue list for `min_height = 1440` before BPV height reduction. |
| `@BPV_BUILD_QUEUE_LIST_HEIGHT_REDUCTION` | `185` | Active GUI value | Reduces the internal build queue list height after the window is shifted down. |

### Default value map

This block mirrors the current preset values in one place. Values marked as calculation helpers are documented here for manual recalculation; they are not assigned in the cleaned `.gui` file unless they are also listed above as active GUI values.

```text
@planet_pop_category_width = 1177
@planet_sidebar_width = 450
@planet_sidebar_list_height = 830
@planet_portrait_window_width = 890
@planet_portrait_window_height_900 = 236
@planet_portrait_window_height_1200 = 336
@planet_portrait_window_height_1440 = 376

@BPV_CITY_ZONE_BUILDING_SLOT_TARGET_COUNT = 48            # calculation helper
@BPV_SECONDARY_ZONE_BUILDING_SLOT_TARGET_COUNT = 48       # calculation helper
@BPV_LOWER_DISTRICT_BUILDING_SLOT_TARGET_COUNT = 48       # calculation helper

@BPV_BUILDING_SLOT_SIZE = 52
@BPV_CITY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_CITY_ZONE_BUILDING_SLOT_ROWS = 8
@BPV_SECONDARY_ZONE_ENTRY_COUNT = 2
@BPV_SECONDARY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_SECONDARY_ZONE_BUILDING_SLOT_ROWS = 8
@BPV_LOWER_DISTRICT_BUILDING_SLOT_COLUMNS = 3
@BPV_LOWER_DISTRICT_BUILDING_SLOT_ROWS = 16
@BPV_LOWER_DISTRICT_CARDS_PER_ROW = 3

@BPV_BUILDING_GRID_FRAME_EXTRA_WIDTH = 8
@BPV_DISTRICTS_AREA_BASE_WIDTH = 570
@BPV_DISTRICTS_AREA_EXTRA_WIDTH = 310

@BPV_MAIN_DISTRICT_ZONES_TOP_Y = 35
@BPV_MAIN_DISTRICT_CARD_REQUIRED_BOTTOM_PADDING = 10      # calculation helper
@BPV_MAIN_DISTRICTS_SCROLL_TRAILING_PADDING = 0           # calculation helper
@BPV_MAIN_DISTRICT_CARD_MIN_HEIGHT = 264                  # calculation helper
@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT = 264
@BPV_MAIN_DISTRICT_CARD_HEIGHT = 891
@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT = 891

@BPV_CITY_ZONE_X = 95
@BPV_CITY_ZONE_BUILDING_GRID_X = 5
@BPV_SECONDARY_ZONES_LIST_X = 420
@BPV_SECONDARY_ZONE_ENTRY_WIDTH = 450
@BPV_SECONDARY_ZONE_BUILDING_GRID_X = 136
@BPV_SECONDARY_ZONE_ENTRY_BOTTOM_PADDING = 2
@BPV_SECONDARY_ZONE_ENTRY_VERTICAL_GAP = 10

@BPV_LOWER_DISTRICT_CARD_WIDTH = 285
@BPV_LOWER_DISTRICT_CARD_HEIGHT = 897
@BPV_LOWER_DISTRICTS_GRID_ROW_SLOT_WIDTH = 288
@BPV_LOWER_DISTRICTS_GRID_BOX_WIDTH = 870
@BPV_LOWER_DISTRICT_TOP_ROW_HEIGHT = 35
@BPV_LOWER_DISTRICT_HEADER_EXTRA_Y = 20
@BPV_LOWER_DISTRICT_ZONE_X = 110
@BPV_LOWER_DISTRICT_BUILDING_GRID_X = 5
@BPV_LOWER_DISTRICTS_VIEWPORT_HEIGHT = 284
@BPV_LOWER_DISTRICTS_CONTENT_ROWS = 1                     # calculation helper
@BPV_LOWER_DISTRICTS_ROW_TRAILING_PADDING = 10            # calculation helper
@BPV_LOWER_DISTRICTS_GRID_ROW_HEIGHT = 907
@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT = 907

@BPV_PLANETARY_RESOURCES_BASE_X = -10
@BPV_PLANETARY_RESOURCES_OFFSET_X = 315
@BPV_PLANETARY_RESOURCES_BASE_Y_900 = 247
@BPV_PLANETARY_RESOURCES_BASE_Y_1200 = 147
@BPV_PLANETARY_RESOURCES_BASE_Y_1440 = 107
@BPV_PLANETARY_RESOURCES_OFFSET_Y = -190
@BPV_PLANETARY_RESOURCES_WIDTH = 300
@BPV_PLANETARY_RESOURCES_HEIGHT = 178

@BPV_BUILD_QUEUE_WINDOW_BASE_Y = 236
@BPV_BUILD_QUEUE_Y_SHIFT = 185
@BPV_BUILD_QUEUE_LIST_WIDTH = 300
@BPV_BUILD_QUEUE_LIST_BASE_HEIGHT_900 = 558
@BPV_BUILD_QUEUE_LIST_BASE_HEIGHT_1200 = 658
@BPV_BUILD_QUEUE_LIST_BASE_HEIGHT_1440 = 698
@BPV_BUILD_QUEUE_LIST_HEIGHT_REDUCTION = 185
```

## Current default preset

The current preset is configured around 48 visible building slots per zone group:

```text
City zone:       6 columns x 8 rows  = 48 slots
Secondary zone:  6 columns x 8 rows  = 48 slots per secondary zone entry
Lower district:  3 columns x 16 rows = 48 slots per lower district card
```

Current secondary zone entries inside the main district card:

```text
2 secondary zone entries
```

Current lower district card layout:

```text
3 lower district cards per row
1 lower district row in the scroll content
```

These are not hard product limits. They are just the values used by the default preset. If you change them, recalculate the dependent values listed below.

## Layout safety rule: scale only vertically

The Planet View layout is horizontally fitted around the current grid widths. Because of that, presets should scale by adding rows, not by adding columns.

Keep these column counts fixed unless you are intentionally redesigning the full horizontal layout:

```text
@BPV_CITY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_SECONDARY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_LOWER_DISTRICT_BUILDING_SLOT_COLUMNS = 3
```

To show more slots, increase the row values:

```text
@BPV_CITY_ZONE_BUILDING_SLOT_ROWS
@BPV_SECONDARY_ZONE_BUILDING_SLOT_ROWS
@BPV_LOWER_DISTRICT_BUILDING_SLOT_ROWS
```

Increasing columns expands grids sideways. That can push building slots outside their frames, overlap neighbouring UI blocks, or break the carefully fitted Planet View composition. Treat column changes as an advanced full-layout redesign, not as normal preset configuration.

If the target slot count does not fit exactly into the fixed column count, add another row for the remaining slots.

Examples:

```text
6 city slots with 6 fixed columns = 1 row
48 city slots with 6 fixed columns = 8 rows
120 city slots with 6 fixed columns = 20 rows

3 lower district slots with 3 fixed columns = 1 row
12 lower district slots with 3 fixed columns = 4 rows
48 lower district slots with 3 fixed columns = 16 rows
```

## Configuration presets

These presets are complete calculation examples for common target values. They keep the horizontal layout stable and change only the number of rows.

The `*_TARGET_COUNT` values are calculation helpers for this guide. The game UI uses the active row and column values in `zz_bpv_planet_view.gui`.

The copy blocks below include the row values and dependent heights for each preset. They repeat the fixed column values so the full grid shape is visible. If your setup has more lower district cards than fit in one lower district row, also recalculate `@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT` using the lower district guide below.

These presets use the current visual spacing values:

```text
@BPV_SECONDARY_ZONE_ENTRY_BOTTOM_PADDING = 2
@BPV_SECONDARY_ZONE_ENTRY_VERTICAL_GAP = 10
@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT = 264
@BPV_MAIN_DISTRICTS_SCROLL_TRAILING_PADDING = 0
@BPV_MAIN_TO_LOWER_DISTRICTS_GAP = 10
@BPV_MAIN_DISTRICT_CARD_REQUIRED_BOTTOM_PADDING = 10
@BPV_LOWER_DISTRICT_CARD_INNER_BOTTOM_PADDING = 10
@BPV_LOWER_DISTRICTS_ROW_TRAILING_PADDING = 10
```

### Vanilla preset

Compact layout close to vanilla-scale slot counts.

Target values:

```text
@BPV_CITY_ZONE_BUILDING_SLOT_TARGET_COUNT = 6
@BPV_SECONDARY_ZONE_BUILDING_SLOT_TARGET_COUNT = 3
@BPV_LOWER_DISTRICT_BUILDING_SLOT_TARGET_COUNT = 3
@BPV_SECONDARY_ZONE_ENTRY_COUNT = 2
```

Calculated row values with fixed columns:

```text
City zone:       6 fixed columns, 6 target slots  = 1 row
Secondary zone:  6 fixed columns, 3 target slots  = 1 row with unused horizontal capacity
Lower district:  3 fixed columns, 3 target slots  = 1 row
```

Derived values:

```text
Secondary entry height:          1 * 52 + 2 = 54
Secondary zones required height: 35 + 10 + ((54 + 10) * 2) - 10 = 163
City zone required height:       35 + 10 + 1 * 52 = 97
Main district card height:       264
Main scroll-content height:      264 + 0 = 264

Lower card building requirement: 35 + 20 + 1 * 52 + 10 = 117
Lower district card height:      280
Lower grid row height:           280 + 10 = 290
Lower scroll-content height:     1 row * 290 = 290
```

Values to copy into `zz_bpv_planet_view.gui`:

```text
@BPV_CITY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_CITY_ZONE_BUILDING_SLOT_ROWS = 1

@BPV_SECONDARY_ZONE_ENTRY_COUNT = 2
@BPV_SECONDARY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_SECONDARY_ZONE_BUILDING_SLOT_ROWS = 1

@BPV_LOWER_DISTRICT_BUILDING_SLOT_COLUMNS = 3
@BPV_LOWER_DISTRICT_BUILDING_SLOT_ROWS = 1
@BPV_LOWER_DISTRICT_CARDS_PER_ROW = 3

@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT = 264
@BPV_MAIN_DISTRICT_CARD_HEIGHT = 264
@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT = 264

@BPV_LOWER_DISTRICT_CARD_HEIGHT = 280
@BPV_LOWER_DISTRICTS_GRID_ROW_HEIGHT = 290
@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT = 290
```

### Expanded preset

Large but moderate configuration.

Target values:

```text
@BPV_CITY_ZONE_BUILDING_SLOT_TARGET_COUNT = 48
@BPV_SECONDARY_ZONE_BUILDING_SLOT_TARGET_COUNT = 12
@BPV_LOWER_DISTRICT_BUILDING_SLOT_TARGET_COUNT = 12
@BPV_SECONDARY_ZONE_ENTRY_COUNT = 10
```

Calculated row values with fixed columns:

```text
City zone:       6 fixed columns, 48 target slots = 8 rows
Secondary zone:  6 fixed columns, 12 target slots = 2 rows
Lower district:  3 fixed columns, 12 target slots = 4 rows
```

Derived values:

```text
Secondary entry height:          2 * 52 + 2 = 106
Secondary zones required height: 35 + 10 + ((106 + 10) * 10) - 10 = 1195
City zone required height:       35 + 10 + 8 * 52 = 461
Main district card height:       1195
Main scroll-content height:      1195 + 0 = 1195

Lower card building requirement: 35 + 20 + 4 * 52 + 10 = 273
Lower district card height:      280
Lower grid row height:           280 + 10 = 290
Lower scroll-content height:     1 row * 290 = 290
```

Values to copy into `zz_bpv_planet_view.gui`:

```text
@BPV_CITY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_CITY_ZONE_BUILDING_SLOT_ROWS = 8

@BPV_SECONDARY_ZONE_ENTRY_COUNT = 10
@BPV_SECONDARY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_SECONDARY_ZONE_BUILDING_SLOT_ROWS = 2

@BPV_LOWER_DISTRICT_BUILDING_SLOT_COLUMNS = 3
@BPV_LOWER_DISTRICT_BUILDING_SLOT_ROWS = 4
@BPV_LOWER_DISTRICT_CARDS_PER_ROW = 3

@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT = 264
@BPV_MAIN_DISTRICT_CARD_HEIGHT = 1195
@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT = 1195

@BPV_LOWER_DISTRICT_CARD_HEIGHT = 280
@BPV_LOWER_DISTRICTS_GRID_ROW_HEIGHT = 290
@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT = 290
```

### Huge preset

Extreme configuration with many secondary zone entries. This preset is useful as a stress-test example and needs careful in-game scrolling checks.

Target values:

```text
@BPV_CITY_ZONE_BUILDING_SLOT_TARGET_COUNT = 120
@BPV_SECONDARY_ZONE_BUILDING_SLOT_TARGET_COUNT = 18
@BPV_LOWER_DISTRICT_BUILDING_SLOT_TARGET_COUNT = 48
@BPV_SECONDARY_ZONE_ENTRY_COUNT = 30
```

Calculated row values with fixed columns:

```text
City zone:       6 fixed columns, 120 target slots = 20 rows
Secondary zone:  6 fixed columns, 18 target slots  = 3 rows
Lower district:  3 fixed columns, 48 target slots  = 16 rows
```

Derived values:

```text
Secondary entry height:          3 * 52 + 2 = 158
Secondary zones required height: 35 + 10 + ((158 + 10) * 30) - 10 = 5075
City zone required height:       35 + 10 + 20 * 52 = 1085
Main district card height:       5075
Main scroll-content height:      5075 + 0 = 5075

Lower card building requirement: 35 + 20 + 16 * 52 + 10 = 897
Lower district card height:      897
Lower grid row height:           897 + 10 = 907
Lower scroll-content height:     1 row * 907 = 907
```

Values to copy into `zz_bpv_planet_view.gui`:

```text
@BPV_CITY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_CITY_ZONE_BUILDING_SLOT_ROWS = 20

@BPV_SECONDARY_ZONE_ENTRY_COUNT = 30
@BPV_SECONDARY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_SECONDARY_ZONE_BUILDING_SLOT_ROWS = 3

@BPV_LOWER_DISTRICT_BUILDING_SLOT_COLUMNS = 3
@BPV_LOWER_DISTRICT_BUILDING_SLOT_ROWS = 16
@BPV_LOWER_DISTRICT_CARDS_PER_ROW = 3

@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT = 264
@BPV_MAIN_DISTRICT_CARD_HEIGHT = 5075
@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT = 5075

@BPV_LOWER_DISTRICT_CARD_HEIGHT = 897
@BPV_LOWER_DISTRICTS_GRID_ROW_HEIGHT = 907
@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT = 907
```

## Configuration workflow

When changing the layout, use this order:

1. Choose the slot size.
2. Choose how many building slots each zone should show.
3. Keep the safe column counts fixed unless you are redesigning the horizontal UI.
4. Calculate how many rows each zone needs.
5. Update the active row values and secondary zone entry count in `zz_bpv_planet_view.gui`.
6. Recalculate the dependent card heights and scroll-content heights.
7. Test the layout in game at the target resolutions and UI scales.

The `.gui` file supports simple arithmetic, but it does not provide a practical way to express every required layout decision. Values that depend on manual row counting, largest-required-height selection, or incomplete final rows must be recalculated by hand.

## Active user-tuned grid values

These are the first values to change for most slot-count presets:

```text
@BPV_BUILDING_SLOT_SIZE

@BPV_CITY_ZONE_BUILDING_SLOT_ROWS

@BPV_SECONDARY_ZONE_ENTRY_COUNT
@BPV_SECONDARY_ZONE_BUILDING_SLOT_ROWS

@BPV_LOWER_DISTRICT_BUILDING_SLOT_ROWS
@BPV_LOWER_DISTRICT_CARDS_PER_ROW
```

These are the first values to change for visual spacing presets:

```text
@BPV_SECONDARY_ZONE_ENTRY_BOTTOM_PADDING
@BPV_SECONDARY_ZONE_ENTRY_VERTICAL_GAP
@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT
@BPV_MAIN_TO_LOWER_DISTRICTS_GAP
```

The remaining padding values are calculation helpers in this guide. If you change them, update the derived active heights in the `.gui` file.

These column values are active GUI values, but they are also layout-safe constants for this framework:

```text
@BPV_CITY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_SECONDARY_ZONE_BUILDING_SLOT_COLUMNS = 6
@BPV_LOWER_DISTRICT_BUILDING_SLOT_COLUMNS = 3
```

Do not increase them for normal configuration. Increase row values instead.

Do not change only the target slot count. The GUI uses columns and rows. If you want 48 slots in 6 fixed columns, write 8 rows. If you want 49 slots in 6 fixed columns, write 9 rows, because the incomplete final row still needs screen space.

## Manual calculation guide

### Building grid width

For every zone, grid width is:

```text
number of columns * slot size
```

Current examples:

```text
City zone grid width:       6 * 52 = 312
Secondary zone grid width:  6 * 52 = 312
Lower district grid width:  3 * 52 = 156
```

### Building grid height

For every zone, grid height is:

```text
number of rows * slot size
```

Current examples:

```text
City zone grid height:       8 * 52 = 416
Secondary zone grid height:  8 * 52 = 416
Lower district grid height: 16 * 52 = 832
```

### How to calculate row count from slot count

Divide the number of slots by the fixed number of columns for that zone.

If the result is exact, use that number of rows.

If there is anything left over, add one more row.

Examples:

```text
48 slots / 6 columns = 8 rows
49 slots / 6 columns = 8 full rows plus 1 remaining slot, so use 9 rows
50 slots / 6 columns = 8 full rows plus 2 remaining slots, so use 9 rows
48 slots / 3 columns = 16 rows
```

### Secondary zone entry height

A secondary zone entry must be tall enough for its building grid plus bottom padding:

```text
secondary entry height = secondary zone rows * slot size + secondary entry bottom padding
```

Current value:

```text
8 * 52 + 2 = 418
```

This value is currently used directly in `zone_entry` as:

```text
size = { width = @BPV_SECONDARY_ZONE_ENTRY_WIDTH height = @[ BPV_SECONDARY_ZONE_BUILDING_SLOT_ROWS * BPV_BUILDING_SLOT_SIZE + BPV_SECONDARY_ZONE_ENTRY_BOTTOM_PADDING ] }
```

### Secondary zones list height inside the main district card

For the list of secondary zone entries plus the trailing space after the last entry:

```text
secondary zones required height = top position + trailing space after the list + ((entry height + vertical gap) * number of entries) - final unused gap
```

The current layout uses the same value for the vertical gap between entries and the trailing space after the list.

Current value:

```text
35 + 10 + ((418 + 10) * 2) - 10 = 891
```

The final unused gap is subtracted because the last entry does not need a gap after it.

### City zone required height

The city zone area must be tall enough for its building grid:

```text
city required height = top position + bottom padding + city zone rows * slot size
```

Current value:

```text
35 + 10 + 8 * 52 = 461
```

### Main district card height

The main district card must be tall enough for all of these:

```text
minimum main card height
city zone required height
secondary zones list height
```

Use the largest of those values.

Current values:

```text
minimum main card height:        264
city zone required height:       461
secondary zones required height: 891

main district card height:       891
```

Then update:

```text
@BPV_MAIN_DISTRICT_CARD_HEIGHT
```

### Main districts scroll-content height

The main districts scroll content must be at least the main district card height plus trailing scroll padding.

Current value:

```text
891 + 0 = 891
```

Then update:

```text
@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT
```

### Main districts viewport and gap

Current visible height of the upper scroll viewport:

```text
@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT = 264
```

Current gap between the upper and lower scroll windows:

```text
@BPV_MAIN_TO_LOWER_DISTRICTS_GAP = 10
```

The lower scroll window starts at:

```text
264 + 10 = 274
```

This matches the previous lower-window start position, so the larger upper viewport does not push the lower viewport down.

### Lower district card height

The lower district card must be tall enough for all of these:

```text
minimum lower card height
lower district top row + header offset + lower building grid height + inner bottom padding
```

Current values:

```text
minimum lower card height: 280
building grid requirement: 35 + 20 + 16 * 52 + 10 = 897

lower district card height: 897
```

Then update:

```text
@BPV_LOWER_DISTRICT_CARD_HEIGHT
```

### Lower district grid row height

One lower district grid row is the lower district card plus trailing row padding.

Current value:

```text
897 + 10 = 907
```

Then update:

```text
@BPV_LOWER_DISTRICTS_GRID_ROW_HEIGHT
```

### Lower districts scroll-content height

First decide how many lower district cards you need to show.

Then divide that number by the number of cards per row.

If the result is exact, use that number of rows.

If there is anything left over, add one more row.

Examples with 3 cards per row:

```text
1 to 3 lower district cards = 1 row
4 to 6 lower district cards = 2 rows
7 to 9 lower district cards = 3 rows
```

Then multiply the number of rows by the lower district grid row height.

Current value:

```text
1 row * 907 = 907
```

Then update:

```text
@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT
```

### Lower districts viewport height

Current value:

```text
@BPV_LOWER_DISTRICTS_VIEWPORT_HEIGHT = 284
```

This value was chosen by in-game layout testing. In the current layout, 285 and above starts clipping. Treat it as a tested viewport value, not as a purely derived formula.

### Current visual spacing values

Current active visual spacing values:

```text
@BPV_SECONDARY_ZONE_ENTRY_BOTTOM_PADDING = 2
@BPV_SECONDARY_ZONE_ENTRY_VERTICAL_GAP = 10
@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT = 264
@BPV_MAIN_TO_LOWER_DISTRICTS_GAP = 10
```

Current calculation-helper padding values:

```text
@BPV_MAIN_DISTRICT_CARD_REQUIRED_BOTTOM_PADDING = 10
@BPV_MAIN_DISTRICTS_SCROLL_TRAILING_PADDING = 0
@BPV_LOWER_DISTRICT_CARD_INNER_BOTTOM_PADDING = 10
@BPV_LOWER_DISTRICTS_ROW_TRAILING_PADDING = 10
```

### Build queue after vertical movement

The build queue window is moved down by:

```text
@BPV_BUILD_QUEUE_Y_SHIFT = 185
```

The inner list height is reduced separately by:

```text
@BPV_BUILD_QUEUE_LIST_HEIGHT_REDUCTION = 185
```

Current calculated list heights:

```text
Base 900 layout:      558 - 185 = 373
min_height 1200:      658 - 185 = 473
min_height 1440:      698 - 185 = 513
```

These values are kept as separate parameters so a future preset can move the window and resize the list independently.

## What to recalculate when changing common values

### If you change slot size

Recheck all grid widths, grid heights, card heights, and scroll-content heights.

### If you change city zone rows

Recheck:

```text
@BPV_MAIN_DISTRICT_CARD_HEIGHT
@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT
```

### If you change secondary zone rows

Recheck:

```text
@BPV_MAIN_DISTRICT_CARD_HEIGHT
@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT
```

### If you change secondary zone entry count

Recheck:

```text
@BPV_MAIN_DISTRICT_CARD_HEIGHT
@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT
```

### If you change lower district rows

Recheck:

```text
@BPV_LOWER_DISTRICT_CARD_HEIGHT
@BPV_LOWER_DISTRICTS_GRID_ROW_HEIGHT
@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT
```

### If you change any column count

Do this only when intentionally redesigning the horizontal layout.

Column changes require checking frame widths, grid X offsets, secondary zone entry width, lower district card width, lower district grid box width, and possible overlap with neighbouring Planet View UI blocks.

Normal presets should not change column counts.

### If you change lower district cards per row

Recheck:

```text
@BPV_LOWER_DISTRICTS_GRID_ROW_SLOT_WIDTH
@BPV_LOWER_DISTRICTS_GRID_BOX_WIDTH
@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT
```

Also make sure the full row width fits inside the lower districts area.

### If you change visual padding or viewport spacing

Recheck:

```text
@BPV_MAIN_DISTRICT_CARD_HEIGHT
@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT
@BPV_LOWER_DISTRICT_CARD_HEIGHT
@BPV_LOWER_DISTRICTS_GRID_ROW_HEIGHT
@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT
```

If you change `@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT` or `@BPV_MAIN_TO_LOWER_DISTRICTS_GAP`, also verify the lower scroll window start position:

```text
@BPV_MAIN_DISTRICTS_VIEWPORT_HEIGHT + @BPV_MAIN_TO_LOWER_DISTRICTS_GAP
```

## Testing checklist

Recommended minimum testing before publishing a preset:

### Resolutions and UI scale

```text
1920x1080, UI scale 1.0
2560x1440, UI scale 1.0
2560x1440, increased UI scale
3840x2160, high UI scale if available
```

### Planet and colony types

```text
normal colony
capital world
habitat
ring world
ecumenopolis
hive or machine world if relevant
modded planet type with many districts or zones
```

### UI states

```text
empty build queue
long build queue
locked slots
many visible slots
planetary resources visible
unemployment / job state visible
scrolling main district area
scrolling lower district area
```

### Regression checks after UOD updates

After UI Overhaul Dynamic updates, compare the new UOD `planet_view.gui` against this mod and check at least these GUI types:

```text
planet_view
planet_district_entry_width_1
planet_district_entry_width_2
zone_entry
```

Then repeat the testing checklist above.


## PIF gameplay preset compatibility

Version `1.1.0` adds a generated visual preset pack for **PIF - More Secondary Zones and Building Slots**.

The active root file remains unchanged:

```text
interface/zz_bpv_planet_view.gui
```

PIF-compatible visual presets are stored here:

```text
_presets/PIF_More_Secondary_Zones_and_Building_Slots/
```

Each preset folder contains:

```text
interface/zz_bpv_planet_view.gui
```

To activate a preset, choose the folder matching the gameplay preset combination, copy its `interface` directory into this mod root, replace files, and restart the game.

Default gameplay visual preset:

```text
S05_G024_MS012_R024_default
```

Default calculated values:

```text
@BPV_CITY_ZONE_BUILDING_SLOT_ROWS = 4
@BPV_SECONDARY_ZONE_ENTRY_COUNT = 5
@BPV_SECONDARY_ZONE_BUILDING_SLOT_ROWS = 2
@BPV_LOWER_DISTRICT_BUILDING_SLOT_ROWS = 8
@BPV_MAIN_DISTRICT_CARD_HEIGHT = 615
@BPV_MAIN_DISTRICTS_SCROLL_CONTENT_HEIGHT = 615
@BPV_LOWER_DISTRICT_CARD_HEIGHT = 481
@BPV_LOWER_DISTRICTS_GRID_ROW_HEIGHT = 491
@BPV_LOWER_DISTRICTS_SCROLL_CONTENT_HEIGHT = 491
```

See `PIF_PRESET_INDEX.md` for the full list of 500 generated presets and the exact calculated values.

## Credits

Built as a configurable submod for UI Overhaul Dynamic.

Derived from / inspired by BPV Reborn - Zone Double Row Mode, then reworked into a configurable zone rows framework.
