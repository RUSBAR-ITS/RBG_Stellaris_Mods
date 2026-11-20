"""Verify AST counting, exclusions, saved artifacts, and unchanged sources."""

from collections import Counter
from pathlib import Path
import json

from count_text import (EXCLUDED_TEXTS, MINIMUM_COUNT, EXPECTED_ERRORS,
                        fingerprint, frequency_rows, measure, read_json, settings, write_json)
from document_package.errors import BuildError
from variable_filter import VARIABLE_FILTER, is_excluded_variable


def fixtures(syntax):
    sample = r'''
# AND OR yes should not be counted from this comment.
AND = { OR = { item = yes item = "yes" values = { AND 10 -1 1.5 } } }
text = "AND OR"
escaped = "quote \"AND\""
formula = @[ 1 + @factor ]
[[!OPTION]
    value = "$NAME|AND$"
]
color = rgb { 1 0 1 }
foo = foo
and = "AND"
empty = ""
'''
    expected = Counter({
        "and": 3, "item": 2, "values": 1, "10": 1, "-1": 1, "1.5": 1,
        "text": 1, "and or": 1, "escaped": 1, r'quote \"and\"': 1,
        "formula": 1, "@[ 1 + @factor ]": 1, "option": 1,
        "value": 1, "color": 1, "rgb": 1, "1": 2, "0": 1,
        "foo": 2, "empty": 1, "": 1,
    })
    actual, details, excluded = measure(sample, syntax)
    assert actual == expected, (actual - expected, expected - actual)
    assert excluded == Counter({"yes": 2})
    assert details["logical_operator_counts"] == {"AND": 1, "OR": 1}
    assert details["skipped_inline_scripts"] == 0
    actual, _, excluded = measure('yes YES Yes no NO No "YES" "No" yes_man no_name', syntax)
    assert actual == Counter({"yes_man": 1, "no_name": 1})
    assert excluded == Counter({"yes": 4, "no": 4})
    combined = measure("FROM rare", syntax)[0] + measure("from From RARE unique", syntax)[0]
    assert frequency_rows(combined) == [{"text": "from", "count": 3}, {"text": "rare", "count": 2}]
    assert measure('"Stra\u00dfe" "STRASSE"', syntax)[0] == Counter({"strasse": 2})
    assert measure("a=1 b<2 c>3 d<=4 e>=5 f!=6", syntax)[0] == Counter("a1b2c3d4e5f6")
    actual, details, excluded = measure('''AND = { NOR = {} not = { keep = keep }
        inline_script = { AND = { malformed = = $OPEN } inline_script = nested }
        Inline_Script = "missing/path" inline_script = bare/path after = 2 }''', syntax)
    assert actual == Counter({"keep": 2, "after": 1, "2": 1}) and not excluded
    assert details["logical_operator_counts"] == {"AND": 1, "NOR": 1, "NOT": 1}
    assert details["skipped_inline_scripts"] == 3
    actual, details, _ = measure('NOT = ethic_a "AND" = {} text = AND reference = "$AND$"', syntax)
    assert actual == Counter({'not': 1, 'ethic_a': 1, 'and': 2, 'text': 1, 'reference': 1})
    assert details['excluded_logical_operators'] == 0
    actual, details, _ = measure('''@Amount = 10 amount = @AMOUNT
        @s_t$TIER$_cost = 20 cost = @s_t$TIER$_cost
        quoted = "@Amount" flag = flag@root parameter = $AMOUNT$
        formula = @[ amount + 1 ] text = "mail@example.org"''', syntax)
    assert actual == Counter({'10': 1, 'amount': 1, '20': 1, 'cost': 1, 'quoted': 1,
                              'flag': 1, 'flag@root': 1, 'parameter': 1,
                              'formula': 1, '@[ amount + 1 ]': 1, 'text': 1, 'mail@example.org': 1})
    assert details['excluded_variable_counts'] == {'@amount': 3, '@s_t$tier$_cost': 2, '$amount$': 1}
    assert details['excluded_variable_occurrences'] == 6
    actual, details, _ = measure('''a = prefix_$NAME$ b = "$VALUE|text with spaces$"
        c = @[ $VALUE$ + 1 ] d = "price$" e = "$5 USD$"''', syntax)
    assert actual == Counter({'a': 1, 'b': 1, 'c': 1, 'd': 1, 'price$': 1, 'e': 1, '$5 usd$': 1})
    assert details['excluded_variable_categories'] == {'template_parameter': 3}
    for text in ("name { number = 2 }", "inline_script = {"):
        try:
            measure(text, syntax)
        except BuildError:
            pass
        else:
            raise AssertionError("A structural defect must not fall back to tokenization")


def main():
    selected = settings("Optional earlier frequency output directory, before variable exclusion")
    fixtures(selected.syntax)
    output = selected.output
    rows, report, manifest = [read_json(output / name) for name in
                              ("frequencies.json", "report.json", "source_manifest.json")]
    assert rows == sorted(rows, key=lambda row: (-row["count"], row["text"]))
    assert len({row["text"] for row in rows}) == len(rows) == report["unique_texts"]
    assert all(isinstance(row["count"], int) and row["count"] >= MINIMUM_COUNT for row in rows)
    assert all(row["text"] == row["text"].casefold() and row["text"] not in EXCLUDED_TEXTS for row in rows)
    assert all(not is_excluded_variable(row['text']) for row in rows)
    assert report['variable_filter'] == VARIABLE_FILTER
    assert sum(report['excluded_variable_categories'].values()) == report['excluded_variable_occurrences']
    assert sum(row["count"] for row in rows) == report["occurrences"]
    assert report["raw_occurrences"] == (report["occurrences"] + report["excluded_singletons"]
                                         + report["excluded_text_occurrences"] + report['excluded_variable_occurrences'])
    for key in ("raw_occurrences", "excluded_text_occurrences", "excluded_logical_operators", "skipped_inline_scripts",
                'excluded_variable_occurrences'):
        assert report[key] == sum(row.get(key, 0) for row in manifest), key
    assert report["excluded_text_occurrences"] == sum(report["excluded_text_counts"].values())
    assert report["minimum_count"] == MINIMUM_COUNT
    assert report["case_normalization"] == "unicode_casefold"
    assert report["excluded_texts"] == sorted(EXCLUDED_TEXTS)
    restored = []
    for line in (output / "frequencies.txt").read_text(encoding="utf-8").splitlines():
        escaped, count = line.rsplit(":", 1)
        restored.append({"text": json.loads('"' + escaped + '"'), "count": int(count)})
    assert restored == rows
    assert len(manifest) == report["txt_files"]
    assert report["counted_files"] + len(report["excluded_prose"]) + report["failed_files"] == len(manifest)
    assert not report["unexpected_diagnostics"] and report["source_hashes_unchanged"]
    assert all(EXPECTED_ERRORS.get(row["file"]) == (row["code"], row["line"])
               for row in report["diagnostics"])
    assert all(fingerprint(selected.game / row["file"]) == row["sha256"] for row in manifest)
    assert all(fingerprint(Path(path)) == digest for path, digest in report["input_hashes"].items())
    result = {"status": "passed", "checks": [
        "hand_counted_ast_fixture", "tree_token_sequence_equality", "token_coverage",
        "logical_operator_names_excluded_but_bodies_counted", "ordinary_logical_name_text_retained",
        "inline_calls_and_payloads_absent", "malformed_inline_internals_not_parsed",
        "no_lexical_fallback_for_failed_documents", "casefold_normalization",
        "whole_element_boolean_exclusion", "minimum_count_after_global_aggregation",
        "ordering_uniqueness_and_totals", "text_json_round_trip", "known_diagnostic_only",
        "unchanged_sources_and_product_inputs",
        'script_variables_excluded_including_parameterized_names',
        'parameterized_names_strings_and_formulas_excluded_whole',
        'plain_formulas_embedded_at_and_literal_dollar_text_retained',
    ]}
    if selected.reference:
        old = read_json(selected.reference / "frequencies.json")
        assert rows == [row for row in old if not is_excluded_variable(row["text"])]
        earlier = read_json(selected.reference / "source_manifest.json")
        assert {r["file"]: r["sha256"] for r in earlier} == {r["file"]: r["sha256"] for r in manifest}
        result["checks"].extend(["same_reference_sources", "only_variable_rows_removed_from_reference"])
    write_json(output / "validation_report.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
