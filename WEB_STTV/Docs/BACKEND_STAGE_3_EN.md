# Third backend stage — configurable parser

## Contents

- [Stage result](#stage-result)
- [Configuration](#configuration)
- [Modules and interface](#modules-and-interface)
- [Nodes and coordinates](#nodes-and-coordinates)
- [Builder and analyzer integration](#builder-and-analyzer-integration)
- [Validation](#validation)
- [Implementation boundaries](#implementation-boundaries)

## Stage result

**Historical guide.** Describes the implementation before the syntax-tree database transition. Current operation and format: [stage six](BACKEND_STAGE_6_EN.md).

Historical stage-three guide. Current signatures with three configurations, logical nodes, and skipped `inline_script` calls are described in the [stage-four guide](BACKEND_STAGE_4_EN.md). Examples and results below refer to stage three.

The approved [third-stage specification](TZ_BACKEND_STAGE_3_EN.md) is implemented. The syntax engine receives text and validated configuration, preserves structure and source spelling, and works without a game-command profile. The builder and analyzer use this engine through shared settings.

Sources are read directly. Validation saved a baseline database and hashes, not copies of game files. The database format remains unchanged; the current build matches the baseline byte for byte.

## Configuration

The selected section in [backend.json](../config/backend.json) is:

```json
{
  "parser": {
    "lexical": {"base": "product", "path": "config/parser/lexical.json"},
    "constructs": {"base": "product", "path": "config/parser/constructs.json"}
  }
}
```

- [lexical.json](../config/parser/lexical.json): BOM, whitespace characters, comment opener, quotation and escaping, multiline strings, operators, and brace delimiters.
- [constructs.json](../config/parser/constructs.json): standalone values, anonymous and mixed blocks, `rgb`/`hsv` tags, parameters with optional defaults, formulas, and conditional fragments.

Select `base: "work"` for custom configurations: paths are relative to `WORK_DIR`. `product` means the product directory. Selection is independent of the terminal working directory; a missing or invalid file does not activate a fallback.

The closed schemas [parser_lexical.schema.json](../schemas/parser_lexical.schema.json) and [parser_constructs.schema.json](../schemas/parser_constructs.schema.json) are generated from `schema_generation/syntax.py` by the shared generator command. Building reads schemas and configurations without rewriting them. Additional checks detect notation conflicts; intentional operator overlaps use the longest match, while compound delimiters are interpreted by state.

Configuration defines notation and switches for implemented forms. A new form requires a code handler. These files contain no game-command list or executable rule language.

## Modules and interface

Inside `src/backend/sttv/script/`:

| Module | Purpose |
|---|---|
| `syntax.py` | Configuration validation and the `Syntax` object |
| `nodes.py` | Source text, tokens, nodes, and coordinates |
| `delimiters.py` | Strings, parameters, formulas, and conditional headers |
| `lexer.py` | Tokenization preserving comments and whitespace |
| `parser.py` | Sequences, nesting, and compound nodes |
| `serialization.py` | Explicit projection of representable forms into current database data |

Standalone Python example with the `sttv` package available:

```python
from sttv.common.paths import PRODUCT_ROOT
from sttv.script.parser import parse_text
from sttv.script.syntax import load_syntax

syntax = load_syntax(PRODUCT_ROOT / "config/parser/lexical.json",
                     PRODUCT_ROOT / "config/parser/constructs.json")
document = parse_text('new_command = { value = @[ 2 * 3 ] }', syntax, "example.txt")
assert document.items[0].key.text == "new_command"
assert document.items[0].value.items[0].value.body == " 2 * 3 "
```

`parse_text(text, syntax, source_name=None)` performs no file reads. `load_syntax` loads separately; `make_syntax(lexical, constructs)` validates already loaded dictionaries. The parser imports neither command validation nor variable resolution.

## Nodes and coordinates

`Document` contains `source`, `tokens`, and `items`. Node lists distinguish `Assignment`, `Scalar`, `Block`, `TaggedBlock`, `Formula`, and `Conditional`. Order and repetitions are preserved.

A scalar retains original `raw`, content `text`, the `quoted` flag, and `parameters`. Each parameter preserves its name, source spelling, coordinates, and `default`: `None` means no default, while an empty string means an explicit empty default. Strings are not decoded as JSON; backslashes are retained.

A formula preserves `raw`, `opener`, and `body`; arithmetic is not evaluated. A conditional fragment contains `parameter`, `negated`, and `items`, without checking actual parameter availability. Reference names remain text without game-semantic interpretation.

`span` contains zero-based `start`/`end` offsets, one-based `line`/`column`, and `end_line`/`end_column`. The end is exclusive. Offsets address decoded Python string characters, not UTF-8 bytes. Tokens, including comments, whitespace, and an initial BOM, cover the entire text without gaps.

## Builder and analyzer integration

`load_settings` reads and validates both configurations before output writes. Selected files participate in protection against output-path collisions. Before working-registry generation and analysis, registry operators are checked against the selected syntax.

`data_entries(document)` projects representable nodes into `DataEntry` for the existing technology converter; `script_block` constructs the current database representation. This is a separate step: successful syntax parsing does not admit a new technology field or value form into the database.

Formulas, conditional fragments, tagged color blocks, and anonymous blocks are not replaced with strings. When they occur in a document being converted, `unsupported_database_form` is reported and the previous database is preserved. Existing command checks run after parsing; their profile was not removed in this stage.

The analyzer also uses explicit projection. A form not representable in its current observations produces an `unsupported_analysis_form` diagnostic for the file and a `partial` result. Observations from that file are not presented as complete analysis. Parameter names come from parsed fragments, including configurable delimiters and defaults.

## Validation

As of 2026-11-15:

- Passed 79 synthetic checks, retaining the previous 54: forms, coordinates, text preservation, configurable notation, configuration failures, output protection, and integration.
- Successfully parsed 2,235 of the 2,238 `.txt` files in `common/` and `events/`, including 86 empty or comment-only files. Two prose documents are listed separately.
- The sole expected diagnostic is `common/named_colors/01_trait_colors.txt:65`, an entry lacking an operator before its block. There are no unexpected failures.
- Reconstructed 3,852,812 significant tokens from nodes of successful files; separately verified complete text coverage during tokenization.
- The database retains 679 technologies and 206 variants and matches the baseline byte for byte. SHA-256: `86624c6b75558115884bddafc1b121bac0ebf04dbaf902a8e16d87575c7c6afd`.
- Hashes of all 2,950 monitored game and localization-source files are unchanged. Every backend and test Python file is at most 200 lines.

Run ordinary tests from `WEB_STTV`:

```powershell
./data/.venv/Scripts/python.exe -B -m unittest discover -s src/backend/tests -v
```

Additional installed-game corpus audit:

```powershell
$env:PYTHONPATH = "$(Resolve-Path src/backend);$(Resolve-Path src/backend/tests)"
./data/.venv/Scripts/python.exe -B src/backend/tests/script/audit_corpus.py
```

Iteration reports are in `data/stage3/`: `corpus_report.json`, `validation_report.json`, and `tests.log`. The corpus audit uses current settings and writes to `WORK_DIR/stage3/`; its two documentation exceptions belong to validation, not the parser.

## Implementation boundaries

The parser does not expand `inline_script`, execute commands, evaluate conditions or formulas, resolve game references, or repair sources. Acceptance establishes supported structure only. Arbitrary configurable grammars and a formatting editor are not implemented.

The reference application still has no UI or portable distribution. Replacing the registry and defining the required domain interpretation require a separately agreed stage.
