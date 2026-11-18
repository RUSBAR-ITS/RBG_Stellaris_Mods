# Stellaris Technological Tree View — three localized databases

## Contents

- [Running](#running)
- [Files and settings](#files-and-settings)
- [Format and localization](#format-and-localization)
- [Publication and diagnostics](#publication-and-diagnostics)
- [Validation](#validation)
- [Limitations](#limitations)

## Running

Implementation of [approved stage 11](TZ_BACKEND_STAGE_11_EN.md). Run explicitly from `WEB_STTV`; the frontend does not invoke this command:

```powershell
$env:PYTHONPATH = 'src/backend'
python -B -m sttv.database_sets
```

In this workspace, `data/.venv/Scripts/python.exe` can replace `python`. Arguments `--variables` and `--config` select the global-variable and set-configuration files. Defaults are `global_variables.json` and `config/backend.json`, relative to the product directory. Exit codes: `0` for success, `1` for failure.

## Files and settings

| Role | Source relative to `STELLARIS_ROOT` | Output relative to `WORK_DIR` |
| --- | --- | --- |
| `technologies` | `TECH_PATH`: `common/technology` | `databases/technologies.json` |
| `components` | `COMPONENTS_DIR`: `common/component_templates` | `databases/components.json` |
| `buildings` | `BUILDINGS_DIR`: `common/buildings` | `databases/buildings.json` |

Shared parser settings are in `config/backend.json` → `parser`. `datasets` specifies each kind's sources and outputs. `localization` selects enrichment configuration; `report` selects the aggregate report. The set schema is `schemas/database_set.schema.json`; `backend.schema.json` describes an individual general-purpose tree build.

In `config/enrichment/localization.json`, languages, source priorities and reference expansion remain shared. `targets` contains each kind's selectors and localization-key rules. All output paths are checked together: collisions, nesting and overlap with protected inputs are rejected.

## Format and localization

Database format: `sttv.parse_database`, version `5`. Each set member has `dataset.kind` and the shared `dataset.set_id`. Identity is computed from canonical SHA-256 hashes of all three fully enriched trees without `dataset`; output filenames and execution time do not affect it.

Databases use compact JSON without indentation. This only changes file representation: AST, item order, expansion provenance and localization remain intact. Parser metadata does not become catalog objects.

RU/EN names and descriptions reside in `enrichments.localization`. Technologies retain variants and description inheritance. Component identity comes from its direct `key`; descriptions use `<key>_DESC`, followed by the explicit `<component_set>_DESC`. `fallback` records the component-set field reference. Found empty text is valid and does not trigger fallback.

Buildings use `<id>_desc` or an explicit scalar `desc`. Each conditional `desc` block has its own `description` from `text`, without `name`. Conditions remain in the tree; no active description is selected. Original strings, expanded static references, dynamic tokens and translation provenance retain stage-ten behavior.

## Publication and diagnostics

The coordinator in `src/backend/sttv/database_sets/` sequentially parses, localizes, validates and stages members. All three results, input hashes and directory inventories are checked before publication. A preparation failure in any member leaves existing final databases untouched.

Each file replacement is atomic; the complete set is published sequentially. Failure between replacements can leave a mixed set. The report records actually written roles; the frontend rejects mismatched `set_id` values. Resolve the cause and rebuild the set.

Default reports: `reports/<kind>_build.json`, `reports/<kind>_localization.json`, `reports/database_set.json`. The aggregate report contains per-kind statuses and counts, input hashes, set identity and publication results. Missing translations and unresolved dynamic tokens are warnings. Selected-translation conflicts, duplicate IDs, parsing failures and changed inputs are errors.

Individual enrichment of a file with `dataset` is rejected because it would invalidate set membership. A general-purpose tree without this metadata may still be enriched independently. Version-four databases must be rebuilt.

## Validation

All 192 Python checks passed, including eight set scenarios: localization across kinds, shared identity, reproducibility, a changed member, third-member failure, shared-input changes, partial publication and rejection of individual member enrichment. TypeScript, the build and opening the complete set in the frontend were also checked.

The complete run uses 118 TXT files and retains 696,588 game nodes:

| Database | Files | Game nodes | Localization objects |
| --- | ---: | ---: | --- |
| Technologies | 35 | 82,246 | 679 technologies and 206 variants |
| Components | 55 | 357,812 | 1,506 components |
| Buildings | 28 | 256,530 | 498 buildings and 21 conditional descriptions |

Compact file sizes: technologies — 39,493,998 bytes; components — 220,001,927 bytes; buildings — 130,987,059 bytes; approximately 390.5 MB in total. The size change from indented serialization does not remove game data.

Names are found for every object in both languages. Technologies and buildings have no missing descriptions; 81 technology variants inherit their base description. Components lack 85 descriptions in each language. Four additional warnings concern two unresolved references in both languages: `SPACE_AMOEBA_WEAPON_DESC` and `null_void_siphon`; original tokens are retained. The component localization report therefore contains 174 warnings and no errors. Component parsing records 14 `unused_inline_argument` warnings from game calls.

Comparison with previously researched upgrades confirms 16 cases and 60 witnesses. Independent content and input verification is recorded in `data/stage11/independent_verification.json`; the final run summary is `data/reports/database_set.json`. Synthetic reproducibility checks compare bytes; the real repeat is additionally compared by content hashes and shared identity.

The final build completed in 758.309 seconds in this environment. The repeat confirmed the same `set_id` and hashes of all three enriched trees; published compact files match an independently compacted representation of the first result byte for byte. All 1,066 input files were checked again with no changes. Parsing, localization and publication succeeded for all three members.

## Limitations

The stage processes TXT files from the three directories; weapon-stat CSV/ODS files are excluded. The parser preserves game constructs without evaluating country state. New card ordering and primary-chain selection belong to a subsequent stage.

[Opening the set in the frontend](frontend/FRONTEND_STAGE_2_EN.md). [Русская версия](BACKEND_STAGE_11_RU.md).
