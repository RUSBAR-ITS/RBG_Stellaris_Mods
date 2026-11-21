import unittest
from unittest.mock import patch

from sttv_server.technology_tooltip import Content, technology_tooltip
from sttv_server.tooltip_labels import Labels


def scalar(text):
    return {'kind': 'scalar', 'text': text}


def entry(key, value):
    return {'kind': 'assignment', 'key': scalar(key), 'operator': '=', 'value': value}


def block(*items):
    return {'kind': 'block', 'items': list(items)}


def logic(operator, *children):
    return {'kind': 'logical_operation', 'operator': operator, 'body': block(*children)}


class TooltipTests(unittest.TestCase):
    def test_flags_use_scope_specific_labels_and_keep_unknown_checks(self):
        rules = {'tooltip_condition': {'prefix': 'test_', 'suffix': ''}}
        labels = Labels('en', rules, None)
        content = Content(labels)
        known = entry('has_country_flag', scalar('found'))
        unknown = entry('has_global_flag', scalar('found'))
        node = content.node(logic('NOR', known, unknown), ('potential',))
        strings = {'test_nor': 'None:', 'test_has_country_flag_found': 'A resource was found',
                   'test_has_global_flag': 'A special galaxy condition is met'}
        result = labels.resolve({'technology_id': 'tech_a', 'node': node},
                                lambda lang, keys: [(k, strings[k]) for k in keys if k in strings])
        self.assertEqual(result['node']['operator'], 'NOR')
        self.assertEqual([c['text'] for c in result['node']['children']],
                         [strings['test_has_country_flag_found'], strings['test_has_global_flag']])
        self.assertEqual(result['diagnostics'], [{'reason': 'missing_flag_label', 'check': 'has_global_flag',
                                                  'flag': 'found', 'technology': 'tech_a', 'language': 'en', 'section': 'potential'}])

    def test_ignored_country_flag_does_not_make_a_weight_bonus_unconditional(self):
        ignored = entry('has_country_flag', scalar('crystal_armor_1_weight'))
        other_scope = entry('has_global_flag', scalar('crystal_armor_1_weight'))
        content = Content(Labels('ru', {'tooltip_condition': {'suffix': ''}}, None))
        addition = entry('add', scalar('5'))
        def rule(*checks):
            return content.weight_rule(entry('modifier', block(addition, *checks)))

        self.assertIsNone(rule(ignored))
        self.assertIsNone(rule(logic('NOT', entry('hidden_trigger', block(ignored)))))
        self.assertNotIn('condition', rule())
        self.assertEqual(rule(ignored, other_scope)['condition']['key'], 'has_global_flag')
        self.assertEqual(rule(other_scope)['operations'][0]['value'], '5')

    def test_single_and_mixed_scalar_prerequisites(self):
        labels = Labels('en', {'tooltip_condition': {'prefix': 'test_', 'suffix': ''},
                               'technology_name': {'suffix': ''}}, None)
        content = Content(labels)
        a, b, c = (scalar(name) for name in ('a', 'b', 'c'))
        only = content.node(logic('OR', a), ('prerequisites',))
        self.assertEqual(only['id'], 'a')
        self.assertEqual(only['text'].keys, ('test_has_technology',))
        self.assertIsNone(only['text'].arguments['technology'].color)
        group = content.node(block(a, logic('OR', b, c)), ('prerequisites',))
        self.assertEqual(group['text'].keys, ('test_and',))
        required, alternatives = group['children']
        self.assertEqual(required, only)
        self.assertEqual(alternatives['text'].keys, ('test_technologies_or',))
        for tech in alternatives['children']:
            self.assertEqual(tech['text'].keys, (tech['id'],))
            self.assertEqual(tech['text'].color, 'Y')

    def test_negation_uses_the_selected_translation_or_keeps_its_group(self):
        labels = Labels('en', {'tooltip_condition': {'prefix': 'test_', 'suffix': ''}}, None)
        content = Content(labels)
        for key in ('has_origin', 'has_authority'):
            with self.subTest(key=key):
                expr = logic('NOT', logic('AND', logic('OR', entry(key, scalar('x')))))
                node = content.node(expr, ('allow',))
                slot = key.removeprefix('has_')
                texts = {'test_not': 'False:', 'test_' + key: 'Has {' + slot + '}', 'x': 'X'}

                def reader(lang, keys):
                    return [(k, texts[k]) for k in keys if k in texts]

                fallback = labels.resolve({'node': node}, reader)
                self.assertEqual(fallback['node']['operator'], 'NOT')
                self.assertEqual(fallback['node']['children'][0]['text'], 'Has X')
                self.assertNotIn('_negative_text', fallback['node'])
                self.assertIn({'reason': 'missing_localization', 'keys': ['test_not_' + key]}, fallback['diagnostics'])
                texts['test_not_' + key] = 'Without {' + slot + '}'
                negative = {'kind': 'condition', 'key': key, 'negated': True, 'text': 'Without X',
                            'reference': {'id': 'x', 'type': slot}}
                self.assertEqual(labels.resolve({'node': node}, reader)['node'], negative)
                double = content.node(logic('NOT', expr), ('allow',))
                self.assertEqual(labels.resolve({'node': double}, reader)['node'],
                                 {'kind': 'group', 'operator': 'NOT', 'text': 'False:', 'children': [negative]})

    def test_simplification_preserves_scopes_and_opaque_operands(self):
        content = Content(Labels('en', {'tooltip_condition': {'suffix': ''}}, None))
        check = entry('has_origin', scalar('x'))
        scope = entry('any_neighbor_country', block(check))
        simplified = content.node(logic('AND', scope), ('allow',))
        self.assertEqual(simplified['key'], 'any_neighbor_country')
        self.assertEqual(simplified['children'][0]['key'], 'has_origin')
        for item in (entry('unknown', block(check)), entry('custom_tooltip', scalar('caption')),
                     entry('hidden_trigger', block(check))):
            for op in ('AND', 'OR'):
                node = content.node(logic(op, item), ('allow',))
                self.assertEqual(node['operator'], op)
                self.assertEqual(node['children'], [content.node(item, ('allow',))])
        for op in ('AND', 'OR'):
            self.assertEqual(content.node(logic(op), ('allow',))['children'], [])
        invalid = {**check, 'operator': '!='}
        child, = content.node(logic('NOT', invalid), ('allow',))['children']
        self.assertEqual((child['kind'], child['expression']), ('partial', invalid))

    def test_headings_describe_the_direct_operands_in_the_same_scope(self):
        rules = {'tooltip_condition': {'prefix': 'sttv_', 'suffix': ''}, 'technology_name': {'suffix': ''}}
        content = Content(Labels('en', rules, None))
        a, b = (entry('has_technology', scalar(key)) for key in ('tech_a', 'tech_b'))
        for op in ('AND', 'OR', 'NOT', 'NAND', 'NOR'):
            with self.subTest(operator=op):
                items = [a] if op == 'NOT' else [a, b]
                group = content.node({'kind': 'logical_operation', 'operator': op, 'body': block(*items)}, ('allow',))
                self.assertEqual(group['text'].keys, ('sttv_technologies_' + op.lower(),))
                self.assertEqual(group['children'][0]['text'].keys, ('tech_a',))
                self.assertEqual(group['children'][0]['text'].color, 'Y')

        alternatives = {'kind': 'logical_operation', 'operator': 'OR', 'body': block(a, b)}
        for different in (entry('can_research_technology', scalar('tech_c')),
                          entry('any_neighbor_country', block(a)), alternatives):
            group = content.node(block(a, different), ('potential',))
            self.assertEqual(group['text'].keys, ('sttv_and',))
            self.assertEqual(group['children'][0]['text'].keys, ('sttv_has_technology',))
        self.assertEqual(group['children'][1]['text'].keys, ('sttv_technologies_or',))

    def test_multiple_children_remain_inside_negation(self):
        a = entry('has_origin', scalar('origin_a'))
        b = entry('has_civic', scalar('civic_b'))
        condition = {'kind': 'logical_operation', 'operator': 'NOT', 'body': block(a, b)}
        labels = Labels('en', {'tooltip_condition': {'prefix': 'sttv_', 'suffix': ''}}, None)
        group = Content(labels).node(condition, ('potential',))
        self.assertEqual(group['operator'], 'NOT')
        self.assertEqual([n['key'] for n in group['children']], ['has_origin', 'has_civic'])

    def test_allow_logic_captions_and_ambiguous_policy(self):
        mystery = entry('unknown_check', block(entry('has_technology', scalar('tech_other'))))
        hidden = entry('hidden_trigger', block(mystery))
        caption = entry('custom_tooltip', block(entry('text', scalar('caption_key')), hidden))
        policy = entry('has_policy_flag', scalar('shared_flag'))
        nand = {'kind': 'logical_operation', 'operator': 'NAND', 'body': block(caption, policy)}
        tech = {'body': block(entry('allow', block(nand)), entry('potential', block()))}
        option = entry('option', block(entry('name', scalar('option')),
                                       entry('policy_flags', block(scalar('shared_flag')))))
        matches = [{'id': key, 'body': block(option)} for key in ('one', 'two')]
        strings = {'sttv_nand': 'Not all', 'sttv_hidden_trigger': 'Condition',
                   'sttv_has_policy_flag_unresolved': 'Policy flag {flag}', 'caption_key': 'Game caption'}
        rules = {'tooltip_condition': {'prefix': 'sttv_', 'suffix': ''}}
        with patch('sttv_server.technology_tooltip.records', return_value=iter([tech])), \
             patch('sttv_server.tooltip_labels.records', return_value=matches):
            response = technology_tooltip(None, rules, lambda lang, keys: [(k, strings[k]) for k in keys if k in strings],
                                          'test', 'en')
        self.assertEqual(list(response['sections']), ['allow'])
        group, = response['sections']['allow']
        self.assertEqual(group['operator'], 'NAND')
        custom, flag = group['children']
        label, check = custom['children']
        self.assertEqual(label['text'], 'Game caption')
        partial, = check['children']
        self.assertEqual((partial['kind'], partial['expression']), ('partial', mystery))
        self.assertEqual(partial['children'][0]['id'], 'tech_other')
        self.assertEqual(flag['text'], 'Policy flag shared_flag')
        self.assertEqual(next(d['matches'] for d in response['diagnostics'] if 'matches' in d), [('one', 'option'), ('two', 'option')])
