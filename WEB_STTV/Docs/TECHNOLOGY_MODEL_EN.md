# Stellaris Technological Tree View — technology object model

## Contents

- [Purpose and scope](#purpose-and-scope)
- [Object and identifier](#object-and-identifier)
- [Type notation](#type-notation)
- [Technology definition fields](#technology-definition-fields)
- [Nested structures](#nested-structures)
- [Prerequisites](#prerequisites)
- [TriggerBlock conditions](#triggerblock-conditions)
- [CalculationBlock expressions](#calculationblock-expressions)
- [ModifierBlock effects](#modifierblock-effects)
- [UnlockDescriptionBlock descriptions](#unlockdescriptionblock-descriptions)
- [Research selection groups](#research-selection-groups)
- [Technology_swap variants](#technology_swap-variants)
- [Related and derived data](#related-and-derived-data)
- [Missing and repeated fields](#missing-and-repeated-fields)
- [Definition example](#definition-example)
- [Model checks](#model-checks)
- [Sources](#sources)

## Purpose and scope

This document describes the game technology object model: its fields, purpose, types, references, and nested structures. It is based on the installed **Stellaris Cygnus v4.5.4 (1b4f)**, checked on **2026-11-15**, comprising 679 base definitions and 206 variant blocks.

It lists **all 25 distinct top-level fields found in these definitions** and all 9 fields found within `technology_swap`. This describes the examined data; observed cardinalities and values are not declared engine limits for other versions or mods.

Type names are notation for this document rather than software class names. Current-stage serialization is described in the [JSON database model](DATABASE_MODEL_EN.md), and the builder implementation in its [guide](BACKEND_STAGE_1_EN.md). Nested conditions and effects use the game's general scripting language; this document describes their structure rather than exhaustively listing every game trigger and modifier.

## Object and identifier

The technology source is obtained by joining `STELLARIS_ROOT` and `TECH_PATH` from [global_variables.json](../global_variables.json). It currently resolves to `E:/SteamLibrary/steamapps/common/Stellaris/common/technology`.

A definition has the form `technology_id = { ... }`. For example, `tech_mega_engineering` is the outer block name and object identifier. There is no separate `id` field inside the original definition. The object identifier is considered separately from the block contents.

A technology has:

- an identifier referenced by other definitions;
- block contents: scalar fields, lists, and nested blocks;
- provenance: the source file and the definition's position within it;
- related data: localization, an image, categories, and definitions of referenced variables.

An ID suffix, localized name, or filename does not determine `tier` or repeat count. A variant with its own `name` remains part of the base technology. Whether a country has researched it is game state, not part of the static definition.

## Type notation

| Type | Contents and example |
| --- | --- |
| `Identifier` | A string identifier, such as `tech_zero_point_power`; when used as a reference, the target's existence is checked |
| `String` | A text atom or quoted string; not necessarily localized text |
| `LocalizationKey` | A string reference to a localization entry, such as `TECH_UNLOCK_COLOSSUS_CONSTRUCTION_TITLE` |
| `Boolean` | `yes` or `no` in game syntax; a semantic logical type, not literal JSON `true` / `false` in the source |
| `Integer` | An integer; some fields use quoted notation, such as `levels = "5"` |
| `Number` | An integer or fractional number, including negative values; restrictions depend on the field |
| `VariableReference` | A reference such as `@tier5cost3`, resolved from a local definition or `common/scripted_variables/` |
| `NumberValue` | A number or reference to a numeric value. Direct numeric technology fields contain literals and `@...`; included calculations also contain `value:...` references requiring game-context evaluation |
| `List<T>` | An ordered list of items of type `T`, represented by a game `{ ... }` block; empty blocks are retained where present |
| `ScriptBlock` | Ordered script block contents with repeated names, operators, and nested blocks |
| `TriggerBlock` | A condition expression depending on scope and game state |
| `CalculationBlock` | Script rules producing or modifying a numeric value |
| `ModifierBlock` | Game modifiers and parameters for describing them |
| `UnlockDescriptionBlock` | Descriptions of unlocked features and presentation controls |
| `PrerequisiteExpression` | A logical expression of predecessor technology references |
| `TechnologySwap` | A conditional base-technology variant with the fields listed separately below |

A field's type, source representation, and evaluated value are distinct. For example, `@tier5cost3` resolves to 24000 in this version, but retaining only the number loses its source reference. Static `@...` and contextual `value:...` references are not interchangeable either.

## Technology definition fields

**“Presence / maximum”** means the number of base technologies containing the field, out of 679, and its largest occurrence count within a single definition. These are observations, not declarations of engine-required fields. For example, `180 / 4` for `technology_swap` means 180 technologies have variants, with at most four blocks in one technology in this dataset.

| Field | Type | Purpose and values | Presence / maximum |
| --- | --- | --- | ---: |
| `area` | `Identifier` | Research area: `physics`, `society`, `engineering` | 679 / 1 |
| `tier` | `Integer` or `VariableReference` | Technology tier; resolved values in this dataset are `0–5`. Not graph depth | 679 / 1 |
| `category` | `List<Identifier>` | Research categories. Every examined base technology has one category, but the source structure is a list | 679 / 1 |
| `cost` | `NumberValue` or `CalculationBlock` | Base research cost. There are 625 variable references, 39 literals, and 10 blocks. Final cost depends on context | 674 / 1 |
| `prerequisites` | `PrerequisiteExpression` | Predecessor requirements; ordinary entries are required together, and `OR` groups provide alternatives. Four blocks are empty | 505 / 1 |
| `potential` | `TriggerBlock` | Country eligibility conditions: DLC, origin, civics, country type, and other checks | 376 / 1 |
| `start_tech` | `Boolean` | Starting technology marker. Both `yes` and `no` occur; additional restrictions are separate | 47 / 2 |
| `starting_potential` | `TriggerBlock` | Additional starting-acquisition conditions, such as `is_nomadic = no` | 19 / 1 |
| `weight` | `NumberValue` | Base research draw weight: a literal or `@...`. Weight is not a percentage probability | 641 / 2 |
| `weight_modifier` | `CalculationBlock` | Changes draw weight according to game conditions; multiple blocks occur | 555 / 3 |
| `weight_groups` | `List<Identifier>` | Research selection groups. Observed values are `repeatable`, `deposit_blockers`, and an empty list | 34 / 1 |
| `mod_weight_if_group_picked` | `Identifier = NumberValue` block | Weight adjustment coefficients when a technology from a specified group is selected; examples: `repeatable = 0.01`, `deposit_blockers = 0.5` | 34 / 1 |
| `ai_weight` | `CalculationBlock` | Research evaluation for AI selection. Its purpose differs from the weight of appearing among offered research options | 508 / 1 |
| `is_rare` | `Boolean` | Rare technology marker; both `yes` and `no` occur | 237 / 1 |
| `is_dangerous` | `Boolean` | Dangerous technology marker; only `yes` appears explicitly in the examined definitions | 52 / 2 |
| `is_insight` | `Boolean` | Insight technology marker. Thirteen definitions in `00_first_contact_tech.txt` set it to `yes`; the flag alone does not fully describe acquisition | 13 / 1 |
| `is_reverse_engineerable` | `Boolean` | Whether the technology permits reverse engineering; both `yes` and `no` occur. Other debris-research conditions still apply | 43 / 1 |
| `levels` | `Integer` | Repetition: observed values are `-1` for no finite limit and `5` for five levels. There are 21 and 5 definitions respectively | 26 / 1 |
| `cost_per_level` | `NumberValue` | Cost increment across repeat levels. Every observed value uses `@...` | 26 / 1 |
| `icon` | `String` | Image name without extension, such as `tech_mega_assembly`; explicitly overrides the image based on the ID | 12 / 1 |
| `modifier` | `ModifierBlock` | Research effects expressed as modifiers, plus description controls | 243 / 1 |
| `feature_flags` | `List<Identifier>` | Unlocked game capabilities, such as `megaengineering`, `modify_traits`, `gateway_activation`; not arbitrary country flags | 37 / 1 |
| `prereqfor_desc` | `UnlockDescriptionBlock` | Descriptions of unlocked features; neither predecessors nor direct effect execution | 125 / 2 |
| `gateway` | `String` | Further-research path marker, such as `robotics`, `psionics`, `ship`; matching explanations exist as `gateway_robotics`, `gateway_psionics`, `gateway_ship`. Not necessarily a reference to another technology | 52 / 1 |
| `technology_swap` | `TechnologySwap` | Conditional presentation and properties of the same technology; the order of multiple blocks matters for subsequent interpretation | 180 / 4 |

Categories in `common/technology/category/00_category.txt`: `materials`, `propulsion`, `voidcraft`, `industry`, `field_manipulation`, `particles`, `computing`, `psionics`, `new_worlds`, `statecraft`, `biology`, `military_theory`, `archaeostudies`. These are separate definitions, not research area names.

`gateway` also contains other strings, including strings resembling technology IDs. Resemblance to an ID does not establish a mandatory dependency; the corresponding localization needs separate checking.

## Nested structures

### Prerequisites

The outer block means that its requirements apply together. Examined sources contain technology IDs and nested `OR` groups. Multiple `OR` groups can occur, each containing alternative IDs.

For `tech_mega_engineering`, the expression is:

```text
(tech_starbase_5 OR tech_arkship_tier_3)
AND tech_zero_point_power
AND (tech_battleships OR tech_stingers)
```

These are three joint requirements, not a requirement to research all five technologies. Explicit logical `AND` explains the meaning here; the actual source expresses conjunction through the outer block rather than a literal `AND` field.

An empty block and an absent block specify no predecessors, but their source representations differ. `has_technology` in weights or conditions cannot automatically be moved into this expression. The `PrerequisiteExpression` type does not mean that every general game trigger is valid inside `prerequisites`.

### TriggerBlock conditions

Used in `potential`, `starting_potential`, `technology_swap.trigger`, and conditional calculation entries. A condition is not an already-known `Boolean`: its result comes from evaluating a country and game state.

Contents include checks such as `has_origin = origin_storm_chasers`, logical blocks such as `OR`, `NOT`, `NOR`, numeric comparisons, nested scopes, and scripted-trigger calls. For example, `any_neighbor_country = { has_technology = tech_titans }` checks a neighboring country, not the owner of the current technology.

Condition names and argument types belong to the game's scripting language. Preserving structure requires operators `=`, `<`, `>`, `<=`, `>=`, entry order, repeated names, and nesting. A `no` argument to a trigger must also be retained.

### CalculationBlock expressions

This semantic type covers costs, weight modifiers, and AI evaluation; available fields depend on the location rather than forming one identical contract for every block.

| Element | Type and role |
| --- | --- |
| `factor` | `NumberValue`: a multiplier or initial value in the relevant calculation context |
| `base`, `weight` | Numeric initial evaluation parameters; present at the top level of `ai_weight` |
| `modifier` | A repeated block containing a numeric adjustment and its conditions; examined calculations use `factor` and `add` |
| `inline_script` | An inclusion path string or a block containing `script` and named parameters; the included file supplies additional rules |

Ten `cost` blocks in `00_cosmic_storm_tech.txt` directly contain `factor = @...` and `inline_script = { script = technologies/cosmic_storms_technologies_cost_modifiers }`. The included file has conditional multipliers such as 0.75 and 1.2.

The inclusion `technologies/cosmic_storms_technologies_weight_modifiers` contains `factor = value:storm_callers_councilor_tech_discovery_chance_multiplier`. This requires evaluation of a game script value; it cannot be resolved as an ordinary `@...` constant.

The inline path and parameters are part of the source model. A final numeric result is not guaranteed without expanding inclusions and providing context. This document does not establish the engine's arithmetic evaluation order.

### ModifierBlock effects

The primary entries are “modifier identifier = numeric value” pairs, such as `ship_armor_mult = 0.05` or `envoys_add = @...`. Specific names belong to the game's modifier catalogue, not to a fixed field list required in every technology.

The following description parameters also occur:

| Field | Type | Purpose |
| --- | --- | --- |
| `description` | `LocalizationKey` | Block description reference |
| `description_parameters` | Named-value block | Description arguments; for example, `POINTS = @tech_gene_tailoring_POINTS` |
| `custom_tooltip` | `LocalizationKey` | Custom effect description reference |
| `show_only_custom_tooltip` | `Boolean` | Controls showing a custom description instead of the automatically generated list |

Numbers have different units: added quantities, relative coefficients, and other values depend on the modifier. Every `0.05` cannot be formatted as a percentage without knowing its purpose. Not every technology effect necessarily lives in `modifier`: other game objects can be unlocked by referencing its ID.

### UnlockDescriptionBlock descriptions

Base definitions contain `component`, `ship`, `custom`, `diplo_action`, and `hide_prereq_for_desc` entries.

| Element | Type | Purpose |
| --- | --- | --- |
| `component`, `ship`, `custom`, `diplo_action` | Repeated blocks containing `title` and optional `desc` | Description of an unlocked feature of the respective kind |
| `title` | `LocalizationKey` | Description title |
| `desc` | `LocalizationKey` | Additional description text, when specified |
| `hide_prereq_for_desc` | `Identifier` | Hides a group of automatically generated descriptions; observed values are `component`, `ship` |

These are presentation data. `ship = { title = ... }` cannot establish which ship is actually buildable: ship definitions and their conditions must be examined for that. Repeated entries and multiple `prereqfor_desc` blocks are retained.

### Research selection groups

The related fields have different structures:

```text
weight_groups = { repeatable }
mod_weight_if_group_picked = { repeatable = 0.01 }
```

The first is a list of labels; the second associates labels with coefficients. Both fields also have empty blocks in `tech_repeatable_lcluster_clue`. These groups are not research categories, acquisition conditions, or predecessor relationships. The exact group-selection algorithm used for research options is not reproduced here.

## Technology_swap variants

“Presence / maximum” here refers to the **206 variant blocks**, not the 679 base technologies. `TechnologySwap` does not automatically inherit the schema of every root field.

| Field | Type | Purpose and values | Presence / maximum |
| --- | --- | --- | ---: |
| `name` | `LocalizationKey` / variant name | Alternative presentation name; may match a base ID and recur across multiple variants | 206 / 1 |
| `trigger` | `TriggerBlock` | Variant selection conditions | 206 / 1 |
| `inherit_icon` | `Boolean` | Inherits the base technology image; both `yes` and `no` occur | 200 / 1 |
| `inherit_effects` | `Boolean` | Inherits base technology effects; both `yes` and `no` occur | 183 / 1 |
| `modifier` | `ModifierBlock` | Variant modifiers and effect descriptions; interaction with base effects depends on inheritance | 59 / 1 |
| `weight` | `{ factor = NumberValue }` block | Variant weight adjustment. All 94 blocks contain `factor`; this differs from scalar base-technology `weight` | 94 / 1 |
| `area` | `Identifier` | Replacement research area. Examined variants explicitly specify only `society`; the base area domain is listed above | 11 / 1 |
| `category` | `List<Identifier>` | Replacement research categories; observed variants use `biology` or `psionics` | 11 / 1 |
| `prereqfor_desc` | `UnlockDescriptionBlock` | Variant unlock descriptions; repetition occurs | 35 / 2 |

For example, `tech_titans` contains `tech_biogenesis_titans` with `country_uses_bio_ships = yes`, area `society`, category `biology`, `inherit_icon = no`, and `inherit_effects = yes`.

A variant name is not a reliable unique key. Distinguishing entries requires the base technology and the block's position in its variant list. The game template describes selecting the first matching variant and replacing the entire category list. These statements come from game documentation; absent inheritance-flag defaults and behavior when conditions overlap have not been tested in the game.

## Related and derived data

The following information helps describe the object but is not an independent root field in its game definition:

| Data | Type / origin |
| --- | --- |
| ID | `Identifier`, the outer block name |
| File and position | Path and definition line numbers; technical provenance |
| Source version | Game version read from `launcher-settings.json` |
| Name key | Usually the base technology ID; a variant uses its name |
| Description key | `<ID>_desc` for the base technology; variant description resolution requires considering the specific variant |
| Name and description text | Localization resolved by key and configured source priority; language and text provenance are separate concerns |
| Image | For the base technology, `gfx/interface/icons/technologies/<icon>.dds`, where `<icon>` is explicit `icon` or the ID; variant inheritance must be considered |
| Resolved `@...` values | Results of matching references to variable definitions; the original reference retains its own meaning |
| Reverse dependencies | Technologies referencing this ID in their `prerequisites`, derived from other objects |
| Unlocked objects | References in component, building, and other object definitions, plus `feature_flags`; `prereqfor_desc` is not a complete catalogue |
| Current eligibility, selected variant, cost, and probability | Computed values dependent on country and game state; not constant properties of the source object |

This table describes provenance without assigning final JSON field names. The technology representation is independent of choosing a graph or another interactive interface.

## Missing and repeated fields

`area`, `tier`, and `category` appear exactly once in all 679 technologies. This confirms coverage of this dataset but does not establish engine requirements for every possible source.

For other fields, absence is a distinct state. It is not automatically replaced with `0`, `false`, an empty string, or a list. For example, five technologies omit `cost`, while others explicitly set `cost = 0`. An empty `prerequisites = { }` remains an explicitly specified block.

Repeated root fields include `technology_swap`, `weight_modifier`, `prereqfor_desc`, and some `start_tech`, `is_dangerous`, and `weight` entries. Both identical and conflicting values occur.

`tech_orbital_arc_furnace`, `tech_dyson_swarm`, and `tech_dyson_gun` have conflicting `weight` values: 0 and 70, 0 and 70, and 0 and 50 respectively after variable resolution. The source model contains both entries in their original order. Choosing the first or last value without confirming engine behavior does not resolve the ambiguity.

Consequently, a source block is not equivalent to an ordinary JSON object with one value per name. Proposed repeated-field storage is provided in the JSON database model. An unknown field in a new source requires investigation and updating this description; the current list does not justify silently discarding it.

## Definition example

An abbreviated fragment from `common/technology/00_megastructures.txt:1`; other fields in the original technology are omitted here:

```text
tech_mega_engineering = {
    area = engineering
    cost = @tier5cost3
    tier = 5
    category = { voidcraft }
    prerequisites = {
        OR = {
            tech_starbase_5
            tech_arkship_tier_3
        }
        tech_zero_point_power
        OR = {
            tech_battleships
            tech_stingers
        }
    }
    weight = @tier5weight3
    is_rare = yes
}
```

The ID comes from the block name; `area` is an area identifier, `category` a list, `tier` an integer, `cost` and `weight` variable references, `is_rare` a Boolean, and `prerequisites` a compound requirement expression. Resolving the cost variable to 24000 does not change the type of the original `cost` entry.

## Model checks

This revision was compared with the complete research snapshot:

- All 25 observed root fields and 9 variant fields are included in the tables.
- Presence counts and maximum cardinalities were obtained across all 679 definitions and 206 variants while retaining repeated entries.
- Confirmed scalar and block forms, empty lists, variables, and additional effect-description structures.
- Hashes of 60 core source files match the research snapshot; relevant inline inclusions and `gateway` localization examples were also read.

The first-stage implementation was checked for preservation of repetitions and order, distinction between absence and explicit values, local-reference resolution, context-appropriate types, and retention of unevaluated expressions. Results are listed in the [builder guide](BACKEND_STAGE_1_EN.md#validation). This document does not establish unverified defaults or exact engine evaluation rules.

## Sources

Primary verification used game files under the configured `STELLARIS_ROOT`:

- `common/technology/*.txt`, particularly `00_megastructures.txt`, `00_eng_tech.txt`, `00_eng_tech_repeatable.txt`, `00_first_contact_tech.txt`, `00_cosmic_storm_tech.txt`, `00_distant_stars_tech.txt`, `00_machine_age_tech.txt`, and `00_nomads_dlc_tech.txt`.
- `common/technology/category/00_category.txt`, `common/technology/tier/00_tier.txt`, and `common/scripted_variables/*.txt`.
- `common/inline_scripts/technologies/cosmic_storms_technologies_cost_modifiers.txt` and `cosmic_storms_technologies_weight_modifiers.txt` in the same directory.
- `localisation/english/technology_l_english.yml:1217`, containing example `gateway` path explanations.
- `common/technology/000_documentation.txt`, a supplementary template whose comments are compared with actual definitions.

The [CWTools technology schema](https://github.com/cwtools/cwtools-stellaris-config/blob/master/config/common/technologies_consolidated.cwt) was also reviewed. It helps compare types but does not replace game sources. For example, it describes `ai_update_type` with `all` / `military`, which does not occur in the 679 examined definitions and is excluded from the observed-field table. Its `OR` cardinality also fails to describe every examined source.

Working materials: `TMP/WEB_STTV/technology_tree_audit.json` and `TMP/WEB_STTV/technology_model_inventory.json`. These are temporary research data, not the application database.

[Technology tree research](RESEARCH_TECH_TREE_EN.md) · [Модель на русском](TECHNOLOGY_MODEL_RU.md).
