"""Check the two scalar-use lists and structural counterexamples."""

from count_text import settings, read_json, write_json
from scalar_usage import UsageInventory, scalar_assignment, scalar_value_only
from stellaris_parser.script.parser import parse_text
from variable_filter import VARIABLE_FILTER, is_excluded_variable


def fixtures(syntax):
    text = '''
single = leaf SINGLE = "other_leaf" other = single
mixed = leaf mixed = {}
formula_rhs = @[ 1 + 2 ]
tag_rhs = rgb { 1 0 1 }
1 = { weighted = 2 }
values = { leaf unique leaf }
inline_script = { single = {} leaf = {} }
AND = { inside = leaf } AND = leaf
literal_ref = $VALUE$
'''
    vocabulary = ['single', 'mixed', 'formula_rhs', 'tag_rhs', 'rgb', '1', 'leaf', 'unique',
                  'and', 'inside', 'literal_ref', '$value$']
    inventory = UsageInventory(vocabulary)
    inventory.consume(parse_text(text, syntax, role='template'), 'fixture.txt')
    rows = {row['text']: row for row in inventory.rows()}
    assert {name for name, row in rows.items() if scalar_assignment(row)} == {
        'single', 'inside', 'literal_ref'}
    assert {name for name, row in rows.items() if scalar_value_only(row)} == {
        'leaf', 'unique'}
    assert rows['$value$']['count'] == 0
    assert rows['single']['roles'] == {'assignment_key': 2, 'scalar_value': 1}
    assert rows['mixed']['right_hand_types'] == {'Scalar': 1, 'Block': 1}
    assert rows['formula_rhs']['right_hand_types'] == {'Formula': 1}
    assert rows['tag_rhs']['right_hand_types'] == {'TaggedBlock': 1}
    assert rows['rgb']['roles'] == {'block_tag': 1}
    assert rows['1']['roles']['assignment_key'] == 1
    assert rows['and']['logical_name_occurrences'] == 1
    assert rows['literal_ref']['right_hand_types'] == {'Scalar': 1}
    text = '[[P] x = P ] "FIELD" = 1 field = {}'
    inventory = UsageInventory(['p', 'field'])
    inventory.consume(parse_text(text, syntax, role='template'), 'fixture.txt')
    rows = inventory.rows()
    assert not any(scalar_assignment(row) or scalar_value_only(row) for row in rows)
    text = '@v = 1 uses = @v only_value = @external @s_$P$ = 2 flag = thing@root'
    inventory = UsageInventory(['@v', '@external', '@s_$p$', 'uses', 'only_value', 'thing@root'])
    inventory.consume(parse_text(text, syntax, role='template'), 'variables.txt')
    rows = {row['text']: row for row in inventory.rows()}
    assert all(rows[name]['count'] == 0 for name in ('@v', '@external', '@s_$p$'))
    assert scalar_assignment(rows['uses']) and scalar_assignment(rows['only_value'])
    assert scalar_value_only(rows['thing@root'])


def main():
    selected = settings("Optional earlier frequency output directory, before variable exclusion")
    fixtures(selected.syntax)
    base = selected.output
    folder = base / 'scalar_analysis'
    all_rows = read_json(folder / 'usage_inventory.json')
    first, second = [read_json(folder / (name + '.json')) for name in ('scalar_assignments', 'scalar_values')]
    report = read_json(folder / 'report.json')
    assert report['variable_filter'] == VARIABLE_FILTER
    frequencies = read_json(base / 'frequencies.json')
    assert [{'text': row['text'], 'count': row['count']} for row in all_rows] == frequencies
    assert first == [row for row in all_rows if scalar_assignment(row)]
    assert second == [row for row in all_rows if scalar_value_only(row)]
    assert len(first) == report['scalar_assignments'] and len(second) == report['scalar_values']
    assert not ({row['text'] for row in first} & {row['text'] for row in second})
    for row in all_rows:
        assert not is_excluded_variable(row['text'])
        assert row['count'] == sum(row['roles'].values())
        assert row['roles'].get('assignment_key', 0) == sum(row['right_hand_types'].values())
        assert sum(row['right_hand_types'].values()) == sum(row['assignment_operators'].values())
        assert row['examples'] and row['count'] >= 2
    import json
    for name, rows in [('scalar_assignments', first), ('scalar_values', second)]:
        restored = []
        for line in (folder / (name + '.txt')).read_text(encoding='utf-8').splitlines():
            escaped, count = line.rsplit(':', 1)
            restored.append({'text': json.loads('"' + escaped + '"'), 'count': int(count)})
        assert restored == [{'text': row['text'], 'count': row['count']} for row in rows]
    result = {'status': 'passed', 'checks': [
        'hand_counted_structural_examples', 'case_and_quoted_key_merging',
        'mixed_rhs_block_formula_and_tagged_block_rejection', 'number_used_as_key_rejection',
        'logical_names_tags_and_conditional_headers_not_values', 'inline_payload_does_not_affect_classification',
        'parameterized_scalar_excluded_without_changing_rhs_type', 'all_original_frequency_counts_match',
        'selection_rules_and_disjoint_lists', 'role_rhs_operator_totals', 'examples_present',
        'txt_json_round_trip_and_ordering',
        'variables_excluded_from_both_lists', 'keys_with_variable_rhs_remain_scalar_assignments',
    ]}
    if selected.reference:
        for name, rows in (("scalar_assignments", first), ("scalar_values", second)):
            old = read_json(selected.reference / "scalar_analysis" / (name + ".json"))
            assert rows == [row for row in old if not is_excluded_variable(row["text"])]
        result["checks"].append("only_variable_rows_removed_from_reference")
    write_json(folder / 'validation_report.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
