import unittest

from sttv_server.progress_sources import ProgressSources
from sttv_server.technology_tooltip import Content
from sttv_server.tooltip_labels import Labels
from sttv_server.tooltip_scopes import ScopeContext
from sttv_server.tree.event_technologies import classify
from test_progress import block, field, record


class EventOutcomeTests(unittest.TestCase):
    def test_project_outcome_and_direct_start_share_a_cyclic_delivery_event(self):
        index = ProgressSources(['X'], ['give', 'relay'])
        index.mechanics.technologies['X'] = block(field('weight', '0'))
        def call(name):
            return field('country_event', block(field('id', name)))
        def event(name, *effects):
            doc = record('country_event', field('id', name), field('is_triggered_only', 'yes'),
                         field('immediate', block(*effects)))
            doc['_id'] = name
            index.add('events', doc)
        event('give', call('relay'), field('add_research_option', 'X'))
        event('relay', call('give'))
        index.add('artifact_actions', record('investigate', field('effect', block(
            field('enable_special_project', block(field('name', 'P')))))))
        index.add('special_projects', record('P', field('on_success', block(call('give')))))
        state = classify(index, {'X': {'starting': False}})['X']
        self.assertTrue(state['event_only'])
        self.assertEqual(state['acquisition_basis']['paths'][0]['origin'], 'artifact_actions')
        index.add('on_actions', record('on_game_start_country', field('events', block(
            {'kind': 'scalar', 'text': 'give'}))))
        index.witness = None
        state = classify(index, {'X': {'starting': False}})['X']
        self.assertFalse(state['event_only'])
        self.assertIn('start', state['acquisition_basis']['sources'])

    def test_unbounded_progress_is_not_confirmed_positive(self):
        index = ProgressSources(['X'], [])
        index.mechanics.technologies['X'] = block(field('weight', '0'))
        index.add('artifact_actions', record('investigate', field('effect', block(
            field('add_tech_progress', block(field('tech', 'X'), field('progress', 'variable')))))))
        result = classify(index, {'X': {'starting': False}})['X']
        self.assertFalse(result['event_only'])
        self.assertIn('unknown_progress_amount', result['acquisition_basis']['issues'])

    def test_exists_this_requires_a_guaranteed_participant(self):
        labels = Labels(None, {'tooltip_condition': {'prefix': 'sttv_tooltip_', 'suffix': ''}}, None)
        labels.scope = ScopeContext(labels, None, ('technologies', 'X'))
        content = Content(labels)
        checks = block(field('exists', 'this'), field('uses_ship_category', 'bio_ship'))
        self.assertEqual(content.node(checks, ('potential',))['key'], 'bioships')
        with labels.scope.nested(['owner?']):
            node = content.node(checks, ('potential',))
            self.assertEqual([c['key'] for c in node['children']], ['exists', 'bioships'])
            neg = content.node(field('hidden_trigger', checks), ('potential',))
            self.assertEqual(neg, node)

    def test_caller_bindings_and_previous_scope_are_independent(self):
        index = ProgressSources([], ['target'])
        index.event_types['target'] = 'country_event'
        labels = Labels(None, {'tooltip_condition': {'suffix': ''}}, None)
        caller = ('archaeological_site_types', 'S')
        index.incoming['target'].append({'source': caller, 'scopes': (), 'caller_scopes': {'from': 'leader'}})
        context = ScopeContext(labels, index, ('events', 'target'))
        with context.nested(['any_owned_planet']):
            self.assertEqual(context.resolve('prev').kind, 'country')
            self.assertEqual(context.resolve('from').kind, 'leader')
        index.incoming['target'].append({'source': ('technologies', 'X'), 'scopes': ()})
        self.assertFalse(context.resolve('from').present)
        self.assertEqual(labels.diagnostics[-1]['id'], 'from')

    def test_subscriber_receives_the_original_battle_and_anomaly_slots(self):
        labels = Labels(None, {'tooltip_condition': {'suffix': ''}}, None)
        index = ProgressSources([], ['report'])
        index.add('on_actions', record('on_space_battle_won', field('events', block(
            {'kind': 'scalar', 'text': 'report'}))))
        context = ScopeContext(labels, index, ('events', 'report'))
        self.assertEqual(context.resolve('from').label.keys, ('participant_defeated_empire',))
        self.assertEqual(context.resolve('fromfrom').label.keys, ('participant_winning_fleet',))
        index.incoming.clear()
        index.add('anomalies', record('site', field('on_success', 'report')))
        self.assertEqual(context.resolve('from').label.keys, ('anomaly_location',))
        index.incoming.clear()
        index.add('anomalies', record('site', field('on_success', block(field('1', block(
            field('ship_event', block(field('id', 'report')))))))))
        self.assertEqual(context.resolve('from').kind, 'ship')
        self.assertEqual(context.resolve('fromfrom').kind, 'planet')

    def test_only_mandatory_country_type_constrains_the_participant(self):
        index = ProgressSources([], ['example'])
        check = field('FROM', block(field('is_country_type', 'formless')))
        event = record('country_event', field('id', 'example'), field('trigger', block(
            {'kind': 'logical_operation', 'operator': 'NOT', 'body': block(check)})))
        event['_id'] = 'example'
        index.add('events', event)
        self.assertNotIn('example', index.caller_country_types)
        event['tree']['value']['items'][1] = field('trigger', block(check))
        index.add('events', event)
        self.assertEqual(index.caller_country_types['example'], 'formless')

    def test_anomaly_spawn_and_outcome_exchange_survey_ship_and_planet(self):
        labels = Labels(None, {'tooltip_condition': {'suffix': ''}}, None)
        for stage, expected in [('spawn_chance', ('planet', 'ship')), ('on_success', ('ship', 'planet'))]:
            context = ScopeContext(labels, None, ('anomalies', 'site'), stages=(stage,))
            self.assertEqual((context.resolve('root').kind, context.resolve('from').kind), expected)
        context = ScopeContext(labels, None, ('on_actions', 'on_building_mining_station'))
        self.assertEqual(context.resolve('root').kind, 'ship')
        self.assertEqual(context.resolve('from').label.keys, ('participant_mining_site',))
        self.assertFalse(context.resolve('from').kind)
        context = ScopeContext(labels, None, ('megastructures', 'structure'), stages=('on_build_complete',))
        self.assertEqual([context.resolve(n).kind for n in ('root', 'from', 'fromfrom', 'fromfromfrom')],
                         ['system', 'country', 'megastructure', 'fleet'])
        context = ScopeContext(labels, None, ('on_actions', 'on_storm_left_system'))
        with context.nested(['from', 'count_system_within_storm', 'owner']):
            self.assertEqual(context.resolve('prev').label.keys, ('counted_system',))
            self.assertEqual(context.resolve('prevprevprev').label.keys, ('participant_cleared_system',))
