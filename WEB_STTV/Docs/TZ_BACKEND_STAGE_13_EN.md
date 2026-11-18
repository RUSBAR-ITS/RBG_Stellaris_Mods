# WEB_STTV — backend stage 13: validation and build optimization

## Contents

- [1. Status and goal](#1-status-and-goal)
- [2. Starting point](#2-starting-point)
- [3. Scope](#3-scope)
- [4. Rules and direct validation dispatch](#4-rules-and-direct-validation-dispatch)
- [5. Shared traversal and contextual checks](#5-shared-traversal-and-contextual-checks)
- [6. Document processing](#6-document-processing)
- [7. Writing, hashes and publication](#7-writing-hashes-and-publication)
- [8. Measurements and diagnostics](#8-measurements-and-diagnostics)
- [9. Modules and implementation sequence](#9-modules-and-implementation-sequence)
- [10. Tests and acceptance](#10-tests-and-acceptance)
- [11. Related documents](#11-related-documents)

## 1. Status and goal

**Approved by the user, implemented and verified on 2026-11-18.** This stage covers the first four optimization proposals: direct node-type dispatch, preparing rules once, a shared traversal, and document processing. Removing repeated full validation and adding measurements are included. MongoDB and parallel execution are deferred. Results are recorded in the [stage 13 guide](BACKEND_STAGE_13_EN.md).

The goal is to reduce mandatory build validation time and memory consumption while retaining the checks and database contents. Complete validation of each finished document remains part of normal builds; the earlier proposal to move the entire audit to a separate operation is not adopted here.

This specification supersedes earlier requirements to accumulate the entire result in memory and repeat full validation after writing. Other stage 12 requirements remain effective.

## 2. Starting point

The [stage 12 acceptance summary](../data/stage12/build_acceptance.json) records 15 databases, 450 documents, 11,762,739,507 bytes and 5490.835 seconds for the full build. Preparing `events` took 4047.299 seconds; its result contains 3,495,153 syntax nodes and occupies 9,386,721,787 bytes. Member preparation time includes all preparation operations, rather than measuring parsing or validation alone.

Process observations identified prolonged execution in the general JSON Schema validator. Exact historical timings for every operation are unavailable; these figures are a baseline reference, not a promise of a particular speedup.

Implementation before stage 13:

- `common/schema.py` rereads and checks a schema when creating a validator; nodes are selected through `allOf/if`, and some values through `anyOf` alternatives.
- `database/validation.py` runs structural validation, followed by separate history and enrichment traversals.
- `common/persistence.py` checks the object before writing, then reads the entire JSON and checks it again.
- `database_sets/member.py` accumulates all documents through `collect()` before selecting and localizing objects throughout the database.
- The single-database builder also repeats validation between `builder.py` and `database/storage.py`.

## 3. Scope

Scope includes the four agreed directions, removing repeated validation of unchanged results, necessary coordinator, writer, counter and report changes, and equivalence and performance tests.

Mandatory paths are the fifteen-database set build and the single-database build. Existing database readers and standalone localization use the shared new validator. Streaming existing JSON input for those separate operations is outside this stage: optimization primarily targets constructing documents from source files. Checking input before modification and checking the modified result concern different data states and must not automatically be treated as duplicates.

Preserve database format `sttv.parse_database` version `6`, all game nodes and metadata, document and item order, provenance, expansion history, localization, import exceptions and `set_id` rules. For identical inputs, new database files must match the previous files byte for byte. This is an optimization equivalence criterion, not a compatibility layer for older formats.

Excluded: grammar or game-semantics changes, a game-command allowlist, new exceptions, data removal, compression, frontend layout changes, new database engines, containers, multiprocessing, caching build results between runs, and a general compiler for arbitrary JSON Schema documents.

## 4. Rules and direct validation dispatch

The single structural rule source is the existing definition in `schema_generation/`, which produces `database.schema.json`. Use one snapshot of the active schema per operation. Prepare specialized validation functions in memory from that snapshot; do not maintain a second handwritten list of fields and constraints. A separate generated Python file and a user configuration for switching validators are unnecessary.

Check the schema itself and prepare its rules once per build operation, including the entire fifteen-database set. Resolve local references ahead of time and prepare regular expressions and dispatch tables. Recursive references link prepared validators rather than expanding indefinitely. A new operation obtains current rules again; a global cache must not hide schema changes.

For a syntax node, check the presence and validity of `kind`, then select the single applicable validator. Current kinds are `scalar`, `formula`, `block`, `tagged_block`, `conditional`, `assignment`, `logical_operation`, `script_value`, and `scripted_trigger_test`. Derive the list and permitted child types from the contract. Use direct dispatch for unions with distinguishable types as well; evaluate remaining small unions according to their existing rules.

Retain required properties, types, nullability, constants and enums, string and numeric constraints, rejection of additional service properties, array and uniqueness constraints, and expansion-history conditions. Branch selection must not skip common constraints. Numeric and boolean values follow the active schema semantics rather than incidental Python type behavior.

Preparation supports constructs used by the current database contract. An unsupported schema constraint produces a clear preparation error before publication; silently ignoring it or falling back to an expensive general traversal is prohibited. Game command and field names inside `key.text` remain unrestricted strings.

The general JSON Schema validator remains the structural equivalence oracle in tests. Normal builds may use it for small configurations and reports, preparing each schema once, but must not run it again over the complete database tree.

## 5. Shared traversal and contextual checks

One validation coordinator traverses the finished document's syntax nodes and invokes small structure, provenance and enrichment handlers. A child must not be recursively validated both inside its parent handler and again by the shared traversal. Service structures are checked by their respective handlers and are not counted as additional game nodes.

Prepare an expansion-record index within the document context, then collect necessary node and container addresses during traversal. Finish references to nodes not yet encountered through those indexes. Traversing reference tables is allowed; another complete tree walk solely to discover localization or provenance is unnecessary.

Retain these checks:

- unique expansion IDs within a document, existing parents and absence of cycles;
- existing provenance `expansion_id` values, including nested fragments and call sites;
- valid insertion addresses and ranges, membership of inserted nodes in their invocation, and specific `script_value` rules;
- valid RU/EN localization roles, missing and found text states, description inheritance and `component_set` references;
- database container format, valid dataset metadata and absence of repeated source documents.

Keep the existing duplicate game-ID check in object selection separate from the structural contract: its scope is the entire corresponding database, including different source documents. Stage 12 rules for anonymous transitions, `on_actions` fragments and event IDs remain unchanged.

Errors must identify the check, source and offending field/node address; preserve existing codes when the cause is unchanged. Exact internal library messages and the discovery order of multiple simultaneous errors need not match. Do not introduce new game-logic checks.

## 6. Document processing

The processing unit is one source document from the `documents` array, not an individual technology or an entire database file.

Sequence: prepare rules and shared sources → read and parse each source document with expansions → substitute static variables → serialize → select and localize targets → validate the finished document → write it into temporary JSON and incorporate it into the hash → release tree references → continue with the next document.

Pass the actual document ordinal. `/documents/N/...` addresses, `inherited_from`, description references and service addresses must not restart at zero for each document. Do not reset expansion state that affects reproducible identifiers. Object, target and localization counters accumulate instead of being replaced by the last document's results.

Between documents, shared settings, template libraries, the localization index and compact ID/source/diagnostic indexes may be retained. The duplicate index stores an identifier and its first location without retaining the full tree. Localization targets and validation contexts are released after their document. The number of retained completed source trees must not grow with the processed file count; temporary coexistence of one document's AST and serialized representation is allowed.

Localization priorities and reference expansion rules remain unchanged. A finished validated document is not subsequently mutated. If an additional step does modify it, validate the result of that modification before writing.

Parsing, expansion, localization and validation failures continue to be recorded. Do not publish a partial result as complete. On a late failure, previously staged documents must not become the active database.

## 7. Writing, hashes and publication

Write one valid JSON container with documents added sequentially; do not introduce JSON Lines. Preserve UTF-8 without BOM, readable Unicode, LF, two-space indentation, key order and the final newline. Serialization continues to reject non-finite JSON constants and encoding failures.

Do not invoke a second `validate_database()` on a prepared result or read the entire temporary file through `read_json()` after writing. A successful check cannot be reused for a different or modified document. Small configurations and reports do not require a new streaming format.

Calculate the member's canonical hash incrementally from the same logical sequence previously processed by `canonical_hash(database)` before adding `dataset`. Preserve sorted keys, compact canonical representation, Unicode rules and data membership. A document hash does not replace the database hash; concatenating document hashes would introduce a different algorithm and is prohibited. `set_id` continues to depend on all member hashes.

Adding `dataset.set_id` after preparing the set may use the existing sequential byte copy with an inserted header. This is not another tree parse or audit. Optimizing this extra copy is not mandatory in this stage. Validate header metadata separately.

Preserve input immutability verification, completion and closing of temporary files, `flush`/`fsync`, write-error handling, temporary-output cleanup and target replacement. The previous published set remains untouched until all members are prepared. Individual file replacement is atomic; do not describe the entire set as one atomic transaction. A failure between replacements is recorded and detected by the frontend through differing `set_id` values.

Rereading and independently auditing output remain acceptance tests for the serializer and build. They do not run automatically after every normal build and are excluded from its measured duration.

## 8. Measurements and diagnostics

Report time spent preparing rules and sources, reading/parsing/expanding/serializing, localizing, validating, canonical hashing, writing, verifying inputs and publishing. Related operations may share a clearly named interval; nested intervals must not be summed as independent work. Do not introduce artificial full passes solely to time parts of the new shared validator.

For each member and document, record the source, node count, validation outcome and duration; include member size and total duration. Separately count rule preparations and final document validations. A successful document in a normal build is validated once after enrichment is complete.

Update the corresponding report schemas. Do not put timing and memory measurements in the database, include them in canonical hashes, or mix them with game data. Peak-memory measurement is required during acceptance, without requiring a permanent heavyweight product profiler; state the measurement method.

Store stage artifacts in `WORK_DIR/stage13/` (default: `WEB_STTV/data/stage13/`). Compare identical documents, inputs, configurations and environments. Do not promise a specific speedup in advance. Removing a repeated check reduces validation count, not necessarily total build time by half.

## 9. Modules and implementation sequence

1. Record control results and baseline validation measurements on selected documents before replacing the old implementation.
2. Implement prepared rules and `kind` dispatch; verify structural equivalence.
3. Combine traversal and contextual checks while retaining separate handlers.
4. Convert builders, localization selection and writing to document processing; remove repeated checks of unchanged results.
5. Complete acceptance and update RU/EN guides, README and changelog.

Affected areas include `common/schema.py`, `database/`, `database_sets/`, shared localization selection and attachment, schema generation and tests. Separate structural preparation, traversal, reference checks and streaming writing by responsibility. Follow DRY and the shared specification's file-size limits. Reuse existing source and localization settings; do not introduce dependencies or user modes without necessity.

## 10. Tests and acceptance

| Area | Required outcome |
| --- | --- |
| Structural contract | The fast validator and JSON Schema oracle agree on valid and corrupted examples of all nine kinds; cover nested rules, unions, conditions, extra/missing properties, numbers, nulls, strings and arrays |
| Preparation | One rule snapshot per operation; a new operation sees schema changes; unsupported constraints and invalid schemas are not silently bypassed |
| Context | Parent, cycle, provenance, insertion, inheritance and localization errors retain diagnostics; cover forward references and invalid addresses |
| Documents | Addresses and order are preserved; cross-document duplicate IDs are detected; counters accumulate; completed trees are not retained |
| Persistence | No full reread/audit in normal builds; formatting and canonical hashes match the prior result |
| Failures | Late document errors, write failures, changed inputs and interrupted publication cannot produce false success; existing results are preserved before publication |
| Integration | Single and fifteen-database builds share the mechanism; standalone enrichment rejects damaged input and validates its changed result |

On a fixed selection of typical and large documents from technologies, components and events, perform comparable old/new validation measurements. Record sources, hashes, node counts, environment, outcomes and at least three measurements per implementation; compare medians and state whether rule preparation is included. Optimized validation must be faster on large examples; absence of improvement requires investigation rather than declaring successful optimization.

Run one complete fifteen-database build with the new measurements. Compare published files byte for byte using streaming hashes against the saved stage 12 result when inputs match. If sources changed, do not present historical timings and hashes as a controlled comparison: record the difference and compare implementations on the same selection. Successful checks, no lost documents or data, and a peak-memory report are mandatory. Another full 91-minute legacy build is unnecessary when an unchanged control result is available.

Independently read new outputs and check containers and addresses without loading the entire set into memory. Apply the JSON Schema oracle to control documents and negative tests; a second complete reference audit of the entire set is not required for every build. Run existing frontend adapter checks and open the full set once in the browser. The database remains compatible with the current frontend without changing its behavior.

The acceptance report must distinguish measured validation speedup, full build duration and separate acceptance costs. Do not claim success from a procedural change without confirmed acceleration. Game files remain unchanged; launching Stellaris is unnecessary for this stage.

## 11. Related documents

- [Shared project principles](TZ_EN.md).
- [Stage 12 specification](TZ_BACKEND_STAGE_12_EN.md) and [results](BACKEND_STAGE_12_EN.md).
- [Transition to a database of parsing results](TZ_BACKEND_STAGE_6_EN.md).
- [Opening fifteen databases in the frontend](frontend/TZ_FRONTEND_STAGE_3_EN.md).
- [Русская версия](TZ_BACKEND_STAGE_13_RU.md).
