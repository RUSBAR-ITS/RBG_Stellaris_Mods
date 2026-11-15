# Stellaris Technological Tree View — stage-one JSON database model

## Contents

- [Status and data scope](#status-and-data-scope)
- [Strict schema and unknown elements](#strict-schema-and-unknown-elements)
- [Database root object](#database-root-object)
- [Technology record](#technology-record)
- [Names in two languages](#names-in-two-languages)
- [Game field representation](#game-field-representation)
- [Numbers and game variables](#numbers-and-game-variables)
- [Requirements and relationships](#requirements-and-relationships)
- [Eligibility and selection conditions](#eligibility-and-selection-conditions)
- [Script blocks](#script-blocks)
- [Conditional variants](#conditional-variants)
- [Repeated and missing fields](#repeated-and-missing-fields)
- [Categories and tiers](#categories-and-tiers)
- [Local variable definitions](#local-variable-definitions)
- [Inclusion history](#inclusion-history)
- [Record example](#record-example)
- [Validation rules](#validation-rules)
- [Related documents](#related-documents)

## Status and data scope

[Stage five](BACKEND_STAGE_5_EN.md) introduces database version `2`: `inline_script` expands before conversion, call history lives in `metadata.inline_scripts`, and source locations contain a root, path, line, column, and call ID. Database version 1 is no longer supported.

Date: **2026-11-15**. The user agreed to the first JSON database model, now implemented under the separately approved [first backend stage](TZ_EN.md#3-first-backend-stage--database-building). It builds on the [game object description](TECHNOLOGY_MODEL_EN.md).

Stage inputs:

- Technology definitions from `STELLARIS_ROOT / TECH_PATH / *.txt`.
- Category and tier definitions from the `category/` and `tier/` subdirectories.
- Local `@...` definitions from those same files.
- **Only technology and conditional variant names**, separately in Russian and English, from the configured localization sources.

Technology descriptions, effect text, category names, and other localized text are not added yet. Their keys remain in game fields where present. External game variables, scripted triggers, images, and definitions of unlocked objects are not loaded at this stage. For example, `common/scripted_variables/` lies outside `TECH_PATH`.

The database stores structure known from these sources. It does not evaluate country eligibility, the active variant, final cost, or draw probability. A graph or another interactive presentation uses the same model.

## Strict schema and unknown elements

The database model is **closed and explicitly declared**. `fields` is not a free-form source-script dictionary. A field is accepted only when its purpose, allowed context, value type, cardinality, and conversion rule are defined. Successful syntax parsing alone does not mean a field is supported.

These rules apply at every level:

- Record envelopes contain only their listed fields. Additional properties are forbidden, including arbitrary `raw`, `extra`, or `unknown` properties.
- `TechnologyRecord.fields` allows only the base-technology table's fields; `VariantRecord.fields`, categories, and tiers allow only their respective tables' fields. Matching names do not transfer rules between contexts: for example, base `weight` and variant `weight` have different types.
- Each union alternative must match its own complete structure. For example, `Requirement` contains exactly one of `tech`, `all`, or `any`; `RepeatedValue` does not permit unknown fields or values of other types.
- Dynamic keys are allowed only in declared collections: technology, category, and tier IDs, and file paths in `file_variables`. A new ID is data rather than a new schema field; its record value must still match the declared type.
- Nested scripts also require declared rules for commands, arguments, operators, and scopes. `ScriptBlock` does not bypass the strict schema.

An unknown field, unsupported nested construct, or invalid type goes into a **separate parsing report outside the working database**: file, line, definition ID, element path, and rejection reason. A small source fragment may be included in the report; automatically copying it into the database, substituting `null`, or silently dropping a condition is prohibited. Sources are read directly in read-only mode; no file copies or persistent primary snapshot are created.

A build with these errors is unsuccessful and must not replace the working database with partial output. The construct must first be investigated and the model and its handling refined. This differs from an explicitly supported unresolved reference: for example, the known `VariableValue` form with `resolved: null` is allowed under this stage's rules.

These restrictions are implemented through a [machine-readable JSON schema](../schemas/database.schema.json) and contextual builder validation. Supported nested commands and their arguments are explicitly listed in the [rule profile](../profiles/stellaris_4_5_4.json), from which the working registry is generated; the general `ScriptBlock` shape does not define that set by itself. Operation and implementation structure are described in the [first-stage guide](BACKEND_STAGE_1_EN.md); profiles and generation are covered in the [second-stage guide](BACKEND_STAGE_2_EN.md).

## Database root object

One UTF-8 JSON file contains the following required fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `format_version` | Integer | File structure version; `2` for this model. Not an application or game version |
| `technologies` | `ID → TechnologyRecord` object | Base technologies; the ID is the entry key and is not duplicated inside the record |
| `categories` | `ID → DefinitionRecord` object | Categories from `category/` |
| `tiers` | `ID → DefinitionRecord` object | Tiers from `tier/`; JSON keys are strings, such as `"0"`, `"5"` |
| `file_variables` | `file path → VariableDefinition[]` object | Local game variable definitions retaining file scope and order |
| `metadata` | Object | Required `inline_scripts` call-history array; outside game fields and analysis |

A valid empty database is:

```json
{
  "format_version": 2,
  "technologies": {},
  "categories": {},
  "tiers": {},
  "file_variables": {},
  "metadata": {
    "inline_scripts": []
  }
}
```

Object key order does not define game order. Arrays are used wherever order matters. Duplicate JSON keys are prohibited. Duplicate base IDs require a separate build decision; silently replacing an entry must not discard a definition.

Absolute roots and source priorities remain in `global_variables.json`. The database contains relative provenance references and can be read without source directories. It has no game-version field at this stage: the version cannot be reliably derived from the technology directory alone.

## Technology record

All `TechnologyRecord` envelope fields are required:

| Field | Type | Purpose |
| --- | --- | --- |
| `source` | `SourceLocation` | Original definition location |
| `name` | `{ "ru": string or null, "en": string or null }` | Two name strings; a missing language does not hide the other |
| `name_sources` | `{ "ru": LocalizationSource or null, "en": LocalizationSource or null }` | Provenance of selected names |
| `fields` | Closed game field object | Only prepared values of allowed fields from the table below; fields absent in the game are omitted |

`SourceLocation` requires `root`, `file`, `line`, `column`, and `inline_call_id`. `root` is `STELLARIS_ROOT`, `TECH_PATH`, or `INLINE_SCRIPTS_DIR`; `file` is relative to that root. Lines and columns start at 1. `inline_call_id` identifies the originating invocation or is `null`. Example: `{"root":"TECH_PATH","file":"00_megastructures.txt","line":1,"column":1,"inline_call_id":null}`. Localization provenance has its own unchanged contract.

`fields` separates game names from database metadata. In particular, the envelope's `name` is localized text, not an additional field in the game definition.

## Names in two languages

For a base technology, the localization key is its ID. A variant uses its original `name` field, stored as `name_key` in the database.

Russian lookup runs **per key**: `RU_LOC_TIER_1` → `RU_LOC_TIER_2` → `RU_LOC_TIER_3`. English lookup runs independently in `EN_LOC_TIER_1`. The corresponding `l_russian` or `l_english` language header is checked.

`LocalizationSource` contains:

| Field | Type | Purpose |
| --- | --- | --- |
| `tier` | String | Name of the selected source variable, such as `RU_LOC_TIER_2` |
| `file` | String | File path relative to that source directory |
| `line` | Integer from 1 | Matched entry line |
| `key` | String | Matched localization key |

Content rules:

- `name.ru` and `name.en` contain the selected entry values without outer quotes or the optional number after the key. These are localization data, not newly authored translations.
- Game markup, grammar markers, `$...$` references, and substitutions remain in the string. Their evaluation and visual formatting are outside this stage; a found string is not necessarily plain text without markup.
- JSON escaping must preserve content: for example, a game backslash followed by `n` is stored as `\\n`. Reading JSON must reproduce the original value's character sequence.
- If a key is absent from every source for a language, the respective `name` and `name_sources` values are `null`. Neither the ID nor another language is stored as a substitute translation. Interface fallback labels will be a separate decision.
- An explicitly empty value is stored as `""` with provenance. It differs from a missing key; lookup moves to the next tier when the key is absent.
- Identical duplicates within one tier provide unambiguous text; provenance is chosen by relative filename and then line number for reproducibility. Different values for one key within the selected tier require a build error rather than arbitrary selection or fallback to a lower tier.

`<ID>_desc` entries are not requested to populate the database. Script keys under `description`, `custom_tooltip`, `title`, and `desc` remain references. Name localization does not automatically extend to them.

## Game field representation

Ordinary fields keep their original names inside `fields`. Numbers become JSON numbers, known Boolean fields `yes` / `no` become `true` / `false`, and identifier lists become string arrays. Nested script representation is defined separately.

| Game field | JSON representation |
| --- | --- |
| `area` | String: `physics`, `society`, or `engineering` |
| `tier`, `levels` | Integer or `VariableValue` when specified through a variable |
| `cost` | Number, `VariableValue`, or `ScriptBlock` |
| `cost_per_level`, `weight` | Number or `VariableValue` |
| `category`, `feature_flags`, `weight_groups` | String array; an explicitly empty source list becomes `[]` |
| `is_rare`, `is_dangerous`, `is_insight`, `is_reverse_engineerable`, `start_tech` | JSON Boolean |
| `icon`, `gateway` | Original identifier or label string; no image file is loaded |
| `prerequisites` | `Requirement`: the logical reference structure defined below |
| `potential`, `starting_potential`, `ai_weight`, `modifier`, `mod_weight_if_group_picked` | `ScriptBlock` |
| `weight_modifier`, `prereqfor_desc` | `ScriptBlock` array in source order, even when there is only one block |
| `technology_swap` | `VariantRecord` array in source order, even when there is only one variant |

This table covers all 25 observed base-definition fields. Assumed game defaults are not inserted. Unexpected repetitions of ordinary fields use the special representation in the repetition section.

## Numbers and game variables

`VariableValue` has exactly two fields:

```json
{
  "variable": "@tier5cost3",
  "resolved": null
}
```

`variable` is the original reference; `resolved` is a known numeric value or `null`. This stage resolves only unambiguous chains of local definitions in the same source file. Missing local variables, cycles, or ambiguity leave `resolved: null`. `null` does not mean zero cost.

For example, although earlier research established `@tier5cost3` in the shared variables directory, the current collection does not read it there or insert a remembered number. Definitions from another `TECH_PATH` file are not automatically treated as global either.

Nested script expressions containing `@...` and `value:...` remain in `ScriptBlock`; `inline_script` invocations expand before conversion. This stage does not evaluate complete cost or weight expressions. A direct reference's `resolved` value is only a local constant, not the final in-game price.

## Requirements and relationships

`Requirement` has one of three forms:

| Form | Meaning |
| --- | --- |
| `{ "tech": "tech_id" }` | Technology reference |
| `{ "all": [Requirement, ...] }` | All nested requirements must hold |
| `{ "any": [Requirement, ...] }` | One nested requirement is sufficient |

Each entry contains exactly one of `tech`, `all`, or `any`. Outer `prerequisites` become `all`, and each original `OR` group becomes a separate `any`. Order is retained. Example for `tech_mega_engineering`:

```json
{
  "all": [
    {
      "any": [
        {
          "tech": "tech_starbase_5"
        },
        {
          "tech": "tech_arkship_tier_3"
        }
      ]
    },
    {
      "tech": "tech_zero_point_power"
    },
    {
      "any": [
        {
          "tech": "tech_battleships"
        },
        {
          "tech": "tech_stingers"
        }
      ]
    }
  ]
}
```

An explicitly empty block becomes `{"all":[]}`. An absent field is omitted. Unknown constructs are not guessed to be ordinary references; handling them requires refining the model.

There is no separate edge array or stored reverse-dependency copy yet. Both can be derived unambiguously from these expressions in the loaded database, avoiding two stored representations that can diverge. `has_technology` in weights or conditions is not added to the requirements.

## Eligibility and selection conditions

Predecessor technologies are only one part of the conditions. Restrictions involving countries, civics, ethics, origins, species, planets, and other circumstances are retained in the appropriate script fields when a handling rule has been declared for the construct. They are not reduced to additional tree edges.

| Mechanism | Storage | Meaning |
| --- | --- | --- |
| Predecessor technologies | `fields.prerequisites` | Logical requirements for predecessor technologies |
| Research tier | `fields.tier` and `tiers` definitions | Tier requirements are considered separately from specific predecessors |
| General technology conditions | `fields.potential` | Country eligibility conditions, such as DLC, civic, origin, or flag |
| Starting conditions | `fields.starting_potential` together with `start_tech` | Separate starting-acquisition conditions; not a substitute for general research conditions |
| Draw conditions | `fields.weight`, `fields.weight_modifier`, and group rules | Change the technology's draw weight. A zero multiplier can prevent ordinary draws; a positive adjustment does not become a mandatory requirement |
| Variant conditions | `fields.technology_swap[].fields.trigger` | Determine applicability of a base technology's variant; do not replace its `potential` |
| AI preferences | `fields.ai_weight` | Affect AI selection rather than imposing an independent player restriction |

Examples from the installed game, with paths relative to `TECH_PATH`:

- `tech_pk_nanobots` places `has_valid_civic = civic_machine_assimilator` inside `potential` (`00_apocalypse_tech.txt:269`). It is part of the technology's conditions alongside DLC and a project flag.
- `tech_synthetic_leaders` places `has_origin = origin_necrophage` and `has_trait = trait_necrophage` in the same weight modifier with `factor = 0.33` (`00_eng_tech.txt:3407–3410`). This adjusts weight when both conditions hold; it does not require that origin and trait for research.

Nested conditions retain their logical groups and evaluation scopes. For example, checking a species trait within a species iterator is not equivalent to checking a country. Building-presence conditions, if encountered, likewise require a declared rule and preservation of the planet scope; they do not introduce an arbitrary top-level `buildings` field.

**Storing a condition does not evaluate whether it holds.** This database contains no state from a particular game: country ethics and civics, species composition, constructed buildings, current flags, and so on. Consequently, no computed “available to this player” result is stored here. Missing information must not be treated as a condition being true or false; zero ordinary draw weight also does not prove that acquisition through another mechanism is impossible.

External scripted triggers and values remain under declared rules without reading their bodies. `inline_script` expands recursively; resulting commands undergo the same strict checks as directly written commands. Unknown commands cause an error and are never discarded.

## Script blocks

`ScriptBlock` is an object with required `entries: ScriptEntry[]`. An empty block is `{"entries":[]}`. `ScriptEntry` contains:

| Field | Type | Purpose |
| --- | --- | --- |
| `key` | String or `null` | Only a name permitted by the current context's rule; `null` for an allowed standalone list item |
| `operator` | String or `null` | Only an operator allowed for this command, such as `=` or `<`; `null` only for a standalone item |
| `value` | String or `ScriptBlock` | Value shape and content are checked against the declared command rule |
| `source` | `SourceLocation` | Physical entry origin and invocation ID |

Inside script blocks, scalars are stored as strings: `"yes"`, `"0.50"`, `"@some_value"`. This is a storage convention for known arguments, not permission to accept unknown ones. Each command rule defines the allowed value meaning: `yes` / `no`, a numeric token, a particular identifier kind, a declared reference, or a nested block. An invalid form is rejected even if it is a valid JSON string. Outer game fields have prepared numbers and Booleans according to the earlier table. Syntactic outer scalar quotes are excluded from its value; original formatting and comments remain in source files and are not copied into the database.

Each supported command needs declared parent blocks, incoming and nested scopes, operators, argument shapes and types, requiredness, cardinality, and a handling rule. A known command in an unsupported context is also an error. `key` and `operator` can be `null` only together and only where the rule permits standalone items. Recognizing an external reference does not evaluate its body.

Example `potential` value:

```json
{
  "entries": [
    {
      "key": "is_nomadic",
      "operator": "=",
      "value": "no",
      "source": {
        "root": "TECH_PATH",
        "file": "example.txt",
        "line": 16,
        "column": 1,
        "inline_call_id": null
      }
    }
  ]
}
```

The structure preserves repeated keys, operators, nesting, and order for supported constructs. It retains declared conditions, numerical rules, modifiers, description keys, and external references. Unknown elements are not copied into `entries`. The interface receives validated structured JSON without reparsing Stellaris source syntax.

## Conditional variants

Each `fields.technology_swap` item is a `VariantRecord` containing:

| Field | Type | Purpose |
| --- | --- | --- |
| `source` | `SourceLocation` | Original block location |
| `name_key` | String | Original variant `name`; localization lookup key |
| `name` | Object with `ru` and `en` | Two name strings under the same rules as base technologies |
| `name_sources` | Object with `ru` and `en` | Sources of selected names |
| `fields` | Closed game field object | Only allowed variant fields from the table below |

Mapping for the remaining eight fields:

| Game field | Representation |
| --- | --- |
| `trigger`, `modifier`, `weight` | `ScriptBlock`; variant `weight` is not converted to a number using base-technology rules |
| `inherit_icon`, `inherit_effects` | Boolean |
| `area` | String: `physics`, `society`, or `engineering` |
| `category` | String array |
| `prereqfor_desc` | `ScriptBlock` array |

Missing fields are not filled with inherited values. No active variant is selected, and no variant effects are merged with base effects. Several variants may share `name_key`: records are distinguished by their parent technology and array index. Original `name` is not duplicated inside `fields`.

The link to the base technology is expressed through **nesting**, not a separate reference field. For example, `technologies.tech_titans.fields.technology_swap[0]` is the first variant of base technology `tech_titans`. The variant record has no `parent_id`: it would duplicate the already known parent. `name_key` is the variant name's localization key, not the base technology ID. A variant does not become a separate entry in `technologies` or a separate requirement node.

## Repeated and missing fields

`technology_swap`, `weight_modifier`, and `prereqfor_desc` arrays represent ordinary repeated blocks. A repetition of a normally single field uses `RepeatedValue` in place of its ordinary value:

```json
{
  "occurrences": [
    {
      "source": {
        "column": 5,
        "file": "00_machine_age_tech.txt",
        "inline_call_id": null,
        "line": 665,
        "root": "TECH_PATH"
      },
      "value": 0
    },
    {
      "source": {
        "column": 5,
        "file": "00_machine_age_tech.txt",
        "inline_call_id": null,
        "line": 668,
        "root": "TECH_PATH"
      },
      "value": {
        "resolved": null,
        "variable": "@tier2weight3"
      }
    }
  ]
}
```

This represents `fields.weight` in `tech_orbital_arc_furnace`. Each `value` has the field's ordinary type; `source` identifies the source occurrence. The array has at least two entries and preserves source order. It does not mean addition, last-value selection, or an established engine precedence rule. Identical repetitions are also retained.

The model distinguishes:

- No key in `fields`: the field is absent from the definition.
- `false`, `0`, `""`, `[]`, `{"entries":[]}`: explicit values of their respective types.
- `VariableValue.resolved = null`: an unresolved game reference.
- `name.ru = null` or `name.en = null`: no name found in that language.
- `RepeatedValue`: multiple source occurrences of a normally single field.

Arbitrary `null` is not used for unknown game fields. A new unsupported field goes into the separate report and prevents a successful build until the model and conversion rules are refined. It must not be automatically retained or silently discarded. Old-format migrations are not introduced at this stage.

## Categories and tiers

`DefinitionRecord` contains only required `source: SourceLocation` and `fields: object`. Categories and tiers use different closed `fields` sets listed below. Names of these objects are not localized yet.

Category `fields` retain `icon: string`, if specified, and `weight_modifier: ScriptBlock[]`, if specified. Tier fields retain `previously_unlocked: number or VariableValue`, if specified, and `weight_modifier: ScriptBlock[]`, if specified. A repeated single field uses `RepeatedValue`.

The empty tier-0 definition remains a record with `fields: {}` rather than being removed. A technology category references a key in `categories`; a known numeric `tier` maps to a string key in `tiers`. An unresolved tier variable does not count as a missing tier definition.

## Local variable definitions

`file_variables` stores local definitions in each input `TECH_PATH` file scope, including expanded inclusions. Each entry contains an ordered `VariableDefinition` array:

| Field | Type | Purpose |
| --- | --- | --- |
| `name` | String | Name including `@` |
| `value` | String | Scalar definition contents, including a possible reference to another variable |
| `source` | `SourceLocation` | Physical definition origin |

File keys are relative to `TECH_PATH`; each definition's `source` identifies its physical origin relative to its own `root`. Files without local variables may be omitted from this object. Repeated names are not collapsed into one dictionary key. These are game variables; project settings from `global_variables.json` are not copied here.

## Inclusion history

`metadata.inline_scripts` is a required array, empty without calls. Each record contains `id`, `parent_id`, `call_site`, `form`, `script: {raw, value}`, `template`, `arguments: [{name, raw, value}]`, and `result_paths: string[]`. IDs are unique within a build; parents precede children. `form` is `reference` or `block`. `template` is relative to `INLINE_SCRIPTS_DIR`. Empty inclusions retain `result_paths = []`.

`call_site` contains `root`, `file`, `span`, and `inline_call_id`; substituted text additionally records `generated_span`, `fragments`, and, where applicable, `placeholder`. A `span` contains `start`, `end` (zero-based character offsets, exclusive end), and `line`, `column`, `end_line`, `end_column` (one-based). `fragments` and `placeholder` use the same recursive origin contract.

`result_paths` are unique JSON Pointers into the final database, validated for existence and forbidden from pointing into `metadata`. Parents may reference nested-call results. History never contributes to command, frequency, or scalar-usage analysis.

`file_variables` retains the calling `TECH_PATH` file scope; inserted definitions record the physical `source` of their template or argument. This does not load global game variables.

## Record example

The following is an abbreviated `technologies.tech_arcane_deciphering` record. It shows the envelope and selected game fields; actual collection must also retain remaining source fields, including `weight_modifier`.

```json
{
  "source": {
    "column": 1,
    "file": "00_ancient_relics_tech.txt",
    "inline_call_id": null,
    "line": 2,
    "root": "TECH_PATH"
  },
  "name": {
    "ru": "Расшифровка загадок",
    "en": "Arcane Deciphering"
  },
  "name_sources": {
    "ru": {
      "tier": "RU_LOC_TIER_2",
      "file": "ancient_relics_l_russian.yml",
      "line": 280,
      "key": "tech_arcane_deciphering"
    },
    "en": {
      "tier": "EN_LOC_TIER_1",
      "file": "ancient_relics_l_english.yml",
      "line": 280,
      "key": "tech_arcane_deciphering"
    }
  },
  "fields": {
    "area": "society",
    "tier": 2,
    "category": [
      "archaeostudies"
    ],
    "cost": {
      "variable": "@tier2cost3",
      "resolved": null
    },
    "weight": {
      "variable": "@tier2weight3",
      "resolved": null
    },
    "is_rare": true,
    "feature_flags": [
      "unlock_arcane_deciphering"
    ]
  }
}
```

The names and provenance were checked in the current directories: the key is absent from `RU_LOC_TIER_1` and present in `RU_LOC_TIER_2`. No technology description is added. This is a documentation example, not output from an implemented importer.

## Validation rules

Implementation should validate database construction as follows:

1. Closed structure of every object, `format_version`, allowed fields for each context, value types, and unique JSON keys.
2. Preservation of every supported game field, repetition, logical group, and array order without assumed defaults.
3. Existence of prerequisite IDs and category definitions, plus correctness of known tier references. Cycle checks apply to the requirement graph, not every technology mention in scripts.
4. No external definition reads to resolve `@...`, inline scripts, or scripted triggers; unavailable values remain explicitly unresolved.
5. Independent RU/EN name lookup by key, Russian source priority, agreement between text and provenance, and exclusion of descriptions from localized fields.
6. Distinction among absent fields, empty values, unresolved references, and repeated entries.
7. Relative provenance paths and the ability to read prepared data without original sources.
8. Nested commands, operators, arguments, and scopes against declared rules; no arbitrary transfer of unknown elements into `fields` or `entries`.
9. A separate report for unsupported constructs and no working-database replacement after errors. An unknown condition must not be dropped or treated as true.
10. Preservation of distinctions among predecessors, general and starting conditions, weights, AI preferences, and variant triggers. A variant's parent is determined by its position within the base technology.

Document checks cover valid JSON examples, table coverage against the current technology model, and language-version consistency. The implemented builder passed synthetic checks and a full database build from the current sources; [first-stage results](BACKEND_STAGE_1_EN.md#validation) are documented separately.

## Related documents

- [Game technology object model](TECHNOLOGY_MODEL_EN.md).
- [Technology tree research](RESEARCH_TECH_TREE_EN.md).
- [Global variables and sources](../README_EN.md#global-variables).
- [Technical specification](TZ_EN.md).
- [Модель базы на русском](DATABASE_MODEL_RU.md).
