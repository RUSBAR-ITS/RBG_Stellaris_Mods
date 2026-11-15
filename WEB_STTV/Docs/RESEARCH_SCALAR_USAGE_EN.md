# Research into scalar values and construct right-hand sides

## Contents

- [Purpose and scope](#purpose-and-scope)
- [Rules for the two lists](#rules-for-the-two-lists)
- [Results](#results)
- [Examples and exclusions](#examples-and-exclusions)
- [Files and rerunning](#files-and-rerunning)
- [Checks](#checks)

## Purpose and scope

**Current working TXT:** after extracting the `is_`, `has_`, `set_`, `add_`, and `remove_` families, the user requested removal of their 635 entries from `scalar_assignments.txt`. It now contains 3,123 lines. JSON, result tables, and checks below retain the complete analysis snapshot before this manual cleanup. Rerunning the handler recreates the TXT from the full analysis.

At the user's request on 2026-11-15, two lists were extracted from the [fourth frequency pass](RESEARCH_TEXT_FREQUENCY_EN.md). Research uses the current parser AST, not command semantics or presumed purpose. It does not change parser rules or add classifications to the agreed language vocabulary.

“Always” means every observed use in successfully parsed files of the current `common/` and `events/` corpus. `inline_script` invocation contents are skipped; template files explicitly included in the corpus are parsed independently. Future versions, mods, and the failed file are outside this claim.

The 56,268 texts in the current frequency list were examined: case is merged with `casefold`; `yes`/`no`, script variables written as `@name`, `$NAME$` substitutions, and global singletons are already excluded. Quotes are not part of matching text, but JSON preserves usage forms.

## Rules for the two lists

1. **Construct names with scalar right-hand sides.** At least one use as an `Assignment` key exists, and every such use has a `Scalar` on the right. No right-hand `Block`, `Formula`, or `TaggedBlock` occurs. Block-tag and logical-name uses also disqualify the candidate. The text may additionally occur as a value; this is recorded separately.
2. **Texts occurring only as scalar values.** Every occurrence is a right-hand `Scalar` or a standalone scalar in a list/sequence. There are no key, block-tag, logical-name, formula, or conditional-header parameter uses.

`Scalar` means one structural value. It can be a number, string, identifier, reference, or contain substitutions. This does not establish that it is constant or a literal. Formulas have a separate parser node type and are excluded from these lists.

Both lists exclude whole `@name` spellings and text containing `$NAME$` substitutions, including `@s_t$TIER$_cost` and `prefix_$NAME$`. The `cost` key in `cost = @cost` remains a candidate with a scalar right-hand side: the variable text is removed, not the entire expression. References such as `flag@root` and unmarked runtime-variable names are not automatically excluded. The shared filter is described in the [frequency research](RESEARCH_TEXT_FREQUENCY_EN.md).

TXT retains the original `text:count` format and ordering. Counts are **total text frequencies**, not only key occurrences. For example, `factor:13475` includes 13,465 keys and 10 values. JSON separately records `roles`, `right_hand_types`, `assignment_operators`, `scalar_forms`, and examples with file, line, and column.

## Results

| Metric | Count |
| --- | ---: |
| Input texts | 56,268 |
| Input occurrences | 1,518,825 |
| Names in the first list | 3,758 |
| Total occurrences of first-list texts | 395,621 |
| Of these, key occurrences | 389,074 |
| First-list names also used as values | 297 |
| Texts in the second list | 33,880 |
| Second-list occurrences | 218,172 |
| Texts meeting neither criterion | 18,630 |

The lists do not overlap. Unselected texts are not declared erroneous or unsupported; they have other or mixed usage forms.

Coverage matches the fourth pass: 2,238 files, 2,235 parsed, two prose documents excluded, and one known error in `common/named_colors/01_trait_colors.txt:65`. Skipped 6,885 outer `inline_script` calls.

## Examples and exclusions

First-list leaders: `id:20358`, `factor:13475`, `has_country_flag:12514`, `template:10368`, `is_triggered_only:9546`, `exists:9484`, `days:7834`.

Second-list leaders: `0.5:2580`, `0.1:2290`, `0.25:1583`, `0.05:1390`, `1000:1273`, `1.5:1210`. Textual identifiers include `large_armor_5:558`.

| Text | Key uses with Scalar | Key uses with Block | Conclusion |
| --- | ---: | ---: | --- |
| `id` | 20,358 | 0 | First list |
| `name` | 24,979 | 762 | Right-hand side is not always scalar |
| `desc` | 10,634 | 4,215 | Right-hand side is not always scalar |
| `text` | 7,790 | 4,935 | Right-hand side is not always scalar |
| `icon` | 10,905 | 386 | Right-hand side is not always scalar |
| `owner` | 1,415 | 18,247 | Right-hand side is not always scalar |

Numbers `0` and `1` are absent from the second list because they also occur as keys. For example, `common/anomalies/00_anomaly_categories.txt:21` contains `1 = anomaly.35`, while line 54 starts `0 = { ... }`. Numeric spelling alone does not determine an element's structural position.

## Files and rerunning

- [scalar_assignments.txt](../data/text_frequency/scalar_analysis/scalar_assignments.txt) and [JSON](../data/text_frequency/scalar_analysis/scalar_assignments.json) — first list.
- [scalar_values.txt](../data/text_frequency/scalar_analysis/scalar_values.txt) and [JSON](../data/text_frequency/scalar_analysis/scalar_values.json) — second list.
- [usage_inventory.json](../data/text_frequency/scalar_analysis/usage_inventory.json) — all 56,268 texts with usage forms and examples, including rejected candidates.
- [report.json](../data/text_frequency/scalar_analysis/report.json), [source_manifest.json](../data/text_frequency/scalar_analysis/source_manifest.json), [validation_report.json](../data/text_frequency/scalar_analysis/validation_report.json) — coverage, totals, diagnostics, hashes, and checks.

Handler: `TMP/WEB_STTV/text_frequency/audit_scalar_usage.py`; traversal and criteria reside in `scalar_usage.py`, checks in `verify_scalar_usage.py`. Inputs are the current frequency list, its manifest, and product settings. Results go to `WORK_DIR/text_frequency/scalar_analysis/`; the original frequency list remains intact.

```powershell
& WEB_STTV/data/.venv/Scripts/python.exe -B TMP/WEB_STTV/text_frequency/audit_scalar_usage.py
& WEB_STTV/data/.venv/Scripts/python.exe -B TMP/WEB_STTV/text_frequency/verify_scalar_usage.py
```

## Checks

All reparsed frequencies exactly matched the original 56,268 records. Checks cover role/right-hand-type totals, disjoint lists, ordering, and JSON reconstruction from TXT. Each text retains an example of every observed role/form.

Fixtures cover mixed right-hand sides, formulas, tagged blocks, numeric keys, case and quote merging, substitutions within Scalar, and ignored inline contents. Checks passed. Source, input-configuration, original-frequency, profile, and database hashes remain unchanged.

Comparison with the pre-filter snapshot confirmed that only variable and substitution rows were removed: 3,077 from the first list and 403 from the second. Frequencies and structural details of every other row are unchanged.
