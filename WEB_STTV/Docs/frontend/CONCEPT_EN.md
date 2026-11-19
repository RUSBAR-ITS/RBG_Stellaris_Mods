# Stellaris Technological Tree View — initial interface concept

## Contents

- [Status](#status)
- [Simple design and atomic structure](#simple-design-and-atomic-structure)
- [Localized strings](#localized-strings)
- [Color and typography dictionary](#color-and-typography-dictionary)
- [Main window](#main-window)
- [Menu panel](#menu-panel)
- [Status panel](#status-panel)
- [Technology field](#technology-field)
- [Card and tooltip](#card-and-tooltip)
- [Language and theme](#language-and-theme)
- [Settings and state persistence](#settings-and-state-persistence)
- [Further design](#further-design)

## Status

Current implementation: [frontend 0.0.6](FRONTEND_STAGE_6_EN.md), with tree connections and hover highlighting.

This document records agreed decisions about the window layout and initial interface. The first stage is implemented under the prepared and approved specifications; running instructions and the actual implementation are described in the [guide](FRONTEND_STAGE_1_EN.md).

The [UI element reference](UI_ELEMENTS_EN.md) contains only a categorized list of current elements with links to their specifications. Agreed requirements are recorded in separate document pairs under `Docs/frontend/elements/`; [Text](elements/TZ_TEXT_EN.md), [Icon](elements/TZ_ICON_EN.md), [Button](elements/TZ_BUTTON_EN.md), [Selection control](elements/TZ_SELECT_EN.md), [Language selector](elements/TZ_LANGUAGE_SELECTOR_EN.md), [Theme toggle](elements/TZ_THEME_TOGGLE_EN.md), [Menu collapse/expand button](elements/TZ_MENU_TOGGLE_EN.md), [Technology card](elements/TZ_TECHNOLOGY_CARD_EN.md), [Tooltip](elements/TZ_TOOLTIP_EN.md), [Menu panel](elements/TZ_MENU_PANEL_EN.md), [Bottom menu button group](elements/TZ_MENU_BUTTON_GROUP_EN.md), and [Technology viewport](elements/TZ_TECHNOLOGY_VIEWPORT_EN.md) are described.

Frontend documentation resides in `Docs/frontend/`, and code in `src/frontend/`. Shared decisions about Python, TypeScript, HTML/CSS, and portable distribution are in the [general specification](../TZ_EN.md). RU/EN names and descriptions already reside in the database under [stage ten](../BACKEND_STAGE_10_EN.md).

Under the [technology stack specification](TZ_TECH_STACK_EN.md), the interface uses React and TypeScript with plain CSS; Vite provides the development environment and build. Current-session state uses React's built-in facilities. Database processing stays in independent TypeScript modules invoked by the Worker. The [frontend structure specification](TZ_STRUCTURE_EN.md) defines code, configuration, localization, and asset directories; exact program interfaces are designed separately.

The [Worker protocol specification](TZ_WORKER_PROTOCOL_EN.md) defines the `open_database` command, `progress`, `ready`, and `error` responses, and shared `operationId`. The application accepts responses only for the current operation from the current Worker; cancellation terminates it without awaiting acknowledgement. The [Worker result specification](TZ_WORKER_RESULT_EN.md) establishes the `data` container with the catalog, links, localization, and diagnostics, technology fields, `base`/`swap:N` representation IDs, and string references to original nodes. The [technology requirements specification](TZ_TECHNOLOGY_REQUIREMENTS_EN.md) describes the tree with an `AND` root and links with paths to occurrences. The [localization index record specification](TZ_LOCALIZATION_INDEX_EN.md) defines `status`, `text`, `origins`, duplicate merging, and failure for contradictory texts. The [diagnostics specification](TZ_DIAGNOSTICS_EN.md) defines the shared record, initial codes, and `error` response: one blocking cause and accumulated warnings. Received diagnostics remain in the main thread after Worker termination. The [report saving specification](TZ_DIAGNOSTIC_REPORT_EN.md) defines the Save report menu action for a completed attempt: JSON with its outcome and diagnostics is opened in an external editor. Integrated viewing is deferred; exact technical details and use of negation in layout are refined separately.

Under the [startup and existing database opening specification](TZ_DATABASE_OPENING_EN.md), the initial interface is tested from the development environment without portable packaging. Startup and page refresh load only the interface; the user explicitly selects a prepared JSON through Open database in the menu. Before that, the bottom status panel prompts the user to open a file through the menu, and the workspace stays clear. File API reading of the selected file, JSON parsing, and TypeScript adapter modules run in a Web Worker. The complete database tree stays in the Worker; the main thread receives the catalog, requirements and links, and the RU/EN localization index. Generation and enrichment do not run, game sources are not read, and a database update button is not provided yet. Viewing a prepared database works without a Python service.

The [database opening specification](TZ_DATABASE_OPENING_EN.md#interface-states) defines five states: No database open, Loading, Ready, Empty catalog, and Error. Loading shows the current stage without percentages and supports cancellation. Cancelling the file dialog preserves the current database; selecting a new file terminates the old Worker and drops previous data. Failed or cancelled loading does not restore the previous database. Success displays new technologies in base representations from the upper left corner while preserving language, theme, and menu state. Reprocessing the same file is explicit; stale Worker messages are ignored.

## Simple design and atomic structure

The first stage uses the simplest practical design: readable text, clear element boundaries, basic spacing, and two themes. Visual complexity belongs to subsequent stages.

The interface follows atomic design principles. Reusable UI elements are defined in a UI kit; composite elements and views are assembled from them. Repeated element behavior and styling are defined in one place.

Preliminary decomposition for the future specification:

| Level | Contents |
| --- | --- |
| Shared styling settings | Day and night theme colors, typography, spacing, borders |
| Basic elements | Text, icon, button, selection control |
| Composite elements | Language selector, theme switch, technology card, shared tooltip |
| Interface regions | Menu panel and scrollable technology field |
| View | Main window assembled from regions and UI kit elements |

Specific component names, source structure, and interface library will be determined in the specification. Decomposition must remain proportionate to the simple initial screen.

A button supports optional text and an optional icon, with a visible or hidden border; a menu item can use the same element. The [Button specification](elements/TZ_BUTTON_EN.md) describes an optional binding to the shared [Tooltip element](elements/TZ_TOOLTIP_EN.md), which also displays technology descriptions. Shared placement and styling rules reside in the Tooltip specification; its consuming component determines visibility conditions.

In the first stage, the [Selection control](elements/TZ_SELECT_EN.md) is a dropdown with one selected value. Its consuming component supplies the option set, label identifiers, and current value, and receives the selection result.

## Localized strings

The [Text element](elements/TZ_TEXT_EN.md) receives a source and a string identifier. The default source is built-in: interface strings reside in separate localized files, and the application language setting determines which file is used. The application database can be a second source: object names and descriptions already reside in its `enrichments.localization` for RU and EN.

A shared localization mechanism receives three values: source, string ID, and current language. Components supply the source and ID and may omit the built-in source; the system provides the language from application state. This applies to button and setting labels, selection options, tooltips, and accessible action names. Changing the language updates displayed strings for the same source/identifier pairs.

Under the [Shared localization specification](TZ_LOCALIZATION_EN.md), separate source configuration describes record locations, language selection, ID matching, and text retrieval. Two small readers handle interface JSON dictionaries and enriched database nodes, preparing an in-memory `source → language → string ID` index. Database IDs come from `requested_key`, and content comes from `text`. Callers supply a string ID without additionally selecting `name` / `description`.

Duplicate IDs with matching text merge while preserving provenance. Differing texts under one ID and language are a blocking data preparation error requiring manual investigation; the prepared result is not published. Index entries have `resolved` and `missing` states. Missing strings display `⟦string ID⟧`, while found empty text remains empty. Missing values together with one unambiguous text produce `resolved` while retaining all original records. No automatic language substitution occurs. Language changes use the prepared index; replacing a source rebuilds its portion of the index.

Built-in strings reside in RU/EN JSON files and may contain named parameters, such as `{number}` for variant suffixes. Database text is displayed as stored: game markup and substitutions remain unprocessed. Localized strings define content, while the styling dictionary defines colors and typography. The complete configuration schema, API, and resource loading require implementation design; existing localization storage in the database is retained.

## Color and typography dictionary

Interface colors and typography properties are defined in a separate centralized styling dictionary under the [Color and typography dictionary specification](TZ_STYLING_DICTIONARY_EN.md). The dictionary resides in CSS files with two variable levels: shared definitions and element-owned variables. UI elements reference their own unambiguously named variables; concrete values and links between variables are assigned in the dictionary. Color literals and typography values are not duplicated in components or views.

Each variable name identifies the element, property role, and state where applicable. Each element defines the background, text, icon, and border colors it uses, along with typography properties: family, size, weight, and line height. Only states that the element actually supports are covered: default, hover, focus, pressed, selected, and disabled. Unneeded states and variables are not added in advance.

Example variable roles with the `--sttv-` prefix; the complete name inventory remains to be determined during implementation design:

| Variable | Purpose |
| --- | --- |
| `--sttv-tech-card-background-default` | Card background in its default state |
| `--sttv-tech-card-background-hover` | Card background on hover |
| `--sttv-tech-card-title-color` | Technology title color |
| `--sttv-tech-card-title-font-family` | Technology title font family |
| `--sttv-tech-card-title-font-size` | Technology title font size |
| `--sttv-tooltip-text-color` | Tooltip text color |

A component selects a variable according to its state; the dictionary determines the value for the active theme. Day and night themes provide the complete set of variables in use; identical values, including typography, may reference shared definitions.

Shared variables define reusable values. For example, a card's own background variable references a shared surface background, while its title font variable references the common interface font. Even when different elements share an appearance, their own variables remain separate. Matching values across elements and states explicitly reference shared definitions; unique values are assigned in the corresponding element dictionary.

In the first stage, each text role's family, size, weight, and line height are identical across both themes. Inter is selected with Cyrillic and Latin coverage; its font files and license are bundled with the portable application for local loading. Neutral gray backgrounds and a muted green accent are agreed: the [palettes](TZ_STYLING_DICTIONARY_EN.md#agreed-palette) and [typography](TZ_STYLING_DICTIONARY_EN.md#typography-and-text-roles) are listed in the dictionary specification. Research areas are distinguished by headings. Shared definitions, day and night theme values, and element assignments are separated into CSS files; element assignments are distributed across small files.

Theme or shared styling changes therefore go through the dictionary; composite components and views keep using the same UI elements and variable names.

## Main window

The [Main window](elements/TZ_MAIN_WINDOW_EN.md) occupies the available application area. The [Status panel](elements/TZ_STATUS_PANEL_EN.md) spans the full width at the bottom; above it sit the menu panel on the left and the [technology viewport](elements/TZ_TECHNOLOGY_VIEWPORT_EN.md) on the right. The menu and viewport occupy the remaining window height. The viewport manages the visible portion of the field and scrolling; the technology field itself determines card placement in rows and columns.

The window assembles existing UI kit elements and connects them to shared state. Without restored state, defaults are Russian, the night theme, an expanded menu, base technology versions, and the upper left field position. Supplied restored state takes precedence; cross-launch persistence is designed separately. Language and theme changes update the entire interface, including open overlays, while retaining technology selections, menu state, and valid offsets.

- The menu panel stays in place when technologies scroll.
- The workspace occupies all remaining space to the right of the panel.
- The vertical scrollbar is on the right of the workspace; the horizontal scrollbar is at the bottom. Each appears when content overflows its respective direction.
- Resizing the window changes the visible portion of the field; card dimensions and their assigned positions remain stable.
- At the leftmost scroll position, the `Level-0` column begins next to the panel with a small gap. The field is left-aligned; resizing the window or collapsing the menu does not introduce empty space before this column.

The default initial viewing position is the upper left corner; supplied restored state takes precedence subject to valid bounds. Changing language or theme, resizing the window, or collapsing and expanding the menu retains valid current scroll offsets. An offset outside the new range is clamped to the nearest valid value on that axis; when overflow disappears, that value is zero. Persistence across launches remains to be discussed within the shared state mechanism.

[Scrollbars](elements/TZ_SCROLLBAR_EN.md) share behavior across both orientations: a track and thumb, configurable thickness and minimum thumb length, and thumb size based on the visible content proportion. Scrollbars remain visible during overflow without overlapping. Dragging and track clicks move the view, with track clicks scrolling approximately one viewport extent; the wheel over the viewport scrolls vertically, and `Shift` + wheel scrolls horizontally. A scrollbar is reachable with `Tab`; while focused, arrows on its axis scroll in small steps, and `Home` / `End` move to the axis's start or end. The container supplies dimensions and offset and receives changes. The track and thumb states use dictionary variables while retaining geometry across state changes.

The window's own colors and viewport background use their corresponding dictionary variables for each theme; child elements use their own styling roles. Tooltips and selection lists appear over content, are not clipped by nested container boundaries, and respect visible window bounds without changing the main layout or field scroll ranges.

## Menu panel

The initial [Menu panel](elements/TZ_MENU_PANEL_EN.md) has two settings: language selection and day/night theme switching. Collapsing the panel is a separate window control action.

The panel is divided into main content at the top with the database action group above language selection, and a bottom group of collapse and theme buttons. Expanded panel width and padding are defined in settings; the panel occupies the available height above the status panel. Background and the workspace border use the dictionary for both themes, and child elements follow their specifications.

The [Menu collapse/expand button](elements/TZ_MENU_TOGGLE_EN.md) uses a left arrow to collapse and a right arrow to expand, without a visible text label and with a localized tooltip. It retains its size and remains available at the bottom of the panel in both states. The menu is expanded on the first launch; a restored state takes precedence. Persistence between launches belongs to the shared application mechanism.

When expanded:

- The panel provides Russian or English language selection.
- Current-state actions appear above language selection: Open database; during loading, Cancel; on error, Retry and Open database.
- The collapse button is at the bottom of the panel.
- The theme button is beside it, to the right.

When collapsed:

- The panel remains as a narrow strip as wide as the expand button plus minimal padding.
- The expand button stays at the bottom.
- Database actions, language selection, and the theme button are hidden; the user expands the menu to access actions. The status panel remains visible.
- The workspace expands into the released space; the active language and theme are retained when collapsing and expanding the panel.

If main menu content exceeds the available height, only that region scrolls vertically and independently of the technology field. The [bottom button group](elements/TZ_MENU_BUTTON_GROUP_EN.md) sits outside the scrollable content and remains available at the bottom of the panel.

Bottom group buttons align to the right edge of the panel with a small amount of padding and form a single row: collapse on the left, theme immediately to its right. They have identical configured dimensions and do not stretch with the panel. Collapsing reserves no space or gap for the theme button; menu button size and group height remain unchanged. The group shares the panel background, and buttons use their own styling. Their tooltips may extend beyond group and panel boundaries without clipping while staying within visible window bounds.

## Status panel

The [Status panel](elements/TZ_STATUS_PANEL_EN.md) is a separate composite UI kit element using Text. It remains visible across the full width at the bottom of the window, occupies its own space below the menu and viewport, does not participate in their scrolling, and does not overlap scrollbars. Collapsing the menu does not change its width.

In the first stage, the panel contains one short localized message about the current state or loading stage. The Ready message uses the actual base technology count from the catalog. Actions stay in the menu; the workspace shows the field only in Ready, stays clear in other states, and does not duplicate messages. The panel's colors and typography use its own styling dictionary variables.

## Technology field

The agreed requirements are collected in a separate [Technology field specification](elements/TZ_TECHNOLOGY_FIELD_EN.md).

The [Database adapter](TZ_DATABASE_ADAPTER_EN.md) prepares an in-memory catalog keyed by base IDs: tier, `prerequisites` tree, representation array, and source-node reference. A representation contains its own ID, effective research area, and name and description string IDs; variants have numbers following original order. A separate requirements processor derives immediate predecessors, requirement counts, and links. The field owns grouping and placement, while application state owns representation selection. The source database remains unchanged.

The field is divided into three regions from top to bottom: **Physics** (`physics`), **Society** (`society`), and **Engineering** (`engineering`). Each card's area is determined by its current representation; dependencies across areas are retained without changing research area order.

A [Research area region](elements/TZ_RESEARCH_AREA_EN.md) is a container with a heading and ordered columns supplied by the field. The heading uses shared Text and built-in RU/EN localization, positioned above the columns and aligned to the left edge of `Level-0`. Region width equals field width, and its height is determined by the tallest column together with the heading and spacing. Headings and configurable vertical gaps distinguish regions; the next region starts below the completed previous one. The heading scrolls with its region. Colors and typography use dedicated dictionary variables that may reference shared theme values.

Within each area, columns correspond to the `tier` field: from left to right, `Level-0`, `Level-1`, …, `Level-5` for the current game data. Columns align across areas. Cards in one column are placed one below another.

A [Tier column](elements/TZ_TIER_COLUMN_EN.md) receives its card order from the field. Its “Уровень N” / “Level N” heading uses shared Text and built-in localization, aligns with the cards' left edge, and repeats in each area. All columns have equal widths matching the card; headings and card list starts align vertically within the region, and the vertical gap between cards is configurable. An empty column retains its width, position, and heading. The heading scrolls with the cards; column and heading colors and typography use dedicated dictionary variables.

The current approach places related technologies in clouds: dependency proximity helps position cards near each other, without requiring a linear row for every chain. Manual technology family definitions will be designed separately.

Vertical order within a column of one research area follows these rules:

- A predecessor in `prerequisites` that belongs to the same column and area appears above the dependent technology; this applies throughout a dependency sequence.
- Subject to those dependencies, technologies with fewer technology requirements appear higher.
- Only technology requirements from `prerequisites` are counted: one mandatory technology contributes one requirement, simultaneously required technologies are added together, and an `OR` alternative group counts as one requirement. Without technology requirements, the count is zero.
- DLC, empire, species, building, and other eligibility conditions are excluded from this count.
- For equal requirement counts, technologies with identical immediate predecessor sets are placed consecutively; ordering within a group is stable by base ID. Technology dependencies retain precedence. Dependencies across research areas do not reorder those areas.

The immediate predecessor set includes technology IDs from `prerequisites`, including alternative members, and does not depend on listing order. It differs from requirement count: mandatory `A` and `B` contribute two requirements, while an `OR` group of those technologies contributes one. Changing the language does not change grouping or card order.

As requested, the first frontend does not draw connecting lines. Ordering between groups is described in the [implementation guide](FRONTEND_STAGE_1_EN.md#display-details); separate alignment of related groups across columns remains future design work.

## Card and tooltip

In the first stage, a [technology card](elements/TZ_TECHNOLOGY_CARD_EN.md) contains only the name in the selected language. All cards share the same configured width and height; changing the window or language, or hovering, does not change their dimensions. The name is centered on both axes, wraps at word boundaries to at most two lines, and receives an ellipsis only on overflow.

Hovering over any part of the card, including padding, shows the shared [Tooltip](elements/TZ_TOOLTIP_EN.md) with the full name as its heading and the description below it in the same language. Moving the pointer away hides it. While that card's variant list is open, its tooltip remains hidden. The card's two-line name limit does not apply to the tooltip. The tooltip overlays content without moving cards and respects visible boundaries.

The card receives the database source and name and description string IDs of the selected representation; the system provides the language, and lookup uses shared source configuration. Default and hover states use the color and typography dictionary, with hover visually highlighting the card. The technology field assigns the research area, column, and vertical position.

Technologies with `technology_swap` support [manual representation selection](elements/TZ_TECHNOLOGY_CARD_EN.md#manual-variant-selection) separately for each card. The base version is displayed by default; clicking opens a choice of the base version and database variants. Selection updates the name and description while retaining the base ID, `tier`, and technology links. If the variant specifies a different research area, the field moves the card there. Selection is retained when language or theme changes; persistence across launches belongs to separate shared state design.

Variants with identical titles remain distinct selection values. Matching variant titles in the list receive [“(Вариант N)” / “(Variant N)” suffixes](elements/TZ_TECHNOLOGY_CARD_EN.md#variant-labels); the number follows the order of `technology_swap` blocks in the database and does not depend on language. The base version retains its title without a suffix. The suffix template comes from built-in localization, leaving original database strings unchanged. Automatic selection based on empire conditions is considered in later stages.

The [variant list](elements/TZ_TECHNOLOGY_CARD_EN.md#variant-list-interaction) uses the shared Selection control: the base version comes first, followed by variants in database order; the current selection is marked. Choosing an option applies the variant and closes the list. Clicking outside or pressing `Escape` closes it without changing the selection. From a focused card, `Enter` / `Space` opens the list, arrow keys move focus between options, and `Enter` confirms the selection; moving focus alone does not apply a variant.

Vanilla images from the overall concept remain an option for later stages; the current card contains only its name.

## Language and theme

The [Language selector](elements/TZ_LANGUAGE_SELECTOR_EN.md) consists of a Язык / Language label and a Русский (`ru`) / English (`en`) dropdown. Selection immediately changes the interface language, technology names, and tooltip descriptions under the [shared localized string rules](#localized-strings). Technology text originates from prepared database localization. Collapsing the menu retains the active language.

The [Theme toggle](elements/TZ_THEME_TOGGLE_EN.md) is a button with an icon and tooltip, without a visible text label. The sun offers to enable the day theme, and the moon the night theme. Switching immediately changes styling throughout the interface, including the menu, cards, and tooltips. Values for both themes are defined in the UI kit's separate [color and typography dictionary](#color-and-typography-dictionary).

The first launch uses Russian (`ru`) and the night theme; a restored user selection takes precedence. Persistence between launches belongs to the shared mechanism described below.

## Settings and state persistence

The user plans to retain many settings and items of application state between launches. The shared persistence and restoration mechanism requires separate design work and a separate specification; its agreed uses include language, theme, expanded/collapsed menu state, selected technology representations, and field viewing position.

UI elements receive the current value and report changes to their consuming component. Persistent storage belongs to the application layer. These boundaries allow element requirements to be discussed alongside separate persistence design.

That design must determine the persisted data, write timing, restoration order, storage format and location, and integration with the rest of the application. The specific storage approach, including the previously discussed JSON-file example, has not been selected yet.

## Further design

Before implementation, a separate specification must define:

- Ordering between distinct groups with equal requirement counts and positioning related groups in neighboring columns under the agreed predecessor grouping; subsequent manual family grouping and connecting line display.
- Remaining manual technology variant selection details: variant availability indication, list geometry and placement, and initial and restored focus.
- Program data representation and adapter module APIs, nested message data for the agreed Worker protocol, and opening and transformation diagnostics. Validation of the produced database remains in the backend under the [division of responsibilities](TZ_DATABASE_OPENING_EN.md#validation-responsibilities); the frontend does not duplicate it.
- A separate specification for shared settings and state persistence and restoration between launches.
- UI kit component structure, specific dimensions, and minimal styling for both themes.
- Exact dictionary CSS files under `src/frontend/styles/`, Inter files under `src/frontend/assets/`, and their loading order; the complete element and state variable name inventory and assignments in both themes based on the agreed palettes and typography.
- Dimensions and spacing for the menu action group and status panel, message identifiers, integrated diagnostic viewing, and invalid template parameter handling; database opening and replacement state behavior is established in the startup specification, and missing-string and conflict rules in the localization specification.
- Checks for layout, scrolling, menu collapse, language, theme, and tooltips.

[Русская версия](CONCEPT_RU.md) · [Overall concept](../CONCEPT_EN.md) · [Project overview](../../README_EN.md).
