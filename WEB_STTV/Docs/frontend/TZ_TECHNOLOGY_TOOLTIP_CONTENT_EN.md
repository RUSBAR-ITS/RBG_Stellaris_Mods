# Extended technology tooltip content

## Contents

- [Stage scope](#stage-scope)
- [Three sections](#three-sections)
- [Titans example](#titans-example)
- [Names and condition phrases](#names-and-condition-phrases)
- [Checks and scope decisions](#checks-and-scope-decisions)

## Stage scope

Hovering over or focusing a base technology card immediately shows its localized name and description. The card requests the sections by game ID and current language. A successful response is reused for that technology and language in the same tree. If the request fails, the tooltip still shows the name and description and retries the next time it opens. The mouse wheel scrolls a long tooltip. Page Up and Page Down scroll it while the card has focus. [Technology card](elements/TZ_TECHNOLOGY_CARD_EN.md) · [Tooltip element](elements/TZ_TOOLTIP_EN.md) · [Request and response](../../src/server/README_EN.md#technology-tooltip-content)

## Three sections

| Section | Source | Interpretation |
|---|---|---|
| Required technologies | The technology's entire `prerequisites` expression | Use names in the selected language. Siblings in the outer block imply AND. Preserve each alternative group and its boundaries, including independent OR groups. The parent chosen for layout cannot represent the full expression. |
| Availability conditions | `potential` and, when present, `allow` | Retain the source block, nested logic, subject, negation, comparison operator and threshold. List the conditions independently of their truth in a particular game. |
| Research draw weight modifiers | Every `weight_modifier` block | Present each rule in source order with its condition and operation. Distinguish the block's direct `factor`, conditional multiplication and conditional addition. Show zero factors explicitly. For a computed value, describe the expression or its dependencies. |

Empty sections may be omitted. Interpret `has_technology` within its enclosing rule. A check on a neighbouring empire inside a weight modifier affects the weight. Nested AND, OR, NOT, NAND and NOR retain their scope. Use parentheses or a nested list when a sentence would be ambiguous. Text parameters of `custom_tooltip` supply labels. Checks inside `hidden_trigger` retain their place in the condition model. [Tooltip semantics](../semantics/TOOLTIPS_EN.md) · [Logic and context](../semantics/LOGIC_AND_CONTEXT_EN.md)

## Titans example

Technology `tech_titans`. The following content follows the existing title and description.

**Required technologies**  
Battleships **or** Advanced Stinger Development.

**Availability conditions**  
The game host has Apocalypse enabled.

**Research draw weight modifiers**

| Applies when | Weight change |
|---|---:|
| At most 100 years have passed since game start | ×0.1 |
| At least one neighbouring empire has researched Titans | ×10 |
| More than 130 years have passed | ×2 |
| More than 140 years have passed | ×3 |
| More than 150 years have passed | ×4 |
| The empire has adopted the Supremacy tradition tree | ×1.25 |

Each row represents a separate modifier. The 130-, 140- and 150-year thresholds are independent. [Game definition](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:236)

## Names and condition phrases

The server dictionary, inventory of nested conditions and coverage check across all base technologies are described in the [phrase dictionary specification](../../src/server/Docs/TZ_TOOLTIP_DICTIONARY_EN.md).

For `has_policy_flag`, look up the option that sets the flag under `policies → option → policy_flags`. For a bypass type, look up the game ID in `bypass` and pass its `name` field to the server localization lookup. [Import specification for both directories](../../src/loader/Docs/TZ_POLICIES_AND_BYPASS_EN.md)

Use the server localization lookup for object names. DLC titles follow the same selection used on the game settings screen. Provide a small bilingual dictionary for condition and operation phrases. For example, `any_neighbor_country` supplies “at least one neighbouring empire”, and the referenced technology supplies its own localized name. [Key rules](../../src/server/config/localization_keys.json)

The initial check of the published dataset found references into the following game directories. Counts refer to distinct scalar IDs in the three agreed sections of base technologies.

| Directory under `common/` | Predicate | IDs with both RU and EN names / distinct IDs |
|---|---|---:|
| `resolutions/` | `is_active_resolution` | 6 / 6 |
| `federation_perks/` | `has_federation_perk` | 2 / 2 |
| `relics/` | `has_relic` | 2 / 2 |
| `planet_classes/` | `is_planet_class` | 4 / 4 |
| `districts/` | `has_district` | 3 / 3 |

The names for these five predicates already exist in `wiki.localization`. Full object definitions are needed when wording depends on additional fields. Identify such imports from the remaining predicates before implementation. Import each selected directory in full. For a technical flag without a game label, retain the ID and identify it as a flag. Keep an unrecognized construct identifiable together with its source expression.

## Checks and scope decisions

- The checked database contains 679 base technologies. 505 explicitly have `prerequisites`, and 376 have `potential`. None has a top-level `allow`. Cover that field with a small synthetic example.
- 555 technologies have `weight_modifier`. Across them there are 1,672 conditional `modifier` blocks. 1,642 specify a scalar factor, 26 specify a `script_value` factor, and four use `add`. Also cover `factor` directly inside `weight_modifier`.
- Check Mega-Engineering for two independent OR groups and the mandatory Zero Point Power technology. For Artificial Personality Matrix, ×0.33 requires both the Necrophage **origin** and the Necrophage **species trait**. These are distinct conditions with identical names. [Technology model](../TECHNOLOGY_MODEL_EN.md)
- For `tech_crystal_armor_1`, check **+5** when the empire has the `crystal_armor_1_weight` flag. For `tech_storm_manipulation`, check a computed factor without assigning an invented numerical value. The draw probability depends on the other available research options.
- Decide separately whether to include `starting_potential` (starting grants, 19 technologies) and `mod_weight_if_group_picked` (weight after a technology in the same group is picked, 34 technologies). Distinguish starting grants from ordinary research availability. Research rewards, AI preferences and tracing event chains are separate tasks.
