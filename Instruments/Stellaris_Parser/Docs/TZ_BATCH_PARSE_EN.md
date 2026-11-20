# Stellaris Parser — batch game script parsing specification

## Contents

- [Objective](#objective)
- [Commands and configuration](#commands-and-configuration)
- [Library preparation](#library-preparation)
- [Directory traversal and JSON output](#directory-traversal-and-json-output)
- [Acceptance checks](#acceptance-checks)

## Objective

**Status — draft for review.** A parser task takes one source file and writes one JSON file. Batch mode distributes these tasks among worker processes. Single-file mode can parse the same source independently and produce the same document.

The current `parse` command already writes JSON for one source file. Each invocation of `parse_file` reloads the rules, collects global variables and indexes named definitions. Inline templates are read on demand. This stage moves preparation of shared data out of the per-file task. [Current implementation](../stellaris_parser/workspace.py)

## Commands and configuration

| Command | Input | Output |
| --- | --- | --- |
| `parse` | `--config`, library mode, one source-root-relative path and an output filename in `--output` | JSON for that source at the exact user-specified path |
| `parse-batch` | `--config`, library mode, one or more source-root-relative directories, an output directory and a worker count | A separate JSON document for each selected source |

The following proposed user configuration describes a WEB_STTV run. In this example, `parser.json` is in the monorepo root.

```json
{
  "roots": ["E:/SteamLibrary/steamapps/common/Stellaris"],
  "library_file": "TMP/WEB_STTV/run-01/artifacts/libraries.json",
  "batch": {
    "directories": ["common/technology", "events"],
    "output": "TMP/WEB_STTV/run-01/artifacts/scripts",
    "workers": 10
  }
}
```

`library_file` sets the path and filename for the prepared libraries. A later run can use the same file independently of the script output directory. Filesystem paths in the configuration resolve relative to the configuration file. Entries in `batch.directories` resolve relative to each source root in `roots`.

For `parse-batch`, positional directories, `--output` and `--workers` override the corresponding `batch` values for one run. An explicit directory list replaces the configured list in full. A command-line output path resolves relative to the working directory. The worker count is a positive integer. A value of 1 processes files sequentially. The `batch` settings are optional for `parse`.

After implementation, the following commands can be run from the monorepo root.

```powershell
python -m stellaris_parser parse-batch --config parser.json --rebuild-libraries
python -m stellaris_parser parse-batch --config parser.json --reuse-libraries --workers 2 --output TMP/WEB_STTV/run-02/artifacts/scripts common/technology
python -m stellaris_parser parse --config parser.json --reuse-libraries --output TMP/WEB_STTV/run-02/artifacts/physics.json common/technology/00_phys_tech.txt
```

## Library preparation

Both commands require exactly one mode flag. Preparation runs once before the first file task.

- `--rebuild-libraries` collects definitions from the current sources and saves the prepared set as JSON. The file is replaced once the entire set is ready.
- `--reuse-libraries` reads the saved set and checks freshness once per run. A missing, damaged or stale file ends the run with a cause and a suggestion to use `--rebuild-libraries`. Freshness depends on the effective library sources, source root priority, preparation rules and library format version.

The set covers inline templates, scripted effects, scripted triggers, script values and global static variables. The parser configuration already defines the five source directories, file pattern and encoding. Preparation honors configured exceptions, including the explicitly permitted extensionless inline file. [Library directories](../stellaris_parser/config/libraries.json) · [Exceptions](../stellaris_parser/config/exceptions.json)

Each worker receives the prepared definitions and rules once and uses its in-memory copy for all assigned files. Call arguments are substituted when parsing each document. Each file starts with fresh local variables, a fresh expansion stack, and its own expansion identifiers and metadata.

## Directory traversal and JSON output

1. Batch mode recursively selects game `.txt` files in the requested directories. It skips the five configured library directories and their contents during this traversal.
2. A path relative to the game or mod root identifies the input. Overlapping directories enqueue a path once. When more than one root provides a file at that path, the first match in `roots` wins.
3. Output preserves the source-root-relative path and changes the extension to `.json`. Selecting both `common` and `common/technology` yields one `<output>/common/technology/demo.json` for `common/technology/demo.txt`. Files with identical names in different directories have distinct outputs.
4. The run uses up to the requested number of worker processes. An available worker receives the next pair of paths, parses the source and writes the entire JSON with line breaks. Node order, variable substitutions and expansion metadata follow single-file behavior. Workers only need to return the path and task outcome to the coordinator.
5. Outputs are protected against overwriting sources, rules and the prepared library file. A completed JSON file is replaced only after the whole new document has been written successfully. A file-level error allows other tasks to finish, identifies the source and cause in diagnostics and produces a nonzero batch exit code. Successfully written documents remain available.

Prepared libraries and parsed documents belong in the run's `artifacts/` directory. Saved reports go in `reports/`. Separate error artifacts, when needed, go in `errors/`.

## Acceptance checks

Checks cover the parser. A small fixture with two source roots and several files is sufficient for the first pass.

| Scenario | Acceptance criterion |
| --- | --- |
| Single-file and batch parsing | The full JSON content of each source, including `source`, `items` and `metadata`, matches across single-file mode and batch mode with 1 and 2 workers |
| Priority and paths | A mod overrides the game file at the same path. Overlapping directories enqueue one task per path. Identically named files in separate directories produce distinct JSON files. Traversal skips library directories |
| Preparation and reuse | Exercise one representative of each library kind and a nested call. Rebuild runs once and each worker initializes definitions once. A repeat run with `--reuse-libraries` produces the same result |
| Freshness | A change to a library source or to a configuration setting used in preparation is detected before file processing. A rebuild picks up the change |
| File isolation | Two files define different local values under the same name and call the same template with different arguments. Their results and metadata are correct in either order on the same worker |
| Errors | A zero worker count and conflicting mode flags are rejected. One malformed source yields diagnostics and a nonzero final exit code. A valid sibling source produces a complete JSON document |
