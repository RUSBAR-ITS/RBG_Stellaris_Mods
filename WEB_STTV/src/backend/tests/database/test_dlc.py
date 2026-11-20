"""Partial DLC semantics and visibility-aware reciprocal links."""

import json
import unittest

from sttv.common.errors import BuildError
from sttv.common.paths import PRODUCT_ROOT
from sttv.enrichment.dlc import catalog, filtering
from sttv.enrichment.dlc.evaluation import Evaluator
from sttv.enrichment.technology_tree.integrity import check_results
from sttv.enrichment.technology_tree.selection import calculate
from sttv.enrichment.technology_tree.evidence import Evidence


def scalar(text):
    return {'kind': 'scalar', 'text': str(text)}


def block(*items):
    return {'kind': 'block', 'items': list(items)}


def field(key, value):
    return {'kind': 'assignment', 'key': scalar(key), 'operator': '=',
            'value': value if isinstance(value, dict) else scalar(value)}


def logic(operator, *items):
    return {'kind': 'logical_operation', 'operator': operator, 'body': block(*items)}


def technology(key, *items, parents=()):
    return {'id': key, 'body': block(*items), 'source': {'pointer': '/items/0'}, 'parents': list(parents),
            'mandatory': list(parents), 'variant': 'base', 'area': 'physics', 'tier': 1, 'category': [],
            'prerequisites': block(), 'variant_condition': []}


class DlcTests(unittest.TestCase):
    def setUp(self):
        self.rules = json.loads((PRODUCT_ROOT / 'config/enrichment/dlc.json').read_text())
        self.names = {'a': 'A', 'b': 'B'}

    def outcome(self, *items, enabled=()):
        return filtering.visibility(technology('t', *items), self.names, enabled, self.rules)[0]

    def test_logic_unknown_scope_and_negation(self):
        evaluator = Evaluator(self.names, ['a'], self.rules)
        yes, no, unknown = field('host_has_dlc', 'A'), field('host_has_dlc', 'B'), field('is_nomadic', 'no')
        for operator, items, expected in [('AND', [yes, unknown], None), ('AND', [no, unknown], False),
                ('OR', [yes, unknown], True), ('OR', [no, unknown], None), ('NOT', [no], True),
                ('NOR', [no, no], True), ('NAND', [yes, no], True), ('NOT', [yes, no], None)]:
            with self.subTest(operator=operator, expected=expected):
                self.assertIs(evaluator.evaluate(logic(operator, *items), '/x')['value'], expected)
        self.assertIsNone(evaluator.evaluate(field('owner', block(no)), '/owner')['value'])
        self.assertIsNone(evaluator.evaluate(logic('NOT', scalar('A')), '/x')['value'])

    def test_potential_baseline_and_negative_unlock(self):
        dlc = field('host_has_dlc', 'A')
        self.assertFalse(self.outcome(field('potential', block(dlc)))['visible'])
        self.assertTrue(self.outcome(field('potential', block(logic('NOT', dlc))))['visible'])
        self.assertFalse(self.outcome(field('potential', block(logic('NOT', dlc))), enabled=['a'])['visible'])
        self.assertTrue(self.outcome(field('potential', block(field('always', 'no'), dlc)))['visible'])
        self.assertTrue(self.outcome(field('potential', block(field('always', 'no'))),
                                     field('potential', block(dlc)))['visible'])
        self.assertTrue(self.outcome(field('potential', block(logic('OR', dlc, field('unknown', 'yes')))))['visible'])

    def test_zero_modifier_and_unsupported_actions(self):
        condition = logic('OR', logic('NOT', field('host_has_dlc', 'A')), field('has_resource', block()))
        def weight(factor, *extra):
            return field('weight_modifier', block(field('modifier', block(field('factor', factor), condition, *extra))))
        self.assertFalse(self.outcome(weight(0))['visible'])
        self.assertTrue(self.outcome(weight(0), enabled=['a'])['visible'])
        self.assertTrue(self.outcome(weight(2), field('weight', 0))['visible'])
        self.assertTrue(self.outcome(weight(0, field('add', 1)))['visible'])
        other_action = weight(0)
        other_action['value']['items'].append(field('modifier', block(field('add', 1))))
        self.assertTrue(self.outcome(other_action)['visible'])
        self.assertTrue(self.outcome(field('weight_modifier', block(field('modifier', block(field('factor', 0))))))['visible'])

    def test_unknown_catalog_name_and_profile_order(self):
        result, diagnostics = filtering.visibility(technology('t', field('potential', block(field('host_has_dlc', 'C')))),
                                                  self.names, [], self.rules)
        self.assertTrue(result['visible'])
        self.assertEqual(diagnostics[0]['code'], 'unknown_dlc_name')
        self.assertEqual(catalog.profile(self.names, ['b', 'a']), catalog.profile(self.names, ['a', 'b']))
        with self.assertRaises(BuildError):
            catalog.profile(self.names, ['c'])

    def test_hidden_parent_never_restored_and_orphan_is_root(self):
        techs = {'a': technology('a', field('potential', block(field('host_has_dlc', 'A')))),
                 'b': technology('b'), 'c': technology('c', parents=['a', 'b']),
                 'd': technology('d', parents=['a'])}
        outcomes, _ = filtering.prepare(techs, self.names, [], self.rules)
        results, decisions, _ = calculate(filtering.select(techs, outcomes), Evidence(), {'rules': []}, {})
        notes = filtering.attach(results, decisions, techs, outcomes)
        check_results(results, techs)
        self.assertEqual(results['c']['parent_tech'], 'b')
        self.assertEqual(results['b']['children'], ['c'])
        self.assertEqual(results['a']['children'], [])
        self.assertEqual(results['d']['status'], 'root')
        self.assertEqual(notes[0]['code'], 'no_visible_parent')

    def test_wrapper_evidence_keeps_actual_pointer(self):
        result = self.outcome(field('potential', block(field('custom_tooltip', block(
            field('text', 'LABEL'), field('hidden_trigger', block(field('host_has_dlc', 'B'))))))))
        self.assertFalse(result['visible'])
        proof = result['evidence'][0]['children'][0]['children'][0]['children'][0]
        self.assertEqual(proof['dlc_id'], 'b')
        self.assertEqual(proof['pointer'], '/items/0/value/items/0/value/items/0/value/items/1/value/items/0')
