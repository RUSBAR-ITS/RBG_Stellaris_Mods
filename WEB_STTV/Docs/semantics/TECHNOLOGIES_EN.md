# Dictionary — technologies and variants

## Contents

- [Technology fields](#technology-fields)
- [Variant fields](#variant-fields)
- [Interpretation boundaries](#interpretation-boundaries)
- [Sources](#sources)

## Technology fields

| Keyword | Value form | Game meaning and analytical use | Sources |
| --- | --- | --- | --- |
| `area` | Identifier: `physics`, `society` or `engineering` | Research area. Determines the field section and the shared-area candidate criterion. | T1, T2 |
| `category` | Identifier list in a block | Scientific categories of the technology. Preserve the complete set for comparison, not just its first member. | T1, T2 |
| `tier` | Integer | Game research tier. Basis for the column; not the ID suffix, research cost or number of repeated research levels. | T1, T3 |
| `prerequisites` | Block of technology IDs and nested logical constructs | Technology dependencies. Preserve the full expression; mandatory requirements differ from members of alternatives. | T4 |
| `start_tech` | `yes` / `no` | Starting-technology flag. Does not prove unconditional granting to every empire; eligibility and initialization rules are separate. Useful for marking starting cards. | T3 |
| `levels` | Integer; `-1` denotes unlimited repetition | Research repeatability. Combined with `tier` and the presence of technology requirements for our separate display rule. | T5 |
| `potential` | Condition block | Conditions under which the technology is considered available to an empire. Used for comparing special conditions and profile filtering; does not replace `prerequisites`. | T6 |
| `technology_swap` | Repeatable variant block | Conditional representation of the base technology. Block order matters; a variant does not become an independently researched technology. | T1, T2 |

## Variant fields

The following entries describe direct children of `technology_swap`.

| Keyword | Value form | Game meaning and analytical use | Sources |
| --- | --- | --- | --- |
| `trigger` | Condition block | Determines when the variant applies. Documentation specifies the first matching variant; manual selection in the reference application is a separate mode. | T1, T2 |
| `name` | Identifier used for the variant name | Links to the localized variant representation. Does not replace the base technology ID in prerequisites. | T1, T2 |
| `inherit_effects` | `yes` / `no` | Controls inheritance of the base technology's effects. Relevant when comparing the selected variant's function. It is not a universal inheritance flag for all fields. | T1, T2 |
| `area` | Area identifier | Overrides the area; omission retains the base area. May change the card section and predecessor selection. | T1, T2 |
| `category` | Identifier list | Replaces the base technology's complete category list; omission retains the original list. It is not automatically appended. | T1, T2 |

## Interpretation boundaries

- `potential`, `technology_swap.trigger` and conditions in `weight_modifier` have different roles. Sharing a nested keyword does not make them interchangeable.
- Technology documentation describes tier progression, but actual definitions can require higher-tier technologies. `tech_reactor_boosters_3` has `tier = 1` and requires `tech_antimatter_power`, which has `tier = 3`. The numerical ID suffix does not correct `tier`.
- Original links and game semantics remain in the database. A selected `parent_tech`, the computed column of repeatable technologies and layout coordinates belong to the reference application's model.
- Logical blocks are preserved structurally; this entry does not assert engine support for every possible operator combination inside `prerequisites`.

## Sources

- [T1 — technology and technology_swap documentation](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/000_documentation.txt:1).
- [T2 — titan variants](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech.txt:269).
- [T3 — starting reactor booster and its successors](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:1734); [antimatter reactor](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_phys_tech.txt:1627).
- [T4 — compound Mega-Engineering requirements](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_megastructures.txt:1).
- [T5 — repeatable engineering technology](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_eng_tech_repeatable.txt:1).
- [T6 — arkship construction availability](E:/SteamLibrary/steamapps/common/Stellaris/common/technology/00_nomads_dlc_tech.txt:1).

[Dictionary index](README_EN.md) · [Русская версия](TECHNOLOGIES_RU.md).
