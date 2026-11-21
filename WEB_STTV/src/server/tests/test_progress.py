import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

from sttv_server.progress_content import ProgressContent
from sttv_server.acquisition_mechanics import AcquisitionMechanics, draw_blocked
from sttv_server.progress_sources import ProgressSources
from sttv_server.tooltip_labels import Labels
from sttv_server.tree.errors import Busy
from sttv_server.tree.service import ReferenceTrees


def field(name, value):
    return {'kind': 'assignment', 'operator': '=', 'key': {'kind': 'scalar', 'text': name},
            'value': {'kind': 'scalar', 'text': value} if isinstance(value, str) else value}


def block(*items):
    return {'kind': 'block', 'items': list(items)}


def record(identifier, *items):
    return {'_id': identifier, 'source': {'file': 'source.txt'}, 'pointer': '/items/0',
            'tree': field(identifier, block(*items))}


class ProgressTests(unittest.TestCase):
    def test_raw_command_line_after_multiline_string(self):
        from acquisition_vanilla_sites import find_sites
        script = (b'country_event = {\n'
                  b' desc = "two lines\n# give_technology = decoy"\n'
                  b' effect_tooltip = { add_research_option = X }\n'
                  b' give_technology =\n { tech = Y }\n id = test.1\n}')
        sites = list(find_sites('events/example.txt', script))
        self.assertEqual([(s['tech'], s['line'], s['tooltip_only'], s['root']) for s in sites],
                         [('X', 4, True, 'test.1'), ('Y', 5, False, 'test.1')])

    def test_blocked_chain_preserves_alternatives_and_terminates_on_cycles(self):
        def requirement(*names):
            return field('prerequisites', block(*({'kind': 'scalar', 'text': n} for n in names)))
        mechanics = AcquisitionMechanics()
        either = {'kind': 'logical_operation', 'operator': 'OR', 'body': requirement('X', 'Y')['value']}
        mechanics.technologies = {'A': block(requirement('B', 'C')), 'B': block(requirement('A', 'X')),
                                  'C': block(field('prerequisites', block(either)))}
        mechanics.blocked = {'X', 'Y'}
        self.assertEqual(mechanics.indirect('A'), [('X', True), ('Y', False)])
        self.assertFalse(draw_blocked(block(field('weight', '0'), field('weight', '70'))))
        self.assertFalse(draw_blocked(block(field('weight', '0'), field('weight_modifier', block(
            field('modifier', block(field('add', '100'), field('is_ai', 'no'))))))))
        self.assertTrue(draw_blocked(block(field('weight', '60'), field('weight_modifier', block(
            field('modifier', block(field('factor', '0.0'), field('always', 'yes'))))))))

    def test_conditional_pool_and_its_empty_outcome(self):
        index = ProgressSources(['common', 'rare'], [])
        for key in ('common', 'rare'):
            index.mechanics.technologies[key] = block(field('area', 'engineering'), field('tier', '2'),
                                                     field('is_rare', 'yes' if key == 'rare' else 'no'))
        index.add('traditions', record('discovery', field('on_enabled', block(field('add_random_research_option',
            block(field('area', 'engineering'), field('tier', '2'), field('add_progress', '0.99'),
                  field('fail_effects', block(field('add_research_option', 'rare')))))))))
        index.index_pools()
        reward, = index.grants['common']['traditions', 'discovery']
        self.assertEqual(reward['amount']['text'], '0.99')
        self.assertNotIn('rare', index.grants)
        failure, = index.rewards['research_options']['rare']['traditions', 'discovery']
        self.assertIn('empty_pool', failure['stages'])
        self.assertFalse(list(index.mechanics.pool_candidates('add_random_research_option', {'only_rare': 'no'})))

    def test_only_reachable_npc_can_send_a_reward_to_playable_country(self):
        for enabled in ('yes', 'no'):
            with self.subTest(enabled=enabled):
                index = ProgressSources(['gift'], ['npc.1', 'gift.1'])
                spawn = field('create_country', block(field('country_event', 'npc.1')))
                conditional = field('if', block(field('limit', block(field('always', enabled))), spawn))
                index.add('solar_system_initializers', record('setup', field('init_effect', block(conditional))))
                for identifier, effect in [('npc.1', field('every_playable_country', block(field('country_event', 'gift.1')))),
                                           ('gift.1', field('give_technology', 'gift'))]:
                    row = record(identifier, field('is_triggered_only', 'yes'), field('immediate', block(effect)))
                    row['tree']['key']['text'] = 'country_event'
                    index.add('events', row)
                self.assertEqual(('events', 'gift.1') in index.routes(), enabled == 'yes')

    def test_weighted_success_calls_with_spawn_rules(self):
        index = ProgressSources([], ['e.1', 'e.2'])
        source = record('anomaly', field('spawn_chance', block(field('modifier', block(
            field('add', '0.1'), field('host_has_dlc', 'DLC'))))), field('on_success', block(
            field('1', block(field('anomaly_event', 'e.1'))), field('2', 'e.2'))))
        index.add('anomalies', source)
        self.assertEqual(set(index.incoming), {'e.1', 'e.2'})
        for identifier, weight in [('e.1', '1'), ('e.2', '2')]:
            hit, = index.incoming[identifier]
            self.assertEqual(hit['chance'], (('weight', weight),))
            self.assertEqual(hit['stages'], ('on_success',))
            self.assertEqual(index.spawn[hit['source']], [('add', '0.1', [field('host_has_dlc', 'DLC')])])

    def test_executable_rewards_only_and_disabled_alternative(self):
        index = ProgressSources(['T'], ['e.1', 'e.2'])
        index.dlc_names = {'a': 'A', 'b': 'B'}
        give = field('add_tech_progress', block(field('tech', 'T'), field('progress', '0.25')))
        either = {'kind': 'logical_operation', 'operator': 'OR', 'body': block(
            field('host_has_dlc', 'A'), field('host_has_dlc', 'B'))}
        event = record('e.1', field('is_triggered_only', 'yes'),
                       field('tooltip', block(give)), field('hidden_effect', block(give)))
        event['tree']['key']['text'] = 'country_event'
        index.add('events', event)
        index.add('events', record('e.2', field('is_test_event', 'yes'), field('immediate', block(give))))
        index.add('special_projects', record('project', field('potential', block(either)),
                                            field('on_success', block(field('country_event', block(field('id', 'e.1')))))))
        index.add('on_actions', record('on_start', field('enable_special_project', block(field('name', 'project')))))
        self.assertEqual(len(index.grants['T']), 1)
        self.assertEqual(len(index.grants['T']['events', 'e.1']), 1)
        terms = {'tooltip_condition': {'prefix': '', 'suffix': ''}}
        for selection in ({'A', 'B'}, {'A'}, set()):
            labels = Labels('en', terms, None)
            labels._dlcs = {'A': (['A'], None), 'B': (['B'], None)}
            content = ProgressContent(labels, index, selection)
            def reader(lang, keys):
                phrases = {'progress_dlc': '{dlc}', 'progress_dlc_disabled': '{dlc} disabled'}
                return [(k, phrases.get(k, k)) for k in keys]
            result = labels.resolve({'technology_id': 'T', 'groups': content.sections('T')}, reader)
            self.assertEqual(len(result['groups']), 1)
            self.assertEqual(str(result['groups']).count(' disabled'), 2 - len(selection))
            self.assertIn("'operator': 'OR'", str(result))

    def test_acquisition_sections_require_player_scope_and_a_rooted_path(self):
        index = ProgressSources(['T'], ['entry', 'reward', 'loop'])
        for identifier, clauses in (
            ('entry', [field('option', block(field('name', 'accept'), field('country_event', 'reward')))]),
            ('reward', [field('immediate', block(field('add_research_option', 'T'),
                field('give_technology', block(field('tech', 'T'))),
                field('create_country', block(field('effect', block(field('give_technology', 'T'))))),
                field('event_target:unresolved', block(field('give_technology', 'T'))),
                field('if', block(field('limit', block(field('is_ai', 'yes'))), field('give_technology', 'T'))),
                field('tooltip', block(field('give_technology', 'T')))))]),
            ('loop', [field('immediate', block(field('country_event', 'loop'), field('give_technology', 'T')))])):
            event = record(identifier, field('is_triggered_only', 'yes'), *clauses)
            event['tree']['key']['text'] = 'country_event'
            index.add('events', event)
        index.add('on_actions', record('on_game_start_country', field('events', block({'kind': 'scalar', 'text': 'entry'}))))
        hits = index.rewards['researched_grants']['T']
        self.assertEqual([index.issue(r) for r in hits['events', 'reward']],
                         [None, 'new_country_recipient', 'unresolved_recipient', 'excluded_by_player_condition'])
        self.assertEqual(index.issue(hits['events', 'loop'][0]), 'unconfirmed_source')
        self.assertIsNone(index.issue(index.rewards['research_options']['T']['events', 'reward'][0]))
        self.assertNotIn('T', index.grants)
        self.assertEqual(index.routes()['events', 'reward']['option'], 'accept')

    def test_shared_build_and_reset_boundaries(self):
        trees = ReferenceTrees(MagicMock(), {'catalogs': []}, {}, None)
        trees.revision = MagicMock(return_value='one')
        trees.tooltips.find_one.return_value = None
        started, release = threading.Event(), threading.Event()
        def build(_db):
            started.set()
            if not release.wait(5):
                raise TimeoutError('Test build was not released')
            return ProgressSources([], [])
        with patch('sttv_server.tree.service.ProgressSources.build', side_effect=build) as called, patch(
                'sttv_server.technology_tooltip.prepare_tooltip', return_value=None), ThreadPoolExecutor(2) as pool:
            a = pool.submit(trees.technology_tooltip, 'T', 'ru', [])
            self.assertTrue(started.wait(5))
            b = pool.submit(trees.technology_tooltip, 'T', 'en', [])
            with self.assertRaises(Busy):
                trees.clear('tooltips')
            with self.assertRaises(Busy):
                trees.clear('progress')
            release.set()
            a.result()
            b.result()
            self.assertEqual(called.call_count, 1)
            trees.clear()
            self.assertIsNotNone(trees.progress)
            trees.prepared = object()
            trees.clear('progress')
            trees.clear('progress')
            self.assertIsNotNone(trees.prepared)
            self.assertEqual(called.call_count, 1)
            trees.technology_tooltip('T', 'en', [])
            trees.revision.return_value = 'two'
            trees.technology_tooltip('T', 'ru', [])
            self.assertEqual(called.call_count, 3)
            trees.clear('all')
            self.assertIsNone(trees.prepared)
            self.assertIsNone(trees.progress)
            trees.db.drop_collection.assert_not_called()
