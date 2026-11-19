# Stage 17 — manifest and separate database documents

## Contents

- [1. Status and purpose](#1-status-and-purpose)
- [2. Scope](#2-scope)
- [3. Configuration and layout](#3-configuration-and-layout)
- [4. Documents and references](#4-documents-and-references)
- [5. Manifest and object index](#5-manifest-and-object-index)
- [6. Identity and revisions](#6-identity-and-revisions)
- [7. Preparing a set](#7-preparing-a-set)
- [8. Reading and verification](#8-reading-and-verification)
- [9. Tree enrichment](#9-tree-enrichment)
- [10. Publishing changes](#10-publishing-changes)
- [11. Modules and interfaces](#11-modules-and-interfaces)
- [12. Reports and measurements](#12-reports-and-measurements)
- [13. Tests and acceptance](#13-tests-and-acceptance)

## 1. Status and purpose

**Approved by the user on 2026-11-19 and implemented.** Completed verification, running and limitations are documented in [the stage guide](BACKEND_STAGE_17_EN.md).

Keep the processing result of each source file separately; locate objects through a manifest without scanning all large databases. Use file parallelism for building and preparing evidence. The new storage format does not change game data or predecessor criteria.

This builds on [stage 15](TZ_BACKEND_STAGE_15_EN.md) and [stage 16](TZ_BACKEND_STAGE_16_EN.md). The first full stage 16 calculation spent about 262 of 279 seconds preparing indexes and about 0.004 seconds selecting parents: this identifies the existing bottleneck, not a promised speedup. The coordinated UI work is specified in [frontend stage 4](frontend/TZ_FRONTEND_STAGE_4_EN.md).

## 2. Scope

Includes the storage format for all 15 database kinds, manifest, object index, shared reader, adaptation of localized builds and tree enrichment, safe publication, audit, schemas and tests. The frontend opens a directory and reads required documents under its separate specification.

Excludes MongoDB, the grid and `location`, changes to criteria/profiles/variant semantics, HTTP API, automatic build invocation, persistent functional projection caches and incremental reparsing of modified game sources. The latter requires separate dependency tracking for insertions, static variables and localization. Rewriting only modified documents during enrichment is included.

The product switches formats without supporting the old 15 monolithic JSON files or requiring their export. Old sets remain unchanged as test references; a legacy converter is not a separate product feature. The insertion library and its explicit operating modes are retained.

## 3. Configuration and layout

The manually maintained `config/storage.json` specifies the set location relative to `WORK_DIR`, manifest name, document subdirectory, operation staging directory, reference to `config/parallel.json`, and audit report path. Source settings and object-kind definitions remain in `config/backend.json` and `config/datasets.json`. Actual files and objects are not manually listed in configuration.

Proposed defaults: set directory `database_set`, manifest `manifest.json`, documents `documents`, temporary operations `staging/storage`, report `reports/storage_audit.json`. Worker count comes from the shared configuration: ten by default. Tree enrichment configuration references storage configuration instead of locating 15 output files through build settings.

```text
data/database_set/
  manifest.json
  documents/
    technologies/<document_id>/<file_hash>.json
    components/<document_id>/<file_hash>.json
    events/<document_id>/<file_hash>.json
    ...
```

Manifest paths are relative to its directory and use `/`. Absolute paths, URLs, `..`, filesystem links escaping the set root and paths conflicting after normalization are forbidden. Reading a prepared set requires no game location. JSON remains UTF-8 with two-space indentation, newlines and readable Unicode.

## 4. Documents and references

One selected game file produces one persistent JSON document, potentially containing multiple objects. Format `sttv.parse_document`, version 1 has `format`, `format_version`, `database`, `document_id`, `source`, `items`, `metadata`. The last three preserve the current parser document: all original entries, order, expanded tree, provenance and insertion history. No new whitelist restricts game object fields.

`document_id` is SHA-256 of the canonical triple of database kind, source root and relative source path. Path identity uses `/` and Windows case-insensitive comparison; preserve original spelling in `source.file`. Two inputs with the same normalized triple are an error. The ID does not depend on worker number, completion order, content or working-directory location.

A node reference becomes `NodeRef = {database, document_id, pointer}`, with a document-relative JSON Pointer such as `/items/7`. A game-ID reference is `ObjectRef = {database, id}`. Game identifiers retain their original case. Positional references resolve only within the selected set revision; editing a source may change entry positions.

Remove persisted references' dependency on global `/documents/N`: adapt localization inheritance, diagnostics, evidence and frontend references. Only structured service fields change, never similar text within the game AST. Local `/items/...` insertion-history addresses and `expansion_id` relationships remain. The new format does not require renumbering existing insertion calls.

Technology variants remain nested in the base technology. `enrichments.localization` and `enrichments.technology_tree[combination_id]` remain on nodes. Shared combination metadata moves from the monolithic database root to manifest `technology_tree`; it is not duplicated into every document.

## 5. Manifest and object index

Generate the manifest from actual prepared and verified results. It may be loaded entirely in memory; it contains neither full ASTs nor localized texts. The initial format uses one manifest without separate index files per kind.

| Field | Contents |
| --- | --- |
| `format`, `format_version` | `sttv.database_manifest`, version 1 |
| `set_id` | Revision of source set content excluding tree enrichment |
| `snapshot_revision` | Revision of the current published state including enrichments |
| `registry_revision` | Hash of object identity rules in the kind registry |
| `datasets` | All 15 kinds, each with `source_revision`, `documents` and `objects` |
| `technology_tree` | Optional shared metadata for stage 16 named combinations |

A document descriptor contains `document_id`, `source`, `path`, `byte_size`, `file_hash`, `source_hash`, `item_count`. An object index row contains `id` (string or `null`), `type`, `document_id`, `pointer`. Its enclosing `datasets` section determines the database kind. All references address declared documents. Index the expanded tree rather than searching source text.

Root object selection and ID extraction follow existing `config/datasets.json`. Non-indexable service entries remain in documents. Subdirectories of `common/technology` do not automatically become displayed technologies: retain existing target-selection rules.

- `identity = key` and `field`: a duplicate ID within a kind is an error reporting both references.
- `identity = fragments`: one ID, such as an `on_actions` handler, resolves to an ordered list of all fragments; silently selecting the first is forbidden.
- `identity = anonymous`: `terraform_link` retains `id = null`; identity is its `NodeRef`, not a fabricated game ID.
- Identical IDs in different kinds are allowed. `technology_swap` is not a separate indexed root object.

Order documents by normalized source path and objects by document and entry position. Process completion order does not affect publication order. Build the compact ID lookup from the manifest without reading data files.

## 6. Identity and revisions

`file_hash` is SHA-256 of exact written bytes, computed during writing and used in the versioned filename. The file does not contain its own hash. Formatting changes alter this hash.

`source_hash` canonically hashes document content excluding only service `enrichments.technology_tree` and an `enrichments` container emptied specifically by that exclusion. AST, entry order, localization and history remain. Include the service format envelope and document ID under fixed algorithm `sttv.document_source.v1`. Do not automatically exclude other enrichments.

A kind's `source_revision` hashes ordered `document_id`/`source_hash` pairs. `set_id` hashes the algorithm version, `registry_revision` and ordered revisions of all kinds. Tree enrichment preserves `set_id`; localization or game-data changes alter it. `snapshot_revision` hashes the entire manifest except itself, including paths, file hashes, index and combination metadata. Runtime metrics and absolute paths are excluded from the manifest.

Canonicalization follows existing Python rules: sorted keys, UTF-8, compact separators, and rejection of NaN/Infinity. The browser verifies exact document byte hashes; it need not reproduce every Python semantic hash.

Stage 16 calculation revisions use manifest source-content revisions and actual rule/parameter/implementation configurations. Initially include all 15 `source_revision` values conservatively: a new witness must invalidate a result even if the previous calculation did not read it. Do not narrow freshness to hashes of previously discovered objects alone. Enrichment must not invalidate itself.

## 7. Preparing a set

Retain parallel per-file jobs within one kind and sequential kind processing from stage 15. Each worker parses its source, expands insertions and variables, applies RU/EN localization, structurally validates and writes its document. The same process gathers index rows and hashes. The coordinator receives compact descriptors and diagnostics, not complete trees.

The coordinator verifies job completeness, identities and index references, then prepares the manifest. Remove mandatory monolithic merging and full-array copying to insert a header. Do not replace stage 13 checks with another complete JSON Schema AST traversal.

Full builds retain explicit `--rebuild-libraries` and `--reuse-libraries`; opening prepared data invokes neither. Temporary-fragment cleanup must not delete persistent documents. The initial manifest contains no calculated tree combinations; a separate operation adds them.

## 8. Reading and verification

The shared reader opens the manifest once and checks its contract, kinds, references, address uniqueness and existence of declared files. It supports listing objects, resolving `ObjectRef`, reading one document and iterating a selected kind. Listing the index and checking file existence do not read file contents.

**The agreed default is verification on read.** Verify every used file's size and SHA-256 in the same stream used for extraction. Also check its envelope, source, ID and indexed root entries. Its results cannot be published or shown as a ready field until verification completes. Repeated access within an operation reuses verified compact projections; full ASTs are not retained unnecessarily.

Looking up an event ID opens only its containing document. A JSON Pointer is not a byte offset: the whole document is still streamed for hashing and node extraction. A large document must not become one huge string; projections may discard irrelevant nodes and history. Other event documents are not opened.

Hashing detects inconsistent or damaged writes; digital signatures and protection against deliberate replacement of an entire set are excluded. Size and modification time do not replace hashes. Unread files remain `not_checked` even when the manifest is valid. This mode trusts the published catalog for unused files and does not promise to detect their external modification.

A separate audit visits every declared file, checking byte hashes, envelopes and index/object correspondence and reporting full coverage. It neither rebuilds the database nor interprets game commands. A successful own build already covers every new document through its checks; subsequent opening does not repeat those checks for unused files.

## 9. Tree enrichment

The stage 16 operation reads technologies and shared metadata through the set reader. For a new calculation, compact evidence from other kinds is extracted per document using a bounded pool from shared configuration. Combine results deterministically; do not transmit the complete AST set between processes. Events are extracted only along agreed routes and IDs using the manifest index.

After preparing shared indexes, run the existing global predecessor algorithm. Do not calculate independent trees per file: a parent and child may occupy different documents. Retain all 13 criteria, stopping at one candidate, skipping empty results, combinations and variant handling.

Reuse compares manifest source revisions, configurations and saved results; it reads and verifies technology documents without building functional indexes. The report explicitly states that other documents were not hashed in that invocation. Forced recalculation remains available.

Validate new results for reciprocal `parent_tech`/`children`, completeness, cycles and original prerequisite membership. Update only documents with changed records, including removal of obsolete records for the chosen combination. Preserve other combinations and localization. The manifest publishes a combination's changes together; identical documents are not rewritten.

## 10. Publishing changes

Published document versions are immutable. Prepare writes in a staging directory on the same filesystem, validate them and move them to final `file_hash` addresses. If an address already exists, verify its content before reuse. Documents do not receive a changing common `set_id` in their envelopes; set identity belongs to the manifest.

The sole set-switching point is atomic replacement of `manifest.json` after every required document is ready. All writing operations lock the set root. Before replacement, check the original manifest revision and snapshots of read inputs and configurations; a changed published snapshot causes a conflict without mixing results.

Failure or cancellation before replacement leaves the previous manifest usable. Failure to write a report after replacement does not undo publication and is recorded separately. Readers pin one manifest revision per operation; retain old file versions so an already opened snapshot can still resolve its references.

Automatic removal of old published versions and garbage collection are out of scope. Clean only temporary files owned by the current operation after path-boundary checks. New files left by interruption before publication do not belong to the set unless referenced by its manifest; report them separately from data errors. Archiving a manifest copy for every change is not required.

## 11. Modules and interfaces

Add `sttv.storage` with small modules for configuration, manifest handling, addressing, reading, verification, revisions, publication and reporting. Reuse structural validation and streaming parsing. Object-selection implementations in building and enrichment must follow one registry rather than divergent ID lists.

Proposed interface: `open_set(manifest_path)` returns a pinned-snapshot reader with `iter_objects(kind)`, `resolve_object(kind, id)`, `read_document(kind, document_id)` and `iter_documents(kind)`. `resolve_object` returns all references for a fragment kind; requesting one object must not hide its other fragments. Streaming projection methods must avoid materializing a whole document.

The existing build CLI uses storage configuration. Enrichment retains `--config`, `--combination`, `--recalculate`, with manifest input configured through storage settings. Add `python -m sttv.storage audit --manifest <path> --report <path>`. Operations return reports; no interactive dialogs or HTTP transport are added.

Add generators for `storage.schema.json`, `database_manifest.schema.json`, `database_document.schema.json`, `storage_report.schema.json`; adapt related configuration and enrichment schemas. Share AST and reference definitions. Do not retain the old database-root format as a supported execution path. Update affected tests without deleting historical documentation. Aim for code files under 200 lines; files above 300 require splitting.

## 12. Reports and measurements

Record input/output revisions, selected kinds/documents, and declared, read, verified, unchanged and written file counts; separately identify unchecked documents. Track data/hashing bytes, writes, additional passes, index/selection/validation/publication/audit time and process memory peaks. Do not count one combined reading-and-hashing pass as two physical reads.

Diagnostics include kind, `document_id`, source path, JSON path, expected/actual hash on mismatch, object reference and snapshot revision. Parent ambiguities retain stage 16 context. Missing or corrupt files must not become empty catalogs.

## 13. Tests and acceptance

1. Manifest building: all 15 kinds, several objects per file, nested variants, constants outside the index, anonymous transitions, `on_actions` fragments, duplicate IDs and path-case conflicts. Task order changes must preserve content results.
2. Reference resolution after relocating the set; local addresses, history and inherited localization. Detect root escapes and documents mixed between sources.
3. Verification on read: damage, truncation, changed size and invalid index; unused documents remain unopened. Full audit detects damaged unused files. Equal size and timestamps with different bytes must not imply equality on read.
4. Publication: failures before/after document writing and before manifest replacement, cancellation, concurrent writers, a reader of an older snapshot, report failure after publication. The old set stays readable until switching; partial combinations never become visible.
5. Enrichment: unchanged documents are not written, own enrichment preserves input revision, new evidence or changed configuration invalidates results, localization changes count, and other combinations survive.
6. Parallelism: one and ten workers produce equivalent documents, indexes and decisions; large documents are streamed. Retain library and source-freshness checks.

Build real data under a separate `WORK_DIR/stage17`, preserving the current reference set. Compare documents for all 15 kinds with the existing set after narrowly defined normalization of the new envelope and service references; AST, order, provenance and localization must match. The test normalizer is not a product converter.

Repeat stage 16 calculation: 679 technologies, 178 roots and 501 parents for the current reference; compare every decision and control example. Check all 206 variants with once-prepared indexes, several combinations, saving and reuse. Measure full build, cold calculation, reuse, full audit and frontend opening separately. Show actual event bytes read and the absence of monolithic merging. No specific speedup is guaranteed in advance.

Update bilingual guides, README, specification index and changelog after implementation. Completed verification and measurements are documented in the stage guide.

[Specification index](TZ_EN.md) · [Frontend](frontend/TZ_FRONTEND_STAGE_4_EN.md) · [Русская версия](TZ_BACKEND_STAGE_17_RU.md).
