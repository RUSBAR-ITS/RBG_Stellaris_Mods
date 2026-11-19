# Stage 17 — using manifests and separate documents

## Contents

- [Format and configuration](#format-and-configuration)
- [Running](#running)
- [Reading and publication](#reading-and-publication)
- [Verification and measurements](#verification-and-measurements)
- [Boundaries](#boundaries)

## Format and configuration

Implemented [backend stage 17](TZ_BACKEND_STAGE_17_EN.md) and [frontend directory opening](frontend/FRONTEND_STAGE_4_EN.md). Each source file becomes one `sttv.parse_document` JSON, version 1. The `sttv.database_manifest` version 1 manifest contains all 15 kinds, file descriptors, object indexes and shared tree combination metadata. Monolithic merging has been removed.

`config/storage.json` defines the set, manifest, document, staging and audit report locations; builders and enrichments reference it. Worker count comes from `config/parallel.json`. The default root is `WORK_DIR/database_set`. The builder supplies actual document and object inventories.

A version is stored at `documents/<database>/<document_id>/<file_hash>.json`. `file_hash` is SHA-256 of written bytes; `source_hash` excludes only root `technology_tree` enrichment. `set_id` depends on source revisions and the registry; `snapshot_revision` identifies the current manifest contents. Node references are `{database, document_id, pointer}`, with `/items/` pointers. All `on_actions` fragments are retained; anonymous `terraform` objects have `id: null`.

The generator produces 32 schemas, including `storage`, `database_manifest`, `database_document` and `storage_report`. `database.schema.json` describes a standalone document. Configuration, localization and expansion history share the AST contract.

## Running

From `WEB_STTV`, with Python dependencies installed:

```powershell
$env:PYTHONPATH="src/backend"
python -B -m sttv.database_sets --reuse-libraries
python -B -m sttv.enrichment.technology_tree
python -B -m sttv.enrichment.technology_tree --recalculate
python -B -m sttv.storage audit --manifest data/database_set/manifest.json --report data/reports/storage_audit.json
```

`--reuse-libraries` requires current libraries; use `--rebuild-libraries` to prepare them explicitly. Tree enrichment reads a ready set without accessing the game. `src/backend/main.py` remains a standalone technology builder, publishing the new manifest with other kinds empty; use `sttv.database_sets` for a full set.

This iteration's full acceptance set is `data/stage17/database_set`. Its isolated settings are `data/stage17/backend.json`, `storage.json` and `tree.json`. Pass `--config data/stage17/tree.json` for tree enrichment and its manifest path for auditing. The old reference files under `data/databases` remain unchanged.

Standalone localization refresh uses the same manifest transaction; the Python function `enrich_localization(..., kind='technologies')` selects a kind. Localization sources and priorities remain configurable. Changed localization updates source revisions, invalidating the previous tree calculation until its next invocation.

## Reading and publication

`sttv.storage.open_set(manifest_path)` pins a snapshot. It exposes `iter_objects`, `resolve_object`, `read_document`, `iter_documents` and streaming projections. ID lookup uses the manifest; checking declared paths does not read file contents. Requested files are parsed and hashed in one pass. `coverage()` distinguishes verified and unread documents.

Tree calculations extract compact evidence in bounded processes and select event documents through indexed requested IDs. Parent selection runs globally after evidence preparation. Reuse checks technology documents and manifest revisions without rebuilding functional indexes.

Publication locks the set root, prepares immutable versions, then atomically replaces only the manifest. Failures before switching preserve the old set. Existing readers can retain old versions; snapshot changes are detected before publishing. Report failure after switching does not hide successful publication.

## Verification and measurements

Working artifacts are under `data/stage17/`:

| Check | Result |
| --- | --- |
| Full build, 10 workers, prepared libraries | 450 documents, 15 kinds, 387.885 s |
| Previous database comparison | All 450 documents match after envelope/reference normalization; AST, history and localization preserved |
| Base combination | All 679 decisions match; 178 roots, 501 parents, no ambiguities |
| Variants | 206 individual variants and 3 combined selections; persistence and reuse of two combinations |
| First calculation with publication | 41.126 s |
| Later forced calculation with unchanged results | 22.384 s; indexes 19.046 s; criteria 0.0025 s |
| Combination reuse | 3.697 s, 35 verified documents, 415 unread |
| Full audit | 450/450, 125.764 s, no errors |

The forced calculation read 2,840,258,013 bytes, including 639,267,104 event bytes; the audit read 11,049,350,511 bytes. Hashing shares the reading pass. These are individual measurements on this computer without clearing the OS file cache; forced recalculation and first publication perform different work.

The complete backend suite passed **all 269 tests**. Synthetic checks cover one/ten worker determinism, used/unused corruption, indexes and paths, reciprocal relationships, variants, locking, failed switching, old readers and report failure. Acceptance artifacts: `source_comparison.json`, `acceptance/acceptance.json`, `storage_audit.json`; test logs are saved nearby.

An additional forced calculation with memory monitoring took 33.244 s: sampled peak coordinator working set was 530,329,600 bytes, with 1,191,682,048 bytes for the process tree. Sampling ran once per second without collection errors; these are observed maxima, not guaranteed memory limits. Results were unchanged and no documents needed writing in this run; see `technology_tree_report.json`.

## Boundaries

The product does not read old monolithic sets. Incremental game-source rebuilding, MongoDB, the new grid and HTTP APIs are excluded. Old versions and files left before failed switching are not automatically deleted. Unread documents are never declared verified; use the audit for complete coverage.

[Русская версия](BACKEND_STAGE_17_RU.md) · [Specification index](TZ_EN.md).
