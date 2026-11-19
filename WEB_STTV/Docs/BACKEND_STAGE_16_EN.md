# Stage 16 — technology parent and child enrichment

## Contents

- [Implementation](#implementation)
- [Running](#running)
- [Configuration and combinations](#configuration-and-combinations)
- [Result format and freshness](#result-format-and-freshness)
- [Reading and publication](#reading-and-publication)
- [Verification and working results](#verification-and-working-results)
- [Stage boundaries](#stage-boundaries)

## Implementation

Implemented the [stage 16 specification](TZ_BACKEND_STAGE_16_EN.md). The [enrichment/technology_tree](../src/backend/sttv/enrichment/technology_tree/__init__.py) module calculates relationships using an existing set of 15 databases. It does not start a build, localization or game-file reading.

Each technology receives one parent, root status or ambiguity status. A child is immediately added to its parent's list even if that object's own parent has not been calculated. Final child lists are ordered by ID for reproducibility; this is not card placement order.

Handlers implement the 13 agreed criteria. Empty results are skipped and selection stops at one candidate. Original requirements and game tiers stay intact. Ambiguity is retained with diagnostics; a cycle or broken reciprocity prevents publication.

## Running

Run from `WEB_STTV` with backend dependencies installed:

```powershell
$env:PYTHONPATH = "src/backend"
& data/.venv/Scripts/python.exe -B -m sttv.enrichment.technology_tree
```

By default the operation enriches `data/databases/technologies.json`, taking other paths from `config/backend.json`. A current combination is reused. To force calculation:

```powershell
& data/.venv/Scripts/python.exe -B -m sttv.enrichment.technology_tree --recalculate
```

Options include `--variables`, `--config`, `--combination`. To use the prepared working copy:

```powershell
& data/.venv/Scripts/python.exe -B -m sttv.enrichment.technology_tree --config data/stage16/operation.json
```

The Python interface returns a report rather than the database tree:

```python
from sttv.enrichment.technology_tree import enrich_technology_tree

report = enrich_technology_tree(config_path="data/stage16/operation.json")
```

Success, including warnings, uses exit code 0. Errors use a nonzero code, with the specific cause in the report's `error`. Opening the interface does not automatically invoke this operation.

## Configuration and combinations

| File | Purpose |
| --- | --- |
| [technology_tree.json](../config/enrichment/technology_tree.json) | Configuration addresses, report and working directory |
| [rules.json](../config/enrichment/technology_tree/rules.json) | Criterion order, enablement and evidence parameters |
| [reference_empire.json](../config/enrichment/technology_tree/profiles/reference_empire.json) | Verified conventional empire facts; absent facts remain unknown |
| [reference_default.json](../config/enrichment/technology_tree/combinations/reference_default.json) | Reference mode, profile and variant selection |

The `rules` order and `enabled` flags are configurable. `parameters` are supplied directly or through a sole `definition_ref` naming a `definitions` block. References replace entire parameter objects without overrides or chains. Disabled rules are also validated. A new calculation type needs a handler and schema; new values of existing mappings are configured separately.

`variants` maps a base technology ID to `base` or `swap:N`, starting at 1. Omitted technologies use the base representation. Candidate area and category changes also affect calculation. Manual selection does not require the variant's game condition to pass.

With `inherit_effects = yes`, base and variant effects participate; with `no`, only variant effects do. A missing flag or conflicting numeric modifiers causes a dependent criterion to be skipped with diagnostics. Technology names do not supply guessed inheritance defaults.

## Result format and freshness

The original technology node stores `enrichments.technology_tree[combination_id]` with `parent_tech`, `children`, `status`. Shared parameters and revisions reside in root `technology_tree.combinations`. Localization and other combinations are retained.

`dataset.set_id` continues identifying the original published set. Separate revisions cover sources, rules, parameters, calculation implementation and resulting relationships. The operation's own enrichment is excluded from the technology input digest. The other 14 files use byte hashes; formatting them conservatively changes the input revision.

Reuse requires a matching calculation revision and valid relationships/result hash. Older combinations are not automatically declared current. Recalculation completely replaces the selected combination, removing obsolete records and child links. Even forced calculation avoids rewriting the database when the checked result matches.

Schemas are produced by `sttv.schema_generation`: five operation, rule, profile, combination and report schemas were added, and `database.schema.json` was extended. Explicit general database validation additionally checks record placement, reciprocity, cycles and revisions. Enrichment does not repeat full original AST validation.

## Reading and publication

The technology database is loaded into memory. Related databases are read sequentially by root object; line formatting does not determine JSON boundaries. The entire events file is never loaded into memory. Only events reached by explicit action routes are retained; textual ID matches do not create relationships.

Evidence indexes are prepared once per calculation. Reuse checks hashes and stored results without rebuilding functional indexes. Matching hashes establish that previously verified headers are unchanged; changed inputs have their headers checked again. Reading input files for hashing is still required. The report separately accounts for reading passes and byte counts.

Only the technology file is published: a temporary JSON file beside it, unchanged-input checks and atomic replacement. Output uses two-space indentation, UTF-8 and line breaks. A lock file prevents concurrent updates of the same destination. Failure before replacement preserves the previous file; report-write failure after replacement honestly retains `database_written = true`.

Reports contain actual selection steps, conditions and evidence addresses. Reuse does not repeat these steps: `trace_state = not_recalculated`, the trace is empty and remaining candidates are not invented. Detailed traces remain in calculation reports. Calculation ambiguities include combination, rule and setting context; absent window state is marked explicitly.

## Verification and working results

Enriched working copy: [data/stage16/technologies.json](../data/stage16/technologies.json). The other 14 files are read-only inputs from `data/databases`. The original technology database is retained.

The base result exactly matched the analytical reference: **679 technologies, 178 roots, 501 selected parents; 0 ambiguities or cycles**. Among technologies with parents, 412 had one original prerequisite and 89 had multiple. All decisions and 12 separate control examples were compared.

Acceptance checked all 206 variants individually and three combinations using indexes prepared once, reversed processing order, and saving/reusing two combinations. No ambiguities or warnings occurred in these runs on the current set; this does not guarantee the same outcome for other data. Expected pairs are read by verification after calculation and are unavailable to selection.

Verification artifacts:

- [acceptance.json](../data/stage16/acceptance.json) — outcome, variants, control cases and operation timings;
- [base_acceptance_report.json](../data/stage16/base_acceptance_report.json) — base trace;
- [variant_report.json](../data/stage16/variant_report.json) — changed combination publication;
- [base_reuse_report.json](../data/stage16/base_reuse_report.json) and [variant_reuse_report.json](../data/stage16/variant_reuse_report.json) — reuse;
- [tests.json](../data/stage16/tests.json) and [tests.txt](../data/stage16/tests.txt) — synthetic and related regression checks.

Passed 58 checks: 33 new enrichment checks and 25 schema generation, structural validation and database-set build checks. Coverage includes write failures, concurrent invocation, changed inputs during calculation, corrupted relationships and obsolete combination records.

The first full calculation took approximately 279 seconds: 262 seconds preparing indexes, 8 seconds hashing and 7 seconds writing. Selection itself took approximately 0.004 seconds. Measurements describe this machine and set; acceptance variant publication uses already prepared indexes and does not measure an independent cold invocation.

After eliminating repeated scans of unchanged JSON, reuse was checked again: approximately 11.1 seconds for the base and 10.9 seconds for the changed combination, without database writes. Reading and hashing sources dominate the time. Ten operation checks were rerun, including a changed header in a previously used set.

## Stage boundaries

The frontend does not yet use the new relationships for sorting and placement. `location`, the grid, a local API and a recalculation button remain subsequent stages. Event-based technology acquisition analysis is deferred; events only support the previously agreed weaponry evidence. Actual empire state and in-game effect execution are not evaluated.

[Stage 16 specification](TZ_BACKEND_STAGE_16_EN.md) · [Русская версия](BACKEND_STAGE_16_RU.md).
