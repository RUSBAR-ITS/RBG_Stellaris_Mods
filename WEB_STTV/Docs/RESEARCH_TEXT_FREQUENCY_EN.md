# Stellaris text element frequencies

## Contents

- [Purpose](#purpose)
- [Counting rules](#counting-rules)
- [Coverage and results](#coverage-and-results)
- [Files and rerunning](#files-and-rerunning)
- [Checks and limitations](#checks-and-limitations)

## Purpose

The fourth frequency pass, dated 2026-11-15, was requested by the user and uses the current [stage-four parser](BACKEND_STAGE_4_EN.md). In addition to the previously excluded logical operators and complete `inline_script` calls, script variables written as `@name` and `$NAME$` substitutions are now removed. Other elements remain in one list for manual review.

This is a research run, not a new backend stage. The handler resides in `TMP/WEB_STTV/text_frequency/`. Product code, configurations, schemas, profile, and database were not changed.

## Counting rules

- Use `parse_text` and three current configurations through `Settings`: `lexical`, `constructs`, `logical_operators`. Do not run game-command semantic validation.
- Exclude the name of each `LogicalOperation` while traversing its body normally. Contents of `AND`, `OR`, `NOT`, `NAND`, and `NOR` remain counted. Names come from configuration.
- Both `inline_script` forms are absent from the AST through the parser stub. Invocation names, paths, arguments, and internal strings are neither counted nor reparsed.
- Physical files in `common/inline_scripts/` remain included as independent documents. Calls are excluded, not the template directory. Includes are not expanded.
- Logical-name exclusion uses node types, not global text removal. `text = AND`, `"AND" = {}`, and `NOT = ethic_a` retain ordinary elements. The final corpus list has no standalone `and/or/not/nand/nor/inline_script` entries after all filters.
- Ordinary keys and values share one list: `foo = foo` yields `foo:2`. `id` and other reviewed keywords are not operators and remain included.
- Exclude whole script-variable spellings such as `@name`, including parameterized names such as `@s_t$TIER$_cost`, in definitions, references, and lists. Quotes and case do not change this filter. Other expression elements remain: `cost = @cost` still contributes `cost`, and `@cost = 100` contributes `100`.
- Exclude text containing `$NAME$` or `$NAME|default$` substitutions as a whole, including `prefix_$NAME$`, strings, and formulas with substitutions. Do not count the remaining text separately. Parameter names are nonempty and contain no whitespace; a lone `$` or text such as `"$5 USD$"` is not treated as a substitution.
- Preserve formulas `@[ ... ]` and `@\[ ... ]` without substitutions and references such as `flag@root`. Do not infer unprefixed runtime-variable names from command semantics; headers such as `[[OPTION] ... ]` retain the previous counting rule. This filter covers explicitly marked variables and substitutions, not every variable mechanism in the engine.
- Normalize text with Unicode `casefold()`. Exclude whole `yes` and `no` elements regardless of case or quotation. Retain substrings in `no_name` and `"yes no"`; the substitution filter excludes `$YES$`.
- Count strings as whole elements without outer quotes, including empty strings. Do not decode escapes or interpret numbers, paths, identifiers, or substitutions. `1`, `1.0`, and `01` differ.
- A `[[!OPTION] ... ]` conditional contributes `OPTION` and its contents. Formulas without substitutions retain complete notation as one element. `rgb { 1 0 1 }` contributes tag and elements.
- Assignment/comparison symbols, braces, comments, whitespace, and BOM are excluded. String, formula, and substitution interiors are not parsed separately.
- Remove global singletons after merging all files. Do not filter separately per file: single `FROM` and `from` occurrences produce retained `from:2`.
- Sort by descending count, then ascending normalized Unicode text.
- Structural errors exclude the entire file and are recorded. Do not fall back to tokenization or count partial trees.

## Coverage and results

All `.txt` files in `common/` and `events/` were scanned recursively under `E:/SteamLibrary/steamapps/common/Stellaris`, the version previously researched as 4.5.4.

| Metric | Result |
| --- | ---: |
| Discovered files | 2,238 |
| Successfully parsed and counted | 2,235 |
| Excluded prose documents | 2 |
| Files with a known structural error | 1 |
| Unexpected diagnostics | 0 |
| Excluded logical-operator names | 36,026 |
| Skipped outer inline_script calls | 6,885 |
| Text occurrences after structural exclusions, before text filters | 1,756,330 |
| Excluded yes occurrences | 76,144 |
| Excluded no occurrences | 29,659 |
| Excluded variable and parameterized-text occurrences, before frequency filtering | 36,247 |
| Distinct excluded variable and parameterized texts, including singletons | 4,677 |
| Other excluded globally singleton elements | 95,455 |
| Final occurrences | 1,518,825 |
| Final distinct elements | 56,268 |

Excluded operations: `AND:2869`, `OR:11647`, `NOT:16232`, `NAND:339`, `NOR:4939`. Before variable and substitution filtering, counted 74 opaque formulas and 53 conditional headers.

Excluded prose: `common/HOW_TO_MAKE_NEW_SHIPS.txt` and `common/edicts/99_README_EDICTS.txt`. `common/named_colors/01_trait_colors.txt` was not counted because of the known missing operator on line 65. The previous tokenizer counted it, but this pass requires a successful tree. The source was not repaired. Other extensions are covered by the [pattern research](RESEARCH_SCRIPT_PATTERNS_EN.md).

Beginning of the list:

```text
trigger:27764
name:25953
modifier:24988
owner:24440
id:20358
from:19085
limit:19049
1:18761
desc:14849
option:13527
```

The third pass had 59,828 distinct elements and 1,553,955 occurrences. Removing 3,560 variable and substitution rows from that list excludes 35,130 occurrences. Another 1,117 singleton texts are now counted under variable/substitution exclusions instead of singleton exclusions. Every other row and frequency exactly matches the previous result. Before frequency filtering, 32,284 script-variable occurrences and 3,963 other parameterized-text occurrences are excluded; overlapping matches count once.

## Files and rerunning

- [Two scalar-use lists](RESEARCH_SCALAR_USAGE_EN.md) — separate research into construct right-hand sides and texts used only as values; recalculated with the same variable exclusion.
- [frequencies.txt](../data/text_frequency/frequencies.txt) — `text:count` list; the last colon is the separator. Quotes, backslashes, and line breaks use JSON escaping without outer quotes.
- [frequencies.json](../data/text_frequency/frequencies.json) — the same ordered `text`/`count` list.
- [report.json](../data/text_frequency/report.json) — settings, totals, exclusions, diagnostics, and input hashes. `raw_occurrences` means AST text after structural exclusions but before `yes/no`, variable, and singleton filters, not all source words. `variable_filter` records the precise rule; `excluded_variable_*` counters include all frequencies.
- [source_manifest.json](../data/text_frequency/source_manifest.json) — paths, SHA-256 hashes, statuses, and per-file counts for successfully parsed documents.
- [validation_report.json](../data/text_frequency/validation_report.json) — checks.
- [Second-pass snapshot](../../TMP/WEB_STTV/text_frequency/pass_2_snapshot/report.json) — previous artifacts remain under `TMP/WEB_STTV/text_frequency/pass_2_snapshot/`.
- [Third-pass snapshot](../../TMP/WEB_STTV/text_frequency/pass_3_snapshot/report.json) — lists before variable exclusion, including both scalar-use lists.

Research modules: [count_text.py](../../TMP/WEB_STTV/text_frequency/count_text.py), [frequency_tree.py](../../TMP/WEB_STTV/text_frequency/frequency_tree.py), [verify_frequency.py](../../TMP/WEB_STTV/text_frequency/verify_frequency.py). All three lists share the filter in [variable_filter.py](../../TMP/WEB_STTV/text_frequency/variable_filter.py). Paths use product settings; output is written to `WORK_DIR/text_frequency/` within the repository. Rerunning replaces current results.

From the repository root:

```powershell
& WEB_STTV/data/.venv/Scripts/python.exe -B TMP/WEB_STTV/text_frequency/count_text.py
& WEB_STTV/data/.venv/Scripts/python.exe -B TMP/WEB_STTV/text_frequency/verify_frequency.py
```

## Checks and limitations

For each parsed file, the AST text sequence matches independent token extraction after excluding exact inline-call spans and logical-node names. Checks cover complete token coverage, ordering, totals, uniqueness, and JSON reconstruction from TXT.

Fixtures cover preservation of logical bodies and ordinary text matching logical names, both inline forms, ignored malformed internal inline content, case, strings, numbers, parameters, formulas, and global frequency filtering.

Balance: **1,518,825 + 105,803 + 36,247 + 95,455 = 1,756,330**. The 36,026 and 6,885 counters match the independent stage-four audit. Additional checks cover variable definitions and references, parameterized text, preserved formulas without substitutions, and embedded `@` references; the entire result matches the third pass with only variable and substitution rows removed. SHA-256 hashes of all 2,238 sources match the second pass and before/after readings; product code, configurations, schemas, profile, and database remain unchanged. Checks passed with no unexpected diagnostics.

Frequency describes remaining physical text, not command execution. Skipped call contents are not reconstructed from raw text. The user decides further classification.
