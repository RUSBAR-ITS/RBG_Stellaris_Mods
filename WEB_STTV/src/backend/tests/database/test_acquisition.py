"""Acquisition proofs distinguish grants, alternatives, runtime scopes and ownership."""

import unittest
from copy import deepcopy

from sttv.common.paths import PRODUCT_ROOT
from sttv.enrichment.acquisition.analysis import Acquisition
from sttv.enrichment.acquisition.extraction import extract
from sttv.enrichment.acquisition.configuration import load
from sttv.enrichment.dlc.conditions import Compiler
from sttv.enrichment.dlc.graph import Graph
from sttv.enrichment.dlc.objects import Library, References
from .test_dlc_recursive import rules
from .test_dlc import block as b, field as a, scalar as s, technology


def options():
    return load({'base': 'product', 'path': 'config/enrichment/acquisition/sources.json'}, PRODUCT_ROOT / 'data')[0]


def evidence(source, *items):
    document = {'source': {'file': source}, 'items': list(items)}
    return extract(document, options())['records']


def prepare(records=(), technologies=None, complete=True):
    config = rules()
    graph = Graph(config['limits'])
    compiler = Compiler(graph, {'a': 'A', 'b': 'B'}, config)
    techs = technologies or [technology('t', a('potential', b(a('host_has_dlc', 'A'))), a('weight', '0'))]
    library = Library(records={'technologies': techs})
    compiler.objects = References(compiler, library)
    model = compiler.acquisition = Acquisition(compiler, library, options(), records=list(records), coverage={'parsed': complete})
    result = model.reference('t')
    model.prepare()
    return model, graph, result


def perk(effect, dlc=None):
    items = [a('on_enabled', b(effect))]
    if dlc:
        items.append(a('potential', b(a('host_has_dlc', dlc))))
    return evidence('common/ascension_perks/test.txt', a('p', b(*items)))


class AcquisitionTests(unittest.TestCase):
    def test_zero_weight_option_is_not_ownership(self):
        model, graph, root = prepare(perk(a('add_research_option', 't'), 'A'))
        self.assertFalse(graph.evaluate([])[root])
        self.assertIsNone(graph.evaluate(['a'])[root])
        self.assertEqual(1, len(model.network.routes))

    def test_independent_grant_does_not_inherit_potential_or_prerequisites(self):
        tech = technology('t', a('weight', '0'), a('potential', b(a('host_has_dlc', 'A'))),
                          a('prerequisites', b(s('missing'))))
        _, graph, root = prepare(perk(a('give_technology', 't')), [tech])
        self.assertIsNone(graph.evaluate([])[root])

    def test_alternative_event_callers(self):
        events = evidence('events/test.txt', a('country_event', b(a('id', 'e.1'),
            a('is_triggered_only', 'yes'), a('immediate', b(a('give_technology', 't'))))))
        records = perk(a('country_event', b(a('id', 'e.1'))), 'A')
        other = perk(a('country_event', b(a('id', 'e.1'))), 'B')
        for record in other:
            record['record_id'] += 'b'
        _, graph, root = prepare(events + records + other)
        self.assertFalse(graph.evaluate([])[root])
        self.assertIsNone(graph.evaluate(['b'])[root])

    def test_dynamic_event_caller_is_not_lost_behind_a_closed_literal_caller(self):
        events = evidence('events/test.txt', a('country_event', b(a('id', 'e.1'),
            a('is_triggered_only', 'yes'), a('immediate', b(a('give_technology', 't'))))))
        records = perk(a('country_event', b(a('id', 'e.1'))), 'A')
        dynamic = evidence('common/ascension_perks/dynamic.txt', a('p2', b(
            a('on_enabled', b(a('country_event', b(a('id', '$EVENT$'))))))))
        _, graph, root = prepare(events + records + dynamic)
        self.assertIsNone(graph.evaluate([])[root])

    def test_dynamic_grant_and_incomplete_sources_never_disappear(self):
        for records, complete in ((perk(a('give_technology', '$TARGET$')), True), ([], False)):
            _, graph, root = prepare(records, complete=complete)
            self.assertIsNone(graph.evaluate([])[root])

    def test_command_case_does_not_hide_a_grant(self):
        _, graph, root = prepare(perk(a('Give_Technology', 't')))
        self.assertIsNone(graph.evaluate([])[root])

    def test_crisis_order_requires_activation_and_previous_level(self):
        records = perk(a('activate_crisis_progression', 'path'), 'A')
        records += evidence('common/crisis_paths/test.txt', a('path', b(a('levels', b(s('l1'), s('l2'))))))
        records += evidence('common/crisis_levels/test.txt',
            a('l1', b(a('allow', b(a('host_has_dlc', 'B'))))),
            a('l2', b(a('on_unlock', b(a('add_research_option', 't'))))))
        _, graph, root = prepare(records)
        self.assertFalse(graph.evaluate(['a'])[root])
        self.assertFalse(graph.evaluate(['b'])[root])
        self.assertIsNone(graph.evaluate(['a', 'b'])[root])
        model, graph, root = prepare(records, complete=False)
        level = model.crisis('l2')
        self.assertIsNone(graph.evaluate([])[level])

    def test_effect_branches_keep_alternative_execution_guards(self):
        branch = b(a('if', b(a('limit', b(a('host_has_dlc', 'A'))), a('give_technology', 'other'))),
                   a('else', b(a('give_technology', 't'))))
        records = perk(a('hidden_effect', branch))
        _, graph, root = prepare(records)
        self.assertIsNone(graph.evaluate([])[root])
        self.assertFalse(graph.evaluate(['a'])[root])

    def test_guard_of_an_irrelevant_branch_still_controls_a_relevant_else(self):
        branch = b(a('if', b(a('limit', b(a('host_has_dlc', 'A'))), a('set_country_flag', 'other'))),
                   a('else', b(a('give_technology', 't'))))
        _, graph, root = prepare(perk(a('hidden_effect', branch)))
        self.assertIsNone(graph.evaluate([])[root])
        self.assertFalse(graph.evaluate(['a'])[root])

    def test_foreign_scope_and_mutation_do_not_inherit_current_ownership(self):
        effect = a('owner', b(a('if', b(a('limit', b(a('has_technology', 'missing'))), a('give_technology', 't')))))
        _, graph, root = prepare(perk(effect))
        self.assertIsNone(graph.evaluate([])[root])

    def test_cycles_without_entry_stay_unknown(self):
        records = evidence('events/test.txt', a('country_event', b(a('id', 'e.1'), a('is_triggered_only', 'yes'),
            a('immediate', b(a('country_event', b(a('id', 'e.1'))), a('give_technology', 't'))))))
        _, graph, root = prepare(records)
        self.assertIsNone(graph.evaluate([])[root])

    def test_random_failure_effect_is_an_independent_possible_grant(self):
        effect = a('add_random_research_option', b(a('area', 'engineering'),
            a('fail_effects', b(a('give_technology', 't')))))
        model, graph, root = prepare(perk(effect))
        self.assertEqual(2, len(model.network.routes))
        self.assertIsNone(graph.evaluate([])[root])

    def test_random_alternatives_and_progress_preserve_uncertainty(self):
        effect = a('random_list', b(a('10', b(a('give_technology', 't'))),
                                  a('90', b(a('give_technology', 'other')))))
        _, graph, root = prepare(perk(effect, 'A'))
        self.assertFalse(graph.evaluate([])[root])
        self.assertIsNone(graph.evaluate(['a'])[root])
        _, graph, root = prepare(perk(a('add_tech_progress', b(a('tech', 't'), a('progress', '0.5')))))
        self.assertIsNone(graph.evaluate([])[root])

    def test_copy_filters_do_not_require_ordinary_prerequisites(self):
        tech = technology('t', a('weight', '10'), a('potential', b(a('host_has_dlc', 'A'))),
                          a('prerequisites', b(s('blocked'))))
        blocked = technology('blocked', a('weight', '0'))
        _, graph, root = prepare(perk(a('copy_random_tech_from', b(a('who', 'from')))), [tech, blocked])
        self.assertFalse(graph.evaluate([])[root])
        self.assertIsNone(graph.evaluate(['a'])[root])

    def test_documented_rare_defaults_and_copy_exclusions_constrain_domains(self):
        rare = technology('t', a('weight', '0'), a('is_rare', 'yes'))
        _, graph, root = prepare(perk(a('add_random_research_option', b())), [rare])
        self.assertFalse(graph.evaluate([])[root])
        _, graph, root = prepare(perk(a('add_random_research_option', b(a('ignore_rare', 'no')))), [rare])
        self.assertIsNone(graph.evaluate([])[root])
        tech = technology('t', a('weight', '0'))
        _, graph, root = prepare(perk(a('copy_techs_from', b(a('target', 'from'), a('except', b(s('t')))))), [tech])
        self.assertFalse(graph.evaluate([])[root])

    def test_compaction_keeps_calls_under_unknown_containers_and_all_guards(self):
        node = a('x', b(a('effect', b(a('unknown', b(a('give_technology', '$T$'))))),
                          a('potential', b(a('host_has_dlc', 'A'))), a('unrelated', b(a('foo', 'bar')))))
        original = deepcopy(node)
        records = evidence('common/other/test.txt', node)
        self.assertEqual(node, original)
        _, graph, root = prepare(records)
        self.assertIsNone(graph.evaluate([])[root])

    def test_route_pointer_identifies_the_command_in_retained_ast(self):
        records = perk(a('if', b(a('limit', b(a('host_has_dlc', 'A'))),
            a('add_random_research_option', b(a('fail_effects', b(a('give_technology', 't'))))))))
        model, _, _ = prepare(records)
        for route in model.network.routes:
            record = next(r for r in records if r['record_id'] == route['record_id'])
            node = record['node']
            for part in route['pointer'][len(record['pointer']):].strip('/').split('/'):
                node = node[int(part)] if isinstance(node, list) else node[part]
            self.assertEqual(node['key']['text'], route['command'])

    def test_unknown_non_assignment_container_cannot_erase_a_possible_grant(self):
        node = {'kind': 'logical_operation', 'operator': 'AND', 'body': b(a('give_technology', 't'))}
        model, graph, root = prepare(perk(node))
        self.assertEqual(len(model.network.routes), 1)
        self.assertIsNone(graph.evaluate([])[root])

    def test_safe_scalar_action_does_not_authorize_discarding_a_nested_grant(self):
        model, graph, root = prepare(perk(a('custom_tooltip', b(a('give_technology', 't')))))
        self.assertEqual(len(model.network.routes), 1)
        self.assertIsNone(graph.evaluate([])[root])

    def test_scoped_dynamic_target_is_not_mistaken_for_a_literal_technology_id(self):
        model, graph, root = prepare(perk(a('give_technology', b(a('tech', 'event_target:chosen')))))
        self.assertEqual(model.network.routes[0]['target'], '*')
        self.assertIsNone(graph.evaluate([])[root])

    def test_event_declaration_is_not_an_event_call_and_unrelated_blocks_are_pruned(self):
        records = evidence('events/test.txt',
            a('country_event', b(a('id', 'unused'), a('immediate', b(a('set_flag', 'irrelevant'))))),
            a('country_event', b(a('id', 'used'), a('immediate', b(a('give_technology', 't'))),
                                a('ai_weight', b(a('huge_unrelated_block', b(a('factor', '1'))))))))
        self.assertEqual([r['id'] for r in records], ['used'])
        self.assertNotIn('huge_unrelated_block', str(records))


if __name__ == '__main__':
    unittest.main()
