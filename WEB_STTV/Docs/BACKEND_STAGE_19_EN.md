# Stage 19 — empire and DLC reference import

## Contents

- [Status](#status)
- [Sources](#sources)
- [Import design](#import-design)
- [Running](#running)
- [Checks](#checks)
- [Limitations](#limitations)

## Status

Implemented the approved [stage 19 specification](TZ_BACKEND_STAGE_19_EN.md): 25 dataset kinds, source settings, nested DLC indexing, descriptor linking, RU/EN targets and selective reading in frontend 0.0.11. The approved CLASS exception enabled the full build and acceptance checks to complete. The set contains 543 documents, 679 technologies, 206 variants and 791 unique technology and research-area images.

The complete directory to open is **`data/stage19/database_set`**, with a published manifest. It includes the default tree combination and a test combination selecting seven alternative variants. The `data/stage17/database_set` reference remains unchanged; its old registry is incompatible with the new frontend.

## Sources

All paths below are relative to `STELLARIS_ROOT` and read-only. The first nine kinds recursively select `*.txt`.

| Kind | Directory | Confirmed results |
| --- | --- | --- |
| `species_archetypes` | `common/species_archetypes` | 1 document, 6 objects |
| `species_classes` | `common/species_classes` | 2 documents, 42 objects |
| `ethics` | `common/ethics` | 2 documents, 17 objects |
| `ethic_categories` | `common/ethic_categories` | 1 document, 5 objects |
| `traits` | `common/traits` | 44 documents, 1127 objects after full expansion |
| `graphical_culture` | `common/graphical_culture` | 2 documents, 52 objects |
| `ship_categories` | `common/ship_categories` | 1 document, 7 objects |
| `authorities` | `common/governments/authorities` | 1 document, 8 objects |
| `civics` | `common/governments/civics` | 6 documents, 358 objects, including 77 origins |
| `dlcs` | `dlc_metadata/dlc_info.txt`, `dlc/**/*.dlc` | 36 catalog entries, 32 descriptors, 32 matches; four entries without descriptors |

Existing technology, template, variable, translation and asset sources remain in use. DLC archives, thumbnails and recommendations are not read. Descriptor presence does not establish ownership or activation.

## Import design

`config/datasets.json`, version 2, configures `containers`, `sourceRoles` and `descriptorLink` alongside existing parameters. `common/object_selection.py` selects objects for indexing and localization. Regular objects use `/items/N`, DLC entries use `/items/N/value/items/M`; the `dlcs` container and flat descriptors receive no invented IDs.

`database_sets/descriptors.py` matches the exact `name` field, records document references in `enrichments.dlc.descriptors`, detects ambiguities and verifies links during a full audit. Final DLC document validation follows linking and localization.

Text targets reside in `config/enrichment/targets/`. Narrative descriptions, explicit `description`/`desc` and named variants remain separate. Graphical cultures can use uppercase keys; the selected key is retained. DLC descriptor fallback is resolved independently for RU and EN; `fallback.kind = dlc_descriptor` identifies its source. Missing translations remain missing while the frontend uses technical `name` as display fallback.

`sttv_dlc_metadata_store_separator` repairs only the agreed sequence in `dlcs/dlc002`, retaining original coordinates and original input hashes. See [import exceptions](SOURCE_IMPORT_EXCEPTIONS_EN.md).

Rules `sttv_trait_icon_class` and `sttv_trait_council_icon_class` in `config/parser/source_exceptions.json` apply only to listed trait files and templates. An explicitly supplied CLASS in the invocation chain takes precedence; otherwise the enclosing trait's sole `leader_class` is used, while multiple distinct classes produce `leader`. Missing or invalid fields remain errors. The build recorded 116 applications in 14 files: 55 icon cases and 61 nested council-element cases. Diagnostics retain substitution provenance and invocation chains. This repairs import only; game sources are unchanged and the game-side `VANILLA-001` task remains separate.

The frontend uses the same registry and checks nested addresses against the actual AST. Initial opening reads only technologies. Targeted reference-data requests add no technology cards; language, zoom and connections retain their behavior.

## Running

From `WEB_STTV`:

```powershell
$env:PYTHONPATH="$PWD/src/backend"
data/.venv/Scripts/python.exe -X utf8 -B -m sttv.database_sets --variables data/stage19/variables.json --rebuild-libraries --prepare-assets
data/.venv/Scripts/python.exe -X utf8 -B -m sttv.enrichment.technology_tree --variables data/stage19/variables.json --recalculate
data/.venv/Scripts/python.exe -X utf8 -B -m sttv.storage audit --manifest data/stage19/database_set/manifest.json --report data/stage19/audit.json
```

Current libraries can use `--reuse-libraries`. Locations come from `WORK_DIR`, `config/storage.json`, `config/backend.json` and enrichment settings. Changed exception rules require library rebuilding. Opening a page never starts a build.

## Checks

- Backend: 281 of 282 tests passed in the full run; the only failure was an outdated expected number of unread datasets (14 instead of 24). The expectation was updated and the test passed on rerun. Logs: `data/stage19/backend_tests_final.log`, `data/stage19/backend_recheck.log`.
- Set integration and new catalog group: 13 tests passed; focused address, exception and localization group: 5 tests passed.
- After the CLASS addition: 10 focused exception checks and 25 expansion/library regression checks passed. Coverage includes single/multiple classes, explicit arguments through an intermediate template, provenance, errors and applicability boundaries.
- Frontend: the initial 67 unit tests, TypeScript and production build passed. After publication, 10 adapter, selective-reading, complete-set and prepared-combination tests ran. The only failure was an outdated expectation of no warnings: three known non-scalar `weight` values in `tech_dyson_gun`, `tech_dyson_swarm`, `tech_orbital_arc_furnace` correctly produce diagnostics. The expectation was updated; all 6 adapter tests passed on rerun. Logs: `frontend_real_tests.log`, `frontend_adapter_recheck.log` under `data/stage19`.
- Browser with the new set: 29 checks passed, one standalone large-file scenario skipped without `STTV_LARGE_FILE`. Opening, prepared variants, cards, images, language, zoom, connections and loading cancellation were checked. Log: `data/stage19/browser_real_tests.log`.
- Full build with rebuilt libraries and prepared images completed in 486.672 s. Reports: `data/stage19/reports/`. Traits produced 0 errors, 739 unused-inline-argument warnings and 116 exception-application records. Missing new-catalog translations are listed in localization reports.
- Default and test tree combinations were recalculated through the standard operation. All 450 documents of the original 15 kinds match the reference by `source_hash`, excluding derived tree and images; parent/child decisions for all 679 technologies match in both combinations. Report: `data/stage19/final_reference_comparison.json`.
- Full audit succeeded: all 543 documents and 791 images verified, no unchecked documents. Report: `data/stage19/audit.json`.

## Limitations

No empire/DLC controls or game-condition evaluator are added. Archetypes, ethics, authorities, origins and traits are imported completely, including definitions unavailable during empire creation. Leader traits are not described as species traits. Images for new catalogs are not copied. These checks do not establish condition behavior in the engine.
