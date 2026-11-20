# Stellaris Parser — batch game script parsing specification

## Contents

- [Objective](#objective)
- [First step — the library module](#first-step--the-library-module)
- [Commands and configuration](#commands-and-configuration)
- [Library preparation](#library-preparation)
- [Reversible library expansion](#reversible-library-expansion)
- [Directory traversal and JSON output](#directory-traversal-and-json-output)
- [Acceptance checks](#acceptance-checks)
- [Verification results](#verification-results)

## Objective

**Status — implemented.** Stellaris Parser includes the parsing core, the library module and worker process management. The user selects directories and a worker limit. The parser runs both phases.

1. Prepare one library set for the run. In rebuild mode the parser distributes independent library files among workers and combines the definitions. In reuse mode it verifies and loads the saved set.
2. Once the library set is ready, distribute the main files among workers. Before the first task, each worker gets access to the definitions in memory. It uses them to expand objects in all its assigned files and writes one JSON document per source. One in-memory copy of the set per worker is acceptable.

The parser is ready for operational use after an end-to-end check covers both phases in one batch invocation. The single-file command exercises the core and libraries on a selected file.

Single-file and batch parsing use the same document expansion and serialization. Both prepare shared definitions before processing the main files. [Entry points](../stellaris_parser/workspace.py)

## First step — the library module

First move library preparation, storage, verification and loading into the `stellaris_parser.libraries` package. Use the existing WEB_STTV module, including its serialization of definitions, references and prepared template plans. The existing `stellaris_parser.script` code performs parsing. The parser's own roots and rules govern source selection. A standalone parser installation must support this operation without importing `sttv`. [Existing snapshot preparation](../../../WEB_STTV/src/backend/sttv/libraries/snapshot.py) · [Storage and loading](../../../WEB_STTV/src/backend/sttv/libraries/storage.py)

Keep the previous module's five JSON library files and manifest. The default names are `inline_scripts.json`, `scripted_effects.json`, `scripted_triggers.json`, `script_values.json`, `scripted_variables.json` and `manifest.json`. The manifest identifies the set and records versions, source inventory and checksums. The user configuration selects the destination directory. The parser's library configuration specifies the six filenames.

Use single-file `parse` for an intermediate check of the library module. Rebuild from a small fixture with game and mod roots, then load the saved set in a separate invocation. Both runs must produce the same expanded tree and metadata as direct parsing of the same fixture. Also verify diagnostics for a changed source and a missing library JSON.

## Commands and configuration

| Command | Input | Output |
| --- | --- | --- |
| `parse` | `--config`, library mode, one source-root-relative path and an output filename in `--output` | JSON for that source at the exact user-specified path |
| `parse-batch` | `--config`, library mode, one or more source-root-relative directories, an output directory and a worker count | A separate JSON document for each selected source |

The following example assumes that `parser.json` is in the monorepo root. The tool also ships a configuration for the technology directory. [Example configuration](../examples/parser.json)

```json
{
  "roots": ["E:/SteamLibrary/steamapps/common/Stellaris"],
  "library_directory": "TMP/WEB_STTV/run-01/artifacts/libraries",
  "batch": {
    "directories": ["common/technology", "events"],
    "exclude_files": ["common/technology/000_documentation.txt"],
    "output": "TMP/WEB_STTV/run-01/artifacts/scripts",
    "workers": 10
  }
}
```

`library_directory` selects the directory for the five libraries and manifest. A later run can read that directory and write its parsed scripts elsewhere. Filesystem paths in the configuration resolve relative to the configuration file. Entries in `batch.directories` resolve relative to each source root in `roots`.

For `parse-batch`, positional directories, `--output` and `--workers` override the corresponding `batch` values for one run. An explicit directory list replaces the configured list in full. A command-line output path resolves relative to the working directory. The worker count is a positive integer. A value of 1 processes files sequentially. The `batch` settings are optional for `parse`.

Run the following commands from the monorepo root with the configuration shown above.

```powershell
python -m stellaris_parser parse-batch --config parser.json --rebuild-libraries
python -m stellaris_parser parse-batch --config parser.json --reuse-libraries --workers 2 --output TMP/WEB_STTV/run-02/artifacts/scripts common/technology
python -m stellaris_parser parse --config parser.json --reuse-libraries --output TMP/WEB_STTV/run-02/artifacts/physics.json common/technology/00_phys_tech.txt
```

## Library preparation

Both commands require exactly one mode flag. Traversal of the main script directories begins once the libraries have been successfully prepared or verified.

- `--rebuild-libraries` collects definitions from the current sources. After successful preparation it writes the five JSON files and publishes the manifest last.
- `--reuse-libraries` reads the saved set and checks freshness once per run. A missing, damaged or stale file ends the run with a cause and a suggestion to use `--rebuild-libraries`. Freshness depends on the effective library sources, source root priority, preparation rules and library format version.

During a batch rebuild the parser schedules independent library files using the same queue ordering and `--workers` limit as for the main files. After per-file parsing, definitions are combined in their established order, honoring source root priority. Cross-file references are resolved once the required definitions are available. Worker completion order does not affect the prepared set. Reuse verifies the saved set and its inputs without parsing the library files again.

The set covers inline templates, scripted effects, scripted triggers, script values and global static variables. The parser configuration already defines the five source directories, file pattern and encoding. Preparation honors configured exceptions, including the explicitly permitted extensionless inline file. [Library directories](../stellaris_parser/config/libraries.json) · [Exceptions](../stellaris_parser/config/exceptions.json)

Each worker receives the prepared definitions and rules once and uses its in-memory copy for all assigned files. Call arguments are substituted when parsing each document. Each file starts with fresh local variables, a fresh expansion stack, and its own expansion identifiers and metadata.

## Reversible library expansion

The saved set must allow reconstruction of the selected library TXT files' script structure, including the original calls and their arguments. Formatting may differ. Preparation must retain the data needed by a future exporter. This stage verifies reversibility using a fixture.

1. Store each selected file's source identity and ordered structure before expansion in the corresponding library JSON. Each top-level `inline_script` retains its position among neighboring entries. Preserve its original form (reference or block), template path, argument order and structure, and original parameter expressions. For example, an argument forwarded from an outer template retains its `$NAME$` expression even if indexing resolved it to a concrete name. Definition bodies retain nested calls until application.
2. For the lookup index, expand the top-level includes needed to discover names. Persist this history in the library JSON under the file being indexed. Each entry identifies the original call site and target, its `id` and `parent_id`, and the ordered insertion result. Each index definition produced by an include refers to the call that produced it. A record address includes the library and file so that identical local identifiers in different files are unambiguous. Repeated calls to one template retain separate records, including calls that produce no entries.
3. For example, a single include in `effects.txt` creates two effects. Both names are available in the index and refer to one include. Reading back the structure of `effects.txt` restores exactly one original call at its position. If the included template called another template, that nested call is restored in its own file. The history of applying an effect in an event belongs to the event document's `metadata.expansions`. Library preparation history is stored once in the five-file library set.

## Directory traversal and JSON output

1. Batch mode recursively selects game `.txt` files in the requested directories. It skips the five configured library directories and files in the optional `batch.exclude_files` list. Each entry is an exact path relative to a game or mod root. Paths are matched before reading the contents or enqueuing the task. The documentation file in the example therefore produces no JSON, while a file with the same name in another directory is processed. The list applies only when selecting main files for a batch run.
2. A path relative to the game or mod root identifies the input. Overlapping directories enqueue a path once. When more than one root provides a file at that path, the first match in `roots` wins.
3. Output preserves the source-root-relative path and changes the extension to `.json`. Selecting both `common` and `common/technology` yields one `<output>/common/technology/demo.json` for `common/technology/demo.txt`. Files with identical names in different directories have distinct outputs.
4. After selecting sources and assigning output paths, the parser builds one work queue for all workers. Each task contains a pair of paths for one file. Files from all selected directories are ordered by descending source size in bytes. For equal sizes, dispatch the lexicographically smaller root-relative path first, using `/` as the separator.
5. The run uses up to `--workers` processes. As soon as a worker finishes its task, it receives the next file from the queue. Different workers may process files from the same directory concurrently. Each worker writes the complete JSON with line breaks and returns the path and task outcome. Node order, variable substitutions and expansion history follow single-file behavior.
6. Outputs are protected against overwriting sources, rules, library JSON files and the manifest. A completed JSON file is replaced only after the whole new document has been written successfully. A file-level error allows other tasks to finish, identifies the source and cause in diagnostics and produces a nonzero batch exit code. Successfully written documents remain available.

Prepared libraries and parsed documents belong in the run's `artifacts/` directory. Saved reports go in `reports/`. Separate error artifacts, when needed, go in `errors/`.

## Acceptance checks

Checks cover the parser. A small fixture with two source roots and several files is sufficient for the first pass.

| Scenario | Acceptance criterion |
| --- | --- |
| Task dispatch | Use files from two directories to check dispatch in descending size order, including two equal-size files to exercise the path tie-breaker. With two workers, finish the second task before the first and verify that the available worker receives the third. The output paths and full JSON content must match a sequential run |
| Reversible library include | Place a template call between two ordinary fixture entries. Have it generate two definitions through a nested include. Repeat the call with different arguments and exercise an include with an empty result. After rebuild and reuse, reconstruct each participating file's structure solely from saved data and compare it with its pre-expansion parse. Check original call order and count, form and arguments, parent links, and links from definitions to calls |
| End-to-end run | Run `parse-batch` with 2 workers on several files using the same template with different arguments. Verify that main file tasks start after library preparation and that processing the next file on the same worker requires no library TXT or JSON reads. Check expansions and output paths for every file. Repeat using the saved library set |
| Single-file and batch parsing | The full JSON content of each source, including `source`, `items` and `metadata`, matches across single-file mode and batch mode with 1 and 2 workers |
| Priority and paths | A mod overrides the game file at the same path. Overlapping directories enqueue one task per path. Identically named files in separate directories produce distinct JSON files. Traversal skips library directories |
| Excluded file | List the path of a file containing deliberately invalid script text. The batch succeeds and creates neither a task nor a JSON file for that path. A valid file with the same name in a neighboring directory produces its own JSON |
| Parallel preparation | Rebuild with 1 and 2 workers using library files with a cross-file reference. The definitions, their values and the resulting script document match. A preparation error prevents main file processing |
| Preparation and reuse | Exercise one representative of each library kind and a nested call. Rebuild runs once and each worker initializes definitions once. A repeat run with `--reuse-libraries` produces the same result |
| Freshness | A change to a library source or to a configuration setting used in preparation is detected before file processing. A rebuild picks up the change |
| File isolation | Two files define different local values under the same name and call the same template with different arguments. Their results and metadata are correct in either order on the same worker |
| Errors | A zero worker count and conflicting mode flags are rejected. One malformed source yields diagnostics and a nonzero final exit code. A valid sibling source produces a complete JSON document |

## Verification results

On 20 November 2026, all 13 standalone parser tests passed. Outputs for two fixture scripts matched checksums recorded with the previous single-file parser. Coverage includes two-worker dispatch, mod overrides, an extensionless template, recovery of nested calls from the saved libraries and preservation of the previous output on a file error. [Batch tests](../tests/test_batch.py) · [Scheduling tests](../tests/test_scheduling.py)

With the installed game as input, the parser rebuilt five libraries from 750 source files. Two workers then processed `common/technology/category/00_category.txt` and `common/technology/tier/00_tier.txt`. A second run with `--reuse-libraries` produced byte-identical JSON for both files. These two directories were the scope of the main-file check on game data.
