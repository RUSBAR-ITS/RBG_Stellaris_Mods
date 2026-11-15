# Stellaris language construct catalog

## Contents

- [Status and coverage](#status-and-coverage)
- [Structure and further subdivision](#structure-and-further-subdivision)
- [Initial inventory contents](#initial-inventory-contents)
- [What the examples already show](#what-the-examples-already-show)
- [Review workflow](#review-workflow)
- [Sources and checks](#sources-and-checks)

## Status and coverage

The `is_…`, `has_…`, `set_…`, `add_…`, and `remove_…` families were extracted at the user's request. Names come from `data/text_frequency/scalar_analysis/scalar_assignments.txt`; structural evidence and examples come from its JSON counterpart. These are initial inventories for manual review, with status `pending_semantic_review`. Family membership follows spelling; each name's purpose remains subject to agreement.

| Family | Names | All text occurrences | Key occurrences |
| --- | ---: | ---: | ---: |
| [is_…](keywords/is/inventory.json) | 235 | 50,814 | 50,731 |
| [has_…](keywords/has/inventory.json) | 184 | 62,120 | 61,590 |
| [set_…](keywords/set/inventory.json) | 132 | 15,700 | 15,700 |
| [add_…](keywords/add/inventory.json) | 40 | 4,127 | 4,127 |
| [remove_…](keywords/remove/inventory.json) | 44 | 6,146 | 6,146 |

Only names from the selected scalar list are included. This is not an exhaustive list of constructs in these language families: other forms, global singletons, and skipped inline-call contents are outside the input selection. Frequencies merge case, which does not itself establish case insensitivity for every game identifier.

## Structure and further subdivision

```text
language/
  README_RU.md
  README_EN.md
  keywords/
    is/
      inventory.json
    has/
      inventory.json
    set/
      inventory.json
    add/
      inventory.json
    remove/
      inventory.json
```

Each family has its own directory from the start. It currently contains one initial inventory; thematic files can follow once purposes have been checked. Possible divisions include conditions, definition fields, and custom scripted checks. These are directions for later review, not assigned categories.

After subdivision, a name's complete record should live in one place within its family. Context-dependent variants belong inside that record. When a reviewed record moves to a thematic file, remove it from the initial inventory to avoid maintaining duplicate copies. Add deeper nesting only for a concrete large group.

## Initial inventory contents

Files use ordinary JSON. Each `keywords` entry occupies one line; entries can use multiple lines as reviewed information is added. Headers contain family, status, name count, and source-list references with SHA-256 hashes. Header paths are relative to `WEB_STTV`.

| Record field | Meaning |
| --- | --- |
| Property name under `keywords` | Normalized construct name |
| `count` | Total text frequency in the input list, including value uses |
| `key_count` | Number of occurrences to the left of an operator |
| `operators` | Observed linking operators, not a language restriction |
| `example` | One exact source assignment or comparison |
| `source`, `line` | File relative to `STELLARIS_ROOT` and one-based example line |

The shared `observed_right_hand_type: "Scalar"` records the input-list criterion: every counted right-hand side for these names is scalar. It does not mean they all accept only `yes/no` or serve the same purpose. Processing rules and localization references have not been assigned automatically. The catalog is not yet consumed by the parser.

## What the examples already show

| Construct | Example | Observed context |
| --- | --- | --- |
| `is_ai` | `is_ai = no` | Condition inside an event's `trigger`: `events/achievement_events.txt:11` |
| `is_triggered_only` | `is_triggered_only = yes` | Event definition field beside `trigger`: `events/achievement_events.txt:8` |
| `is_rare` | `is_rare = yes` | Technology field: `common/technology/00_ancient_relics_tech.txt:8`; its purpose is also documented in `common/technology/000_documentation.txt` |
| `is_country_type` | `is_country_type = default` | Condition with a textual identifier: `common/achievements.txt:510` |
| `has_technology` | `has_technology = tech_hyper_drive_1` | Technology-presence condition: `common/achievements.txt:2013` |
| `has_morale` | `has_morale = no` | Army definition field: `common/armies/00_defense_armies.txt:57` |
| `has_planetary_ascension_tier` | `has_planetary_ascension_tier >= 3` | Numeric comparison: `common/ai_budget/04_influence_budget.txt:440` |

These examples show why a prefix alone cannot determine a shared processing rule. Observing a particular context does not establish the absence of other contexts.

## Review workflow

For each name, inspect sources and available documentation, then agree on its purpose, value forms, and contexts. Add processing rules afterwards where needed. Link existing rules to their current configurations, retaining a single configuration source.

When reviewing localization, retain verified game keys and source references. Do not guess a localization key from a command name. An absent localization field in the initial inventory means “not yet checked.” Keep explanatory documentation in the category's `_RU` and `_EN` files. Shared approved decisions remain in the [keyword and value reference](../Docs/KEYWORDS_AND_VALUES_EN.md).

## Sources and checks

The [scalar analysis](../Docs/RESEARCH_SCALAR_USAGE_EN.md) remains preserved in JSON. At the user's separate request, 635 names from the five extracted families were removed from the working `scalar_assignments.txt`, leaving 3,123 lines. Frequency statistics and family files are unchanged. Catalog-header source hashes refer to the complete list at extraction time.

Initial export: `TMP/WEB_STTV/text_frequency/export_keyword_families.py`. It checks TXT/JSON agreement, exact prefix selection, counts, uniqueness, frequency order, and complete examples. Rerunning refuses to overwrite existing files to preserve manual decisions. [Extraction report](../data/text_frequency/keyword_families_report.json).

Game sources were read only. Changes are limited to the initial catalog, research export, and documentation; parser behavior is unchanged.
