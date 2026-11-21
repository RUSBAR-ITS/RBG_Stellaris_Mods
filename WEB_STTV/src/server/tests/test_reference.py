import json
import unittest
from pathlib import Path
from threading import Lock
from unittest.mock import Mock

from sttv_server.tree.builder import PreparedTree
from sttv_server.tree.empire import compatible
from sttv_server.tree.errors import BuildError, Busy
from sttv_server.tree.layout import place
from sttv_server.tree.service import ReferenceTrees


RULES = json.loads((Path(__file__).resolve().parents[1] / 'config/reference_tree.json').read_text())
CONTEXT = RULES, lambda node, scope: None


def term(key, value):
    return {'kind': 'assignment', 'operator': '=', 'key': {'text': key},
            'value': value if isinstance(value, dict) else {'kind': 'scalar', 'text': value}}


def block(*items):
    return {'kind': 'block', 'items': list(items)}


def logic(op, *items):
    return {'kind': 'logical_operation', 'operator': op, 'body': block(*items)}


def tech(*conditions):
    return {'potential': [block(*conditions)]}


class EmpireTests(unittest.TestCase):
    def test_nomad_and_default(self):
        nomad = term('is_nomadic', 'yes')
        options = {'arkship': tech(nomad), 'station': tech(term('is_nomadic', 'no'))}
        for child, keep in [(tech(), ['station']), (tech(nomad), ['arkship'])]:
            self.assertEqual(compatible(child, list(options), options, CONTEXT)[0], keep)

    def test_alternatives_unknown_and_negation(self):
        tests = [term('has_origin', key) for key in 'abc']
        options = {key: tech(value) for key, value in zip('abc', tests)}
        child = tech(logic('OR', tests[0], logic('AND', tests[1], logic('NOT', tests[2]))))
        self.assertEqual(compatible(child, list(options), options, CONTEXT)[0], ['a', 'b'])
        child = tech(logic('OR', child['potential'][0], term('unknown_state', 'yes')))
        self.assertEqual(compatible(child, list(options), options, CONTEXT)[0], list('abc'))
        civics = [term('has_civic', 'civic_' + str(i)) for i in range(15)]
        options = {'positive': tech(civics[0]), 'negative': tech(logic('NOT', civics[0]))}
        self.assertEqual(compatible(tech(*civics), list(options), options, CONTEXT)[0], ['positive'])

    def test_founder_is_not_a_federation_member(self):
        machine = term('is_archetype', 'MACHINE')
        options = {'founder': tech(term('founder_species', block(machine))), 'any': tech()}
        child = tech(term('federation', block(term('any_member', block(machine)))))
        self.assertEqual(compatible(child, list(options), options, CONTEXT)[0], ['any'])


class TreeTests(unittest.TestCase):
    def test_zero_matches_tie_and_hidden_parent(self):
        fixture = object.__new__(PreparedTree)
        fixture.options = {'parent_rules': [{'id': 'mandatory', 'enabled': True}]}
        fixture.analysis = Mock()
        fixture.evidence = None
        fixture.techs = {k: {'parents': [], 'mandatory': []} for k in 'abc'}
        fixture.techs['c']['parents'] = ['a', 'b']
        for shown, expected in [('abc', None), ('bc', 'b'), ('c', None)]:
            nodes = {k: {'children': [], 'availability': k in shown, 'parent_tech': None} for k in 'abc'}
            fixture.parents(nodes, {}, 'test')
            self.assertEqual(nodes['c']['parent_tech'], expected)
            self.assertEqual(nodes['b']['children'], ['c'] if expected else [])

    def test_bilingual_cross_area_and_cycle(self):
        nodes = {k: {'availability': True, 'parent_tech': None, 'children': [], 'area': 'physics',
                     'location': {}} for k in 'abc'}
        nodes['c'].update(parent_tech='a', area='society')
        nodes['a']['children'] = ['c']
        techs = {k: {'tier': 1, 'starting': False, 'levels': 1, 'parents': []} for k in nodes}
        ranks = {'ru': dict(a=1, b=0, c=2), 'en': dict(a=0, b=1, c=2)}
        place(nodes, techs, ranks, RULES['layout'])
        self.assertEqual(nodes['a']['location'], {'ru': [1, 1], 'en': [1, 0]})
        self.assertEqual(nodes['c']['location'], {'ru': [1, 0], 'en': [1, 0]})
        nodes['a']['parent_tech'] = 'c'
        with self.assertRaisesRegex(BuildError, 'cycle'):
            place(nodes, techs, ranks, RULES['layout'])

    def test_cleanup_exclusion(self):
        trees = object.__new__(ReferenceTrees)
        trees.opens, trees.clearing, trees.gate = 0, False, Lock()
        with trees.operation():
            with self.assertRaises(Busy):
                trees.clear()
        with trees.operation(clear=True):
            with self.assertRaises(Busy):
                trees.open({})
