import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from sttv_server.technology_tooltip import Content
from sttv_server.tooltip_labels import Labels
from sttv_server.tooltip_document import pack, render
from test_technology_tooltip import block, entry, logic, scalar


class ConditionTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.rules = json.loads((root / 'config/localization_keys.json').read_text())
        self.strings = {}
        for lang, folder in [('ru', 'russian'), ('en', 'english')]:
            table = {}
            for file in (root.parents[1] / 'localization' / folder).glob('*.yml'):
                for line in file.read_text(encoding='utf-8-sig').splitlines():
                    if line.startswith(' sttv_'):
                        key, text = line.strip().split(':', 1)
                        if text.lstrip().startswith('"'):
                            table[key] = text.strip()[1:-1]
            self.strings[lang] = table

    def resolve(self, node, lang, **names):
        labels = Labels(None, self.rules, None)
        expr = Content(labels).node(node, ('potential',))
        packed = pack(labels, {'technology_id': 'T', 'node': expr})
        values = {**self.strings[lang], **names}
        return render(packed, self.rules, lambda _, ks: [(k, values[k]) for k in ks if k in values],
                      lang, None)['node']

    def test_war_comparisons_and_filtered_counts(self):
        threshold = {**entry('value', scalar('superior')), 'operator': '>='}
        power = entry('relative_power', block(entry('who', scalar('root')),
                      entry('category', scalar('fleet')), threshold))
        self.assertIn('≥ Superior', self.resolve(power, 'en', RELATIVE_POWER_4='Superior')['text'])
        fraction = {**entry('attacker_war_exhaustion', scalar('0.6')), 'operator': '<'}
        self.assertIn('< 60%', self.resolve(fraction, 'en')['text'])
        count = entry('count_country', block(entry('count', scalar('3')), entry('limit', block(fraction))))
        node = self.resolve(count, 'en')
        self.assertIn('3', node['text'])
        self.assertIn('60%', node['children'][0]['text'])
        unknown = entry('relative_power', block(entry('who', scalar('root')), entry('value', scalar('novel'))))
        self.assertEqual(self.resolve(unknown, 'en')['kind'], 'partial')

    def test_fauna_contact_uses_both_positive_checks_on_the_same_target(self):
        def check(predicate, target):
            return entry(predicate, scalar('event_target:' + target + '_country'))

        def encounter(target):
            return logic('AND', check('exists', target), check('has_communications', target))

        requirement = logic('OR', encounter('tiyanki'), encounter('amoeba'))
        for lang in ('ru', 'en'):
            rendered = self.resolve(requirement, lang, tiyanki='Tiyanki', space_amoeba_plural='Amoebas')
            self.assertEqual(rendered['key'], 'one_fauna_contact')
            self.assertIn('Tiyanki', rendered['text'])
            self.assertIn('Amoebas', rendered['text'])
            self.assertEqual(len(rendered['evidence']['alternatives']), 2)
        different = logic('AND', check('exists', 'tiyanki'), check('has_communications', 'amoeba'))
        self.assertEqual(self.resolve(different, 'en')['operator'], 'AND')
        negated = logic('AND', check('exists', 'tiyanki'), logic('NOT', check('has_communications', 'tiyanki')))
        self.assertEqual(self.resolve(negated, 'en')['operator'], 'AND')

    def test_science_ship_and_optional_target(self):
        staffed = logic('AND', entry('exists', scalar('leader')),
                        entry('is_ship_class', scalar('shipclass_science_ship')))
        self.assertEqual(self.resolve(staffed, 'en')['key'], 'staffed_science_ship')
        other = logic('OR', entry('exists', scalar('leader')),
                      entry('is_ship_class', scalar('shipclass_science_ship')))
        self.assertEqual(self.resolve(other, 'ru')['operator'], 'OR')
        optional = self.resolve(entry('exists', scalar('event_target:marauder_country_1?')), 'en')
        self.assertIn('marauder', optional['text'].lower())
        for owner in ('root', 'root.controller'):
            target = self.resolve(entry('exists', scalar('event_target:georadiation_undetonated_planet@' + owner)),
                                  'en', UNDETONATED_GEORADIATION_PROJECT='Undetonated Device')
            self.assertIn('Undetonated Device', target['text'])
            self.assertNotIn('→', target['text'])

    def test_empty_scope_keeps_its_subject_without_an_empty_conjunction(self):
        scope = entry('event_target:thalassocracy_target_system', block())
        result = self.resolve(scope, 'en')
        self.assertEqual((result['kind'], result['key'], result['children']),
                         ('scope', 'event_target:thalassocracy_target_system', []))
        for operator in ('AND', 'OR'):
            explicit = self.resolve(logic(operator), 'en')
            self.assertEqual((explicit['operator'], explicit['children']), (operator, []))

    def test_event_negation_and_scope(self):
        event = logic('NOT', entry('has_active_event', block(scalar('crisis.4135'))))
        node = self.resolve(event, 'ru', **{'crisis.4135.name': 'Конец близок'})
        self.assertTrue(node['negated'])
        self.assertEqual(node['reference']['id'], 'crisis.4135')
        self.assertIn('не должно быть активно', node['text'])
        scope = entry('CAPITAL_SCOPE', block(entry('observation_outpost', block(entry('has_mission', scalar('specimen_collection'))))))
        node = self.resolve(scope, 'en', mission_specimen_collection='Aggressive Observation')
        self.assertEqual(node['children'][0]['children'][0]['reference']['type'], 'mission')

    def test_source_title_and_hidden_caller_survive_cached_rendering(self):
        caller = ('events', 'visible.1')
        hidden = ('events', 'hidden.2')
        index = SimpleNamespace(saved_targets={}, hidden={hidden[1]}, event_keys=lambda ident: (ident + '.name',),
                                incoming={hidden[1]: [{'source': caller, 'issue': None}]}, routes=lambda: {caller})
        for lang in ('ru', 'en'):
            labels = Labels(None, self.rules, None)
            content = Content(labels, index)
            document = pack(labels, {'technology_id': 'T', 'caller': content.name(caller),
                                     'hidden': content.name(hidden)})
            values = {**self.strings[lang], 'visible.1.name': 'Test'}
            result = render(document, self.rules, lambda _, ks: [(k, values[k]) for k in ks if k in values], lang, None)
            self.assertIn('Test', result['caller'])
            self.assertIn(result['caller'], result['hidden'])
            contexts = [issue for issue in result['diagnostics'] if issue['reason'] == 'source_named_by_context']
            self.assertEqual([(issue['source'], issue['basis']) for issue in contexts], [(list(hidden), 'calling_source')])

    def test_operand_forms_and_unknown_alternative(self):
        expr = logic('OR', entry('has_deposit', scalar('no')), entry('has_deposit', scalar('d_a')),
                     entry('mystery', block(entry('has_starbase_module', scalar('anchor')))))
        node = self.resolve(expr, 'en', d_a='Deposit A', sm_anchor='Anchor')
        a, b, c = node['children']
        self.assertEqual(a['text'], 'There are no deposits')
        self.assertIn('Deposit A', b['text'])
        self.assertEqual(c['expression'], expr['body']['items'][2])
        self.assertIn('Anchor', c['children'][0]['text'])

    def test_starbase_construction_queue(self):
        check = block(entry('custom_tooltip', block(entry('fail_text', scalar('requires_detection_array')),
            logic('OR', entry('has_starbase_module', scalar('detection_array')),
                 entry('starbase_buildable_is_in_queue_before', block(entry('first', scalar('detection_array')),
                                                                      entry('second', scalar('dark_matter_detector'))))))),
            logic('NOT', entry('has_starbase_building', scalar('dark_matter_listening_post'))))
        result = self.resolve(check, 'en', sm_detection_array='Detection Array', sm_dark_matter_detector='Detector',
                              sm_dark_matter_listening_post='Listening Post')
        def descendants(node):
            yield node
            for child in node.get('children', []):
                yield from descendants(child)
        nodes = list(descendants(result))
        branch = next(n for n in nodes if n.get('operator') == 'OR')
        self.assertEqual(branch['children'][0]['reference']['type'], 'starbase_module')
        self.assertIn('Detector', branch['children'][1]['text'])
        forbidden = next(n for n in nodes if n.get('operator') == 'NOT')['children'][0]
        self.assertEqual(forbidden['reference']['type'], 'starbase_building')
        self.assertIn('Listening Post', forbidden['text'])

    def test_localized_quantity_retains_operator(self):
        for sign in ('>', '>='):
            check = entry('resource_stockpile_compare', block(entry('resource', scalar('astral_threads')),
                          {**entry('value', scalar('1000.5')), 'operator': sign}))
            for lang, value in [('en','1000.5'), ('ru','1000,5')]:
                node = self.resolve(check, lang, astral_threads='Threads')
                self.assertIn(value, node['text'])
                self.assertIn({'>' : '>', '>=' : '≥'}[sign], node['text'])

    def test_calculated_stockpiles(self):
        def script(*steps):
            return {'kind': 'script_value', 'scope': None, 'body': block(*steps)}

        factor = script(entry('base', scalar('0')), entry('complex_trigger_modifier',
            block(entry('trigger', scalar('years_passed')), entry('mode', scalar('add')))),
            entry('divide', scalar('10')), entry('floor', scalar('yes')), entry('min', scalar('1')),
            entry('max', scalar('5')), entry('mult', scalar('0.1')))
        amount = {**entry('value', scalar('50')), 'operator': '>='}
        node = self.resolve(entry('resource_stockpile_compare', block(entry('resource', scalar('influence')),
                            amount, entry('mult', factor))), 'en', influence='Influence')
        for text in ('Influence', '≥ 50', 'min(max(⌊', 'Years since the start of the game', '0.1'):
            self.assertIn(text, node['text'])

        value = script(entry('base', scalar('1')), entry('modifier', block(entry('add', scalar('-0.25')),
                       entry('has_anomaly', scalar('no')))), entry('mult', scalar('5000')))
        node = self.resolve(entry('resource_stockpile_compare', block(entry('resource', scalar('energy')),
                            {**amount, 'value': value})), 'en', energy='Energy', HAS_NOT_ANOMALY='No anomaly')
        self.assertIn('Energy', node['text'])
        steps = node['formula'][0]['children']
        self.assertIn('-0.25', steps[1]['children'][0]['text'])
        self.assertEqual('No anomaly', steps[1]['children'][1]['text'])
        self.assertIn('5000', steps[2]['text'])
