"""Candidate logic, reciprocal links and active representation behavior."""

from copy import deepcopy
import unittest

from sttv.common.errors import BuildError
from sttv.enrichment.technology_tree.evidence import Evidence
from sttv.enrichment.technology_tree.selection import calculate
from sttv.enrichment.technology_tree.integrity import check_results
from sttv.enrichment.technology_tree.representations import prepare
from sttv.enrichment.technology_tree.ast import requirements
from .support import assignment, block, logical, value, tech, catalog, rules


class SelectionTests(unittest.TestCase):
    def evaluate(self, nodes, rule_ids, variants=None, evidence=None, order=None):
        technologies = prepare(catalog(nodes), variants or {})
        result = calculate(technologies, evidence or Evidence(), rules(*rule_ids), {}, order=order)
        check_results(result[0], technologies)
        return result

    def test_mandatory_intersection_and_nested_alternatives(self):
        node = logical('OR', block(value('a'), value('b')), logical('AND', value('a'), value('c')))
        self.assertEqual(requirements(node), ({'a','b','c'}, {'a'}, False))
        nodes = [tech(k) for k in 'abc'] + [tech('child', [node])]
        result, decisions, _ = self.evaluate(nodes, ['mandatory', 'highest_tier'])
        self.assertEqual(result['child']['parent_tech'], 'a')
        self.assertEqual([s['rule'] for s in decisions[-1]['trace']], ['mandatory'])

    def test_immediate_children_survive_later_parent_processing(self):
        nodes = [tech('z_parent'), tech('a_child', ['z_parent']), tech('b_child', ['z_parent'])]
        forward = self.evaluate(nodes, ['highest_tier'])[0]
        reverse = self.evaluate(nodes, ['highest_tier'], order=['z_parent','b_child','a_child'])[0]
        self.assertEqual(forward, reverse)
        self.assertEqual(forward['z_parent']['children'], ['a_child','b_child'])

    def test_zero_matches_are_skipped_and_disabled_rules_do_not_run(self):
        nodes = [tech('a', tier=1, area='engineering'), tech('b', tier=2, area='society'), tech('c', ['a','b'])]
        result, decisions, _ = self.evaluate(nodes, ['same_area','highest_tier'])
        self.assertEqual(result['c']['parent_tech'], 'b')
        self.assertEqual(decisions[-1]['trace'][0]['skip_reason'], 'empty_matches')
        config = rules('highest_tier')
        config['rules'][0]['enabled'] = False
        output = calculate(prepare(catalog(nodes),{}), Evidence(), config, {})
        self.assertEqual(output[0]['c']['status'], 'ambiguous')
        self.assertEqual(output[1][-1]['trace'], [])

    def test_reordering_and_area_variants_change_selection(self):
        nodes = [tech('a', tier=1), tech('b', tier=2, area='engineering'),
            tech('c', ['a','b'], extra=[assignment('technology_swap', block(assignment('area','engineering')))])]
        self.assertEqual(self.evaluate(nodes,['same_area','highest_tier'])[0]['c']['parent_tech'],'a')
        self.assertEqual(self.evaluate(nodes,['highest_tier','same_area'])[0]['c']['parent_tech'],'b')
        self.assertEqual(self.evaluate(nodes,['same_area'],{'c':'swap:1'})[0]['c']['parent_tech'],'b')

    def test_variant_on_candidate_and_preserved_requirements(self):
        nodes=[tech('a',area='society',extra=[assignment('technology_swap',block(assignment('area','physics'),
            assignment('tier',99),assignment('prerequisites',block(value('missing')))))]),tech('b',area='engineering'),tech('c',['a','b'])]
        result=self.evaluate(nodes,['same_area'],{'a':'swap:1'})[0]
        self.assertEqual(result['c']['parent_tech'],'a')
        self.assertEqual(prepare(catalog(nodes),{'a':'swap:1'})['a']['tier'],1)

    def test_invalid_graphs_and_variants(self):
        for nodes in ([tech('a',['missing'])], [tech('a'),tech('a')],
                      [tech('a',[logical('NOT',value('a'))])], [tech('a',[logical('OR')])]):
            with self.subTest(nodes=nodes), self.assertRaises(BuildError):
                prepare(catalog(nodes),{})
        with self.assertRaises(BuildError):
            self.evaluate([tech('a',['b']),tech('b',['a'])],['highest_tier'])
        for variants in ({'a':'swap:0'}, {'a':'swap:1'}, {'unknown':'base'}):
            with self.subTest(variants=variants), self.assertRaises(BuildError):
                prepare(catalog([tech('a')]),variants)

    def test_inheritance_unknown_no_yes_and_conflicting_modifiers(self):
        base = [assignment('modifier',block(assignment('production',1)))]
        swaps = [assignment('technology_swap', block(*contents)) for contents in (
            [assignment('modifier',block(assignment('other',2)))],
            [assignment('inherit_effects','no'),assignment('modifier',block(assignment('other',2)))],
            [assignment('inherit_effects','yes'),assignment('modifier',block(assignment('other',2)))],
            [assignment('inherit_effects','yes'),assignment('modifier',block(assignment('production',3)))])]
        records=catalog([tech('a'),tech('b'),tech('child',['a','b'],extra=base+swaps)])
        evidence=Evidence(production={'production':[{'owners':['a']}]})
        for index, expected in ((1,'ambiguous'),(2,'ambiguous'),(3,'resolved'),(4,'ambiguous')):
            t=prepare(records,{'child':f'swap:{index}'})
            result,_,diagnostics=calculate(t,evidence,rules('production_affinity'),{})
            self.assertEqual(result['child']['status'],expected)
            if index in (1,4): self.assertTrue(diagnostics)

    def test_reciprocity_and_cycle_checks_reject_corruption(self):
        results=self.evaluate([tech('a'),tech('b',['a'])],['highest_tier'])[0]
        damaged=deepcopy(results)
        damaged['a']['children']=[]
        with self.assertRaises(BuildError): check_results(damaged)
