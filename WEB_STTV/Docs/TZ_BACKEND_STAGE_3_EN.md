# Third-stage backend specification — parsing engine and syntax configuration

## Contents

- [1. Status and purpose](#1-status-and-purpose)
- [2. Scope](#2-scope)
- [3. Module responsibilities](#3-module-responsibilities)
- [4. Syntax configuration](#4-syntax-configuration)
- [5. Parsing result](#5-parsing-result)
- [6. Engine behavior](#6-engine-behavior)
- [7. Backend integration](#7-backend-integration)
- [8. Diagnostics](#8-diagnostics)
- [9. Validation and acceptance](#9-validation-and-acceptance)
- [10. Deliverables](#10-deliverables)

## 1. Status and purpose

**Status: approved by the user and implemented.** Date: 2026-11-15. See the [third-stage guide](BACKEND_STAGE_3_EN.md) for the interface, settings, and validation results.

The user chose an incremental approach: improve the parser first and separate its engine from construct configuration. Sources are the [corpus research](RESEARCH_SCRIPT_PATTERNS_EN.md), [syntax description](SCRIPT_SYNTAX_EN.md), current `script/parser.py`, and its consumers. Shared principles are in the [main specification](TZ_EN.md#2-project-structure-and-coding-principles).

This stage delivers an independent syntax engine that reads supported forms using two compact JSON configurations. It preserves structure and source spelling, requires no list of game commands, and does not validate their game semantics.

A strict database structure and full validation of embedded engine code are separate tasks. This stage separates the new parser from existing command validation; the need for and design of that validation will be reconsidered separately. This specification does not extend its requirements.

## 2. Scope

Included:

- Separate tokenization, structural parsing, node representation, and configuration loading.
- Support the constructs listed below, preserving previously lost formula boundaries, conditional fragments, and quotation information.
- Two configurations, closed structural schemas, and selection through backend settings.
- Required adaptation of existing consumers: builder, converter, analyzer, and tests.
- Validation against focused examples and the complete researched vanilla corpus.

Excluded: removing or rebuilding `profiles/stellaris_4_5_4.json`, creating a command catalog, changing the admission of unknown commands into the database, evaluating formulas, expanding includes, executing conditions, resolving game-object references, UI, and an HTTP service.

Game and Workshop sources remain read-only. Working output belongs inside the configured `WORK_DIR`; research materials may remain in `TMP/WEB_STTV/`. No persistent copies of game sources are created.

## 3. Module responsibilities

Separate responsibilities inside the existing `sttv/script/` package:

| Module | Responsibility |
|---|---|
| `syntax.py` | Load and validate both configurations; prepare combined settings |
| `lexer.py` | Read tokens, strings, comments, and compound delimiters |
| `nodes.py` | Represent documents, tokens, nodes, and coordinates |
| `parser.py` | Parse sequences and nesting |
| `serialization.py` | Explicitly convert supported nodes into the existing database `ScriptBlock` |

Extract helpers into small modules in the same package when needed. Existing `rules.py` and `variables.py` serve separate purposes and are not imported by the parser. Code and comments are English. Follow DRY and the main specification's file-size limits.

The engine receives text and validated configuration through a programmatic interface. Reading files, selecting sources, and writing output remain the caller's responsibility. The parser performs no hidden profile discovery, command-registry loading, or console dialogue.

## 4. Syntax configuration

Supplied files:

- `config/parser/lexical.json` — delimiters, comments, strings, and operators;
- `config/parser/constructs.json` — compound forms and their notation.

Expected `lexical.json` content:

```json
{
  "format_version": 1,
  "allow_initial_bom": true,
  "whitespace": [" ", "\t", "\r", "\n"],
  "line_comment": "#",
  "string": {"quote": "\"", "escape": "\\", "multiline": true},
  "operators": ["=", "<", ">", "<=", ">=", "!="],
  "block": {"open": "{", "close": "}"}
}
```

Expected `constructs.json` content:

```json
{
  "format_version": 1,
  "bare_values": true,
  "anonymous_blocks": true,
  "mixed_blocks": true,
  "tagged_blocks": ["rgb", "hsv"],
  "parameters": {"open": "$", "close": "$", "default_separator": "|"},
  "formulas": [{"open": "@[", "close": "]"}, {"open": "@\\[", "close": "]"}],
  "conditional": {"open": "[[", "header_close": "]", "body_close": "]", "negation": "!"}
}
```

Section names identify forms supported by the engine. Notation, operators, color-block tags, and switches come from configuration. Nesting and state handlers remain Python code. The configurations contain no executable code, function paths, arbitrary grammar language, or lists of game commands, arguments, and scopes.

Add generated `parser_lexical.schema.json` and `parser_constructs.schema.json` through the existing schema generator. Reject unknown properties and format versions. Beyond structural schema validation, check empty markers, duplicates, and delimiter conflicts. Overlaps such as `>`/`>=`, `$` opening and closing a parameter, and `]` in different compound forms are intentional and resolved by context. Reject ambiguous configurations instead of relying on JSON key order.

Add `parser.lexical` and `parser.constructs` selectors to `backend.json`, both using the existing `{ "base": "product" | "work", "path": "..." }` convention. Resolve paths independently of the process working directory and protect selected configuration files from output writes. A missing or invalid selected configuration stops the operation without a fallback. Validate before writing the registry, generation report, or database.

Configuration can change notation and enable or disable implemented forms. A fundamentally new form requires a separate handler implementation; changing JSON does not promise support for an arbitrary new language.

## 5. Parsing result

The result is an internal in-memory document representation, separate from the database model. Distinguish:

| Element | Preserved information |
|---|---|
| Document | Ordered elements and source-text information |
| Named entry | Key with quotation information, operator, and value |
| Scalar | Source spelling, quotation flag, and content without outer quotes |
| Block | Ordered children; may be empty |
| Tagged block | `rgb`/`hsv` or another explicitly configured tag and its nested block |
| Formula | Complete source spelling, opening delimiter type, and unevaluated body |
| Conditional fragment | Parameter name, negation flag, and children |
| Parameterized scalar | Preserved text and recognized substitution fragments; an absent default differs from an empty default |

An anonymous block is a block appearing as a sequence element, without an invented key. A standalone scalar also receives no artificial key. Compound names and references remain scalars; the parser does not decide whether `a.b` is an event identifier or a scope chain.

Preserve source coordinates for nodes and significant tokens: line and column starting at 1, start and end offsets starting at 0 in the decoded text. The end offset is exclusive. These are Python string coordinates, not UTF-8 byte offsets. The original text may be retained in memory for retrieving slices.

Comments and whitespace do not become commands. It must remain possible to verify complete tokenization coverage and reconstruct the significant-token sequence without loss. A source-formatting editor is outside this stage.

## 6. Engine behavior

1. Support strings containing spaces and line breaks, quoted keys, and preserved backslashes; do not decode strings as JSON/Python. Lexical quote escaping must account for runs of backslashes.
2. Distinguish comments, strings, formulas, parameters, conditional fragments, and brace blocks. Characters inside one construct must not incorrectly close another.
3. Apply the longest matching operator. Recognize compound delimiters before ordinary atoms and process nesting through the corresponding state.
4. Preserve standalone elements, lists of anonymous blocks, mixed containers, numeric keys, and repetitions. Configuration switches must actually constrain the corresponding forms.
5. Read a formula as one complete value. Arithmetic precedence parsing, expression-value validation, and evaluation are outside scope; `%` inside a preserved body requires no separate game rule.
6. Preserve `$PARAM$`, `$PARAM|default$`, parameters within names and strings, and standalone parameters between entries. Recognizing a form does not perform substitution.
7. Support `[[PARAM] ... ]` and `[[!PARAM] ... ]`, including nested supported constructs, without evaluating the condition.
8. Parse `inline_script` and scripted-function calls as ordinary named entries. Do not read an included file or require a known command name or argument set.
9. Accept an unknown game name when its syntax is valid. Do not check scopes, technology existence, command-specific value types, or DLC availability.
10. Do not generally permit `name { ... }` without an operator. This form is allowed only for explicitly configured block tags; the known questionable color entry receives a diagnostic.

Preserve `@name`, `event_target:name`, `value:name`, `owner?`, and names containing apostrophes without truncation or normalization. The supplied configuration has no separate `?=` operator. Check unmatched delimiters according to the current state: for example, ordinary string content is not treated entirely as a template or game code.

## 7. Backend integration

The builder and analyzer use the same engine and explicitly selected configurations. Internal interfaces may change; do not preserve old interfaces for backward compatibility. Migrate all current consumers and tests to the new representation within this stage.

Existing command validation remains a separate downstream operation. The parser runs without `stellaris_4_5_4.json` and `script_rules.json`. Removing them or relaxing database admission rules is outside this stage; retaining them here does not establish full command validation as a requirement for the future product.

Keep the first-stage database model. Convert new nodes into `ScriptBlock` explicitly and only for representable forms. Do not turn formulas, tagged blocks, anonymous entries, or conditional fragments into ordinary strings or silently discard them to make a build succeed. An unrepresentable construct produces a conversion error, and a partial result must not replace the existing working database.

Adapt the analyzer to new nodes without crashes or silent fragment loss; report a diagnostic when domain analysis does not yet support a form. Change the analysis-result schema only if required to represent that diagnostic, without extending the recommendation algorithm.

Remove imports of the fixed `OPERATORS` from `parser.py` in registry validation and schema generation. Lexical operators come from the selected configuration. Operators allowed by the database format remain a separate part of its existing model contract; extending the grammar does not automatically extend the database. Before building or analyzing, check that registry operators in use are supported by the selected syntax. An ordinary parser-configuration change must not implicitly regenerate application schemas.

## 8. Diagnostics

Distinguish invalid configuration, unterminated strings/blocks/formulas/conditional fragments, unexpected closing delimiters, missing values, disabled forms, and unsupported database conversion. Include the file when supplied by the caller and source coordinates; configuration diagnostics identify the file and field path.

Do not present recognized values as evaluated results. Do not suppress structural errors with placeholders. Unexpected depth overflow must become a diagnostic rather than an unhandled `RecursionError`. Do not introduce automatic source correction or heuristic filename-based skipping.

## 9. Validation and acceptance

- Meaningful synthetic checks cover all forms in sections 5–6, repeated keys, order, multiline strings, apostrophes, references, and nested conditional fragments.
- Negative examples cover closing delimiters, quotes, missing values, and ambiguous configurations. Changing a comment marker/operator/tag or disabling a form must change behavior without Python edits.
- The parser processes an unknown command name without a profile. A separate check demonstrates that this does not admit an unknown technology field into the database.
- Check both configuration base directories, invocation from another working directory, and absence of configuration fallback. Configuration errors must not replace existing build outputs.
- For the recorded research corpus, expect 2,235 successful syntax parses, including 86 files without active entries; review the two prose documents separately; expect one explained diagnostic at `common/named_colors/01_trait_colors.txt:65`. The two-document list belongs to corpus validation, not the parser core.
- For successful files, verify text coverage and reconstruction of the significant-token sequence. Unexpected failures, omissions, or construct changes count as unfinished work.
- With unchanged game and localization sources, the current technology build must match the database saved before the changes byte for byte; existing first- and second-stage checks must pass. Do not change expectations merely to make tests pass.
- Compare source hashes before and after validation. If the installation has changed since the research, report file-set changes and their causes separately instead of forcing counts to match the old corpus.

This stage does not test game execution of scripts. Acceptance establishes syntax parsing and integration quality, not the correctness of all game commands.

## 10. Deliverables

Deliver engine code, two configurations, declarations and generated configuration schemas, consumer adaptations, permanent tests, and a bilingual guide. Update README files and changelogs; save corpus-validation reports in the working folder. Do not distribute original game files, temporary snapshots, or the baseline database with product source code.

The next decision after this stage concerns replacing the current command registry and determining which domain interpretation the reference application actually needs. It is specified separately and is not an implicit part of improving the parser.
