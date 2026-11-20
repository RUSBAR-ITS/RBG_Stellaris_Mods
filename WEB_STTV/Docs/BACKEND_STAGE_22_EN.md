# Stage 22 — loading the localization dictionary

## Contents

- [Running on Windows](#running-on-windows)
- [Package and publication](#package-and-publication)
- [Test server verification](#test-server-verification)

## Running on Windows

Run PowerShell from the `WEB_STTV` root with the backend environment installed. The first command installs the dependencies, including PyMongo. Each of the three operations can run independently.

```powershell
.\data\.venv\Scripts\python.exe -m pip install -r src/backend/requirements.txt
$env:PYTHONPATH = 'src/backend'
.\data\.venv\Scripts\python.exe -B -m sttv.localization_import prepare
.\data\.venv\Scripts\python.exe -B -m sttv.localization_import load
.\data\.venv\Scripts\python.exe -B -m sttv.localization_import verify
```

| Operation | Input | Result |
| --- | --- | --- |
| `prepare` | Game and mod localization directories on the workstation | Prepared JSON package and report in `WORK_DIR/localization_import` |
| `load` | Prepared package, Vault and MongoDB | Publishes the complete dictionary to `wiki.localization` |
| `verify` | Same package and server access | Compares every published document with the package |

Stage 22 combined source and publication settings. For the current version see the [parser sources](../config/parser_sources.json), [loader settings](../config/loader.json) and [stage 23 commands](BACKEND_STAGE_23_EN.md).

Network operations use Windows `curl.exe` with Schannel and the client certificate in the user's personal store. The loader obtains the `wiki` password and the public MongoDB CA certificate from Vault, revokes its token and connects directly to MongoDB using TLS and SCRAM-SHA-256. It removes the temporary public CA file after closing the connection.

## Package and publication

`manifest.json` lists batches with SHA-256 digests and document counts. Formatted JSON is stored in `batches/`. A successful preparation ends by atomically replacing the manifest. The `prepare_report.json` file records counts by language and source, conflict locations and the `blocking` flag. A conflict in the selected tier stops preparation before manifest publication.

The loader checks file digests, writes batches to a uniquely named temporary collection and reads it back in full for comparison with the package. Once all documents match, one same-database rename replaces the target collection. Keys removed from all sources disappear from the published dictionary. The loader drops its temporary collection on a write or verification error.

To retrieve the selected text and source in `mongosh`, select the `wiki` database and run:

```javascript
const row = db.localization.findOne({ _id: { language: "ru", key: "tech_titans" } })
row.definitions[row.selected]
```

## Test server verification

On 20 November 2026 the Windows workstation prepared the package, published it twice and checked the published collection in full on `192.168.1.39:27017`. The reader processed 706 files and 453,781 definitions. The collection contains 153,242 RU documents and 150,258 EN documents, totalling 303,500. Higher-priority translations override all 13 conflicts in the vanilla Russian source.

Checks covered `tech_titans` (`Титаны` and `Titans`), both descriptions, the preserved `$02_ACCEPT_NEGOTIATE_EXISTING_AGREEMENT_NEUTRAL$` reference and the Russian-only key `Awareness_rinfix`. A separate test collection exercised reload, a duplicate-key error in the second batch and removal of an obsolete key after a successful replacement. The entire previous dictionary could be read after the error.

To repeat the four targeted tests, set `$env:STTV_TEST_MONGO_LOCALIZATION = '1'` and run `.\data\.venv\Scripts\python.exe -B -m unittest discover -s src/backend/tests -p test_localization_import.py` with the same `PYTHONPATH`. Omitting the environment variable runs the offline checks. The full set of 51 enrichment tests and 3 schema generation tests also passed. [Stage specification](TZ_BACKEND_STAGE_22_EN.md)
