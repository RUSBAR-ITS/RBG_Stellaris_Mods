import unittest
from unittest.mock import patch

from sttv_server.technology_tooltip import technology_tooltip


def scalar(text):
    return {'kind': 'scalar', 'text': text}


def entry(key, value):
    return {'kind': 'assignment', 'key': scalar(key), 'operator': '=', 'value': value}


def block(*items):
    return {'kind': 'block', 'items': list(items)}


class TooltipTests(unittest.TestCase):
    def test_multiple_children_remain_inside_negation(self):
        from sttv_server.technology_tooltip import Content
        from sttv_server.tooltip_labels import Labels

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
        self.assertEqual(check['children'], [{'kind': 'unrecognized', 'expression': mystery}])
        self.assertEqual(flag['text'], 'Policy flag shared_flag')
        self.assertEqual(response['diagnostics'][0]['matches'], [('one', 'option'), ('two', 'option')])
