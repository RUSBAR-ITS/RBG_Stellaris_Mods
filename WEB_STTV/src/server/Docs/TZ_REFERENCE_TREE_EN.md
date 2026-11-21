# WEB_STTV server. The reference technology tree

## Contents

- [Purpose](#purpose)
- [Collections and tree identity](#collections-and-tree-identity)
- [First pass. DLC availability](#first-pass-dlc-availability)
- [Second pass. Parent and children](#second-pass-parent-and-children)
- [Third pass. Coordinates](#third-pass-coordinates)
- [Opening and publication](#opening-and-publication)
- [Clearing generated trees](#clearing-generated-trees)
- [DLC profile matrix](#dlc-profile-matrix)
- [Acceptance](#acceptance)

## Purpose

This document describes the initial reference tree. The [tree settings specification](TZ_REFERENCE_TREE_MODES_EN.md) extends its collection identity, visibility and layout contract.

**Approved specification.** On request, the server opens or builds a reference tree in MongoDB. The set of enabled DLCs is the only user setting that determines membership. This stage uses the base representation of each technology. For one DLC set the server selects parents once and prepares coordinates for both Russian and English.

The source is the published game data in `wiki`. The inspected import contained 679 technologies in `technologies` and 36 expansions in `dlcs`. The server reads game IDs from `_id`, expanded definitions from `tree` and translations from `localization`. A separate server rules configuration defines the order of criteria, default empire characteristics and placement rules. Its path is a server setting. The starting points for the port are the [parent rules](../../../config/enrichment/technology_tree/rules.json), [DLC rules](../../../config/enrichment/dlc.json) and [layout settings](../../../config/frontend/tree_layout.json).

## Collections and tree identity

- `tree_configs` contains one document per configuration. It records the tree `_id`, `mode = "reference"`, `enabled_dlc`, `state`, and the source and rules revisions. A failed build records its cause.
- Validate incoming IDs against `wiki.dlcs`, remove duplicates and sort by ID. For example, `["dlc036","dlc032","dlc036"]` and `["dlc032","dlc036"]` identify the same configuration. An empty array disables every DLC. The initial “all enabled” selection expands to all IDs in the current catalog.
- The `tree_id` is the SHA-256 digest of compact UTF-8 JSON containing `mode` followed by `enabled_dlc`, in that order. The `tree_<tree_id>` collection holds one document per source technology, including hidden ones. Language and zoom are outside the identity.

| Node field | Value |
| --- | --- |
| `_id` | Game technology ID |
| `availability` | Boolean indicating visibility in the reference tree with the selected DLCs |
| `parent_tech`, `children` | Selected parent ID or `null`, and the IDs of immediate children in stable order without duplicates |
| `area` | Research area of the technology |
| `location` | For a visible node, an object such as `{"ru":[2,7],"en":[2,4]}`. Each pair gives the zero-based column and row within its research area. A hidden node has `null` |

A hidden node has `parent_tech: null` and `children: []`. Both layouts use the same edges. Names and descriptions remain in the game localization source.

## First pass. DLC availability

The function receives the technology catalog, enabled DLCs and the game definitions needed to evaluate conditions. It creates a record for every ID. The DLC catalog provides the game name used by `host_has_dlc`. For example, `dlc036` maps to `BioGenesis`.

Hiding requires a proven DLC dependency. The selection must make `potential` false or activate a weight modifier with `factor = 0`. Comparison with an evaluation in which DLC state is unknown distinguishes DLC effects from constant conditions. Recursively evaluate logical blocks, wrappers and supported indirect references in their original scope. A zero base weight or an ethic requirement alone leaves the card visible. An unknown result also keeps the technology visible and records the reason in diagnostics. [Filtering rules](../../../Docs/TZ_BACKEND_STAGE_20_EN.md) · [Indirect dependencies](../../../Docs/TZ_BACKEND_STAGE_21_EN.md)

The previous file-based system had a technology acquisition index covering `common`, `events` and `prescripted_countries`. The current MongoDB import lacks that complete index. For a `has_technology` reference, blocking ordinary research alone cannot establish that acquisition through an event is impossible. When route coverage is incomplete, the reference evaluates to unknown. Another branch of the same condition can still decide the outcome. Diagnostics identify the affected technology and condition path. [Acquisition analysis](../../../Docs/TZ_BACKEND_STAGE_21_ACQUISITION_EN.md)

## Second pass. Parent and children

The function visits visible technologies. Candidates are visible technologies referenced by their original `prerequisites`, preserving the distinction between mandatory requirements and alternatives. Apply configured criteria in the existing order until a single candidate remains. If a criterion leaves zero matches, keep the previous candidates and continue. Once selected, immediately write the parent to the child's `parent_tech` and append the child to the parent's `children`. At this point every node already exists in memory.

**Each child technology supplies its own empire context.** In the former position of `standard_empire`, before the highest-tier criterion, perform these steps:

1. Recursively read the child's own `potential`, preserving `AND`, `OR`, supported negations and the scope of each characteristic. A founder-species check and a check on a federation member refer to different objects. The child does not inherit candidate characteristics through `prerequisites`.
2. Use the child's constraints for the characteristics that it specifies. Use the ordinary empire defaults for the remaining free characteristics. Keep allowed alternatives intact. With `A OR B`, either branch can qualify and defaults must preserve each viable branch. When a check refers to another game definition, follow the reference only under a known rule for its meaning and scope. An unknown predicate, unresolved reference or cycle leaves the affected branch uncertain.
3. Evaluate each candidate's own `potential` in this context with the selected DLCs. Eliminate a candidate only when it is provably incompatible with every viable branch. A match on any branch or an undecided outcome keeps the candidate. Log the alternatives considered, the facts used and the outcome of this criterion. The earlier exact `potential` match retains its priority. [Matching conditions](../../../Docs/frontend/CHAIN_AVAILABILITY_EN.md)

If every candidate is hidden, a visible technology starts its own branch with a `no_visible_parent` diagnostic. Multiple remaining candidates also yield `parent_tech: null`. Log the ambiguous technology, remaining candidates, tree ID, DLCs and rules revision. A technology with no source prerequisites is an ordinary root.

## Third pass. Coordinates

Place the same graph twice, looking up names through server localization for `ru` and `en`. Research areas appear in the order physics, society, engineering. The column is the display tier, including tier 6 for technologies with `tier = 5`, `levels = -1` and at least one technology prerequisite. A cross-area edge remains in the data and its child starts a branch in its own area.

Trees with a starting root come first. Among children, continuations whose IDs match after digit removal come first. Sort each tied group by the displayed name using the appropriate language's collation, then by game ID. A missing translation uses the same key placeholder as the card. The first child tries the parent's row in a different column or the following row in the same column. Subsequent branches start below the preceding subtree. Each visible technology occupies exactly one free cell per language. The client computes lines and pixel geometry. [Grid placement rules](../../../Docs/frontend/TZ_FRONTEND_STAGE_5_EN.md)

## Opening and publication

The endpoint is `POST /api/trees/reference`. A request of `{"enabled_dlc":[]}` opens a tree with all DLCs disabled and `{}` opens one with all enabled. Invalid types, unknown IDs or unsupported settings return HTTP 400. The HTTP 200 response contains `tree_id`, normalized `enabled_dlc`, an `items` array of visible nodes with both layouts, and card fields in `cards`.

1. Reuse a `ready` tree when its collection exists and its source and rules revisions are current. The source revision covers the UUIDs of all published input collections used, including localization. The rules revision covers the algorithm and the rules configuration contents. The current loader replaces source collections on reimport. [Loader collection revision check](../../loader/sttv_loader/__main__.py)
2. A missing, stale or `failed` result starts a build. Concurrent requests for the same ID share one calculation. The three functions run sequentially in memory. After checking edges and placements, the server writes the complete result and changes the configuration from `building` to `ready`.
3. The server must avoid serving a mixture of source revisions during loader publication or if the source revision changes during calculation. A failure records the reason for retry. After a process interruption, the next request recovers the abandoned build. Clients can access only complete trees. Server writes target tree results and their configuration records.

## Clearing generated trees

Add a **Clear generated trees** button to the actions in the left menu panel. It is available even when no tree is open and applies to all DLC sets in reference mode. Use the shared UI button and built-in localization. Disable the button while its request is pending. [Menu panel](../../../Docs/frontend/elements/TZ_MENU_PANEL_EN.md)

On activation the client sends `DELETE /api/trees/reference` without parameters. The server selects `reference` records from `tree_configs`. For each record it drops the `tree_<tree_id>` collection if it exists, then removes the configuration record. This order allows a retry after a partial failure. Cleanup covers only generated trees for this mode and their registry records.

If a build is active, the server returns HTTP 409 before starting deletion. Requests to open a tree during cleanup also receive HTTP 409. An abandoned `building` record with no active calculation is eligible for cleanup.

On success the server returns HTTP 200 with the number of collections actually removed, for example `{"removed_collections":2}`. An empty set returns zero. The client clears the displayed tree, retains the selected DLCs and shows the count in the status panel. A new build starts the next time the user explicitly opens a tree. On failure the status panel displays the reason.

## DLC profile matrix

HTTP acceptance covers **10 distinct selective DLC sets** and two additional boundary cases. For rows 1–9, pass only the listed IDs in `enabled_dlc`. For row 10, take all IDs from the current `wiki.dlcs` catalog and exclude the two listed. Reordering input IDs tests reuse. Switching languages checks the second layout of the same tree.

| Profile | DLC selection | Visible in the response | Hidden from the response |
| --- | --- | --- | --- |
| All DLCs | `{}` | `tech_cosmogenesis_weaver`, `tech_archaeo_pk_devolving_beam` | `tech_archeology_lab` |
| No DLCs | `{"enabled_dlc":[]}` | `tech_archeology_lab`, `tech_missiles_1` | `tech_weaver_bio_anti_evasion_1`, `tech_arcane_deciphering` |
| 1 | `dlc036` | `tech_weaver_bio_anti_evasion_1` | `tech_identity_copy`, `tech_cosmogenesis_weaver` |
| 2 | `dlc032` | `tech_identity_copy` | `tech_weaver_bio_anti_evasion_1`, `tech_cosmogenesis_weaver` |
| 3 | `dlc032`, `dlc036` | `tech_cosmogenesis_weaver` | `tech_titans` |
| 4 | `dlc021` | `tech_archeology_lab_ancrel`, `tech_arcane_deciphering` | `tech_archeology_lab`, `tech_archaeo_pk_devolving_beam` |
| 5 | `dlc017` | `tech_titans`, `tech_archeology_lab` | `tech_archaeo_pk_devolving_beam`, `tech_arcane_deciphering` |
| 6 | `dlc017`, `dlc021` | `tech_archaeo_pk_devolving_beam`, `tech_titans` | `tech_archeology_lab` |
| 7 | `dlc023`, `dlc027` | `tech_juggernaut`, `tech_hyper_relays` | `tech_titans` |
| 8 | `dlc029`, `dlc031` | `tech_cloaking_1`, `tech_rift_sphere` | `tech_hyper_relays` |
| 9 | `dlc034`, `dlc040` | `tech_dyson_gun`, `tech_galactic_archivism` | `tech_rift_sphere` |
| 10 | All except `dlc032`, `dlc036` | `tech_missiles_1`, `tech_archaeo_pk_devolving_beam` | `tech_identity_copy`, `tech_weaver_bio_anti_evasion_1` |

Rows 1–3 exercise the indirect biological ship condition in combination with The Machine Age. Rows 4–6 distinguish the negative Ancient Relics condition, the joint Apocalypse and Ancient Relics requirement, and the zero-weight modifier for `tech_arcane_deciphering`. In row 10 missiles remain visible through an alternative in `OR`.

For each set, open the tree, read its MongoDB collection, then open it again. Match source IDs against collection documents and each document’s `availability` flag against membership in the HTTP response. Check the expected IDs above, reciprocal edges, unique cells within each area for RU and EN, and `location: null` for hidden nodes. For each set, record the requested IDs, `tree_id`, visible and hidden counts and any differences from the expected IDs. Distinct sets must have distinct tree IDs. Reopening the same set must reuse its ready collection.

## Acceptance

| Scenario | Expected result |
| --- | --- |
| `tech_science_arkship` | When candidates reach the empire criterion, use the child's `is_nomadic = yes`. Candidate `tech_arkship_construction` passes the nomadic check. |
| `tech_modular_engineering` | This child has no `potential`. With both candidates visible at the criterion's input, the default profile keeps `tech_starbase_3` from its pair with `tech_waystation_2`. |
| `tech_transcendent_faith` | Preserve the alternative between spiritualism and a non-gestalt empire with the relevant federation perk. The earlier exact match with `tech_consecration_fields` is evaluated first. |
| Small fixtures | Cover nested alternatives, negation and an unknown branch, all parents hidden, a criterion with zero matches and an unresolved tie. A cycle of selected parent edges blocks publication. |
| Edges and grid | Check reciprocal parent and child records for each selected edge. Verify cell uniqueness within each area for RU and EN, differing translated name order, stable ties and a cross-area branch. |
| Reuse, concurrency and failure | Reordered or repeated DLC IDs return the same ready tree. A second request shares the calculation. Verify failure before publication, recovery, and invalidation after a source or rule revision change. |
| Clear from the menu | Start with an empty test registry and build all 12 trees in the matrix. Activating the button once returns `{"removed_collections":12}` and removes all 12 collections and their records. Source game collections remain accessible and DLC selection is retained. Repeating the action returns zero. Explicitly reopening rebuilds only the selected tree. |
| Concurrent cleanup and failure | Cleanup during an active build returns HTTP 409 and preserves the trees. After interruption between dropping a collection and removing its registry record, a retry completes cleanup. |

Run synthetic checks on small fixtures. Run integration checks over HTTP on the Ubuntu VM with published game data. Compare the DLC matrix with the previous stage for comparable source versions and explain differences. Measure each pass of the initial build and the time to reopen the ready tree. [Stage 21 reference results](../../../Docs/BACKEND_STAGE_21_EN.md)
