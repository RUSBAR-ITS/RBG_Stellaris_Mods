# Fourth-stage backend specification — logical operators and the inline_script handler

## Contents

- [1. Status and goal](#1-status-and-goal)
- [2. Scope](#2-scope)
- [3. Configuration](#3-configuration)
- [4. Result representation](#4-result-representation)
- [5. Recognizing logical operators](#5-recognizing-logical-operators)
- [6. The inline_script handler](#6-the-inline_script-handler)
- [7. Modules and integration](#7-modules-and-integration)
- [8. Diagnostics and checks](#8-diagnostics-and-checks)
- [9. Acceptance criteria](#9-acceptance-criteria)
- [10. Deliverables](#10-deliverables)

## 1. Status and goal

**Status: approved by the user and implemented.** Date: 2026-11-15. The [stage guide](BACKEND_STAGE_4_EN.md) describes the interface, limitations, and validation results.

Basis: the [agreed classification](KEYWORDS_AND_VALUES_EN.md), [implemented third stage](TZ_BACKEND_STAGE_3_EN.md), `sttv/script/` sources, and current parser consumers. General coding principles are in the [main specification](TZ_EN.md#2-project-structure-and-coding-principles).

Goal: represent `AND`, `OR`, `NOT`, `NAND`, and `NOR` as logical operations in the tree, using a separate configuration. Provide an expansion function for `inline_script`, implemented at this stage as a stub returning an empty result. Both reference and block forms are passed to this function as one opaque value; their contents are not parsed.

The user's latest clarification supersedes retaining an opaque scalar in the resulting tree: the value exists only as handler input, and the entire `inline_script` invocation is skipped. The source text remains available in the document.

## 2. Scope

Included:

- A separate logical-operator configuration, its schema, and backend-settings integration.
- A logical-operation node and recognition without checking conditions' game semantics.
- Reading outer `inline_script` value boundaries, a separate expansion function, and an empty-result stub.
- Adapting serialization, builder, analyzer, reports, and checks to the tree change.
- Corpus checks, source preservation, and precisely defined changes to build output.

Excluded: actual inline-file expansion, parameter parsing, condition execution, logical simplification, classification of other commands, replacing the profile/registry, extending the technology-dependency model, UI, and a new frequency pass. `yes`/`no` and `id` receive no new node types in this stage.

Game files are read-only. Working reports go under configured `WORK_DIR`; temporary research may use `TMP/WEB_STTV/`. Internal-interface backward compatibility is not required.

## 3. Configuration

Add **`config/parser/logical_operators.json`**:

```json
{
  "format_version": 1,
  "case_sensitive": false,
  "assignment_operator": "=",
  "operators": ["AND", "OR", "NOT", "NAND", "NOR"]
}
```

`operators` specifies names and their canonical spelling in logical-operation nodes. With `case_sensitive: false`, match names using `casefold`, preserving source spelling separately. An empty list is valid and disables special recognition. Do not duplicate the list in Python, `lexical.json`, `constructs.json`, or the game profile to operate the parser. The configuration controls form recognition, not truth evaluation.

`assignment_operator` must be a configured lexical operator. Validate name uniqueness under the selected case mode, nonempty names without whitespace or syntax delimiters, and conflicts with the inline-handler keyword. Missing or invalid configuration must not select a fallback operator set. Editing the list must change recognition without code changes; this does not establish engine support for new names.

Add required selection `parser.logical_operators` to `config/backend.json`, using the existing form `{"base":"product","path":"config/parser/logical_operators.json"}`. Support the same path bases as `lexical` and `constructs`. The analyzer receives these settings through shared `Settings`, without a separately configured parser.

Add a construct-name setting to `constructs.json`; it does not define content-parsing rules:

```json
{
  "inline_script": {
    "keyword": "inline_script",
    "case_sensitive": false
  }
}
```

This is an added fragment of the existing configuration. String, comment, and brace notation continues to come from `lexical.json`. The handler name is connected to an implemented function in code; configuration does not load arbitrary Python functions.

Update closed schemas through the permanent generator: new `parser_logical_operators.schema.json`, changed `parser_constructs.schema.json` and `backend.schema.json`. The `Syntax` loader receives three explicitly selected configurations. Old configurations lacking required new fields are not replaced by defaults.

## 4. Result representation

| Element | Proposed fields and purpose |
| --- | --- |
| `LogicalOperation` | `operator`: canonical configured name; `name`: original name `Scalar`; `assignment_operator`: actual connecting symbol; `body`: `Block`; `span`: coordinates of the complete operation |
| `InlineScriptValue` | Internal opaque scalar: `raw`: exact value text; `form`: `reference` or `block`; `span`: value coordinates. No parameter fields or child nodes |
| `Document.skipped_inline_scripts` | Ordered `Span` list for complete invocations skipped by the stub; bookkeeping, not tree items |

`LogicalOperation` is a distinct node type, not an ordinary `Assignment` with a textual key. It can occur in any item sequence. Mixed-container checks must treat it as a named construct alongside `Assignment`, so the type change does not prohibit previously valid blocks.

`InlineScriptValue` exists only when calling the handler and never enters `Document.items` or child blocks. A skipped invocation is not replaced with `null`, an empty node, or a string. Preserve an emptied parent block; neighboring entries must not disappear or change order.

`Document.source` and the token sequence preserve the complete source text. The opaque value may be represented as one `opaque_value` token without parsed parameters. Coordinates remain decoded-character offsets with exclusive ends. The skipped-span list distinguishes deliberate exclusion from accidental traversal losses.

## 5. Recognizing logical operators

1. Outside strings, comments, and opaque inline values, match a separate unquoted name against configuration.
2. Recognize a logical operation only with the configured connecting symbol and a brace-delimited block on the right.
3. Create `LogicalOperation`, recursively parsing its body through the normal engine while preserving order and repetitions.
4. Support standalone identifiers, named expressions, and nested operations in the body. Do not limit `NOT` to one entry; preserve empty blocks too.
5. Do not evaluate truth, validate technologies/ethics/scopes, or simplify nesting.

For example, `or = { tech_a tech_b }` produces an operation with `operator = "OR"`, original name `or`, and two standalone body scalars. `NOT = { has_technology = tech_a has_technology = tech_b }` preserves both entries.

`localization = AND`, `"AND" = { … }`, `and_flag = yes`, `$AND$`, and `NOT = tech_a` do not match the full rule and remain ordinary structural forms. Failure to classify a logical operation does not itself introduce a syntax error. Names inside opaque `inline_script` values are not inspected at all.

The lexer must not classify every `AND` word as an operator regardless of position. The parser determines the operation class from the complete construct.

## 6. The inline_script handler

A separate configured unquoted name to the left of `=` selects a special path before general value parsing. Handle both `inline_script = path` and `inline_script = { … }`, including quoted references.

Sequence:

1. Read the outer value boundaries and construct `InlineScriptValue`, preserving the exact source fragment.
2. Call a separate `expand_inline_script(value, source)` function exactly once for that outer invocation.
3. The function returns a node sequence for the insertion point. **At this stage, its body is a stub returning an empty list.**
4. Add no invocation to the resulting sequence; record its coordinates in `Document.skipped_inline_scripts` and continue with the neighboring entry.

The function does not open files, resolve the path, check template existence, parameters, or a profile, or analyze contents. Plain references and blocks receive identical treatment. This is deliberate stage behavior, not suppression of a failed expansion error.

For a block value, read balanced braces while respecting strings, escaped quotes, and comments. For a reference, read one outer string or atom. Process only the necessary outer boundaries; do not validate assignments, `$…$`, formulas, conditional fragments, or names inside the block. A nested `inline_script` inside the opaque value does not invoke the handler again.

Do not build the ordinary contents AST and delete it afterward: that still parses the ignored code. Adapt the current up-front tokenization of the entire document so opaque regions are read before normal internal-text handlers run. Reuse shared string/comment reading helpers.

An unfinished outer string, missing value, or unclosed brace block remains an error: the next entry cannot be located reliably without the boundary. Properly delimited values containing unknown or structurally unparseable internal entries are skipped.

The rule concerns construct invocations, not directory-name filtering. Explicitly supplied template text is parsed as an independent document, and invocations inside it pass through the stub again. Templates are never read automatically.

## 7. Modules and integration

| Location | Change |
| --- | --- |
| `script/syntax.py`, `sources/settings.py` | Third configuration, consistency checks, paths, and protection against outputs overwriting configurations |
| `script/nodes.py`, `script/parser.py` | Logical node, rule application, include handler, and skipped-span bookkeeping |
| `script/lexer.py`, a small reading helper | Opaque regions before internal tokenization, preserving coordinates and text |
| `script/inline.py` | Input structure and expansion function with an empty stub; no internal inline parser |
| `script/serialization.py` | Explicit projection of logical nodes into the current data model; skipped invocations are already absent from input |
| Builder, analyzer, schema generator, and tests | Consumer adaptation and bookkeeping for deliberately skipped includes |

Small helper module names may be refined during implementation. Follow modularity, DRY, and file-size limits from the main specification; do not introduce a general plugin system for one function.

When projecting `LogicalOperation` into `DataEntry`/`ScriptBlock`, use its canonical name as `key`, preserved connecting symbol as `operator`, and body as an entry sequence. This is explicit conversion between the AST and existing database model; original spelling remains in the AST. Do not normalize ordinary keys or values.

The database schema itself stays unchanged. Builder and analyzer must not reconstruct skipped `inline_script` invocations, extract their parameters from raw text, or validate their signatures. Retain checks for other fields/commands and protection of the existing database on errors. Recognizing all five logical operators does not automatically extend the separate `prerequisites` model, which currently represents `all`/`any`.

Add required `counts.skipped_inline_scripts` to build and analysis reports, with zero when nothing was skipped; add the corresponding `counts` container to the analysis report. Update report declarations and generated schemas. This counts the known stub behavior, not errors or individual invocation warnings. Store detailed coordinates in the corpus-audit report. The analysis count covers actually parsed selected sources.

Expected database differences from stage three: complete `inline_script` entries disappear from `ScriptBlock.entries`, and recognized logical-block names use canonical case. Do not remove emptied parent blocks. Numbers, localization, identifiers, and other data must remain unchanged. Update the database description and guides during implementation: this stage's database excludes the contribution of skipped includes.

## 8. Diagnostics and checks

Configuration checks: a separate file, `product`/`work` path selection, no hidden default operator set, case-variant duplicate names, notation conflicts, and a connecting symbol missing from lexical configuration. Adding/removing a name and changing case sensitivity must alter the AST; do not change the game registry to test the parser engine.

Logical-node checks: all five names, case variants, nesting, identifier lists, multiple entries in `NOT`, empty bodies, repetitions, unknown commands inside, coordinates, and section 5 counterexamples. Test `mixed_blocks = false` with adjacent ordinary named entries and logical operations.

Stub checks: unquoted/quoted references, blocks, empty blocks, multiline code strings, braces inside strings/comments, and escaped quotes. Place ordinary entries and logical operations before and after the invocation and verify full preservation. Separately test an unbalanced `$…` substitution and an invalid internal entry inside an externally balanced block: ignored contents must not invoke the internal parser. An unclosed outer envelope must produce a coordinate-bearing error.

Verify exactly one expansion-function call with exact `raw`, an empty result, and no file I/O. A nested reference inside an opaque block must not trigger a second call. Reconstruct the entire source from tokens; compare AST reconstruction with tokens after excluding exactly the recorded skipped spans.

Save a baseline database before implementation. Independently derive the expected result: remove only `inline_script` entries and normalize names only for logical blocks. The new build must equal this result, pass schema validation, and preserve technology/variant counts and both localizations. Byte equality with the unchanged stage-three database is no longer an acceptance criterion.

## 9. Acceptance criteria

1. Logical operations have a distinct node type, with names supplied only by a separate configuration.
2. Both `inline_script` forms reach the expansion function as opaque values; the stub excludes the complete invocation from the tree and projection.
3. Internal fields and strings are not parsed, references are not opened, and other data is preserved.
4. Consumers, configuration/report schemas, and meaningful tests are updated. Other strict data checks remain intact.
5. Check 2,238 `.txt` files in the unchanged researched corpus: expect 2,235 successful parses, two separately accounted prose documents, and the known `common/named_colors/01_trait_colors.txt:65` error. Expect 36,026 logical nodes and 6,885 skipped outer invocations; inline text inside strings is not expanded or added to these counts.
6. Verify full text coverage, exact skipped spans, node order, and no unexpected diagnostics. Do not pin the old significant-token or empty-tree counts: opaque tokens and skips change these metrics.
7. The build matches the independently transformed baseline database; reports show skip counts. Errors preserve the previous working database.
8. Game-source hashes match before and after. Record changes to the installation relative to the manifest separately instead of adjusting results to expected totals.

Acceptance covers the syntax engine and agreed temporary exclusion of includes. It does not establish execution of game conditions or complete effects of expanded templates.

## 10. Deliverables

Parser and stub-handler code, a separate logical-operator configuration, updated declarations/schemas, integration, permanent tests, and a bilingual guide. Corpus and database-comparison reports go under `WORK_DIR/stage4/`.

During implementation, update README files, changelogs, the keyword document, and database documentation. Actual `inline_script` expansion is designed as a separate later stage; this specification does not define its rules.
