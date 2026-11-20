# Stellaris Parser — unified data preparation run

## Contents

- [Profile and invocation](#profile-and-invocation)
- [Output](#output)
- [Acceptance](#acceptance)
- [Verification results](#verification-results)

## Profile and invocation

Status — implemented. The `prepare-all --config <profile>` command accepts one of the existing flags `--rebuild-libraries` or `--reuse-libraries`. WEB_STTV owns its reference profile. It defines source roots, file selection, language priorities and output paths. [WEB_STTV profile](../../../WEB_STTV/config/parser_sources.json)

1. After reading the profile, the coordinator starts one dedicated localization process. At the same time, script preparation builds or verifies the five libraries. `batch.workers` limits the script workers. A setting of 10 allows up to ten script workers and one localization process to run concurrently.
2. The localization process calls the existing handler once to read all configured RU and EN YML files, check conflicts and write the dictionary. It only needs the localization settings and sources. The profile determines translation priority. For Russian, the order is the translation mod's `replace` directory, its Russian localization directory, then vanilla Russian. English uses vanilla English localization. Within a tier, definitions are ordered by relative path and line number.
3. Once the libraries are ready, the script workers process TXT and DLC files selected by `batch.sources`. Each entry is an exact path or a glob relative to a source root. A `**` segment matches zero or more subdirectories. Existing rules for root priority, exact exclusions and deduplication apply. Each available worker takes one file from the queue, largest first, breaking ties by relative path. For TXT files, including `dlc_metadata/dlc_info.txt`, and for descriptors matching `dlc/**/*.dlc`, the parser writes JSON with the original path in `source.file`.
4. The coordinator waits for both tasks and returns the overall result. Success requires both successful script preparation and a successfully written dictionary.

## Output

| Profile setting | Contents |
| --- | --- |
| `batch.output` | One expanded JSON document per TXT or DLC source, preserving the relative path, syntax tree and expansion history |
| `localization.output` | The existing loader-ready dictionary. One document per `language` and `key`, preserving raw strings, sources and the selection by priority |
| `library_directory` | Five library JSON files and their manifest for subsequent parser runs |

Output paths resolve relative to the profile file. Game documents retain their original localization references. Resolving names and descriptions onto objects belongs to server-side enrichment. Successful completion means both groups of loader inputs are ready. The command prints its summary and errors to the console. The `artifacts` directory holds only output artifacts.

## Acceptance

- Exercise a regular TXT file, a nested file, DLC metadata, a DLC descriptor and RU/EN strings including a mod override. Compare each output to its existing reader.
- On a fixture with `batch.workers = 2`, verify that the localization handler starts once and can begin reading before library preparation finishes. Hold it active while two script jobs execute concurrently. Check that the command waits for both tasks in either completion order. Compare script JSON with the `batch.workers = 1` output, and compare dictionary batches and their manifest byte for byte with standalone `prepare`.
- Exercise both library modes. A script parsing failure or conflicting localization definitions in the winning tier produce a nonzero overall exit code.
- Compare script paths with the previous 30-dataset run and localization inputs with the profile directories. The installation checked on 20 November 2026 contains 619 game files and 706 localization files. These counts describe that game snapshot. Acceptance covers the parser.

## Verification results

On 20 November 2026, all 17 parser tests passed. The fixture confirmed concurrent execution of two script jobs and one dictionary build, both completion orders and an identical dictionary package to standalone preparation. [Process tests](../tests/test_prepare_all_parallel.py) · [Command tests](../tests/test_prepare_all.py)

The reference profile took 178.63 s with a library rebuild and ten script workers. All 619 game JSON files matched the previous run byte for byte. The dictionary was ready in 21.5 s and contains 153,242 Russian and 150,258 English documents from 706 files. Checksums of all five libraries and all 304 dictionary batches were verified after completion.
