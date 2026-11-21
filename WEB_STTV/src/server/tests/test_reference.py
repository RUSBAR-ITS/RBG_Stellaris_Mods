import json
import unittest
from pathlib import Path
from threading import Lock
from unittest.mock import MagicMock, Mock

from sttv_server.tree.builder import PreparedTree
from sttv_server.tree.empire import compatible
from sttv_server.tree.errors import BuildError, Busy, InvalidRequest
from sttv_server.tree.layout import place
from sttv_server.tree.event_technologies import classify, weight_status
from sttv_server.tree.service import ReferenceTrees
from sttv_server.progress_sources import ProgressSources


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
    def test_ready_tree_identity_and_request_types(self):
        db = MagicMock()
        db.dlcs.distinct.return_value = ['D']
        db.list_collection_names.side_effect = lambda **kw: [kw['filter']['name']]
        trees = ReferenceTrees(db, {'catalogs': []}, {}, None)
        trees.revision = lambda: 'current'
        trees.cards_revision, trees.cards = 'current', {}
        keys = set()
        for enabled in (['D'], []):
            for mixed in (False, True):
                for hide in (False, True):
                    params = dict(enabled_dlc=enabled, mixed_trees=mixed, hide_event_technologies=hide)
                    result = trees.open(params)
                    key = result['tree_id']
                    self.assertNotIn(key, keys)
                    keys.add(key)
                    trees.registry.find_one.assert_called_with({'_id': key, 'mode': 'reference', **params,
                        'source_revision': 'current', 'rules_revision': trees.rules_revision, 'state': 'ready'})
        self.assertEqual(trees.open({}), trees.open({'enabled_dlc': ['D', 'D'], 'mixed_trees': False,
                                                    'hide_event_technologies': False}))
        trees.registry.replace_one.assert_not_called()
        for invalid in ({'mixed_trees': 1}, {'hide_event_technologies': 'false'}):
            with self.assertRaises(InvalidRequest):
                trees.open(invalid)

    def test_event_classification_requires_a_confirmed_exclusive_route(self):
        index = ProgressSources(('tech',), ('grant',))
        def add(kind, identifier, *items):
            index.add(kind, {'_id': identifier, 'source': {'file': 'test.txt'}, 'pointer': '/0',
                             'tree': term('country_event' if kind == 'events' else identifier, block(*items))})
        index.mechanics.technologies['tech'] = block(term('weight', '0'))
        techs = {'tech': {'starting': False}}
        add('events', 'grant', term('is_triggered_only', 'yes'), term('immediate', block(term('give_technology', 'tech'))))
        self.assertFalse(classify(index, techs)['tech']['event_only'])
        add('anomalies', 'entry', term('on_success', block(term('country_event', 'grant'))))
        self.assertTrue(classify(index, techs)['tech']['event_only'])
        add('ascension_perks', 'perk', term('on_enabled', block(term('country_event', 'grant'))))
        row = classify(index, techs)['tech']
        self.assertFalse(row['event_only'])
        self.assertEqual(row['acquisition_basis']['sources'], ['ascension_perks', 'event'])

    def test_research_weights_exclude_ai_and_keep_uncertain_additions_visible(self):
        base = term('weight', '0')
        bonus = lambda n: block(term('modifier', block(term('add', n))))
        self.assertEqual(weight_status(block(base, term('ai_weight', bonus('5')))), 'zero_weight')
        self.assertEqual(weight_status(block(base, term('weight_modifier', bonus('5')))), 'positive_add')
        self.assertEqual(weight_status(block(base, term('weight_modifier', bonus('script_value')))), 'unknown_add')
        self.assertEqual(weight_status(block(base, term('weight', '80'))), 'conflicting_weights')

    def test_zero_matches_tie_and_hidden_parent(self):
        fixture = object.__new__(PreparedTree)
        fixture.options = {'parent_rules': [{'id': 'mandatory', 'enabled': True}]}
        fixture.analysis = Mock()
        fixture.evidence = None
        fixture.techs = {k: {'parents': [], 'mandatory': []} for k in 'abc'}
        fixture.techs['c']['parents'] = ['a', 'b']
        for shown, expected in [('abc', None), ('bc', 'b'), ('c', None)]:
            nodes = {k: {'children': [], 'availability': k in shown, 'parent_tech': None} for k in 'abc'}
            fixture.parents(nodes, {}, {'mixed_trees': False})
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
