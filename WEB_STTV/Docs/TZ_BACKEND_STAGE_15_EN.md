# WEB_STTV — backend stage 15: parallel file processing

## Contents

- [1. Status and goal](#1-status-and-goal)
- [2. Existing implementation and scope](#2-existing-implementation-and-scope)
- [3. Configuration and invocation](#3-configuration-and-invocation)
- [4. Coordinator and worker processes](#4-coordinator-and-worker-processes)
- [5. Processing one document](#5-processing-one-document)
- [6. Validation responsibilities](#6-validation-responsibilities)
- [7. Intermediate files and merging](#7-intermediate-files-and-merging)
- [8. Document and set identity](#8-document-and-set-identity)
- [9. Failures and publication](#9-failures-and-publication)
- [10. Diagnostics and measurements](#10-diagnostics-and-measurements)
- [11. Tests and acceptance criteria](#11-tests-and-acceptance-criteria)
- [12. Implementation structure and documents](#12-implementation-structure-and-documents)

## 1. Status and goal

**The user approved this specification on 2026-11-18. Implementation and acceptance checks are complete; results are recorded in the [stage 15 guide](BACKEND_STAGE_15_EN.md).**

Process source files within one database in parallel. The initial setting is **10 worker processes**, in addition to the coordinator process. Each worker completes document preparation and validation, then saves an intermediate JSON file. The coordinator merges validated documents into the final database.

The user agreed to increased memory use, intermediate files, validation before writing, pool reuse between databases, fixed merge order and database identity derived from document hashes. Runtime and memory are measured; a tenfold speedup is neither promised nor an acceptance criterion.

## 2. Existing implementation and scope

At the time of specification:

- `database/collection.py` reads, expands and serializes documents sequentially.
- `database_sets/member.py` adds localization, collects member object identities and passes documents to `DocumentWriter`.
- `database/streaming.py` validates a document, traverses it for a canonical hash and writes formatted JSON.
- `database/checks/context.py` validates expansion history, provenance and enrichments within a document. `DatabaseValidator` also tracks repeated sources across documents.
- `database_sets/operation.py` sequentially prepares fifteen databases, calculates `set_id`, verifies inputs and publishes results.
- Stage 14 libraries are available through the current process context. Their definitions are reusable, but mutable counters, reports and invocation contexts cannot be shared between jobs.

Scope includes the fifteen-database set, standalone builds through the shared document-processing mechanism, configuration, reports, necessary schemas and checks. Databases within a set remain sequential relative to one another: only files of the current database are processed concurrently.

Preserve `sttv.parse_database` version `6`, complete trees, expansion history, provenance, RU/EN localization and formatted JSON. The `content_hash` algorithm changes, consequently changing `dataset.set_id`; preserving old values is unnecessary. The library's `library_set_id` remains a separate stage 14 identity.

Excluded: building different databases concurrently, splitting a single game file into independent jobs, parallel library preparation, MongoDB, incremental builds, resuming interrupted builds from intermediate files, new game rules, new import exceptions and UI changes. Analytics commands do not move to the pool in this stage; their existing library integration remains functional.

## 3. Configuration and invocation

Add `config/parallel.json`, referenced from `config/backend.json` using the established `base`/`path` convention. The proposed reference name is `parallel`. Builders must not hard-code these values.

| Field | Initial value | Requirement |
| --- | --- | --- |
| `format_version` | `1` | Configuration contract version |
| `workers` | `10` | Positive integer worker count; reject zero, negative, fractional and boolean values |
| `staging_directory` | `staging/parallel` | Intermediate results directory relative to `WORK_DIR` |

`workers` limits concurrent file jobs. Each worker runs one job at a time. Fewer active workers are acceptable when insufficient jobs exist. Do not silently cap the setting by CPU count or reduce it automatically due to memory use. A value of `1` uses the same new mechanism and provides sequential comparison without retaining a separate legacy engine.

The staging directory follows existing path restrictions: inside `WORK_DIR`, without overlaps with sources, library artifacts or final outputs. Each operation creates its own subdirectory; random temporary names never enter game data.

Preserve explicit, mutually exclusive `--rebuild-libraries` and `--reuse-libraries`. Worker count and temporary locations do not affect library freshness or user-facing database content identity. No new interactive dialog or additional mandatory CLI switches are needed.

## 4. Coordinator and worker processes

The coordinator reads settings, captures the input inventory and performs the selected library mode. It alone owns the preparation/reuse operation, directory locks, library publication and aggregate reports.

Once the snapshot is ready, create a pool compatible with launching separate Windows processes. Child initialization must not re-enter the CLI, create nested pools or start an independent `library_operation` that competes for locks and writes the shared report.

Each worker loads the prepared library artifacts into its own memory once, checking them against the snapshot description fixed by the coordinator. Loading neither rebuilds plans nor performs a separate full traversal of game source directories. A one-time check of loaded artifacts per process is allowed and counted as physical work. Game-source freshness verification belongs to the coordinator.

The pool lasts for the entire set build while library inputs and rules remain identical. Move to the next database after processing and merging the current one. Prepare structural validation rules once per worker. Reuse localization lookup tables and resolved static texts for identical sources and settings rather than rereading them for every document. This stage does not introduce a separate persistent localization library.

Separate immutable data from mutable job state: local variables, invocation history, selected translations, diagnostics and counters. Neither the previous job in the same process nor job distribution across workers may alter results.

Before dispatch, the coordinator fixes an ordered source list for the current database using the existing file-selection order. Assign a stable zero-based `document_index` to each source. Queue small job descriptions. Each available worker takes the next file; prepartitioning the list into ten permanent groups is unnecessary.

Existing expansion identities use cumulative database counters. To preserve their values, after expanding a document the worker reports invocation counts by kind. The coordinator calculates offsets in original document order; the worker then serializes with those offsets, validates and writes the tree. The tree remains in worker memory across this intermediate boundary; only counters and offsets pass through the queue. Measure offset waiting separately.

## 5. Processing one document

A file job contains dataset kind, `document_index`, relative source path, encoding, a reference to the agreed settings and its own intermediate output location. One source file produces one database document.

The worker:

1. Reads the source in read-only mode and records the hash of the bytes read.
2. Performs existing parsing, nested expansion, variable substitution and tree serialization with unchanged semantics.
3. For localized builds, selects objects and attaches localization using existing rules and priorities.
4. Validates the completed document and its local relationships.
5. Calculates its content hash, writes formatted intermediate JSON and returns the result to the coordinator.

A temporary one-document container must not change its global address: `inherited_from`, diagnostic pointers and other `/documents/N/...` references immediately use the assigned `document_index`, not zero or completion order. Node order and document-local expansion history identities remain the same as in sequential processing.

The response contains status, job identity, completed file path and size, hashes, node count, object identities with definition pointers, source information, diagnostics and measurements. Do not transfer a complete AST or complete JSON content through the process queue.

Release the job tree and mutable context after returning its result. Prepared libraries, rules and reusable lookup tables remain in the worker. Return separate job deltas, not repeated snapshots of all cumulative process counters.

## 6. Validation responsibilities

| Area | Worker | Coordinator |
| --- | --- | --- |
| Settings and libraries | Initialize from fixed settings and artifacts | Validate configuration, snapshot freshness and input selection |
| Tree | One structural validation of the completed document | Validate the final container without revisiting document trees |
| Provenance and history | Nodes, insertion addresses, parent calls and document enrichments | Aggregate source information and perform final freshness verification |
| Object identities | Duplicates within a document | Duplicates across documents within one database |
| Completeness | Result of its particular job | Exactly one successful result per selected source file |
| Intermediate JSON | Correct serialization and hash of written bytes | Size and checksum during streaming copy |

Cross-document checks use compact worker summaries. Do not introduce a second full JSON Schema audit, reparsing or revalidation of already validated trees during merging.

Source and object duplicates follow existing normalization and identity rules. Object ID validation applies within one database and respects `identity`, `idField` and `rootTypes` in the existing registry; anonymous definitions and fragments do not receive invented unique IDs. Identical ID strings in different dataset kinds are not inherently conflicts.

Merge information about the same physical source by source identity. Different hashes for that source in job results indicate changed inputs. Do not sum shared-definition counts or repeat initial library warnings per document or worker. Deduplication must not remove separate identical warnings from distinct actual calls.

## 7. Intermediate files and merging

Within the operation subdirectory, separate results by dataset kind and stable document number. Workers never write concurrently to one file. Incomplete writes are distinguishable from completed results; the coordinator accepts only validated, fully written documents.

Each file contains one serialized document with line breaks and Unicode. Prepare indentation for insertion into the final `documents` array, avoiding reserialization during merging. Final JSON retains the current two spaces per indentation level, key order and LF line endings.

After all jobs for the current database succeed, the coordinator:

1. Checks result completeness and cross-document constraints.
2. Creates a temporary final database.
3. Streams documents in `document_index` order, adding container framing, separators and metadata.
4. Verifies each intermediate file's size and byte SHA-256 during the same copy.
5. Releases that database's intermediate documents after successful merging.

Completion order does not affect document position. The coordinator never retains the complete set in memory. Measure intermediate JSON writing and copying separately as costs of the chosen result-transfer mechanism.

The aggregate `set_id` becomes available after all members are prepared. Adding it to staged databases remains a streaming operation; account separately for additional metadata-copying time. Optimizing this copy must not introduce another JSON parse.

## 8. Document and set identity

Let `C(value)` denote the existing canonical JSON serialization: sorted keys, `ensure_ascii=False`, `,` and `:` separators, no whitespace or line breaks, NaN/Infinity rejected, UTF-8 bytes. Let `H(bytes)` denote SHA-256 expressed as a lowercase hexadecimal string.

For each document, the worker computes:

```text
document_hash = H(C(document))
```

The document includes its complete tree, source, history and localization. Do not omit fields to accelerate hashing. Do not persist canonical JSON as a second full file; it serves hashing only. Separately calculate `shard_hash` over the actual formatted bytes written to verify copying.

The coordinator computes database `content_hash` as `H(C(payload))`, where `payload` has exactly this structure:

```json
{
  "identity_algorithm": "sttv.document_hashes.v1",
  "format": "sttv.parse_database",
  "format_version": 6,
  "documents": [
    { "index": 0, "content_hash": "<document_hash>" }
  ]
}
```

The list includes exactly all documents in established order. Each entry uses its `document_index`; reject gaps and repetitions before calculation. The algorithm is a versioned technical contract, not a user-configurable hash-function choice.

Set `set_id` remains the canonical SHA-256 of the `kind → content_hash` mapping for all fifteen members. The revised `content_hash` definition changes its value relative to stage 14. Exclude `dataset.set_id` from document hashes and `payload`, avoiding circular dependency.

Library mode, worker count, PIDs, scheduling, temporary paths, durations and formatted JSON sizes do not enter content identity. Identical inputs produce identical values and output bytes for `workers=1` and `workers=10`, and for `rebuild` and `reuse`.

Record the identity algorithm version and hashes in reports. Do not add parallel-processing service fields to version `6` game documents. The frontend continues to compare member `set_id` values; it need not recalculate identity when opening a set.

## 9. Failures and publication

A job failure, worker crash, damaged intermediate file, duplicate/missing result or source change fails the build. Do not treat a partial database as complete, omit a failed document or silently retry through a sequential fallback.

After a fatal failure, stop issuing new work, finish or stop running jobs, collect available diagnostics and release owned temporary resources. Distinguish completed, failed, cancelled and not-started jobs. An absent response following a worker crash must not cause an indefinite wait.

Cleanup is restricted to the verified operation subdirectory within the configured staging directory. Never remove the shared `WORK_DIR`, persisted libraries, final databases or another operation's results. Leftovers from forced termination are not reused by a subsequent build; report their locations when diagnostics remain available.

Before publishing a set, all fifteen databases must be ready, workers must be stopped and final source/inventory checks must pass. Published databases remain unchanged until then. The coordinator retains library-directory ownership until workers finish using the libraries.

Replacing fifteen files remains a sequence of individual replacements, not a filesystem transaction. On failure during publication itself, report exactly which members were replaced; a mixed set is detected through its shared `set_id`. A new transaction or rollback system is outside this stage.

## 10. Diagnostics and measurements

Retain existing build, localization, set and library reports, extending them with necessary parallel-processing and identity-version information. The coordinator writes reports; children return records and measurements without overwriting shared report files.

Document errors preserve dataset kind, source, `document_index`, stage, cause code, coordinates/node pointer and expansion chain when available. A service process identifier is allowed in diagnostics but never affects game-data sorting. Order final document records by job identity rather than response arrival time.

Measure:

- configured and actually used process counts, job counts and statuses;
- wall-clock operation and database times, library and pool preparation, worker library/localization loading;
- per-document reading/expansion/serialization, localization, validation, hashing and intermediate writing;
- cross-document checks, merging, set-metadata insertion, source verification and publication;
- physical library loads, rule preparations, source reads, plan uses and intermediate/final file volumes;
- coordinator peak memory and aggregate process-tree consumption, measurement method and maximum temporary storage.

Do not label summed job durations as build wall time: intervals overlap. Likewise, the sum of individual memory peaks is not a simultaneously observed peak. State limitations if exact measurement is unavailable. Increased memory use is accepted; no silent automatic reduction in worker count is needed.

Aggregate statistics according to meaning: processing events sum, depth takes the maximum, source/shared-definition sets unite, and one-time preparation is not multiplied by consumer count.

## 11. Tests and acceptance criteria

| Area | Required scenarios |
| --- | --- |
| Settings | `1`, `10`, more workers than files; invalid values; staging relocation; path overlaps |
| Windows | Fresh-process invocation, no recursive CLI/pool startup, worker shutdown after success and failure |
| Scheduling | Empty selection under existing rules, one file, more files than workers, deliberately varied completion order |
| Independence | Repeated jobs in one worker, different local variables and arguments, nested calls of all supported kinds; unchanged libraries |
| Addresses | Expansion history and `inherited_from` in a document with a nonzero index, identical local call IDs in different documents |
| Localization | Existing RU/EN priorities, inheritance, conflicts, missing texts, no selected-key statistics leaking between jobs |
| Global checks | Duplicate sources, duplicate IDs within/across documents, anonymous objects, missing/duplicate/foreign results |
| Files | Truncated or modified completed JSON, write/copy errors, safe cleanup of owned intermediate files |
| Failures | Job exception, initialization failure, worker crash, cancellation, source and inventory changes during processing |
| Identity | Identical results across schedules and worker counts; document changes alter hashes; service metrics do not |
| Integration | Fifteen-database set, standalone build, both library modes, existing analytics and frontend set opening |

Preserve a stage 14 reference on fixed inputs before changing the mechanism. Compare whole documents against the previous result: values, order, provenance, history and localization. The allowed database difference is the new `dataset.set_id`; equal node counts alone are insufficient. Compare game diagnostics and logical counters as well, treating new process metrics separately.

Run a complete new fifteen-database build with `workers=1` and `reuse`, then with `workers=10` and `reuse` on the same inputs. Separately verify the complete set with `workers=10` and `rebuild`. All three sets must be byte-identical with identical `content_hash`/`set_id` values. Do not overlap measurements with other acceptance builds, heavy tests or frontend reads of the complete set.

On a fixed representative sample containing different file sizes, run at least three measurements each for `1` and `10`, comparing medians. Show worker initialization, validation, writing and merging costs separately; state disk-cache conditions to the extent controlled. Earlier stage 14 timings are historical context, not the sole proof of improvement.

If performance does not improve or regresses, investigate whether a single large file, library loading, disk throughput, merging or another measured stage limits runtime. Do not declare success solely from CPU utilization; changing the agreed algorithm beyond this specification requires a separate decision.

Run backend and frontend-adapter checks relevant to the change. Reference comparison and full result audits are acceptance activities, not requirements for every ordinary product run. Save verification materials under `WORK_DIR/stage15/`. Launching the game is unnecessary; game files remain unchanged.

## 12. Implementation structure and documents

Proposed module group: `src/backend/sttv/parallel/`, covering settings, job/result models, process initialization, job execution, pool management and report aggregation. Document writing/merging and identity calculation remain alongside `database/`; set publication remains in `database_sets/`.

Use existing parsing, expansion, localization and validation through shared functions. Do not copy their implementations into a separate parallel engine. Separate persisted tables/plans from job state and expose worker library loading without duplicating the user-facing ownership operation.

Update the schema generator, configurations, affected settings/report schemas, entry points and tests. Follow shared module-size and DRY requirements. Frontend and library format changes require demonstrated necessity within the agreed contract; additional changes must be agreed first.

After approval: reference cases and measurements → configuration and job protocol → pool lifecycle → document processing/validation → intermediate files and hashes → merging and publication → acceptance → bilingual guide, README and changelog.

- [Shared project principles](TZ_EN.md).
- [Stage 13: validation optimization](TZ_BACKEND_STAGE_13_EN.md) and [results](BACKEND_STAGE_13_EN.md).
- [Stage 14: libraries](TZ_BACKEND_STAGE_14_EN.md) and [implementation](BACKEND_STAGE_14_EN.md).
- [Fifteen-database set](TZ_BACKEND_STAGE_12_EN.md).
- [Русская версия](TZ_BACKEND_STAGE_15_RU.md).
