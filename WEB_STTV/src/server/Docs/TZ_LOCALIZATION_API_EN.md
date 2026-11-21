# WEB_STTV server. First game localization API

## Contents

- [Purpose](#purpose)
- [Determining a key](#determining-a-key)
- [Looking up strings](#looking-up-strings)
- [Server acceptance](#server-acceptance)

## Purpose

**Approved and implemented.** The new server lives in `WEB_STTV/src/server/` as an independent application with its own connection configuration. Game localization comes from the published `wiki.localization` collection. This stage covers determining a key from a game value and reading one or more translations. Both operations require read access only. [Startup and verification results](../README_EN.md)

## Determining a key

An internal function takes a context and a game value and returns a case-sensitive key. A [separate rules file](../config/localization_keys.json) defines the mappings. At startup the server reads it from `localization_keys_file`, relative to the [server configuration](../config/server.json). Russian and English use the same key selection rules. Callers that already know the key can pass it directly to the lookup.

| Context | Initial rule | Example |
| --- | --- | --- |
| Research area name | Explicit mappings for the three areas | `physics → PHYSICS`, `society → SOCIETY`, `engineering → ENGINEERING` |
| Research category name | Category identifier | `computing → computing` |
| Base technology name | Technology identifier | `tech_titans → tech_titans` |
| Base technology description | Technology identifier with the `_desc` suffix | `tech_titans → tech_titans_desc` |

For an unknown context or missing explicit mapping, the function reports that it could not determine a key. Lookup checks whether the resulting key exists. The base technology rules apply when a caller needs the conventional name or description for an ID. Variant selection and description inheritance belong to object handling.

## Looking up strings

The public endpoint `POST /api/localization/lookup` accepts one language (`ru` or `en`) and an array of exact keys. Pass a single-element array for one string.

```json
{"language":"ru","keys":["PHYSICS","tech_titans","__missing_example__"]}
```

```json
{
  "language": "ru",
  "items": [
    {"key": "PHYSICS", "text": "Физика"},
    {"key": "tech_titans", "text": "Титаны"},
    {"key": "__missing_example__", "text": null}
  ]
}
```

Lookup reads the distinct keys in a batch using the composite `_id` index with `{language, key}` in that order. The server takes source text from `definitions[selected].raw` and resolves available references on read. The selected definition already reflects translation priority. Results preserve request order and duplicates. A key missing in the requested language returns `null`. An existing empty string returns `""`. Both cases return HTTP 200. Invalid requests return 400 and database unavailability returns 503.

In `text`, each ordinary `$KEY$` reference is resolved recursively in the requested language when the dictionary supplies its text. For example, `physics_research` contains `$concept_physics_research$` and returns “Физические исследования” for `ru` and “Physics Research” for `en`. If a referenced key is missing, the reference closes a cycle, or a substitution requires game context, the server preserves the fragment's original spelling. For example, `[Root.GetName]` stays in the text. Other fragments resolve independently. Game markup is preserved. At each additional step the server can fetch all outstanding keys together and reuse previously read definitions within the request.

## Server acceptance

Development takes place in the monorepo. For acceptance, copy the new server to a dedicated working directory on the Ubuntu VM, start it there and run HTTP requests against that instance. It reads the existing `wiki.localization` over a local TLS connection. A repeat run may clear that run's dedicated working directory. MongoDB, its data and service configuration are outside the cleanup scope. Additional test software requires prior agreement.

- Check key selection for all three research areas, a category and the base technology fields. Test an unknown context and an unmapped area.
- Request `PHYSICS` and `tech_titans` individually and together in both languages. Expect “Физика”/“Physics” and “Титаны”/“Titans”.
- Request `PHYSICS`, an absent key and then `PHYSICS` again. Check the order, repeated result, missing value and case sensitivity.
- Check `physics_research` expansion in both languages. Use small examples for a reference chain, a cycle and a string containing a known reference, a missing key and a dynamic substitution together. Run these examples in memory on the VM.
- Compare strings without references with the selected MongoDB definition and check the invalid-language response.
