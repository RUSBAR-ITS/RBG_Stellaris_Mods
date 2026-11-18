# WEB_STTV — stage 15: parallel document builds

## Contents

- [Status](#status)
- [Invocation and configuration](#invocation-and-configuration)
- [Processing order](#processing-order)
- [Preserving expansion identities](#preserving-expansion-identities)
- [Validation and publication](#validation-and-publication)
- [Database identity](#database-identity)
- [Reports and measurements](#reports-and-measurements)
- [Acceptance results](#acceptance-results)
- [Modules](#modules)
- [Related documents](#related-documents)

## Status

Implementation of the [approved stage 15 specification](TZ_BACKEND_STAGE_15_EN.md) is complete and verified. The frontend remains at `0.0.3`; the database format is `sttv.parse_database` version `6`.

## Invocation and configuration

From `WEB_STTV`:

```powershell
$env:PYTHONPATH = (Resolve-Path src/backend).Path
python -B -m sttv.database_sets --reuse-libraries
```

To prepare libraries from scratch, replace `--reuse-libraries` with `--rebuild-libraries`. The coordinator performs the selected mode; workers load the prepared library JSON. Opening the application or page does not start a build.

`config/backend.json` references `config/parallel.json`:

```json
{
  "format_version": 1,
  "workers": 10,
  "staging_directory": "staging/parallel"
}
```

`workers` is the maximum worker count, excluding the coordinator. A value of `1` uses the same mechanism for sequential execution. Fewer workers may be busy with a small source selection. CPU count and estimated free memory do not automatically cap concurrency.

The intermediate directory is relative to `WORK_DIR`. Each operation creates its own subdirectory. Overlap with sources, library artifacts, configurations or database outputs is rejected. Results remain in `data/databases/` and reports in `data/reports/` unless configured otherwise.

## Processing order

1. The coordinator validates settings, captures inputs and prepares or loads the library snapshot.
2. A pool of separate Windows processes starts. Each loads libraries and prepares validation rules once.
3. Workers receive files of the current database: parsing/expansion, variable substitution, serialization, localization, validation, hashing and intermediate JSON writing.
4. The coordinator checks completeness and global constraints, then streams documents together in original file order.
5. The same pool moves to the next database. After all fifteen members are prepared, workers stop; the coordinator verifies inputs and publishes the set.

Trees never pass through the process queue. Messages carry jobs, counters, paths, hashes, diagnostics and statistics. Localization tables and resolved texts are reused for identical sources and reference settings. Cached texts replay their own source records; selected keys and counters remain document-local. Shared libraries do not acquire mutable game-call state.

## Preserving expansion identities

Previous builds accumulated `inline_N`, `scripted_effect_N`, `scripted_trigger_N` and `script_value_N` numbers across a database. Simply expanding documents independently would restart numbering and alter history.

After expansion, a worker therefore sends invocation counts and waits for document offsets. The coordinator calculates them in original order regardless of worker readiness. Serialization shifts only service identities and their references; game strings are not renamed. Validation receives the tree with its final identities.

This wait is measured separately as `id_order_wait` and subtracted from `parse_expand_serialize`. The tree stays in worker memory. A slow early file can delay serialization of later files, but no extra intermediate JSON read or parse is required.

## Validation and publication

Workers validate document structure, expansion history, node provenance and enrichments before writing. The coordinator checks for missing/duplicate results, repeated sources and duplicate object IDs within one database. Copying verifies each intermediate file's size and checksum.

Merging does not repeat a complete tree traversal. Anonymous definitions and fragments retain existing identity rules. A job error or worker crash fails the build; cancelled jobs are identified separately and do not increment failed-source counts.

Intermediate documents are removed after a member is merged, and remaining owned temporary files are removed when the operation ends. Other operations' directories and libraries are untouched. Leftovers from forced termination do not automatically resume a subsequent build.

Published databases remain unchanged until the complete set is prepared successfully. Publication then performs individual file replacements: failure at this step reports already replaced members, and differing `set_id` values reveal a mixed set.

## Database identity

Workers compute SHA-256 of canonical JSON for the complete document and a separate SHA-256 of formatted bytes written. The former contributes to content identity; the latter verifies copying.

The new `sttv.document_hashes.v1` algorithm derives `content_hash` from the format version and ordered document hashes. Shared `set_id` derives from the mapping of dataset kinds to their `content_hash` values. The exact contract is in [specification section 8](TZ_BACKEND_STAGE_15_EN.md#8-document-and-set-identity).

Worker count, PIDs, temporary paths and durations do not affect identity. Relative to stage 14, `dataset.set_id` changes; game-tree format and set-opening rules remain unchanged. This algorithm does not replace the library's `library_set_id`.

## Reports and measurements

Each database report's `performance.parallel` contains configured/actual worker use, job statuses, document sizes and hashes, process initialization measurements and memory samples. Stage durations reside in `performance.timings`; summed worker intervals can exceed build wall time.

Shared definitions and sources merge without multiplication by worker count. Validated documents, actual calls and other events sum; maximum depth takes the maximum. The coordinator writes reports.

Memory is sampled from Windows working sets once per second during the pool lifetime: the coordinator separately and the simultaneously observed sum of its process tree. This is a sampled maximum, not a sum of historical individual peaks. `errors` counts unsuccessful samples. `temporary_peak_bytes` measures document files in the operation subdirectory; additional staged final databases during merging and header insertion are excluded.

Measurements separate localization table loading (`localization_load`), offset waiting, merging, set-metadata insertion and final source verification. File-size distribution, worker preparation, disk throughput and sequential coordinator work limit speed; no speedup factor is predetermined.

## Acceptance results

Full acceptance runs under `data/stage15/`. The stage 14 reference is preserved in `baseline_hashes.json` and `baseline/`. Comparison normalizes only the header's `set_id` value, then verifies the checksum of all remaining file bytes.

Full runs were completed on 2026-11-18 on an Intel Core Ultra 9 275HX (24 logical processors), with 64 GiB installed memory:

| Workers / mode | Full build, s | Minutes and seconds | Process-tree peak, GiB |
| --- | ---: | ---: | ---: |
| `1 / reuse` | 2083.637 | 34:44 | 4.09 |
| `10 / reuse` | 500.060 | 8:20 | 21.34 |
| `10 / rebuild` | 510.998 | 8:31 | 20.92 |

The complete `reuse` build is **4.17 times faster**. All three results are byte-identical: 15 databases, 450 documents and 11,762,739,507 bytes. Relative to stage 14, only `dataset.set_id` changed. Game counters, diagnostics, provenance and localization match; hashes of all 1612 reference inputs are preserved. The new report classifies fifteen localization rule files as configuration, but still includes them in final verification.

Each document was validated once. Rules were prepared twice with one worker and eleven times with ten: coordinator plus each worker. In `reuse`, the coordinator loaded five library artifacts; workers loaded another five or fifty respectively. Actual template-application counts did not change.

| Complete `reuse` measurement, s | 1 worker | 10 workers |
| --- | ---: | ---: |
| Coordinator library loading | 63.2 | 67.9 |
| Worker initialization, sum | 63.1 | 467.5 |
| Parsing / expansion / serialization, sum | 631.3 | 479.6 |
| Localization table loading, sum | 9.2 | 92.0 |
| Document validation, sum | 306.5 | 209.7 |
| Document hashing, sum | 356.6 | 228.5 |
| Intermediate JSON writing, sum | 545.7 | 386.4 |
| History-offset waiting, sum | 14.6 | 676.0 |
| Coordinator streaming merge | 27.0 | 26.0 |
| Set-header insertion | 16.2 | 16.4 |

Worker intervals overlap: their sums cannot be added and presented as build duration or CPU time. For example, events took 1444.0 s with one worker and 191.7 s with ten. One-time library loading, waiting for earlier files and sequential merging reduce whole-set speedup compared with this largest database.

The fixed sample contains twelve technology, component and event files, 81,100 nodes and approximately 141.6 MiB of intermediate JSON. Each pool performed three passes:

| Workers | Pass 1, s | Pass 2, s | Pass 3, s | Median, s |
| --- | ---: | ---: | ---: | ---: |
| 1 | 71.672 | 20.516 | 17.241 | 20.516 |
| 10 | 57.554 | 7.977 | 8.225 | 8.225 |

All six results match; the median ratio is **2.49**. The first pass includes worker startup/loading; subsequent passes reuse the same pool. Coordinator library loading, final input verification and localization are outside this separate sample measurement. The full builds above cover those actions. The sample's single-worker initialization took 49.2 s; initializations recorded in the first parallel pass took 45.5–47.4 s each and ran concurrently.

The OS disk cache was not flushed. Runs were sequential, without other acceptance builds, heavy tests or frontend reads of the full set. One full run per mode cannot guarantee a permanent speedup factor or establish the significance of the `reuse`/`rebuild` difference.

Memory was sampled once per second; each complete ten-worker run skipped one unsuccessful sample. This is not a build failure. Observed intermediate documents peaked at 8.74 GiB; staged final databases and header copying need additional space excluded from this measurement.

All 240 backend tests and 33 frontend checks passed without skips, including the published set. Catalogs match stage 14: 679 technologies, 1506 components and 498 buildings; links, upgrade evidence and the existing 214 missing-localization warnings are preserved. The game was not launched: game files were unchanged and this stage requires no in-game check.

Primary artifacts under `data/stage15/`: `acceptance_summary.json`, `one_worker/acceptance.json`, `ten_workers/acceptance.json`, `rebuilt/acceptance.json`, `benchmark/acceptance.json`, `tests_complete.log`, `frontend_tests.log`, `frontend_acceptance.json` and `documentation_check.json`. The published set is in `data/databases/`; main reports correspond to the final complete `rebuild` run, with separate measurements retained under `stage15/`.

## Modules

| Module | Responsibility |
| --- | --- |
| `parallel/settings.py` | Configuration and path restrictions |
| `parallel/pool.py` | Pool, bounded job dispatch and staging-directory ownership |
| `parallel/worker.py` | Process initialization and document lifecycle |
| `parallel/ordering.py` | Cumulative invocation numbering and wait cancellation |
| `parallel/localization.py` | Table reuse without leaking job state |
| `parallel/text_cache.py` | Resolved text reuse with exact source replay |
| `parallel/results.py` | Report deltas and cross-document constraints |
| `parallel/memory.py` | Process-tree memory sampling |
| `database/collection.py` | Shared source-document processing |
| `database/streaming.py` | Hashing, intermediate JSON and streaming merge |

Schemas are generated from `schema_generation/`, including the new parallel configuration schema. The old sequential `DocumentWriter` is replaced by the shared intermediate-document and merging mechanism.

## Related documents

- [Stage 15 specification](TZ_BACKEND_STAGE_15_EN.md).
- [Stage 14 libraries](BACKEND_STAGE_14_EN.md).
- [Stage 13 validation optimization](BACKEND_STAGE_13_EN.md).
- [README](../README_EN.md).
- [Русская версия](BACKEND_STAGE_15_RU.md).
