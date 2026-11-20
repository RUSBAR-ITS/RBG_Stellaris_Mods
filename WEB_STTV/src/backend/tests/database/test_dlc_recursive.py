"""Cross-object DLC proofs, alternative paths and conservative context boundaries."""

from copy import deepcopy
import unittest

from sttv.common.json_io import read_json
from sttv.common.paths import PRODUCT_ROOT
from sttv.enrichment.dlc.analysis import Analysis
from sttv.enrichment.dlc.settings import resolve
from sttv.enrichment.dlc.evaluation import Evaluator
from .test_dlc import block as b, field as a, logic, scalar as s, technology


def rules():
    return resolve(read_json(PRODUCT_ROOT / 'config/enrichment/dlc.json'),
                   lambda path, schema: read_json(path), PRODUCT_ROOT / 'data')


def record(key, *items):
    return {'id': key, 'body': b(*items), 'source': {'document_id': key, 'pointer': '/items/0'}}


def analysis(condition, records=None, options=None):
    return Analysis({'t': technology('t', a('potential', b(condition)))}, {'a': 'A', 'b': 'B'},
                    options or rules(), records=records)


def visible(prepared, enabled=()):
    return prepared.evaluate(enabled)[0]['t']['visible']


class RecursiveDlcTests(unittest.TestCase):
    def test_providers_are_alternatives_and_npc_is_not_a_player_choice(self):
        records = {'ship_categories': [record('bio')], 'graphical_culture': [
            record('one', a('ship_kinds', b(s('bio'))), a('selectable', b(a('host_has_dlc', 'A')))),
            record('two', a('ship_kinds', b(s('bio'))), a('selectable', b(a('host_has_dlc', 'B')))),
            record('npc', a('ship_kinds', b(s('bio'))), a('selectable', b(a('always', 'no'))))]}
        p = analysis(a('uses_ship_category', 'bio'), records)
        before = deepcopy(records)
        self.assertFalse(visible(p))
        self.assertTrue(visible(p, ['a']))
        self.assertTrue(visible(p, ['b']))
        self.assertEqual(before, records)
        p.evaluate(['b'])
        self.assertTrue(p.graph.statistics['reused_profile'])
        # A missing/unclassified provider is not a proof that all choices are forbidden.
        records['graphical_culture'].append(record('unknown', a('ship_kinds', b(s('bio')))))
        self.assertTrue(visible(analysis(a('uses_ship_category', 'bio'), records)))
        records['graphical_culture'] = []
        self.assertTrue(visible(analysis(a('uses_ship_category', 'bio'), records)))

    def test_tradition_category_adoption_finish_and_multiple_categories(self):
        for member in ('traditions', 'adoption_bonus', 'finish_bonus'):
            value = b(s('tr')) if member == 'traditions' else 'tr'
            records = {'ascension_perks': [record('ap', a('possible', b(a('has_tradition', 'tr'))))],
                'traditions': [record('tr')], 'tradition_categories': [
                    record('category', a(member, value), a('potential', b(a('host_has_dlc', 'A'))))]}
            p = analysis(a('has_ascension_perk', 'ap'), records)
            self.assertFalse(visible(p), member)
            self.assertTrue(visible(p, ['a']))
            self.assertIsNone(p.values[p.roots['t']['potential']])
            records['tradition_categories'].append(record('alternative', a(member, value)))
            self.assertTrue(visible(analysis(a('has_ascension_perk', 'ap'), records)))

    def test_cycles_refine_external_ban_independently_of_order(self):
        one = record('one', a('potential', b(a('has_ascension_perk', 'two'))))
        two = record('two', a('potential', b(a('has_ascension_perk', 'one'), a('host_has_dlc', 'A'))))
        for rows in ([one, two], [two, one]):
            p = analysis(a('has_ascension_perk', 'one'), {'ascension_perks': rows})
            self.assertFalse(visible(p))
            self.assertTrue(visible(p, ['a']))
            self.assertIn('dlc_dependency_cycle', {d['code'] for d in p.graph.diagnostics})
        two['body'] = b(a('potential', b(a('has_ascension_perk', 'one'))))
        self.assertTrue(visible(analysis(a('has_ascension_perk', 'one'), {'ascension_perks': [one, two]})))

    def test_long_chain_and_shared_reference_compile_one_object_per_identity(self):
        rows = [record(f'p{i}', a('possible', b(a('has_ascension_perk', f'p{i+1}')))) for i in range(24)]
        rows.append(record('p24', a('potential', b(a('host_has_dlc', 'A')))))
        p = analysis(logic('AND', a('has_ascension_perk', 'p0'), a('has_ascension_perk', 'p12')),
                     {'ascension_perks': rows})
        self.assertFalse(visible(p))
        self.assertEqual(len(p.compiler.objects.cache), 25)
        self.assertTrue(visible(p, ['a']))
        limited = rules()
        limited['limits']['max_depth'] = 4
        p = analysis(a('has_ascension_perk', 'p0'), {'ascension_perks': rows}, limited)
        self.assertTrue(visible(p))
        self.assertIn('dlc_depth_limit', {d['code'] for d in p.graph.diagnostics})

    def test_government_requirements_keep_negation_and_ignore_labels(self):
        records = {'civics': [record('origin', a('is_origin', 'yes'), a('playable', b(a('host_has_dlc', 'A'))))],
            'authorities': [record('authority', a('possible', b(a('origin', b(a('value', 'origin'))))))]}
        self.assertFalse(visible(analysis(a('has_authority', 'authority'), records)))
        records['authorities'][0]['body'] = b(a('possible', b(a('origin', b(logic('NOT', a('text', 'label'), a('value', 'origin')))))))
        self.assertTrue(visible(analysis(a('has_authority', 'authority'), records)))

    def test_selection_does_not_infer_traits_swaps_fallback_or_ownership(self):
        records = {'traits': [record('trait', a('species_potential_add', b(a('host_has_dlc', 'A'))))],
            'authorities': [record('auth', a('advanced_authority_swap', b(a('name', 'alt'),
                a('trigger', b(a('host_has_dlc', 'A'))))), a('ai_playable', b(a('always', 'no'))))]}
        self.assertTrue(visible(analysis(a('has_trait', 'trait'), records)))
        self.assertTrue(visible(analysis(a('has_authority', 'auth'), records)))
        self.assertTrue(visible(analysis(a('has_authority', 'alt'), records)))
        self.assertTrue(visible(analysis(a('has_technology', 't'))))

    def test_conditionals_and_count_bounds(self):
        evaluate = Evaluator({'a': 'A', 'b': 'B'}, [], rules()).evaluate
        dlc = a('host_has_dlc', 'A')
        guarded = a('if', b(a('limit', b(a('always', 'yes'))), dlc))
        self.assertIs(evaluate(b(guarded), '/x')['value'], False)
        guarded['value']['items'][0] = a('limit', b(a('unknown', 'yes')))
        self.assertIsNone(evaluate(b(guarded), '/x')['value'])
        self.assertIs(evaluate(b(guarded, a('else', b(dlc))), '/x')['value'], False)
        threshold = {**a('amount', 2), 'operator': '>='}
        self.assertIs(evaluate(a('calc_true_if', b(threshold, dlc, a('unknown', 'yes'))), '/x')['value'], False)
        self.assertIsNone(evaluate(a('any_owned_planet', b(dlc)), '/x')['value'])

    def test_limits_missing_objects_and_duplicate_ids(self):
        p = analysis(a('has_ascension_perk', 'missing'), {'ascension_perks': []})
        self.assertTrue(visible(p))
        self.assertIn('missing_dlc_reference', {d['code'] for d in p.graph.diagnostics})
        options = rules()
        options['limits']['max_steps'] = 1
        self.assertTrue(visible(analysis(a('host_has_dlc', 'A'), options=options)))
        options['limits']['max_nodes'] = 1
        self.assertTrue(visible(analysis(a('host_has_dlc', 'A'), options=options)))
        one, two = record('duplicate'), record('duplicate')
        two['source']['pointer'] = '/items/1'
        with self.assertRaisesRegex(Exception, 'Duplicate'):
            analysis(a('always', 'yes'), {'ascension_perks': [one, two]})

    def test_unknown_wrapper_reports_deep_dlc_without_proving_it(self):
        p = analysis(a('unknown_wrapper', b(a('host_has_dlc', 'A'))))
        self.assertTrue(visible(p))
        report = p.report()['coverage']
        self.assertEqual(report['dlcs']['a']['status'], 'unresolved_paths')
        self.assertEqual(report['dlcs']['b']['status'], 'no_dependencies_found_in_studied_scope')
