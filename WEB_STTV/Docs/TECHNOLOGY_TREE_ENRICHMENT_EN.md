# Technology tree enrichment — agreed approach

## Contents

- [Status and scope](#status-and-scope)
- [Calculation placement](#calculation-placement)
- [Extensible rule configuration](#extensible-rule-configuration)
- [Combinations and per-object results](#combinations-and-per-object-results)
- [Constructing relationships](#constructing-relationships)
- [Freshness and frontend invocation](#freshness-and-frontend-invocation)
- [Future storage model](#future-storage-model)
- [Implementation specification details](#implementation-specification-details)

## Status and scope

Records the decisions discussed on 2026-11-19: backend parent and child calculation using existing databases, results for named combinations, separate extensible rule configuration, and objects as future MongoDB storage units. This is an agreed approach, not an approved implementation specification. New field names and the proposed configuration filename illustrate the contract; the final schema belongs in the specification.

The criteria are grounded in the [complete analytical pass](frontend/CHAIN_RULES_FULL_REVIEW_EN.md). Analysis of event-based technology access is deferred; previously agreed functional evidence, including weaponry, remains applicable. Grid layout and `location` calculation are still being designed.

## Calculation placement

- A standalone Python enrichment module selects `parent_tech` and constructs `children`.
- Inputs are the existing prepared database set, combination parameters and rule settings. Related databases support upgrade, function, production and capacity criteria.
- The operation uses stored data without invoking the parser or collecting game files again. Original definitions and the complete `prerequisites` graph are retained.
- The frontend consumes the result and requests a backend operation when recalculation is needed. Duplicating the same rule evaluation in two programming languages is unnecessary.

## Extensible rule configuration

Enrichment rules reside in a separate configuration. The proposed location is `config/enrichment/technology_tree.json`, with reusable groups extracted into adjacent files as its size grows.

The configuration describes rule identifiers, execution order, enabled states, parameters and mappings. Examples include indirect search depth, related object fields and kinds, functional groups, production modifier mappings and capacity mappings. The combination profile supplies known empire facts without repeating them in every rule.

A proposed compact rule representation, illustrated with two criteria rather than a complete operational ruleset:

```json
{
  "rules": [
    {"id": "same_area", "enabled": true, "parameters": {}},
    {"id": "indirect_affinity", "enabled": true, "parameters": {"depth": 1}}
  ]
}
```

Array order defines application order. Python implements supported criterion types and the shared invocation mechanism. Order, parameters and mappings are configurable; a fundamentally new computation requires a separate handler. Unknown rules produce diagnostics rather than being silently ignored. The configuration does not become a registry of every game-language command.

The agreed selection constraints remain: candidates are immediate technology prerequisites; selection stops at one candidate; an empty criterion result is skipped; eliminated candidates do not return. These constraints are not replaced by exceptions for specific technology pairs.

## Combinations and per-object results

The initial combination is the reference view (`reference`). Its shared record stores the identifier, mode, empire profile, selected technology variants, applied settings and rule revision, and input data identity. A mode name alone does not identify a particular result.

Each technology stores its result for the relevant combination. Schematic object enrichment fragment:

```json
{
  "technology_tree": {
    "reference_default": {
      "parent_tech": "tech_a",
      "children": ["tech_c"],
      "status": "resolved"
    }
  }
}
```

Shared combination parameters are stored once and referenced by identifier. `status` distinguishes a root without requirements, a selected parent and unresolved ambiguity. Ambiguities enter diagnostics with a state snapshot under the [agreed rules](frontend/CHAIN_AMBIGUITIES_EN.md).

A variant selection can change its technology's parent and other technologies' child lists. Combination parameters therefore describe selected representations across the entire field. Calculations cover requested combinations without precomputing every possible variant combination.

Relationship structure is language-independent. Alphabetical child ordering and coordinates belong to later layout and may depend on RU/EN; structural `children` array order does not itself determine visual order.

## Constructing relationships

Technology objects are addressable by ID before parent selection starts. Empty child lists are prepared for a new combination calculation. For each technology:

1. Select its parent using the configured criterion sequence.
2. Store that ID in the technology's `parent_tech`.
3. Immediately append the technology ID to the selected parent's `children`, without duplicates. Extend any existing list.

The parent's own parent does not need to have been calculated yet. Processing it later preserves accumulated children. No reverse link is added without a selected parent. A separate pass over every technology to construct child lists is unnecessary.

Recalculation constructs a new consistent combination result instead of accumulating obsolete links. Once complete, check relationship reciprocity and absence of cycles. Ambiguities are not resolved by arbitrary selection.

## Freshness and frontend invocation

Source set identity and computed enrichment revision are separate. Changing a combination must not require collecting data again or republishing the other large databases. However, changed source objects or rules must invalidate the old result. Enrichment's own output fields must not falsely change its input identity.

This requires changing the current set identity contract: it is based on prepared file contents, and the existing localization operation prohibits independently enriching a set member. The exact separate revision and safe publication format belongs in the specification.

Calling Python from the browser frontend requires a local API and a mapping from the opened set to the set available to the backend. The standalone calculation function should remain independent of transport. Application startup and page refresh do not generate databases; relationship recalculation is a separate requested operation.

## Future storage model

The user defined the future MongoDB document unit: **one game object**, such as one technology, building or component. This is a future direction rather than a current implementation task.

- Computed relationships belong to the object; children and parent contain identifiers without embedded subtree copies.
- Object identity accounts for its kind and ID; equal IDs of different kinds are not merged.
- Technology variants remain representations of their base object, and combination results belong to that object.
- Shared combination descriptions and set information remain metadata without duplicating the full context in each technology.

Current JSON files retain their existing source-tree storage structure. This work does not introduce MongoDB, a container, migration, one file per object or a separate generic storage abstraction.

## Implementation specification details

The [stage 16 specification](TZ_BACKEND_STAGE_16_EN.md) was approved and implemented. It specifies the backend details below; results and running are described in the [guide](BACKEND_STAGE_16_EN.md). Grid layout, API and frontend integration remain subsequent stages.

Define exact configuration and enrichment schemas, object addressing, combination identification, separate input and result revisions, and the operation and publication contract. API and frontend integration require explicit specification scope. Coordinate calculation will follow further grid discussion.

Checks should cover relationship reciprocity, duplicates and cycles, recalculation, configured order and empty-result skipping, ambiguity and variant changes. The existing complete analytical pass validates base representations but does not replace variant checks for the new implementation.

[Chain rules](frontend/TECHNOLOGY_CHAINS_AND_SORTING_EN.md) · [Русская версия](TECHNOLOGY_TREE_ENRICHMENT_RU.md).
