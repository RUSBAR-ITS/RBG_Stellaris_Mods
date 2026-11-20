"""Generic publication and read-only profile tests. Live tests use a private collection."""

import os
from dataclasses import replace
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
from threading import Thread
from urllib.error import HTTPError
from urllib.request import urlopen
import json

from bson import BSON
from pymongo.errors import BulkWriteError

from document_package.errors import BuildError
from document_package.package import Package, commit_manifest, write_batch
from sttv.loader.__main__ import run
from sttv.loader.publication import identity, publish, verify
from sttv.mongo.connection import database
from sttv.mongo.settings import settings
from sttv.server.http import make_server

CONFIG = Path(__file__).resolve().parents[4] / 'config'


class LoaderTests(unittest.TestCase):
    def test_profiles(self):
        for component, default in [('loader', 'network'), ('server', 'local')]:
            path = CONFIG / f'{component}.json'
            self.assertEqual(settings(path).name, default)
            for name in ['local', 'network']:
                self.assertEqual(settings(path, name).name, name)
            with self.assertRaises(BuildError):
                settings(path, 'wrong')

    def test_id_types_and_order(self):
        self.assertNotEqual(identity({'_id': {'x': 1, 'y': 2}}), identity({'_id': {'y': 2, 'x': 1}}))
        self.assertNotEqual(identity({'_id': True}), BSON.encode({'_id': 1}))

    @unittest.skipUnless(os.getenv('STTV_TEST_MONGO_LOCALIZATION') == '1', 'requires the test MongoDB')
    def test_publication(self):
        config = settings(CONFIG / 'loader.json')
        with TemporaryDirectory() as temporary, database(config) as db:
            root = Path(temporary)
            target = db['stage23_test_' + uuid4().hex]
            rows = [{'_id': 'tech_b', 'options': {'rank': 2, 'list': [True, 'raw']}},
                    {'_id': 'tech_a', 'options': {'rank': 1}}, {'_id': 'obsolete'}]
            batches = [write_batch(root, [row]) for row in rows]
            def package(descriptors):
                commit_manifest(root, 'technologies', descriptors)
                return Package(root)
            try:
                empty = package([])
                with self.assertRaisesRegex(BuildError, 'Unpublished collection'):
                    verify(target, empty)
                self.assertEqual(publish(target, empty), 0)
                original = package(batches)
                fixture = replace(config, options={**config.options, 'collections': {'technologies': target.name}})
                self.assertEqual(run('load', fixture, original)['documents'], 3)
                self.assertEqual(run('verify', fixture, package(batches[::-1]))['documents'], 3)
                with self.assertRaises(BuildError):
                    verify(target, package([batches[0], batches[0], batches[2]]))
                with self.assertRaises(BulkWriteError):
                    publish(target, package([batches[0], batches[0]]))
                self.assertEqual(verify(target, original), 3)
                broken = write_batch(root, [{'_id': 'damaged'}])
                (root / broken['path']).write_text('[]', encoding='utf-8')
                with self.assertRaisesRegex(BuildError, 'Checksum mismatch'):
                    publish(target, package([batches[0], broken]))
                self.assertEqual(verify(target, original), 3)
                self.assertEqual(publish(target, package(batches[:2])), 2)
                self.assertIsNone(target.find_one({'_id': 'obsolete'}))
                self.assertFalse(db.list_collection_names(filter={'name': {'$regex': '^' + target.name + '__loading_'}}))
            finally:
                target.drop()

    @unittest.skipUnless(os.getenv('STTV_TEST_MONGO_LOCALIZATION') == '1', 'requires the test MongoDB')
    def test_http_read(self):
        config = settings(CONFIG / 'server.json', 'network')
        with database(config) as db, make_server(db[config.options['collection']],
                {**config.options['http'], 'port': 0}) as server:
            thread = Thread(target=server.serve_forever)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_port}{config.options['http']['prefix']}"
                with urlopen(url + '/en/tech_titans', timeout=10) as response:
                    row = json.load(response)
                    self.assertEqual(row['definitions'][row['selected']]['raw'], 'Titans')
                with self.assertRaises(HTTPError) as missing:
                    urlopen(url + '/en/__stage23_missing__', timeout=10)
                self.assertEqual(missing.exception.code, 404)
                missing.exception.close()
            finally:
                server.shutdown()
                thread.join()
