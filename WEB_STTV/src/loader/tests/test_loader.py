"""Standalone loader checks. Live publication requires an explicitly isolated MongoDB."""

import json
import os
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from bson import BSON
from document_package.errors import BuildError
from document_package.package import commit_manifest, write_batch
from pymongo.collection import Collection

from sttv_loader.__main__ import collection_versions, run
from sttv_loader.connection import database
from sttv_loader.importer import MAX_DOCUMENT, prepare, typed_id
from sttv_loader.inputs import InputRecord, Inputs
from sttv_loader.provenance import restore_tree, split_tree
from sttv_loader.publication import CONTROL, local_lock, promote, writer
from sttv_loader.settings import settings


SPAN = {'start': 3, 'end': 9, 'line': 1, 'column': 4, 'end_line': 1, 'end_column': 10}
ORIGIN = {'root': 'GAME', 'file': 'template.txt', 'span': SPAN, 'generated_span': SPAN,
          'expansion_id': 'call_2'}


def scalar(text):
    return {'kind': 'scalar', 'text': text, 'origin': ORIGIN, 'span': SPAN}


def assign(key, value):
    return {'kind': 'assignment', 'key': scalar(key), 'operator': '=', 'value': value}


def block(*items):
    return {'kind': 'block', 'origin': None, 'items': list(items)}


def write_script(path, file, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {'source': {'root': 'GAME', 'file': file}, 'items': items, 'metadata': {'expansions': [
        {'id': 'call_1', 'parent_id': None}, {'id': 'call_2', 'parent_id': 'call_1'}]}}
    path.write_text(json.dumps(data), encoding='utf-8')


def fixture(root):
    transition = assign('terraform_link', block(assign('from', scalar('A')), assign('to', scalar('B'))))
    items = [assign('namespace', scalar('test')), transition, transition]
    write_script(root / 'scripts/transitions.json', 'common/terraform/a.txt', items)
    write_script(root / 'scripts/empty.json', 'common/terraform/empty.txt', items[:1])
    write_script(root / 'scripts/nested/events.json', 'events/test.txt', [
        assign('country_event', block(assign('id', scalar('test.1')), assign('origin', scalar('test_origin')))),
        assign('country_event', block(assign('id', scalar('test.2'))))])
    (root / 'empty').mkdir()
    entries = [{'_id': {'language': 'en', 'key': 'name'}, 'text': 'Example'}]
    commit_manifest(root / 'loc', 'localization', [write_batch(root / 'loc', entries)])
    return [
        {'path': 'scripts', 'identity': 'anonymous', 'collection': 'terraform', 'provenance': 'terraform_src'},
        {'path': 'scripts/nested', 'identity': 'field', 'field': 'id', 'root_types': ['country_event'],
         'collection': 'events', 'provenance': 'events_src'},
        {'path': 'empty', 'identity': 'key', 'collection': 'empty', 'provenance': 'empty_src'},
        {'path': 'loc', 'identity': 'package', 'collection': 'localization'},
    ]


class LoaderTests(unittest.TestCase):
    def test_round_trip_and_invalid_reference(self):
        tree = block(assign('origin', scalar('example')), assign('span', scalar('example')))
        compact, provenance = split_tree(tree, 'key')
        document = {'_id': 'key', 'tree': compact}
        self.assertEqual(BSON.encode(restore_tree(document, provenance)), BSON.encode(tree))
        self.assertEqual(provenance['origins'][0]['generated_span'], 0)
        self.assertEqual(provenance['spans'], [SPAN])
        self.assertEqual(len(provenance['origins']), 1)
        self.assertIsNone(compact['origin'])
        self.assertNotIn('span', compact)
        for bad in (-1, 1, True):
            compact['items'][0]['key']['origin'] = bad
            with self.assertRaisesRegex(BuildError, 'reference'):
                restore_tree(document, provenance)
        with self.assertRaisesRegex(BuildError, 'another object'):
            restore_tree(document, {**provenance, '_id': 'other'})

    def test_bson_limits_and_types(self):
        self.assertNotEqual(typed_id({'_id': True}), typed_id({'_id': 1}))
        self.assertNotEqual(typed_id({'_id': {'a': 1, 'b': 2}}), typed_id({'_id': {'b': 2, 'a': 1}}))
        for key in ('tree', 'provenance'):
            node = scalar('test')
            if key == 'tree':
                node['text'] = 'x' * MAX_DOCUMENT
            else:
                node['origin'] = {**ORIGIN, 'file': 'x' * MAX_DOCUMENT}
            with self.assertRaisesRegex(BuildError, 'BSON bytes'):
                prepare(InputRecord('events', {'_id': 'too_large', 'tree': node}, 'events_src'))

    def test_discovery_and_identity(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            sources = fixture(root)
            options = {'input_root': '.', 'history_collection': 'history', 'sources': list(reversed(sources))}
            records = list(Inputs(options, root).records())
            self.assertEqual([r.document['_id'] for r in records if r.collection == 'events'], ['test.1', 'test.2'])
            ids = [r.document['_id'] for r in records if r.collection == 'terraform']
            self.assertEqual(ids, [{'root': 'GAME', 'file': 'common/terraform/a.txt', 'item': i} for i in (1, 2)])
            self.assertEqual(sum(r.collection == 'history' for r in records), 3)
            with self.assertRaises(BuildError):
                Inputs({**options, 'sources': sources + sources[:1]}, root)

    def test_workspace_lock(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'lock'
            with local_lock(path), self.assertRaises(BuildError):
                with local_lock(path):
                    self.fail('second writer acquired the same lock')


@unittest.skipUnless(os.environ.get('STTV_LOADER_TEST_CONFIG'), 'requires a dedicated MongoDB test configuration')
class MongoTests(unittest.TestCase):
    def test_publication_lifecycle(self):
        supplied = Path(os.environ['STTV_LOADER_TEST_CONFIG']).resolve()
        config = settings(supplied)
        self.assertTrue(config.profile['database'].startswith('sttv_loader_test_'))
        with TemporaryDirectory() as directory, database(config) as db:
            self.assertEqual(db.list_collection_names(), [], 'use a fresh, empty test database')
            root = Path(directory)
            sources = fixture(root)
            options = {**config.options, 'input_root': '.', 'scratch_directory': 'scratch',
                       'history_collection': 'history', 'sources': sources}
            path = root / 'loader.json'
            path.write_text(json.dumps(options), encoding='utf-8')
            try:
                run('create', path)
                db.empty.insert_one({'_id': 'keep'})
                run('create', path)
                self.assertIsNotNone(db.empty.find_one({'_id': 'keep'}))
                run('drop', path)
                self.assertEqual(db.list_collection_names(), [])
                run('create', path)
                expected = run('load', path)['documents']
                self.assertEqual(expected['events'], 2)
                self.assertEqual(expected['history'], 3)
                self.assertEqual(expected['empty'], 0)
                self.assertEqual(run('verify', path)['documents'], expected)
                self.assertEqual(db.events.find_one({'tree.value.items.value.text': 'test_origin'})['_id'], 'test.1')
                original_ids = list(db.terraform.find({}, {'_id': 1}).sort('_id'))
                copied = root / 'copied'
                shutil.copytree(root / 'scripts', copied / 'scripts')
                (copied / 'scripts/transitions.json').rename(copied / 'scripts/aaa.json')
                shutil.copytree(root / 'loc', copied / 'loc')
                (copied / 'empty').mkdir()
                options.update(input_root='copied', sources=list(reversed(sources)))
                path.write_text(json.dumps(options), encoding='utf-8')
                run('drop', path)
                run('load', path)
                self.assertEqual(list(db.terraform.find({}, {'_id': 1}).sort('_id')), original_ids)
                versions = collection_versions(db, list(expected))
                with patch('sttv_loader.publication.promote', side_effect=self.interrupt_promotion):
                    with self.assertRaisesRegex(RuntimeError, 'injected'):
                        run('load', path)
                self.assertEqual(collection_versions(db, list(expected)), versions)
                insert = Collection.insert_many

                def fail_metadata(collection, rows):
                    if 'origins' in rows[0]:
                        raise RuntimeError('injected metadata write failure')
                    return insert(collection, rows)

                with patch.object(Collection, 'insert_many', fail_metadata):
                    with self.assertRaisesRegex(RuntimeError, 'metadata write failure'):
                        run('load', path)
                self.assertEqual(collection_versions(db, list(expected)), versions)
                # Leave the same journal and namespaces that an interrupted rename would leave.
                with writer(db, settings(path).scratch):
                    entry = {'name': 'events', 'stage': 'sttv__new_test', 'backup': 'sttv__old_test',
                             'existed': True}
                    db[CONTROL].update_one({'_id': 'writer'}, {'$set': {'plan': [entry], 'phase': 'promoting'}})
                    db.create_collection(entry['stage'])
                    promote(db, [entry])
                with self.assertRaisesRegex(BuildError, 'recovery'):
                    run('verify', path)
                run('create', path)
                self.assertEqual(collection_versions(db, list(expected)), versions)
                self.assertEqual(run('verify', path)['documents'], expected)
                with patch('sttv_loader.importer.restore_tree', side_effect=BuildError('test', 'staged verification')):
                    with self.assertRaisesRegex(BuildError, 'staged verification'):
                        run('load', path)
                self.assertEqual(run('verify', path)['documents'], expected)
                db.events_src.update_one({'_id': 'test.1'}, {'$set': {'spans': []}})
                with self.assertRaises(BuildError):
                    run('verify', path)
                run('load', path)
                (copied / 'scripts/nested/copy.json').write_bytes((copied / 'scripts/nested/events.json').read_bytes())
                with self.assertRaisesRegex(BuildError, 'Duplicate'):
                    run('load', path)
                self.assertEqual(db.events.count_documents({}), 2)
                self.assertFalse(any(n.startswith(('sttv__old_', 'sttv__new_')) for n in db.list_collection_names()))
            finally:
                db.client.drop_database(db.name)

    @staticmethod
    def interrupt_promotion(db, plan):
        promote(db, plan[:2])
        raise RuntimeError('injected promotion failure')
