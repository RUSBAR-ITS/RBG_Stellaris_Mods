"""Manifest transactions, selective reuse and combination invalidation."""

from copy import deepcopy
import os
from unittest.mock import patch

from sttv.common.json_io import read_json
from sttv.storage import open_set
from sttv.storage.publication import Publication
from sttv.storage.settings import load
from sttv.enrichment.technology_tree import revisions
from storage.fixtures import publish, documents
from .support import SetFixture, tech, assignment, block


class OperationTests(SetFixture):
    def test_publication_reuse_force_and_other_inputs_unchanged(self):
        before = read_json(self.manifest)
        first = self.run_operation()
        self.assert_success(first)
        self.assertTrue(first['database_written'])
        actual = read_json(self.manifest)
        self.assertEqual(before['set_id'], actual['set_id'])
        self.assertNotEqual(before['snapshot_revision'], actual['snapshot_revision'])
        for kind in before['datasets']:
            if kind != 'technologies':
                self.assertEqual(before['datasets'][kind], actual['datasets'][kind])
        with patch('sttv.enrichment.technology_tree.evidence.load', side_effect=AssertionError('No evidence on reuse')):
            second = self.run_operation()
        self.assert_success(second)
        self.assertEqual(second['action'], 'reused')
        self.assertEqual(second['coverage']['verified'], 1)
        self.assertEqual(second['coverage']['not_checked'], 14)
        forced = self.run_operation(recalculate=True)
        self.assert_success(forced)
        self.assertEqual(forced['action'], 'computed')
        self.assertFalse(forced['database_written'])
        self.assertEqual(first['revisions'], forced['revisions'])

    def test_combinations_variants_and_old_children_replaced(self):
        self.db['documents'][0]['items'] = [tech('a'), tech('b', area='engineering'), tech('c', ['a', 'b'],
            extra=[assignment('technology_swap', block(assignment('area', 'engineering')))])]
        self.save_db()
        first = self.run_operation()
        self.assert_success(first)
        self.combo.update(id='other', variants={'c': 'swap:1'})
        self.save(self.work / 'combination.json', self.combo)
        self.assert_success(self.run_operation())
        self.assertEqual(len(read_json(self.manifest)['technology_tree']['combinations']), 2)
        self.combo.update(id='reference_default')
        self.save(self.work / 'combination.json', self.combo)
        self.assert_success(self.run_operation())
        rows = {n['key']['text']: n['enrichments']['technology_tree']['reference_default']
                for n in self.read_db()['documents'][0]['items']}
        self.assertEqual(rows['a']['children'], [])
        self.assertEqual(rows['b']['children'], ['c'])
        self.assertEqual(rows['c']['parent_tech'], 'b')

    def test_changed_evidence_and_rules_invalidate_reuse(self):
        first = self.run_operation()
        self.assert_success(first)
        building = documents(self.manifest, 'buildings')[0]
        building['items'].append(assignment('new', block()))
        publish(self.variables, {'buildings': [building]})
        second = self.run_operation()
        self.assert_success(second)
        self.assertNotEqual(first['revisions']['input_revision'], second['revisions']['input_revision'])
        with patch.object(revisions, 'IMPLEMENTATION_REVISION', 'changed'):
            third = self.run_operation()
        self.assert_success(third)
        self.assertNotEqual(second['revisions']['calculation_revision'], third['revisions']['calculation_revision'])

    def test_invalid_results_are_recomputed_and_obsolete_nodes_removed(self):
        self.assert_success(self.run_operation())
        self.db = self.read_db()
        node = self.db['documents'][0]['items'][0]
        node['enrichments']['technology_tree']['reference_default']['children'] = []
        obsolete = assignment('category_definition', block())
        obsolete['enrichments'] = deepcopy(node['enrichments'])
        self.db['documents'][0]['items'].append(obsolete)
        self.save_db()
        result = self.run_operation()
        self.assert_success(result)
        self.assertEqual(result['action'], 'computed')
        self.assertNotIn('enrichments', self.read_db()['documents'][0]['items'][-1])

    def test_errors_lock_and_atomic_failure_keep_previous_snapshot(self):
        before = self.manifest.read_bytes()
        original = os.replace
        def fail_manifest(source, target):
            if target == self.manifest:
                raise OSError('Injected failure')
            return original(source, target)
        with patch('os.replace', side_effect=fail_manifest):
            result = self.run_operation()
        self.assertEqual(result['status'], 'failed')
        self.assertFalse(result['database_written'])
        self.assertEqual(self.manifest.read_bytes(), before)
        with Publication(load(self.variables)):
            self.assertEqual(self.run_operation()['error']['code'], 'storage_busy')
        for variants in ({'unknown': 'base'}, {'child': 'swap:1'}):
            self.combo['variants'] = variants
            self.save(self.work / 'combination.json', self.combo)
            self.assertEqual(self.run_operation()['status'], 'failed')
            self.assertEqual(self.manifest.read_bytes(), before)

    def test_snapshot_detects_mid_operation_file_change(self):
        from sttv.enrichment.technology_tree import operation
        original = operation.evidence.load
        reader = open_set(self.manifest)
        path = reader.paths[('components', reader.document_ids('components')[0])]
        def changed(*args):
            result = original(*args)
            with path.open('a') as handle:
                handle.write(' ')
            return result
        before = self.manifest.read_bytes()
        with patch.object(operation.evidence, 'load', side_effect=changed):
            result = self.run_operation()
        self.assertEqual(result['error']['code'], 'changed_input')
        self.assertEqual(self.manifest.read_bytes(), before)

    def test_report_failure_retains_true_publication_state(self):
        with patch('sttv.enrichment.technology_tree.operation.save_json', side_effect=OSError('Report unavailable')):
            result = self.run_operation()
        self.assertEqual(result['status'], 'failed')
        self.assertTrue(result['database_written'])
        self.assertEqual(result['error']['code'], 'report_write_error')

    def test_projection_worker_reports_corrupt_document_with_context(self):
        reader = open_set(self.manifest)
        identifier = reader.document_ids('buildings')[0]
        path = reader.paths[('buildings', identifier)]
        raw = path.read_bytes()
        path.write_bytes(raw.replace(b'"items": []', b'"items": {}'))
        result = self.run_operation()
        self.assertEqual(result['status'], 'failed')
        self.assertFalse(result['database_written'])
        self.assertEqual(result['error']['details']['document_id'], identifier)
        self.assertEqual(result['error']['details']['database'], 'buildings')
