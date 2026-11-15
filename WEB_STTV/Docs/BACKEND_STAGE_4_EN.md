# Fourth backend stage — logical operators and the inline_script stub

## Contents

- [Stage result](#stage-result)
- [Configurations](#configurations)
- [Interface and tree](#interface-and-tree)
- [Handling inline_script](#handling-inline_script)
- [Database and reports](#database-and-reports)
- [Running and verification](#running-and-verification)
- [Limitations](#limitations)

## Stage result

The approved [fourth-stage specification](TZ_BACKEND_STAGE_4_EN.md) is implemented. The parser creates distinct logical-operation nodes according to configuration. Both forms of `inline_script` invocation reach an expansion function that currently returns an empty list. Invocation contents are not parsed.

## Configurations

`config/backend.json` has three required selections under `parser`: `lexical`, `constructs`, `logical_operators`. Each supports `product` and `work` bases; missing or invalid files cause an error without default settings. Output files cannot overwrite selected configurations.

| File | Purpose |
| --- | --- |
| `config/parser/lexical.json` | Symbolic operators, strings, comments, braces, and whitespace |
| `config/parser/constructs.json` | Structural forms; `inline_script.keyword` and `case_sensitive` select the handler name |
| `config/parser/logical_operators.json` | Logical names, canonical spelling, case sensitivity, and connecting operator |

Supplied logical names are `AND`, `OR`, `NOT`, `NAND`, `NOR`, matched case-insensitively with `=` as the connecting operator. An empty list disables special recognition. The parser engine does not duplicate these names. Adding a name does not establish game support for it.

The permanent `sttv.schema_generation` generator produces schemas: `parser_logical_operators.schema.json` was added, and construct, backend-setting, and report schemas were updated. The database schema is unchanged.

## Interface and tree

```python
from sttv.common.paths import PRODUCT_ROOT
from sttv.script.parser import parse_text
from sttv.script.syntax import load_syntax

syntax = load_syntax(
    PRODUCT_ROOT / "config/parser/lexical.json",
    PRODUCT_ROOT / "config/parser/constructs.json",
    PRODUCT_ROOT / "config/parser/logical_operators.json",
)
document = parse_text("or = { tech_a tech_b }", syntax, "example.txt")
operation = document.items[0]
assert operation.operator == "OR"
assert operation.name.raw == "or"
assert [item.text for item in operation.body.items] == ["tech_a", "tech_b"]
```

`make_syntax(lexical, constructs, logical_operators)` accepts three already loaded dictionaries. `parse_text` neither reads files nor uses a game profile. Builder and analyzer receive the same `Syntax` through `Settings`.

`LogicalOperation` holds `operator`, original `Scalar` in `name`, `assignment_operator`, `body: Block`, and `span`. Recognition requires an unquoted standalone name to the left of the configured sign and a block on the right. `NOT = tech_a`, `localization = AND`, and `"AND" = {}` remain ordinary assignments.

Bodies preserve lists, repetitions, nested operations, empty blocks, and multiple entries in `NOT`. With `mixed_blocks: false`, a logical operation counts as a named construct alongside `Assignment`. Conditions are not evaluated.

## Handling inline_script

The parser reads tokens on demand. After the `inline_script` name and `=`, it switches to outer-boundary reading before normal parameter, formula, and conditional-fragment parsing.

`script/opaque.py` accounts for brace nesting, strings, escaping, and comments. `script/inline.py` defines `InlineScriptValue(raw, form, span)` and `expand_inline_script(value, source)`. The function is called once per outer invocation and returns `[]`; nested invocations within the opaque value are not handled separately.

The value is not an AST node. `Document.skipped_inline_scripts` retains coordinates for the entire invocation, including its name; `source` and tokens retain the full source text. The value uses one `opaque_value` token. Emptied parent blocks remain present.

Unknown commands, unfinished `$…` fragments, and invalid assignments inside a properly bounded block are not checked. Missing values, unclosed strings, and outer blocks still produce errors with coordinates. Explicitly supplied text from `common/inline_scripts` is parsed as an ordinary standalone document; referenced files are never opened automatically.

## Database and reports

Logical-node projection into `DataEntry`/`ScriptBlock` uses the canonical name as `key`. Ordinary keys and values retain their case. Skipped invocations are absent before conversion, so their signatures are not validated and their contents are not reconstructed from text.

Build and analysis results require `counts.skipped_inline_scripts`, including zero. A skip is neither an error nor an individual warning. Per-invocation coordinates are in `stage4/corpus_report.json`.

The current database excludes contributions from inline inclusions. Vanilla technology data lost 301 `inline_script` entries; all other data matched the baseline. The 679 technologies, 206 variants, and their RU/EN names remain intact. Logical names in the current technology directory were already canonical; case conversion was checked synthetically.

## Running and verification

From `WEB_STTV`:

```powershell
./data/.venv/Scripts/python.exe -B src/backend/main.py
./data/.venv/Scripts/python.exe -B -m unittest discover -s src/backend/tests -v
```

Full audit from `WEB_STTV/src/backend/tests`:

```powershell
../../../data/.venv/Scripts/python.exe -B -m script.audit_corpus
```

Verification results on 2026-11-15:

- 101 synthetic tests: configurations, nodes, opaque reading, integration, and database preservation on errors.
- Checked 2,238 vanilla `.txt` files: 2,235 parsed, two prose documents accounted separately, and the known `common/named_colors/01_trait_colors.txt:65` error retained.
- Found 36,026 logical operations and 6,885 skipped outer invocations, without unexpected diagnostics. Full source reconstruction from tokens was checked.
- The new database matched an independently transformed baseline and passed schema validation. Build and analysis each report 301 skips; analysis completed fully.
- Build: 0 errors and 1,272 warnings from existing data checks. Skipped invocations do not create warnings.
- Before/after source hashes match; no changes relative to the research manifest were found.

Artifacts are under `WORK_DIR/stage4/`: `corpus_report.json`, `validation_report.json`, `build_report.json`, `analysis_report.json`, `test_report.json`, `tests_final.log`, and the baseline `database_before.json`. Research and validation artifacts are not product inputs.

## Limitations

Actual `inline_script` expansion is deferred to a separate stage. The current database cannot reconstruct skipped contributions or evaluate technology eligibility for a particular country. Other strict field checks remain; `prerequisites` still supports `all`/`any`. The game-command profile was not replaced, and the frequency list was not recalculated. Game files were not modified; launching the game is unnecessary for this stage's checks.
