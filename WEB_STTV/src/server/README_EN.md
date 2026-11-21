# Stellaris reference server

## Contents

- [Running on Ubuntu](#running-on-ubuntu)
- [Looking up translations](#looking-up-translations)
- [Selecting a key in code](#selecting-a-key-in-code)
- [Technology tooltip content](#technology-tooltip-content)
- [Technology tree](#technology-tree)
- [Checks](#checks)

## Running on Ubuntu

On the `stellaris-wiki` VM, systemd runs `rit-mongodb-wiki`, `sttv-reference` and `sttv-frontend`. Check them with `systemctl is-active rit-mongodb-wiki sttv-reference sttv-frontend`. Browsers connect on port 5173 and the loader connects to MongoDB over TLS on port 27017. The nftables rules use the `192.168.1.0/24` source subnet. After another IP change, check the client addresses, SSH host key entry and MongoDB certificate against the new address.

Run the following from `WEB_STTV/src/server` or its copy on the VM in an environment with Python 3.10+ and PyMongo 4.19.0. Supply the MongoDB password through the `STTV_MONGO_PASSWORD` environment variable.

```sh
python3 -B -m sttv_server --config config/server.json
```

By default the server listens on `127.0.0.1:8788` and reads `wiki.localization` over TLS at `127.0.0.1:27017`. The [server configuration](config/server.json) specifies the HTTP and MongoDB addresses, CA path, database and collection.

## Looking up translations

```sh
curl -sS http://127.0.0.1:8788/api/localization/lookup \
  -H 'Content-Type: application/json' \
  -d '{"language":"en","keys":["PHYSICS","physics_research","tech_titans"]}'
```

The response has a `language` field and an `items` array with `key` and `text` pairs in request order. This example returns “Physics”, “Physics Research” and “Titans”. A missing key returns `null`, an empty translation returns `""`. The server expands static references in the requested language. Unresolved references, game markup and game-context expressions retain their original text. [API contract](Docs/TZ_LOCALIZATION_API_EN.md)

## Selecting a key in code

The rules live in [localization_keys.json](config/localization_keys.json). The `localization_keys_file` setting in `server.json` specifies a path relative to the directory containing `server.json`. The server reads the rules at startup.

The internal function `sttv_server.localization.determine_key(rules, context, value)` takes the loaded rules and returns the exact key or `None`. Supported contexts are `research_area`, `research_category`, `technology_name`, `technology_description` and `dlc_project_name`. For example, `research_area` and `physics` give `PHYSICS`. Pass the resulting key in the HTTP request.

## Technology tooltip content

Request one base technology by game ID and language. The request reads the source documents and localization from MongoDB. [Content rules](../../Docs/frontend/TZ_TECHNOLOGY_TOOLTIP_CONTENT_EN.md)

```sh
curl -sS http://127.0.0.1:8788/api/trees/technology-tooltip \
  -H 'Content-Type: application/json' \
  -d '{"technology_id":"tech_titans","language":"en"}'
```

The response contains `technology_id`, `language`, `name`, `description`, `sections` and `diagnostics`. Empty sections are omitted. Each source block under `prerequisites`, `potential` and `allow` produces one expression. Logical groups carry an `operator` and ordered `children`. Entries under `weight_modifier` retain their source order. Each `modifier` contains ordered `operations` and an optional `condition` expression. Simultaneous checks form an `AND` group. Each operation supplies localized `text` for the start of the row, such as `×0.1` or `+5`. Inline game color codes delimit highlighted names. A calculated factor can include a `formula` with its operations or a `trigger` identifying its game-state dependency.

The server returns the simplified condition ready for display. A negated origin or authority check retains its original `key` and carries `negated: true`. When the negative translation is missing, the API returns a `NOT` group containing the original check. [Rules and examples](Docs/TZ_TOOLTIP_CONDITION_SIMPLIFICATION_EN.md)

A node’s localized label is in `text`. Unrecognized nodes carry `kind = unrecognized` and the original `expression`. If a name is unavailable the condition retains its game ID and `diagnostics` identifies the missing key. An unknown technology returns HTTP 404. An unsupported language or invalid request body returns HTTP 400. [API acceptance checks](tests/tooltip_acceptance.py)

For country and galaxy flags the server looks up a complete phrase by check type and flag ID in the selected language. If the translation is missing, the tooltip displays a neutral phrase and `diagnostics` records the check type, flag ID, technology and section. The tooltip omits the `crystal_armor_1_weight` check. [Flag dictionary and display rules](Docs/TZ_TOOLTIP_FLAGS_EN.md)

## Technology tree

Open the test site in a browser and choose **Technology tree**. Under **Game settings → DLC**, change the selection and choose **Apply**. The reference mode switch is on the **Empire settings** tab. To clear generated trees, open **System settings → Database operations**. [Test site](http://192.168.1.36:5173/)

The published frontend proxies `/api/trees/` and `/api/localization/` to the API on the same VM over HTTP. Game PNGs are served under `/game-assets/`. For development, set the Vite proxy target with `STTV_SERVER_URL` and the build-time image base URL with `VITE_STTV_ASSETS_URL`.

| Request | Result |
| --- | --- |
| `GET /api/trees/reference/dlcs` | DLC IDs, RU/EN names and a relative PNG path in `thumbnail` or `null` |
| `POST /api/trees/reference` with `{}` | Tree with all DLCs |
| The same request with `{"enabled_dlc":[]}` | Tree with all DLCs disabled. Supply selected IDs in the array to enable them |
| `DELETE /api/trees/reference` | Number of collections removed in `removed_collections` |

One HTTP server instance owns the `tree_configs` registry. Each tree collection contains every source technology ID. The client receives visible nodes and their card fields. Language switching selects one of the two stored layouts. The ordered criteria live in the [tree configuration](config/reference_tree.json). [Specification and control technologies](Docs/TZ_REFERENCE_TREE_EN.md)

## Checks

Run the dictionary check from the monorepo root in an environment with the parser, loader and server packages and access to the network MongoDB profile. It verifies RU/EN templates and game references through the API and scans four sections of the base technologies. The report shows grouped requirements, thresholds and weight modifiers from the database. Unknown constructs retain their technology, path and expression. [Tooltip dictionary](Docs/TZ_TOOLTIP_DICTIONARY_EN.md)

```powershell
python WEB_STTV/tests/tooltip_dictionary_acceptance.py --lookup-url http://192.168.1.36:5173/api/localization/lookup --report TMP/WEB_STTV/tooltip-dictionary/reports/coverage.json
```

The live reference-tree matrix requires a separate HTTP instance and an empty registry. Put a copy of `config/server.json` beside the original, assign a separate port and a unique `tree_collection_prefix` matching `tree_test_[a-z0-9]+_`, and start the instance with that copy. From the server directory run `PYTHONPATH=. python3 -B tests/reference_acceptance.py config/test_server.json /path/to/run/reports/matrix.json`. The test checks every stored technology against the HTTP response, duplicate and reordered DLCs, both layouts, removal of all 12 results and explicit rebuilding. Set `STTV_TREE_PUBLICATION_TEST=1` for the additional unittest covering concurrent requests, failed publication and revision changes.

With the server running, execute the following from its source directory with the same database connection environment.

```sh
STTV_API_URL=http://127.0.0.1:8788/api/localization/lookup \
  python3 -B -m unittest discover -s tests -v
```

Eight tests passed on the `stellaris-wiki` Ubuntu VM, including loading a rules file in a subdirectory specified in `server.json`. HTTP checks covered single and batch RU/EN lookups, missing keys, case sensitivity, duplicates, expansion of a published reference and invalid requests. The same run used in-memory examples to check empty translations, cycles, a chain of over 1000 keys, mixed constructs and the response to a database outage. Each run stores its server copy under `artifacts/server` and its logs under `reports`.
