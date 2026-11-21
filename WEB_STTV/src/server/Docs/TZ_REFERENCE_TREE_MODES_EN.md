# Mixed research trees and the event technology filter

## Contents

- [Tree settings](#tree-settings)
- [Mixed branches](#mixed-branches)
- [Events and debris](#events-and-debris)
- [Placement and card appearance](#placement-and-card-appearance)
- [Acceptance](#acceptance)

## Tree settings

Approved specification. In System settings, add a **Tree settings** tab alongside Database operations. Place two independent switches on this tab, “Mixed trees” and “Hide event and debris technologies”. Both default to off. [Tabs specification](../../../Docs/frontend/elements/TZ_TABS_EN.md)

Changing either switch opens the selected combination on the server through `POST /api/trees/reference`. The `tree_id` includes the reference mode, normalized list of enabled DLC and both boolean fields, `mixed_trees` and `hide_event_technologies`. Each field defaults to `false`. Explicit defaults produce the same ID as omitted fields.

The server saves the complete settings in the `tree_configs` document with that ID and the result in its own `tree_<tree_id>` collection. The first request for a combination builds and publishes it. Subsequent requests open the ready collection if its source and rule revisions are current. A given DLC selection can have up to four collections, one per requested switch combination. Clear generated trees removes these collections and their settings records. [Reference tree contract](TZ_REFERENCE_TREE_EN.md)

## Mixed branches

When enabled, skip only the `same_area` parent selection criterion. Apply the remaining criteria in the existing order to direct prerequisites available under the selected DLC, before applying the event technology filter. Keep the existing diagnostics if more than one candidate survives.

Place the whole branch in its root's research area section. Each descendant retains its own area, color, research currency and tier column. Draw the selected parent connection across research areas, including connections to a lower tier. Display each card once. With mixed trees disabled, apply the existing area boundaries and connection rules.

## Events and debris

The classifier distinguishes starting grants, setup for a future project and the outcome that awards the technology. [Revised acquisition rules](TZ_EVENT_TECHNOLOGIES_AND_SCOPE_TEXT_EN.md)

The server classifies technologies whenever it builds a tree, regardless of the visibility filter. It marks a technology when all of the following hold.

1. The base technology has an explicit, unambiguous weight of zero. Its research draw modifiers have no positive additive bonus. Multipliers are allowed. Use the original game rules, including conditions suppressed in the tooltip. Treat AI selection weight separately.
2. At least one route to this technology is confirmed through an event, anomaly, excavation, astral rift, special project or debris analysis. Include research options, fully researched grants and partial progress. Debris requires a confirmed carrier. A random reward requires evidence that the technology is eligible.
3. All established independent acquisition routes belong to that group. Starting grants and ascension perk rewards belong to other settings. If a technology has one of those routes alongside an event or debris, keep it visible through this filter. Classify by what initiates the chain. For example, an ascension perk may start a special project whose final event grants the technology.

For conflicting weights, an unresolved additive operation or a material unresolved acquisition route, the server keeps the technology visible and records the reason. Determine the property from acquisition routes across the complete game snapshot. Apply the existing DLC availability check separately when the user changes the selection. Use the existing reward index, debris evidence and game fields on the server. Tree preparation requires no rendered tooltip text. [Acquisition evidence and audit limits](TECHNOLOGY_ACQUISITION_RESULTS_EN.md)

## Placement and card appearance

- When assigning coordinates, always place marked technologies without prerequisites as the last trees in their area. Within a tree, place independent ordinary branches above marked branches. If an ordinary technology continues a marked technology, keep that descendant in the same subtree. Apply the existing continuation and localized alphabetical order to ties.
- In mixed mode, this ordering applies within the root's section. A marked descendant from another research area stays in the shared branch. A technology with no visible parent follows the root placement rule and retains the reason for its missing connection.
- Contrasting diagonal stripes are the permanent style of the inner surface of every marked card, including on first opening the tree. Draw the stripes over the card's research area color. Define stripe colors for both themes in the style dictionary. The title, icon and rare or dangerous frame remain legible.
- After parent selection and layout, the server writes final visibility to the node's existing `availability` field in `tree_<tree_id>`. The value is `true` when the selected DLC allow the technology and the filter permits it. With the filter on, marked technologies have `availability = false`. With the filter off, only the selected DLC determine the value.
- The tree API returns nodes with `availability = true` in `items`. In the saved collection, a card hidden only by the filter has the same `parent_tech`, `children` and RU/EN coordinates as with the filter off. Its ordinary child keeps its position. A connection is visible when both cards are available. The technology page keeps its complete game prerequisites.

## Acceptance

1. Open System settings → Tree settings and check both switches in RU and EN. Request all four combinations with all DLC, then with no DLC. For each DLC selection, verify four distinct IDs, four records with the exact settings in `tree_configs` and four corresponding collections. Return to a previous combination and verify that the ready collection is read without rebuilding. For pairs that differ only by filter, compare every node's parent, children and coordinates in both languages, and verify expected visibility. Check reciprocal edges, unique visible positions and absence of cycles and overlapping cards.
2. Colonial Bureaucracy (Society, tier 2) has cross-area continuations Quantum Firewalls and Quantum Hacking (Physics, tier 1). In mixed mode verify the parent under the applicable criteria, the root's section, the cards' own color, tier 1 column and connections. Also cover a branch in which choosing between two parents actually depends on `same_area`. [Original example](../../../Docs/frontend/TECHNOLOGY_CHAINS_AND_SORTING_EN.md)
3. Check the classification and supporting reasons across all technologies. Distinguish events, debris, start, ascension perks, mixed paths and insufficient evidence. Verify weight and reward type for every marked technology. The 97 technologies with an unambiguous zero weight in the 4.5.4 snapshot form the initial audit set.
4. Examples include Trinary Computing for observation events, Mining Drone Lasers for debris progress, Subspace Drive for a conditional starting grant, Xeno-Linguistics for `add = 100`, and `tech_crystal_armor_1` for the `add = 5` suppressed in the tooltip. Check the ascension perk path to Colossi, an alternative non-event route, an unknown route and conflicting weight declarations.
5. On first opening the tree and in both branch modes, check stripes, root and child branch ordering, light and dark themes, and 50% scale. Enable the filter on a branch with an ordinary child of a marked parent. Verify that the child keeps its position and the connection to the hidden parent disappears. Disable the filter and compare parents, coordinates, stripes and edges to the original tree. The hidden technology's standalone page and references in the prerequisites of other cards remain accessible.
6. For both collections, compare the IDs in `items` with the IDs of documents where `availability = true`, on initial build and when reopening. Verify the `true → false` change for a DLC-eligible marked technology when the filter is enabled. Expect `true` in both collections for an eligible ordinary technology and `false` in both for a DLC-excluded technology.

[Русская версия](TZ_REFERENCE_TREE_MODES_RU.md)
