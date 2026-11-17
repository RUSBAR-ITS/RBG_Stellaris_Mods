# Stellaris Technological Tree View — technology requirements and links specification

## Contents

- [Status and scope](#status-and-scope)
- [Inspected data](#inspected-data)
- [Requirement tree nodes](#requirement-tree-nodes)
- [Root group and nesting](#root-group-and-nesting)
- [Derived values](#derived-values)
- [Link entries](#link-entries)
- [Paths to occurrences](#paths-to-occurrences)
- [Negative logical operations](#negative-logical-operations)
- [Acceptance criteria](#acceptance-criteria)
- [Further design](#further-design)

## Status and scope

This document records the agreed `prerequisites` and `links` formats and computation of `prerequisiteIds` and `requirementCount` for simultaneous requirements and alternatives. It supplements the [Worker result](TZ_WORKER_RESULT_EN.md), [adapter](TZ_DATABASE_ADAPTER_EN.md), and [technology field](elements/TZ_TECHNOLOGY_FIELD_EN.md) specifications.

This iteration produces documentation. The source database and parser are unchanged. Requirements come only from the base technology's `prerequisites`; eligibility conditions from other fields are excluded.

## Inspected data

Inspection of the current `data/stage10/database.json` covered 679 base technologies. It found ordinary requirement lists and 21 logical `OR` blocks; `NOT`, `NAND`, and `NOR` are absent from the inspected requirements. Four technologies have explicitly empty lists. No unknown technology IDs were found among the requirements.

These figures describe the inspected file and do not constrain implementation. The model supports nested groups and all five known logical operators; rules for using negation in layout are not agreed yet.

## Requirement tree nodes

There are two node kinds:

| Kind | Fields | Purpose |
| --- | --- | --- |
| Technology | `kind: "technology"`, `technologyId: string` | Reference to a base game technology ID |
| Group | `kind: "group"`, `operator`, `items` | Logical operation and an ordered array of child nodes |

`operator` stores one of `AND`, `OR`, `NOT`, `NAND`, or `NOR`. `items` contains technology nodes and/or nested groups. Conditions are not evaluated for a particular empire.

## Root group and nesting

`prerequisites` always has an `AND` root group. It represents the ordinary list of simultaneous requirements. An absent field and an explicitly empty list are normalized to the same form:

```json
{
  "kind": "group",
  "operator": "AND",
  "items": []
}
```

Original nodes remain in the database tree accessible through `sourceRef`. Normalizing to a shared root applies only to the derived interface model.

Element order and logical group nesting are preserved. Nested `OR` is not turned into a set of mandatory technologies; repeated occurrences are not removed from the tree.

Example for an illustrative technology `D`: `A` and either `B` or `C` are required.

```json
{
  "kind": "group",
  "operator": "AND",
  "items": [
    {
      "kind": "technology",
      "technologyId": "A"
    },
    {
      "kind": "group",
      "operator": "OR",
      "items": [
        { "kind": "technology", "technologyId": "B" },
        { "kind": "technology", "technologyId": "C" }
      ]
    }
  ]
}
```

## Derived values

The shared processor receives the tree and computes the data once during catalog preparation:

| Field | Rule |
| --- | --- |
| `prerequisiteIds` | Unique IDs from all technology nodes in this tree, including alternatives, without traversing those technologies' own requirements |
| `requirementCount` | A technology node contributes `1`; `AND` sums child values; an `OR` group contributes `1`; an empty root `AND` contributes `0` |

For the example above, the set is `A`, `B`, `C`, and the requirement count is `2`. Two `OR` groups inside a root `AND` produce a count of `2`. The `OR = 1` rule applies to the entire group rather than the sum of its alternatives.

`requirementCount` is the agreed card-sorting metric. It does not compute the minimum number of research steps across the full chain. `prerequisiteIds` represents a set: listing order does not change grouping. The logical tree remains the source of requirement meaning.

The count formula for trees containing `NOT`, `NAND`, or `NOR` is not defined yet; rules for `AND` and `OR` do not automatically replace it.

## Link entries

`data.links` contains one entry per ordered pair of base technology IDs:

| Field | Type and purpose |
| --- | --- |
| `from` | String: ID of the mentioned technology |
| `to` | String: ID of the technology whose requirement tree contains the occurrence |
| `requirementPaths` | Array of paths to all corresponding nodes in technology `to`'s `prerequisites` |

A link points from the mentioned technology to the dependent one. If one technology occurs multiple times in another's requirements, there is one link with multiple paths. The reverse ID pair is a different link.

A link alone does not imply unconditional necessity. Membership in `OR` or other groups is determined through the tree and retained paths. Logical information is not replaced by a single mandatory/alternative flag.

Links use base IDs. Manual representation selection and language or theme changes do not rebuild them; moving a card into another research area preserves its links. Line appearance remains part of field design.

## Paths to occurrences

Each path is an array of non-negative, zero-based integer indexes. Its first index selects an item from the root group's `items`; each subsequent index selects an item from the next nested group's `items`. The path ends at a `technology` node whose `technologyId` matches `from`.

For link `B → D` in the example:

```json
{
  "from": "B",
  "to": "D",
  "requirementPaths": [[1, 0]]
}
```

Path `[1, 0]` selects the root's second item, the `OR` group, then its first item, `B`. The path for `A` is `[0]`; for `C`, it is `[1, 1]`.

These paths refer to the derived `data.technologies[to].prerequisites`. They are not `sourceRef` values and do not directly address the source JSON. Database replacement replaces the tree and paths together with the remaining result data.

## Negative logical operations

The group format preserves `NOT`, `NAND`, and `NOR` together with their child nodes. Their impact on `requirementCount`, card placement, and use of links as predecessors requires separate agreement.

A negative condition cannot automatically be treated as a requirement to research the mentioned technology first. Under additional user approval on 2026-11-17, `NOT`, `NAND`, or `NOR` in `prerequisites`, including nested groups, stop preparation with `invalid_database`. The status message is "Could not prepare data for display", with the path and reason retained in the report. No arbitrary formula or numeric placeholder is introduced; no partial catalog is published. This case does not occur in the inspected current database.

## Acceptance criteria

Checks are performed after implementation:

1. Absent and explicitly empty requirements produce a root `AND` with empty `items`, an empty ID set, and count `0`.
2. Individual, simultaneous, and alternative requirements preserve order, nesting, and operator distinctions.
3. `A AND (B OR C)` produces three unique IDs and count `2`; two `OR` groups produce count `2`.
4. Each `from`/`to` pair has one link; repeated occurrences retain separate paths.
5. Every path resolves to a `technology` node with ID `from` in technology `to`'s tree.
6. Direct requirements, alternatives, and nested groups remain distinguishable through the tree without losing logic in the flat link list.
7. Representation selection preserves base IDs and links; transitive predecessors are not added.
8. Structural support for negative operators is not considered approval of their counting and layout rules.

## Further design

- Counting and layout for trees containing `NOT`, `NAND`, or `NOR`; opening stops with diagnostics until these rules are agreed.
- Checks for malformed structures, unresolved IDs, and contradictory dependencies, with diagnostics.
- Module interfaces and remaining layout and line display rules.

[Русская версия](TZ_TECHNOLOGY_REQUIREMENTS_RU.md) · [Worker result](TZ_WORKER_RESULT_EN.md) · [Interface concept](CONCEPT_EN.md).
