# Exporting policies and bypass types

## Contents

- [Sources and output](#sources-and-output)
- [Publication](#publication)
- [Acceptance](#acceptance)

## Sources and output

Add the game TXT files from both directories and their subdirectories to the [standard parser profile](../../../config/parser_sources.json). Apply the existing documentation exclusions, expansion rules and history handling. Each input produces one JSON file at the corresponding relative path in the artifact directory.

| Stellaris source | Path relative to the loader's `input_root` | MongoDB collection |
|---|---|---|
| `common/policies/**/*.txt` | `scripts/common/policies` | `wiki.policies` |
| `common/bypass/**/*.txt` | `scripts/common/bypass` | `wiki.bypass` |

Policies and bypass types have named top-level blocks. Use `identity = key` in the [loader profile](../../../config/loader.json). Each block becomes one document with its game ID as `_id`. Keep every section and the order of repeated entries. Each policy `option` retains its own `name` and `policy_flags`, and a bypass retains the game's localization key in `name`. This stage prepares and publishes the source data. [Tooltip content draft](../../../Docs/frontend/TZ_TECHNOLOGY_TOOLTIP_CONTENT_EN.md)

## Publication

Use the loader's existing split between the game object, source locations in `policies_provenance` or `bypass_provenance`, and per-file history in `script_history`. Publish the additions to the running test database while preserving the other collections and file histories. Both sources participate in subsequent full runs.

## Acceptance

1. Match the JSON files to the input TXT files and compare the complete set of game IDs with the published documents. The installed snapshot contains eight policy files and one bypass file. The counts are snapshot checks.
2. Use the loader's verification to compare reconstructed trees with the prepared JSON, including source locations and history for all nine files.
3. Query the published data for the policy and option granting each of `robots_outlawed`, `ai_outlawed` and `slavery_allowed`. Check that `robots_outlawed` belongs to the `robot_pops_outlawed` option of `robot_pop_policy`. [Game definition](E:/SteamLibrary/steamapps/common/Stellaris/common/policies/00_policies.txt:4159)
4. Check `gateway`, `wormhole`, `lgate` and `relay_bypass`. Resolve their `name` keys in RU and EN using the existing localization lookup. For `relay_bypass`, expect «Гиперретранслятор» and “Hyper Relay”. Import every other bypass type as well. [Game definition](E:/SteamLibrary/steamapps/common/Stellaris/common/bypass/00_bypasses.txt:160)
