# Dictionary — unlocked object relations

## Contents

- [Requirements and upgrades](#requirements-and-upgrades)
- [Object conditions](#object-conditions)
- [Terraforming transitions](#terraforming-transitions)
- [Displayed unlocks](#displayed-unlocks)
- [Interpretation boundaries](#interpretation-boundaries)
- [Sources](#sources)

## Requirements and upgrades

| Keyword | Context and form | Meaning and use | Sources |
| --- | --- | --- | --- |
| `prerequisites` | Object, such as a component or building; block of technology IDs | Object technology requirements. Links unlocked objects to technologies; see [technologies](TECHNOLOGIES_EN.md) for logical structure. | R1, R2 |
| `has_technology` | Country condition; technology ID | Checks for a researched technology. In construction conditions it may establish an object–technology link; in AI weights it serves another role. | R3 |
| `upgrades` | Building; list of building IDs | Lists building upgrade destinations. Technologies unlocking the original and upgraded buildings provide direct evidence for a chain continuation. | R2 |
| `upgrades_to` | Component; component ID | Specifies the next component upgrade. Follow component IDs first, then their technology requirements. | R1 |
| `component_set` | Component; set ID | Component set membership. A group, not a directed upgrade link; sets have separate definitions. | R1, R4 |
| `building_sets` | Building; list of set IDs | Building set membership, such as `foundry` and `industrial`. Helps compare function; a shared group does not prove a direct upgrade. | R2 |

## Object conditions

| Keyword | Context and form | Meaning and use | Sources |
| --- | --- | --- | --- |
| `potential` | Building, starbase building or component; condition block | Determines whether the object is considered in its availability context. For components, this includes appearing among installable components. Scope depends on object type. | R2, R3, R4 |
| `allow` | Planetary building; condition block | Conditions permitting construction. Does not replace `potential` or technology requirements. | R2 |
| `possible` | Starbase building here; condition block | Conditions allowing construction, including required base equipment. In components it instead constrains compatibility within the ship design. | R3, R4 |
| `has_starbase_module` | Starbase conditions; module ID | Checks module presence. May establish a functional relation between a building and a module. | R3 |
| `has_starbase_building` | Starbase conditions; building ID | Checks building presence. Under negation it can express incompatibility, so the reference alone is not a positive requirement. | R3 |
| `starbase_buildable_is_in_queue_before` | Starbase conditions; block with ID arguments `first` and `second` | Checks construction queue order. The detector uses it as an alternative to an already built detection module. `first` and `second` are arguments of this check here. | R3 |

## Terraforming transitions

| Keyword | Context and form | Meaning and use | Sources |
| --- | --- | --- | --- |
| `terraform_link` | Root block in `common/terraform` | Defines a terraforming transition between planet classes. This is a repeated construct type, not a unique identifier for an individual transition. | R5, R6 |
| `from` | Inside `terraform_link`; planet class ID | Source class of the transition. Not a `FROM` scope reference in this context. | R5, R6 |
| `to` | Inside `terraform_link`; planet class ID | Target class of the transition. | R5, R6 |
| `condition` | Inside `terraform_link`; condition block | Access conditions for the transition. A `has_technology` check links it to a required technology; retain condition logic and check context. | R5, R6 |

Different `from` and `to` values confirm a planet class change. This underpins the approved [functional group](../frontend/CHAIN_FUNCTIONAL_GROUPS_EN.md#planet-class-change). Seek the technology requirement in `condition`, not in an arbitrary ID reference, AI weights or tooltip text. Negation does not become a positive unlock; alternatives are retained.

## Displayed unlocks

| Keyword | Context and form | Meaning and use | Sources |
| --- | --- | --- | --- |
| `show_in_tech` | Starbase building here; technology ID | Associates the displayed object with a technology. Useful for discovering related objects, but does not replace actual construction conditions. | R3 |
| `show_tech_unlock_if` | Object; condition block | Controls display of the technology unlock. Does not by itself establish object availability. | R2, R3 |

## Interpretation boundaries

A direct upgrade relation requires both sides: object A upgrades to B and their technology requirements are known. If an object requires multiple technologies, the object relation alone does not select a unique predecessor. The approved [direct upgrade selection rule](../frontend/CHAIN_DIRECT_UPGRADES_EN.md) describes comparing mandatory requirements after subtracting their shared part; original dependencies are retained.

`component_set` and `building_sets` refer to definitions beyond the dictionary entry. This stage adds no set databases and does not invent their contents. Likewise, `upgrades_to` in another object type requires its own context description.

The `possible` block of `dark_matter_detector` contains the alternative “module already exists or is earlier in the queue” and a prohibition on another building. Link extraction must retain the alternative and condition polarity. Tooltip strings are not required-object IDs.

Using these relations for predecessor selection is described by the approved [direct functional relation rule](../frontend/CHAIN_DIRECT_RELATIONS_EN.md). It uses a relation requiring or enhancing an object and retains its conditions; resource consumption is not treated as an equivalent relation.

## Sources

- [R1 — armor component requirements, set and upgrade](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/00_utilities_aux.txt:250).
- [R2 — foundry building sets, requirements and upgrades](E:/SteamLibrary/steamapps/common/Stellaris/common/buildings/04_manufacturing_buildings.txt:95).
- [R3 — dark matter detector](E:/SteamLibrary/steamapps/common/Stellaris/common/starbase_buildings/00_starbase_buildings.txt:2353).
- [R4 — component documentation](E:/SteamLibrary/steamapps/common/Stellaris/common/component_templates/000_documentation.txt:37).
- [R5 — transition between ordinary planet classes](E:/SteamLibrary/steamapps/common/Stellaris/common/terraform/00_basic_terraform_links.txt:8).
- [R6 — transition from the volcanic planet class](E:/SteamLibrary/steamapps/common/Stellaris/common/terraform/01_advanced_terraform_links.txt:2224).

[Dictionary index](README_EN.md) · [Русская версия](OBJECT_RELATIONS_RU.md).
