# Stellaris Technological Tree View — Database adapter specification for the interface

## Contents

- [Status and purpose](#status-and-purpose)
- [Source data and scope](#source-data-and-scope)
- [Technology catalog](#technology-catalog)
- [Technology representations](#technology-representations)
- [Identity and source references](#identity-and-source-references)
- [Technology requirements](#technology-requirements)
- [Localization integration](#localization-integration)
- [Responsibility split](#responsibility-split)
- [Display updates](#display-updates)
- [Acceptance criteria](#acceptance-criteria)
- [Subsequent implementation details](#subsequent-implementation-details)

## Status and purpose

As of 2026-11-17, this document's single-file and unqualified-reference provisions are superseded by the approved [stage-two specification](TZ_FRONTEND_STAGE_2_EN.md). The current implementation opens three version-five databases as one set and uses `{ database, pointer }` references; other applicable requirements remain in effect.

This document records the interface data model and adapter responsibilities agreed by the user on 2026-11-16. The adapter has not been implemented yet.

The basis is the [interface concept](CONCEPT_EN.md), [Technology field specification](elements/TZ_TECHNOLOGY_FIELD_EN.md), [Card specification](elements/TZ_TECHNOLOGY_CARD_EN.md), and [Shared localization specification](TZ_LOCALIZATION_EN.md).

The adapter extracts first-screen data from the prepared database and builds an in-memory catalog. Components receive clear technology and representation objects; tree-reading rules are centralized in the adapter.

The adapter is implemented as TypeScript modules and runs in a Web Worker under the [database opening specification](TZ_DATABASE_OPENING_EN.md#file-reading-and-web-worker). File reading and the message protocol are separated from technology extraction and requirement processing. The complete tree stays in Worker memory; the main thread receives prepared display data. `sourceRef` is resolved in the Worker, which holds the corresponding original node.

## Source data and scope

The source is the prepared database containing parsed trees and `enrichments.localization`. The adapter uses stored data; reparsing game files and evaluating conditions for a particular empire are outside its responsibilities.

Inspection of the current stage-ten database found:

| Metric | Value |
| --- | --- |
| Base technologies | 679; all define `area` and `tier` |
| `technology_swap` variants | 206 |
| Variants changing research area | 7 |
| Logical blocks in `prerequisites` | 21 `OR` blocks |
| Unresolved technology references in `prerequisites` | 0 |
| Other research category and tier definitions | 19; do not become technology cards |

These counts describe the inspected data and are not hardcoded. Technology membership follows game definitions and their locations, rather than translation availability or a particular field prefix. Exact selection settings are established during implementation design.

The catalog is a derived in-memory representation. The source database contents, structure, and preserved game mechanics remain unchanged. Fields unnecessary for the first screen remain accessible in source nodes; they are not copied into every card.

## Technology catalog

The adapter produces a dictionary keyed by base technology ID. One entry corresponds to one base technology and one field card.

| Field | Contents |
| --- | --- |
| `id` | String: base technology ID from the database; matches the catalog key |
| `tier` | Integer: technology level used for column assignment |
| `prerequisites` | Technology requirement tree preserving logical operations |
| `prerequisiteIds` | Array of unique directly mentioned technology IDs, including alternatives; produced by the shared requirement processor |
| `requirementCount` | Non-negative integer requirement count under the agreed rules; produced by the shared requirement processor |
| `representations` | Ordered array: base representation and variants |
| `sourceRef` | Reference to the base technology's original node in the loaded database |

Research area belongs to the representation: the selected representation determines the card's effective area. `tier` and requirements belong to the base technology and remain unchanged during manual variant switching under the card specification.

Tier is extracted from data, rather than the technology name. The `0…5` range describes the current database and does not replace reading `tier`.

## Technology representations

Every technology has a base representation. Separate representations for all its `technology_swap` blocks follow in database order.

| Field | Contents |
| --- | --- |
| `id` | Identifier of the base representation or a specific variant block; distinguishes representations within a base technology |
| `variantNumber` | Positive variant number starting at 1; the field is absent from the base representation |
| `area` | Effective research area: `physics`, `society`, or `engineering` |
| `nameId` | Name string ID for the shared localization mechanism |
| `descriptionId` | Description string ID for the shared localization mechanism |
| `sourceRef` | Reference to the source node for the base representation or corresponding `technology_swap` block |

The base representation takes `area` from the base technology. A variant uses its own area when defined, otherwise the base technology's area. The catalog representation already contains the effective value, so the card does not compute this inheritance.

`variantNumber` follows `technology_swap` block order, rather than matching titles or localized label order. It supplies suffixes under the card specification and does not replace representation identity.

Example for `tech_titans`:

| Representation | Variant number | Effective area | `nameId` |
| --- | --- | --- | --- |
| Base | Absent | `engineering` | `tech_titans` |
| First variant block | 1 | `engineering`, inherited | `tech_nomads_titans` |
| Second variant block | 2 | `society`, defined by the variant | `tech_biogenesis_titans` |

`trigger` conditions do not select or exclude variants automatically. The user switches representations manually in the first stage.

## Identity and source references

The base ID persists across representation, language, theme, and research area changes. The selected representation is identified by the combination of base technology and specific representation identifier.

Different blocks with matching titles or localization IDs remain separate representations. Representation identity is not derived solely from displayed text or its name key.

Under the [Worker result specification](TZ_WORKER_RESULT_EN.md), the base representation has ID `base`, and variants have `swap:1`, `swap:2`, and so on in original order. The number in `swap:N` matches `variantNumber`; `base` has no `variantNumber` field.

Representation identity is guaranteed within the loaded database. Matching selected variants after a database rebuild belongs to persistent-state design; block numbering or locations are not assumed stable across builds.

`sourceRef` is a string path to the original node within the loaded database tree, for example `/documents/7/items/5` for `tech_titans` in the current file. It refers only to the database from which the catalog was produced; replacement discards old references with the catalog. The Worker retaining the tree resolves the path.

## Technology requirements

The adapter extracts only the base technology's `prerequisites`, preserving nesting and logical operations. Conditions from `potential`, DLC, empire, species, building checks, and other eligibility restrictions are not added to this tree.

A plain list retains simultaneous-requirement meaning. Missing `prerequisites` means no technology requirements. Alternative groups are not converted into simultaneously mandatory technology lists.

For example, `tech_titans` requirements have this structure:

```text
OR
├─ tech_battleships
└─ tech_stinger_growth_2
```

A separate shared requirements processor consumes this tree and derives:

- The immediate predecessor set: unique directly mentioned technology IDs, including alternatives, without transitive expansion.
- Requirement count: a single mandatory technology contributes one, simultaneous requirements are added together, an `OR` group counts as one, and no requirements gives zero.
- Links from predecessors to the dependent technology for subsequent field use.

The example has two predecessor IDs but one requirement. The tree remains the source of logic: links alone do not imply that all alternatives are mandatory. Listing order does not change the predecessor set; the original tree is preserved.

Calculation rules are not duplicated in cards, grouping, or other consumers. The [technology requirements specification](TZ_TECHNOLOGY_REQUIREMENTS_EN.md) defines `technology` and `group` nodes, an `AND` root, counting for `AND`/`OR`, and `from`/`to` links with `requirementPaths`. Using `NOT`, `NAND`, and `NOR` in counting and layout requires separate agreement.

## Localization integration

`nameId` and `descriptionId` match `requested_key` in the selected representation's name and description records. The consumer passes these IDs to localization with the database source; the application provides the language.

Text, provenance, duplicate merging, and inherited descriptions follow the [Localization specification](TZ_LOCALIZATION_EN.md) and [index record specification](TZ_LOCALIZATION_INDEX_EN.md). A record contains `status`, `text`, and `origins`; missing translations allow viewing with markers, while contradictory texts block result preparation and require manual investigation. The adapter does not copy translations for each language into representations or expand game markup.

Selecting a representation changes the string IDs in use. Changing the language changes their resolved text while preserving the base technology and selected representation.

## Responsibility split

| Part | Responsibility |
| --- | --- |
| Database adapter | Extract technologies and representations, effective areas, string IDs, requirement trees, and source references |
| Shared requirements processor | Derive immediate predecessors, requirement counts, and links |
| Localization mechanism | Retrieve text by source, ID, and system language |
| Technology field | Account for selected representations, group and position cards under agreed rules |
| Application state | Store representation selection for each base technology |
| Card and tooltip | Display supplied data through UI kit elements |

The adapter does not assign card coordinates, choose representations for the user, or persist user state. Data extraction is separate from layout and display.

## Display updates

Manual variant selection uses the corresponding `representations` entry. If `area` changes, the field moves the same card to the other region and applies the agreed ordering rules. The base technology's `id`, `tier`, and `prerequisites` remain unchanged.

Language or theme changes do not require catalog extraction or technology requirement calculation to run again. Replacing the source database updates the catalog and its derived data from the new database. Loading and coordinated replacement are refined alongside frontend-to-local-service integration.

## Acceptance criteria

Checks are performed after implementation:

1. The catalog has one entry per base technology; category and tier definitions do not become cards. The inspected database provides a reference of 679 technologies and 206 variants, without hardcoding these counts.
2. Every entry has a base ID, numeric `tier`, requirement tree, representation array, and source-node reference.
3. The base representation comes first and has no `variantNumber`; variants follow database order and are numbered from 1.
4. Checks cover a variant's own area and inheritance of the base area. Selecting `tech_biogenesis_titans` changes the card area to `society` while preserving its base ID, tier, and requirements.
5. Blocks with identical titles and localization keys remain distinct through representation identity and source references.
6. Checks cover no requirements, one mandatory technology, multiple mandatory technologies, and `OR`. Logic is preserved; `tech_titans` produces two immediate predecessors and one requirement.
7. Predecessors are not expanded transitively; listing order does not change their set. Conditions outside `prerequisites` do not affect links or requirement count.
8. Name and description IDs match `requested_key`; the shared localization mechanism retrieves translations, including inherited descriptions.
9. Language and theme changes preserve the catalog, requirements, and selected representations. The field owns layout; the adapter does not calculate coordinates.
10. `sourceRef` resolves to the corresponding original node in the loaded database. Catalog preparation does not change the database file or its game data.

## Subsequent implementation details

The adapter receives data only after the user explicitly opens a prepared JSON under the [startup and database opening specification](TZ_DATABASE_OPENING_EN.md). In-memory catalog preparation does not run the generator, read game sources, or change the database file. Application startup and page refresh do not themselves load the database.

Messages and operations are defined by the [Worker protocol](TZ_WORKER_PROTOCOL_EN.md), the `ready` container, technology fields, representation IDs, and string `sourceRef` values by the [result specification](TZ_WORKER_RESULT_EN.md), and the tree and links by the technology requirements specification. Module APIs, selection settings, and use of negative logical operations in counting and layout remain to be defined. The adapter consumes the database contract validated by the backend; full validation of the original tree is not repeated. Diagnostics for problems discovered while transforming data into the display model are refined within the [division of responsibilities](TZ_DATABASE_OPENING_EN.md#validation-responsibilities). The catalog is published together with links and localization only after successful preparation; a blocking error does not become an empty catalog, and cancelled-operation results are not used.

Ordering between technology groups, positioning across columns, and drawing links remain field-design responsibilities. Worker messaging details, persistent state, and matching variants across database builds are considered separately. These remaining details are not considered approved by this document.

[Русская версия](TZ_DATABASE_ADAPTER_RU.md) · [Interface concept](CONCEPT_EN.md).
