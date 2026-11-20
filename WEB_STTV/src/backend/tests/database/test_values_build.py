"""Preserve calculation boundaries, binding environments, and mixed history."""

from copy import deepcopy

from database.value_support import ValueFixture
from sttv.database.validation import validate_database
from stellaris_parser.script.parser import parse_text
from sttv.sources.settings import load_settings
from sttv.sources.expansion import expansion_context
from script.corpus_statistics import Statistics


class ValueBuildTests(ValueFixture):
    def test_scalar_position_order_and_unevaluated_operations(self):
        self.setup_values('constant={base=1.25 mult=2 mult=3}',
                          'before=0 factor=value:constant after=1')
        doc, report = self.document()
        self.assertEqual([n['key']['text'] for n in doc['items']], ['before', 'factor', 'after'])
        node = doc['items'][1]['value']
        self.assertEqual(node['kind'], 'script_value')
        self.assertIsNone(node['scope'])
        self.assertEqual([n['value']['text'] for n in node['body']['items']], ['1.25', '2', '3'])
        self.assertEqual(doc['metadata']['expansions'][0]['insertion'], {'node': '/items/1/value'})
        self.assertEqual(report['counts']['scripted_calls']['script_value']['expanded'], 1)

    def test_nested_argument_and_scopes_remain_separate(self):
        self.setup_values('outer={base=$MULT$} inner={base=5}',
                          'v=owner.value:outer|MULT|event_target:x.value:inner|')
        doc, _ = self.document()
        outer = doc['items'][0]['value']
        inner = outer['body']['items'][0]['value']
        self.assertEqual([outer['scope'], inner['scope']], ['owner', 'event_target:x'])
        history = doc['metadata']['expansions']
        self.assertEqual(history[1]['parent_id'], history[0]['id'])
        self.assertEqual(history[1]['insertion'], {'node': '/items/0/value/body/items/0/value'})
        self.assertEqual(history[0]['arguments'][0]['value'], 'event_target:x.value:inner')

    def test_defaults_conditions_empty_and_unused_arguments(self):
        self.setup_values('x={base=$N|3$ [[ON] add=$A$] [[!ON] subtract=1] '
                          '[[UNUSED] mult=$MISSING$] text="$EMPTY|fallback$"}',
                          'a=value:x b=value:x|ON|no|EMPTY|| '
                          'c=value:x|ON|yes|A|value:y|N|no|UNUSED|no| '
                          'd=value:y|UNUSED|value:missing|')
        with (self.values / 'definitions.txt').open('a', encoding='utf-8') as stream:
            stream.write(' y={base=7}')
        doc, report = self.document()
        bodies = [n['value']['body']['items'] for n in doc['items']]
        self.assertEqual(bodies[0][0]['value']['text'], '3')
        self.assertEqual(bodies[1][-1]['value']['text'], '')
        self.assertEqual(bodies[2][0]['value']['text'], 'no')
        self.assertEqual(bodies[2][1]['value']['kind'], 'script_value')
        self.assertEqual(report['counts']['warnings'], 1)

    def test_four_kinds_and_comparison_value_history(self):
        self.setup_values('outer={inline_script=part ready>value:inner} inner={base=2}', 'x=value:outer')
        (self.inline/'part.txt').write_text('emit={N=value:inner}', encoding='utf-8')
        (self.effects/'a.txt').write_text('emit={amount=$N$}', encoding='utf-8')
        (self.triggers/'a.txt').write_text('ready={some_condition=yes}', encoding='utf-8')
        doc, _ = self.document()
        records = doc['metadata']['expansions']
        self.assertEqual([r['kind'] for r in records],
                         ['script_value', 'inline_script', 'scripted_effect', 'script_value',
                          'scripted_trigger', 'script_value'])
        comparison = doc['items'][0]['value']['body']['items'][1]
        self.assertEqual(comparison['operator'], '>')
        self.assertEqual(comparison['value']['kind'], 'script_value')
        self.assertEqual(records[-1]['parent_id'], records[-2]['id'])

    def test_local_argument_default_and_inline_static_values(self):
        self.setup_values('@n=20 x={base=@n add=$N|@n$ inline_script=part}',
                          '@n=10 a=value:x|N|@n| b=value:x')
        (self.inline/'part.txt').write_text('mult=@n', encoding='utf-8')
        doc, _ = self.document()
        bodies = [n['value']['body']['items'] for n in doc['items'][1:]]
        self.assertEqual([[n['value']['text'] for n in b] for b in bodies],
                         [['20', '10', '20'], ['20', '20', '20']])

    def test_static_alias_and_raw_parser_separation(self):
        self.setup_values(caller='@alias=value:constant x=@alias')
        doc, report = self.document()
        self.assertEqual(doc['items'][0]['value']['text'], 'value:constant')
        self.assertEqual(doc['items'][1]['value']['kind'], 'script_value')
        self.assertEqual(report['counts']['static_variables']['substituted'], 1)
        settings = load_settings(self.variable_file, self.config_file)
        raw = parse_text('x=value:constant', settings.syntax)
        self.assertEqual(type(raw.items[0].value).__name__, 'Scalar')

    def test_nonvalue_positions_and_independent_repetitions(self):
        self.setup_values(caller='value:constant=1 a="value:missing" b=@[value:missing] '
                          'c={value:constant value:constant} value=ordinary')
        doc, report = self.document()
        self.assertEqual(doc['items'][0]['key']['text'], 'value:constant')
        self.assertEqual(doc['items'][1]['value']['kind'], 'scalar')
        self.assertEqual(doc['items'][2]['value']['kind'], 'formula')
        self.assertEqual(report['counts']['scripted_calls']['script_value']['expanded'], 2)

    def test_library_names_are_separate_and_root_inline_is_indexed(self):
        self.setup_values('inline_script=library', 'same=yes x=value:same')
        (self.inline/'library.txt').write_text('@n=9 same={base=@n}', encoding='utf-8')
        (self.effects/'a.txt').write_text('same={effect=yes}', encoding='utf-8')
        doc, report = self.document()
        self.assertEqual(doc['items'][1]['value']['body']['items'][0]['value']['text'], '9')
        self.assertEqual(report['counts']['scripted_calls']['script_value']['definitions'], 1)

    def test_configurable_markers_and_name_case(self):
        self.setup_values('Constant={base=2}', 'x=owner/calc:CONSTANT~UNUSED~1~')
        self.change_options('script_values', reference_prefix='calc:', scope_separator='/', argument_separator='~')
        doc, _ = self.document()
        self.assertEqual(doc['items'][0]['value']['scope'], 'owner')

    def test_exact_indexed_name_and_parameter_case_configuration(self):
        self.setup_values('named.calculation={base=$MULT$}', 'x=value:named.calculation|mult|7|')
        self.change_options('scripted_calls', parameter_case_sensitive=False)
        doc, _ = self.document()
        self.assertEqual(doc['items'][0]['value']['body']['items'][0]['value']['text'], '7')

    def test_statistics_ignore_history_and_unreached_library(self):
        self.setup_values('x={base=2} unused={irrelevant=1}', 'a=value:x b=value:x')
        self.document()
        settings = load_settings(self.variable_file, self.config_file)
        from sttv.libraries.operation import library_operation
        with library_operation(settings, 'reuse'):
            context = expansion_context(settings)
        doc = parse_text('a=value:x b=value:x', settings.syntax, 'test.txt', expansion=context)
        statistics = Statistics()
        statistics.consume(doc)
        self.assertEqual(statistics.rows['base']['count'], 2)
        self.assertNotIn('irrelevant', statistics.rows)
        self.assertNotIn('value:x', statistics.rows)

    def test_corrupt_single_node_history_is_rejected(self):
        self.setup_values()
        self.document()
        saved = self.database()
        for change in ('pointer', 'missing', 'kind'):
            with self.subTest(change=change):
                database = deepcopy(saved)
                records = database['documents'][0]['metadata']['expansions']
                if change == 'pointer':
                    records[0]['insertion']['node'] = '/items/0/key'
                elif change == 'missing':
                    records.clear()
                else:
                    records[0]['kind'] = 'scripted_effect'
                with self.assertRaises(Exception):
                    validate_database(database)
