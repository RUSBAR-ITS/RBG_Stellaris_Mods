# Second backend stage — rule profiles and source analysis

## Contents

- [Stage result](#stage-result)
- [Code structure](#code-structure)
- [Application schemas](#application-schemas)
- [Profile selection and outputs](#profile-selection-and-outputs)
- [Profile structure](#profile-structure)
- [Additional analysis sources](#additional-analysis-sources)
- [Observations and recommendations](#observations-and-recommendations)
- [Programmatic operations](#programmatic-operations)
- [Persistence and errors](#persistence-and-errors)
- [Validation and limitations](#validation-and-limitations)

## Stage result

**Historical guide.** Describes the implementation before the syntax-tree database transition. Current operation and format: [stage six](BACKEND_STAGE_6_EN.md).

The subsequent [configurable parser](BACKEND_STAGE_3_EN.md) adds syntax configurations, new nodes, and explicit projection into the current model. Profiles described here retain their separate role.

The approved [second-stage specification](TZ_BACKEND_STAGE_2_EN.md) is implemented. The backend is organized into packages; schema generation resides in permanent code. Building uses an explicitly selected JSON profile, while a separate analyzer produces observations and recommendations.

The database retains format 1: technologies, variants, categories, tiers, local variables, and RU/EN names. Unchanged inputs produce a byte-identical first-stage database. Basic invocation and Python preparation are documented in the [builder guide](BACKEND_STAGE_1_EN.md).

## Code structure

| Package within `src/backend/sttv/` | Responsibility |
| --- | --- |
| `common/` | Errors, JSON, paths, schemas, diagnostics, safe persistence |
| `sources/` | Source settings, variables, file selection and reading |
| `script/` | Parsing, variables, command and value validation |
| `technologies/` | Shared field contracts, definition collection and conversion |
| `localization/` | Names by key and priority |
| `database/` | Completed-database and reference validation, publication |
| `schema_generation/` | Application-schema declarations and generation |
| `rules/` | Profile loading, validation, expansion and persistence |
| `analysis/` | Additional sources, observations and recommendations |

`builder.py` coordinates builds; `src/backend/main.py` remains the CLI entry point. Tests are grouped by subsystem in `src/backend/tests/`, with shared fixtures in `support.py`.

The sole object-field declaration is `src/backend/sttv/technologies/contracts.py` (removed in stage six): context, name, conversion kind and cardinality. The converter and database-schema generator both consume it. A new technology field requires contract and supporting-code changes under an agreed specification.

## Application schemas

| Schema within `schemas/` | Validates |
| --- | --- |
| `database.schema.json` | Database format 1 |
| `backend.schema.json` | Build settings |
| `report.schema.json` | Build report |
| `profile.schema.json` | Input rule profile |
| `registry.schema.json` | Expanded registry |
| `analysis.schema.json` | Analysis settings |
| `analysis_report.schema.json` | Observations, recommendations and sources |
| `generation_report.schema.json` | Registry persistence result |
| `parser_lexical.schema.json` | Lexical configuration, added in stage three |
| `parser_constructs.schema.json` | Compound forms, added in stage three |

The generator derives structure from application declarations, not a completed database or a particular game installation. Schemas are closed; dictionaries with arbitrary identifiers allow only explicitly declared value types.

Explicit developer operation from `WEB_STTV`:

```powershell
$env:PYTHONPATH = (Resolve-Path src/backend).Path
./data/.venv/Scripts/python.exe -B -m sttv.schema_generation
```

It replaces validated schemas in `schemas/` and reports actual writes. Identical declarations produce identical bytes. Ordinary building reads schemas without rewriting them. The former `data/make_schemas.py` was removed; there is no second generator.

## Profile selection and outputs

[config/backend.json](../config/backend.json) now includes:

```json
{
  "rules": {
    "profile": {
      "base": "product",
      "path": "profiles/stellaris_4_5_4.json"
    },
    "registry": "rules/script_rules.json",
    "report": "reports/generation_report.json",
    "game_version": "4.5.4"
  }
}
```

`base: "product"` resolves from the product directory. A user profile uses `base: "work"` and, for example, `path: "profiles/my_profile.json"`. There is no fallback search. `game_version` explicitly declares the source version; `null` means unknown. A known mismatch with the profile produces a warning without automatically changing profiles.

| Output relative to `WORK_DIR` | Setting |
| --- | --- |
| `database.json` | `outputs.database` |
| `reports/build_report.json` | `outputs.report` |
| `rules/script_rules.json` | `rules.registry` |
| `reports/generation_report.json` | `rules.report` |
| `reports/analysis_report.json` | `output` in `config/analysis.json` |
| `profiles/my_profile.json` | Explicit profile-save argument |

Output paths are relative and stay inside `WORK_DIR`. Configuration, sources, schemas, supplied profiles, code and documentation are protected from working writes. Changing `WORK_DIR` does not move earlier outputs.

## Profile structure

The supplied `profiles/stellaris_4_5_4.json` (removed in stage six) transfers effective first-stage rules: 183 shared condition commands, 23 contexts and 10 inline signatures. Shared definitions use 67 templates and 89 command groups. This is an initial profile for the researched version, not a complete engine-language specification.

| Field | Contents |
| --- | --- |
| `format_version` | Profile format version; currently 1 |
| `profile_id`, `revision`, `game_version` | Identifier, positive content revision, target game version or `null` |
| `provenance` | Sources: `id`, `kind`, `file`, `line`, `record`, `game_version`, `notes` |
| `value_types` | Named argument types |
| `scopes`, `root_scope` | Declared scopes and initial validation scope |
| `contexts` | Contexts with `conditions` and `required` lists |
| `templates` | Templates: `rule` and optional single `extends` |
| `command_groups` | `context`, `template`, explicit `commands` list, `evidence` references |
| `overrides` | `context`, `command`, changed `rule` properties, `reason` and `evidence` |
| `inline_scripts` | Inclusion paths, `scalar` flag and `parameters` type mapping |

Types are based on `boolean`, `number`, `integer`, `identifier`, `string`, `enum`, `block` and `inline`. Identifiers require `pattern`; strings may optionally specify one. Numbers accept `minimum`, `maximum` and regular expressions for permitted reference forms in `references`. Enums require `values`. Inapplicable constraints are rejected.

An expanded rule contains `type`, `scopes`, `operators`, `many`, `context` and `scope`. `scopes: null` retains unrestricted scope acceptance; a block's `scope: null` retains its incoming scope. Blocks require a known nested `context`; scalar rules have `context` and `scope` set to `null`. Each template must resolve to all rule properties after inheritance.

The special group context `"$conditions"` defines shared condition commands. An ordinary context includes them through `conditions: true`; its own rule takes precedence over a shared rule. This explicit behavior is preserved from stage one.

Identical definitions within one context consolidate; different definitions conflict. An override changes an existing rule after group expansion; multiple overrides for the same command are prohibited. Inheritance cycles and unknown references fail, while recursive conditions under the declared grammar are allowed.

For inline signatures, `scalar: true` permits scalar invocation in addition to block invocation; `false` permits only a block. Parameter names must match exactly and values must be scalar. A parameter occurring in every observed example does not by itself establish requiredness.

Per-command evidence was not recorded for the original registry. Initial-profile provenance is therefore marked `unverified` with the former registry's hash. Missing evidence is not presented as engine documentation.

## Additional analysis sources

`config/analysis.json` (removed in stage six) defaults to an empty additional-source list. Technologies use existing `TECH_PATH`, category and tier settings. Rule analysis does not require localization.

Example explicitly connected source:

```json
{
  "id": "trait_triggers",
  "kind": "scripted_triggers",
  "path": "common/scripted_triggers",
  "pattern": "05_scripted_triggers_traits.txt",
  "recursive": false,
  "encoding": "utf-8-sig",
  "enabled": true,
  "game_version": "4.5.4"
}
```

Relative `path` resolves from `STELLARIS_ROOT`; absolute paths and global-variable references in `${NAME}` form are supported. Disabled sources are not opened and their variables are not resolved. An unavailable enabled source, empty file selection or unsupported format produces an error and `partial` analysis status.

| `kind` | Supported format and limitations |
| --- | --- |
| `engine_documentation` | A log containing `== TRIGGER DOCUMENTATION ==`, `command - description` sections, examples and `Supported Scopes:`. Explicit scopes and operators are extracted; complex argument descriptions require review. Other formats, including effect logs, are unsupported. |
| `scripted_triggers` | Named text blocks in supported game syntax; names, `$NAME$` parameters and nested constructs. Bodies are neither executed nor expanded into the database. |
| `inline_scripts` | Inclusion files; path relative to the selected root without `.txt`, parameters and nested constructs. Select `common/inline_scripts` as the root to retain full names such as `technologies/…`. |

`max_examples` limits evidence examples and template candidates per observation; the complete observation collection remains in the report. `excerpt_length` limits a source-line excerpt to 1–500 characters. Machine-specific additional-source paths are not embedded in Python.

## Observations and recommendations

An observation contains a stable `id`, command, context and scope or `null`, operator, argument form, parameter names, `inline_path`, coordinates and original nesting. Documented statements are distinguished from actual usage. The source manifest retains paths, versions, status and hashes of files read.

An unknown parent block does not give child commands an assumed `country` scope. An external script's invocation context is likewise unknown until explicitly established. The analyzer does not evaluate country state.

A recommendation includes a target, current rule, alternatives, supporting evidence, questions and contradictions. Alternatives can add a command, argument form, operator, scope or inline parameter, or request review of a new block or model field. A candidate template is an inference from the observed form and requires verification.

`profile_id` and `profile_fingerprint` bind results to exact profile content. `validate_recommendation_profile` rejects stale results. No operation applies recommendations automatically; the user edits JSON, increases its revision and explicitly selects it for subsequent work.

`complete` means selected-source reading completed without errors. It does not mean every construct is permitted by the profile or confirmed by the engine. Absence of a command from sources is not a reason to remove its rule.

## Programmatic operations

After adding `src/backend` to the import path:

```python
from sttv.common.paths import PRODUCT_ROOT
from sttv.common.json_io import read_json
from sttv.sources.settings import load_settings
from sttv.rules.compiler import load_profile, validate_profile, generate_registry
from sttv.rules.operations import save_profile, generate
from sttv.analysis.operations import analyze, save_analysis
from sttv.analysis.recommendations import validate_recommendation_profile
from sttv.database.validation import validate_database

settings = load_settings(PRODUCT_ROOT / "global_variables.json",
                         PRODUCT_ROOT / "config/backend.json")
profile = load_profile(settings.profile)
validation = validate_profile(profile)
registry = generate_registry(profile)

report = analyze(settings, PRODUCT_ROOT / "config/analysis.json")
validate_recommendation_profile(report, profile)
saved = save_analysis(settings, PRODUCT_ROOT / "config/analysis.json", report)
```

`generate_registry(profile)` returns a validated registry in memory. `generate(settings)` explicitly generates and saves a registry and report, returning `(registry, report)`. `save_profile(settings, profile, "profiles/my_profile.json")` validates and saves a user profile without changing active configuration. `save_registry(settings, registry)` is separately available in `rules.operations`.

Completed-database validation with an explicitly supplied registry:

```python
validate_database(read_json(settings.database), read_json(settings.registry))
```

It neither opens game sources nor reconstructs a missing registry. `build` regenerates the registry from the selected profile; an invalid profile cannot reuse the old file. Building does not run analysis. These operations have no console prompts, web service or UI.

## Persistence and errors

JSON is validated before writing, then a temporary file beside its destination is reread and replaces the target. A pre-replacement failure preserves the previous file. Multiple replacements are not described as one transaction.

The build report includes `database_written`, `registry_written` and `generation_report_written`. If registry writing succeeds but its report fails, the `generate` error carries a `result` recording the registry write; the builder retains that fact in its report. The schema generator returns the files actually replaced.

Data errors use `BuildError` with `code`, message, and available `line` and `field_path`. Unknown constructs remain build errors even when analysis has proposed changes for them.

## Validation and limitations

As of 2026-11-15, **54 synthetic tests** pass, including the previous 29. Coverage includes inheritance, conflicts, required arguments, repetition, types, scopes, operators, inline signatures, profile selection, safe persistence, partial outputs, stale recommendations and additional formats.

Current-source build: **679 technologies, 206 variants, 13 categories, 6 tiers**, with all 885 names present in both languages. There are no errors; 1,265 external-variable warnings and 7 repeated-field warnings remain. Database bytes match the first-stage reference; hashes of 741 source files are unchanged. Independent comparison covers 7,337 field occurrences.

Technology-only analysis: **10,231 observations, 0 recommendations**. Reading an existing trigger log, the trait-trigger file and one technology inline file was also checked; the log's unknown version is explicitly reported. Those recommendations were not applied.

Working evidence resides in `data/reports/`: `validation_report.json`, `stage_two_validation_report.json`, `unittest_output.txt`, `analysis_report.json` and `analysis_optional_sources_report.json`. These are not product inputs. Python files, including tests, stay within 200 lines.

UI, HTTP service, images and portable packaging remain future stages. Engine-language completeness, execution of game conditions and behavior in a running game have not been verified.

[Russian guide](BACKEND_STAGE_2_RU.md) · [Project overview](../README_EN.md).
