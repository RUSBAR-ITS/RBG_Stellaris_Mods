# Technology chains — direct object upgrades

## Contents

- [Status and purpose](#status-and-purpose)
- [Inputs](#inputs)
- [Matching rule](#matching-rule)
- [Selection result](#selection-result)
- [Rule boundaries](#rule-boundaries)
- [Examples](#examples)
- [Related documents](#related-documents)

## Status and purpose

Approved on 2026-11-18 for the future `parent_tech` selection algorithm. This is part of chain design, not an implementation specification. The current iteration changes documentation only.

A direct building or component upgrade helps select a continuation among the remaining technology prerequisites. The selected `parent_tech` is a layout anchor; the full game requirement graph is retained.

## Inputs

- Current technology `T` and remaining candidate set `C` after earlier criteria.
- Explicit directed object link `A → B`: building `upgrades` or component `upgrades_to`. Each listed transition is considered separately.
- Both objects' technology `prerequisites` and their source references.

If `C` already contains one candidate, selection is complete and this rule is not applied.

## Matching rule

1. Consider one direct link `A → B`.
2. Establish that each object's requirements contain only mandatory positive technology references: a plain list or an `AND` combination.
3. Obtain requirement sets `R_A` and `R_B`. Repeated occurrences of an ID do not create additional requirements.
4. Find the shared part `S = R_A ∩ R_B` and derive `D_A = R_A − S`, `D_B = R_B − S` for comparison.
5. The link witnesses continuation `P → T` only if `D_A = {P}`, `D_B = {T}` and `P` belongs to the current set `C`.

The simple case “object A requires only P, object B requires only T” follows the same rule: the shared part is empty. If either side contains zero or multiple technologies after subtraction, this link does not witness a unique continuation.

Removing the shared part is an analytical comparison. Object and technology requirements in the database are neither reduced nor overwritten.

## Selection result

Collect set `M` of all candidates in `C` witnessed by at least one qualifying link:

| Result | Action |
| --- | --- |
| One candidate in `M` | Select it and finish selection. |
| Multiple candidates in `M` | Pass `M` to the next criterion. |
| Empty `M` | Skip the criterion, retaining the previous set `C`. |

Previously discarded candidates are not reintroduced. Witness counts do not provide extra votes: component variants for different ship sizes must not outweigh another chain. All witnesses and source references to the upgrade link and both objects' requirements are nevertheless retained to explain the result.

## Rule boundaries

- Requirements containing `OR`, negation or other complex logic are not used as proof at this step. Their original structure is retained; alternatives are not converted into mandatory requirements.
- One explicit object transition is considered. Automatic traversal through intermediate upgrades belongs to later indirect relation design.
- Shared `component_set`, `building_sets`, name or function alone does not prove a direct upgrade.
- Matching special availability conditions and functional affinity are separate subsequent criteria.

## Examples

Examples were checked against local Stellaris 4.5.4 files. The table shows witnessing pairs, not results of a new complete algorithm run.

| Predecessor `P` | Continuation `T` | Direct object link |
| --- | --- | --- |
| `tech_cloaking_3` | `tech_cloaking_dark_matter` | [SCIENCE_CLOAKING_3 → SCIENCE_CLOAKING_DARK_MATTER](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux_first_contact.txt:1249) |
| `tech_basic_health` | `tech_frontier_health` | [building_medical_1 → building_medical_2](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/07_amenity_buildings.txt:732) |
| `tech_xeno_diplomacy` | `tech_xeno_relations` | [building_embassy → building_grand_embassy](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/02_government_buildings.txt:763) |

Shared mandatory technology example: [BIO_DRIVE_2](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_drives.txt:337) upgrades to [BIO_DRIVE_3](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_drives.txt:367).

```text
R_A = {tech_hyper_drive_2, tech_hyper_drive_bio_integration}
R_B = {tech_hyper_drive_3, tech_hyper_drive_bio_integration}
S   = {tech_hyper_drive_bio_integration}
D_A = {tech_hyper_drive_2}
D_B = {tech_hyper_drive_3}
```

This witnesses `tech_hyper_drive_2 → tech_hyper_drive_3` if the former ID remains a candidate for the latter. The prerequisite itself is present in the [technology definition](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:2669).

## Related documents

- [General chain and sorting rules](TECHNOLOGY_CHAINS_AND_SORTING_EN.md).
- [Object relation dictionary](../semantics/OBJECT_RELATIONS_EN.md).
- [Русская версия](CHAIN_DIRECT_UPGRADES_RU.md).
