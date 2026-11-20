# Stage 21 — recursive DLC restrictions and technology acquisition

## Contents

- [Result](#result)
- [Startup](#startup)
- [Data and configuration](#data-and-configuration)
- [Evaluation and cache](#evaluation-and-cache)
- [Checks](#checks)
- [Limitations and engine testing](#limitations-and-engine-testing)

## Result

Implemented the [main specification](TZ_BACKEND_STAGE_21_EN.md) and [acquisition addendum](TZ_BACKEND_STAGE_21_ACQUISITION_EN.md). Frontend version: **0.0.13**; tree enrichment implementation: **1.3.0**. Prepared set: **`data/stage21_acquisition/database_set`**.

The registry has 30 kinds: `ascension_perks`, `traditions`, `tradition_categories`, `crisis_paths`, and `crisis_levels` extend the previous 25. The crisis catalogs contain 5 paths and 25 levels. Names and available descriptions use the existing RU/EN priorities; missing text is not invented.

All 25 levels have names and descriptions in both languages. The five paths have no own strings under their IDs/standard keys: missing-localization states are retained rather than substituting perk or currency names.

Indirect restrictions follow related game objects. Grants and research unlocks are analysed separately from normal research selection. Possible acquisition does not imply present ownership. `has_technology` becomes false only when all acquisition paths are proven impossible; incomplete information remains `unknown`.

## Startup

From the repository root, PowerShell:

```powershell
$env:PYTHONPATH = (Resolve-Path WEB_STTV/src/backend).Path
WEB_STTV/data/.venv/Scripts/python.exe -X utf8 -B -m sttv.service
```

In another terminal, from `WEB_STTV`:

```powershell
$env:PATH = (Resolve-Path data/frontend-tools/node-v24.22.3-win-x64).Path + ';' + $env:PATH
npm run dev
```

Open `http://127.0.0.1:5173/` and explicitly select `data/stage21_acquisition/database_set`. `config/service.json` selects `data/stage21_acquisition/variables.json`. Use the new set and frontend: the manifest has `format_version = 2`; the previous format is not supported.

Startup, page refresh and Apply never build databases. Preparation uses the existing Python function `sttv.database_sets.operation.build_database_set(variables, library_mode='reuse', prepare_images=True)`; use `library_mode='rebuild'` to rebuild libraries. Full audit is separate: `sttv.storage.audit.audit(manifest_path)`. Explicitly rebuild an obsolete set rather than editing its manifest manually.

No services were started during this iteration. These commands are for the user to run.

## Data and configuration

| Path | Purpose |
| --- | --- |
| `config/enrichment/dlc.json`, `dlc/*.json` | Predicates, object sources, contexts, logic and limits |
| `config/enrichment/acquisition/sources.json` | Index roots, format, location and rule group references |
| `config/enrichment/acquisition/effects.json` | Six acquisition commands, target fields, scopes and semantic evidence |
| `config/enrichment/acquisition/entries.json` | Entry points, guards, event calls and crisis progression |
| `config/enrichment/targets/crisis_*.json` | Crisis catalog localization rules |
| `schemas/acquisition_*.schema.json` | Generated schemas for the index and its configuration |

The index covers 1509 source TXT files in `common`, `events`, and `prescripted_countries`, excluding insertion libraries. It reuses prepared database results for 586 files and processes 923 additional files in the same worker pool. Each source has a separate indented JSON document. Sizes and timings are recorded in the build report; these are corpus measurements, not constants.

The final build reusing libraries took 581.253 s, including 84.814 s for index preparation. The index occupies 307,244,108 bytes (293.011 MiB). Publication includes 619 ordinary documents and 822 unique PNG images; executable-source parsing has no errors. These measurements are from the current computer, not an isolated comparative benchmark.

`common/HOW_TO_MAKE_NEW_SHIPS.txt` is English documentation with examples, not executable script. `sources.json` classifies it as documentation using its exact SHA-256 and an explanation. Coverage records this explicitly; changed bytes invalidate the classification and go through the normal parser. There is no general rule to skip unfamiliar TXT files.

The manifest's `acquisition` section declares source membership, hashes, target/call indexes, coverage, and revisions of configuration, implementation, libraries and preparation. This is a technical index, not a 31st user catalog. Publication of ordinary documents and the index is atomic. Unread documents are not marked verified; full audit checks them separately.

## Evaluation and cache

Normal acquisition considers `potential`, prerequisites and weight; starting acquisition also considers `starting_potential`. Special grants do not automatically inherit ordinary-route restrictions. Supported mechanisms include direct grants, research options, progress, random options and both copy commands with confirmed constraints. Alternatives, calls, recipients and effect addresses are preserved.

Backward calls connect perks/traditions, events, `on_action`, crisis activation and ordered levels. Effect branches follow execution guards. Unknown state changes, scopes, entries, dynamic targets and cycles do not become proven prohibitions.

The graph covers required technologies and their dependencies. The service retains one prepared graph across DLC applications; changing the set, rules or variants invalidates reuse. Integrity is checked on read and unchanged verified dependencies are reused. Apply does not read game sources. The frontend checks set membership but does not read acquisition-index contents for the ordinary tree.

The `dlc_analysis` report contains shared graph nodes, acquisition/ownership states, special routes, uncertainty reasons and coverage. DLC causality is checked against evaluation with unknown DLC states. A zero base weight alone never hides a card.

## Checks

Working results are in `data/stage21_acquisition/`:

| File | Check |
| --- | --- |
| `reports/database_set.json` | Preparation of 30 kinds, index, images, build time and memory |
| `matrix.json` | 86 DLC combinations on one graph, reads and evaluation timings |
| `acquisition_summary.json` | Two Cosmogenesis technology routes and unknown constructs |
| `publication.json`, `service_memory.json` | In-process service profile applications without an HTTP listener, cache and memory |
| `audit.json` | Full published-snapshot audit |
| `frontend_acceptance.json` | Loader opening, RU/EN layouts and crisis localization |

The matrix checks that Weaver weapons are hidden without BioGenesis. In all 43 profiles without Machine Age, six Lathe technologies are hidden by their own DLC condition; missiles and torpedoes remain through other OR branches. Control results: 678 visible technologies with all DLC and 448 with none. All 679 source objects remain in the database.

Final matrix run: 179,299 nodes, 8.644 s to construct the graph, and 0.278–1.647 s per profile without rereading documents. It read 440 of 2128 declared ordinary/technical documents; the remainder are explicitly unverified by this run. Sampled process working-set peak: approximately 989 MiB. The matrix used a pinned snapshot while another check published combinations; these timings are not an isolated benchmark.

Control applications through the service without HTTP:

| Profile | Visible technologies | Full operation with report, s | Action |
| --- | --- | --- | --- |
| No DLC | 448 | 73.600 | Calculation and publication |
| `dlc002`, `dlc036` | 507 | 82.930 | Calculation, reused graph |
| All DLC | 678 | 88.444 | Calculation, reused graph |
| All DLC again | 678 | 35.018 | Stored combination, 0 documents written |

These operations blocked reads from the game directory. Peak coordinator working set was approximately 1191 MiB; the process tree peaked at approximately 2001 MiB. Full application includes separate parent-selection evidence preparation, publication and a large diagnostic report, so it differs from DLC-graph evaluation time.

The frontend loader opened all three results in 4.5–4.7 s each. Initial loading verified only 35 technology documents and did not read the acquisition index. RU/EN layouts matched published visibility and had no overlapping cards. Separate catalog requests checked localized crisis levels and explicitly missing path strings.

Full published-snapshot audit passed in 327.975 s: all 2128 documents (619 ordinary and 1509 technical) and 822 images were verified without errors. Ordinary documents occupy 11,531,945,655 bytes, mostly events. This full scan does not run on ordinary opening or every DLC application.

Type checking and the production build passed; 71 ordinary frontend tests passed and 4 real-data checks were skipped in the general run. The new real-set test was run separately and passed. All 41 schemas match the generator; links and contents in 14 changed documents were checked. Targeted Python acquisition, storage, cache and recalculation tests passed, including 21 acquisition-semantics scenarios.

Unit tests cover branches, grants without normal prerequisites, zero weight, dynamic targets, foreign recipients, level order, cycles, incomplete coverage, membership/rule changes, damaged files and cancellation. Loader tests run without a browser window and are not visual acceptance. The production frontend build is checked separately.

## Limitations and engine testing

Complete source parsing does not mean complete execution of all game rules. Unknown mechanisms and conditions remain in reports; campaigns are not simulated. Cosmogenesis IDs are not hardcoded into rules.

The normal `ap_cosmogenesis` and crisis-level chain is confirmed. However, random grants with `ignore_rare = no` prevent proving impossibility of every acquisition route for `tech_cosmogenesis_world` / `tech_cosmogenesis_escort`. One example is `events/shroud_events.txt:1247`. Local documentation for `add_random_research_option` does not establish `potential` or zero-weight checks. These routes remain unknown; this is not a claim that the game actually grants those technologies.

Engine verification needs a separate controlled in-game test: compare random selection of a rare technology with positive/zero weight, true/false `potential`, satisfied/unsatisfied prerequisites and `ignore_prereqs = yes/no`; check both success and `fail_effects`. Several unsuccessful draws do not prove exclusion. No test mod or game edits were made; such testing requires a separate task. Visual verification of DLC changes also remains with the user.

[Русская версия](BACKEND_STAGE_21_RU.md).
