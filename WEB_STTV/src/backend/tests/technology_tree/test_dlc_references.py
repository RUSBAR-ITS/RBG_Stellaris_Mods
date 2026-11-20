"""Real reader, publication and revision boundaries for recursive DLC evaluation."""

from copy import deepcopy
from unittest.mock import patch

from sttv.enrichment.technology_tree.settings import load
from sttv.enrichment.dlc.analysis import Analysis
from sttv.storage import open_set
from storage.fixtures import publish
from .support import SetFixture, tech, assignment as a, block as b, value


class DlcReferencesTests(SetFixture):
    def setUp(self):
        super().setUp()
        def document(kind, items):
            return [{'source': {'root': 'STELLARIS_ROOT', 'file': f'common/{kind}/sample.txt'},
                     'items': items, 'metadata': {'expansions': []}}]
        catalogs = {'ship_categories': document('ship_categories', [a('bio', b())]),
                    'graphical_culture': document('graphical_culture', [a('bio_provider', b(
                        a('ship_kinds', b(value('bio'))), a('selectable', b(a('host_has_dlc', 'Example')))))])}
        catalogs['dlcs'] = [{'source': {'root': 'STELLARIS_ROOT', 'file': 'dlc_metadata/dlc_info.txt'},
                             'items': [a('dlcs', b(a('dlc1', b(a('name', 'Example')))))], 'metadata': {'expansions': []}}]
        self.catalogs = catalogs
        publish(self.variables, catalogs)
        self.db['documents'][0]['items'] = [tech('parent', extra=[a('potential', b(a('uses_ship_category', 'bio')))]),
                                           tech('child', ['parent'])]
        self.save_db()

    def test_new_provider_invalidates_the_whole_relation_not_only_old_objects(self):
        before = self.read_db()['documents'][0]['items'][0]['value']
        first = self.run_operation(dlc_enabled=[])
        self.assert_success(first)
        self.assertEqual(first['counts']['hidden'], 1)
        repeated = self.run_operation(dlc_enabled=[])
        self.assert_success(repeated)
        self.assertEqual(repeated['action'], 'reused')
        providers = deepcopy(self.catalogs['graphical_culture'])
        providers[0]['items'].append(a('free_provider', b(a('ship_kinds', b(value('bio'))))))
        publish(self.variables, {'graphical_culture': providers})
        added = self.run_operation(dlc_enabled=[])
        self.assert_success(added)
        self.assertEqual(added['action'], 'computed')
        self.assertEqual(added['counts']['hidden'], 0)
        self.assertNotEqual(added['revisions']['input_revision'], first['revisions']['input_revision'])
        self.assertEqual(self.read_db()['documents'][0]['items'][0]['value'], before)

    def test_shared_objects_are_projected_once_and_profiles_do_not_read_again(self):
        from sttv.enrichment.technology_tree.inputs import technology_input
        from sttv.enrichment.technology_tree.representations import prepare
        reader, settings = open_set(self.manifest), load(self.variables, self.config)
        _, records, _ = technology_input(settings, reader)
        technologies = prepare(records, {})
        technologies['another'] = {**technologies['parent'], 'id': 'another'}
        with patch.object(reader, 'project', wraps=reader.project) as calls:
            analysis = Analysis(technologies, {'dlc1': 'Example'}, settings.dlc_rules, reader=reader)
            self.assertEqual(calls.call_count, 2)
            for enabled in ([], ['dlc1'], [], ['dlc1']):
                analysis.evaluate(enabled)
            self.assertEqual(calls.call_count, 2)
        self.assertEqual(len(analysis.library.loaded), 2)
        self.assertFalse((self.root / 'absent_game').exists())

    def test_service_cache_reuses_graph_without_reading_dependencies_again(self):
        from sttv.enrichment.dlc.cache import AnalysisCache
        from sttv.enrichment.technology_tree.inputs import technology_input
        from sttv.enrichment.technology_tree.representations import prepare
        settings, cache = load(self.variables, self.config), AnalysisCache()
        first = open_set(self.manifest)
        _, records, _ = technology_input(settings, first)
        technologies = prepare(records, {})
        prepared = cache.get(technologies, {'dlc1': 'Example'}, settings.dlc_rules, first)
        prepared.evaluate([])
        second = open_set(self.manifest)
        with patch.object(second, 'project', wraps=second.project) as reads:
            reused = cache.get(technologies, {'dlc1': 'Example'}, settings.dlc_rules, second)
            self.assertIs(prepared, reused)
            self.assertTrue(reused.graph.statistics['reused_graph'])
            self.assertEqual(reads.call_count, 0)
            self.assertTrue(reused.evaluate(['dlc1'])[0]['parent']['visible'])
        providers = deepcopy(self.catalogs['graphical_culture'])
        providers[0]['items'].append(a('free_provider', b(a('ship_kinds', b(value('bio'))))))
        publish(self.variables, {'graphical_culture': providers})
        third = cache.get(technologies, {'dlc1': 'Example'}, settings.dlc_rules, open_set(self.manifest))
        self.assertIsNot(third, prepared)
