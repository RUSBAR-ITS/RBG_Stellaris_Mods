"""Exercise publication races and interrupted writes on an isolated VM namespace."""

import json
import os
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

from sttv_server.config import load_config
from sttv_server.database import connect
from sttv_server.http import make_server
from sttv_server.tree.service import ReferenceTrees


@unittest.skipUnless(os.environ.get('STTV_TREE_PUBLICATION_TEST'), 'requires the test VM')
class PublicationTests(unittest.TestCase):
    def test_publication_lifecycle(self):
        cfg = load_config(Path(__file__).resolve().parents[1] / 'config/server.json')
        prefix = 'tree_test_' + uuid4().hex + '_'
        with connect(cfg['mongodb']) as client:
            db = client[cfg['mongodb']['database']]
            trees = ReferenceTrees(db, cfg['tree_rules'], cfg['key_rules'], None, prefix)
            self.assertFalse(db.list_collection_names(filter={'name': {'$regex': '^' + prefix}}))
            revision = trees.revision()
            item = {'_id': 't', 'availability': True, 'children': [], 'parent_tech': None,
                    'area': 'physics', 'location': {'ru': [1, 0], 'en': [1, 0]}}
            started, release = threading.Event(), threading.Event()
            def build(*_):
                started.set()
                if not release.wait(8):
                    raise TimeoutError('build was not released')
                return [item.copy()], {}
            with patch('sttv_server.tree.service.PreparedTree') as prepare, patch(
                    'sttv_server.tree.service.cards.catalog', return_value={'t': {}}), make_server(
                        ('127.0.0.1', 0), None, trees) as api:
                builder = prepare.return_value
                builder.build.side_effect = build
                url = 'http://127.0.0.1:%d/api/trees/reference' % api.server_port
                def call(method='POST'):
                    req = Request(url, method=method, data=b'{}' if method == 'POST' else None)
                    try:
                        with urlopen(req, timeout=12) as response:
                            return response.status, json.load(response)
                    except HTTPError as exc:
                        return exc.code, json.load(exc)
                thread = threading.Thread(target=api.serve_forever)
                thread.start()
                try:
                    with ThreadPoolExecutor(2) as pool:
                        a = pool.submit(call)
                        self.assertTrue(started.wait(5))
                        b = pool.submit(call)
                        self.assertEqual(call('DELETE')[0], 409)
                        release.set()
                        self.assertEqual(a.result(), b.result())
                        self.assertEqual(a.result()[0], 200)
                        key = a.result()[1]['tree_id']
                    self.assertEqual(builder.build.call_count, 1)
                    with trees.operation(clear=True):
                        self.assertEqual(call()[0], 409)
                    trees.rules_revision += '-test'
                    builder.build.side_effect = RuntimeError('injected publication failure')
                    self.assertEqual(call()[0], 500)
                    self.assertEqual(trees.registry.find_one({'_id': key})['state'], 'failed')
                    builder.build.side_effect = build
                    self.assertEqual(call()[0], 200)
                    with patch.object(trees, 'revision', return_value=revision + '-test'):
                        self.assertEqual(call()[0], 200)
                    self.assertEqual(builder.build.call_count, 4)
                    db.drop_collection(prefix + key)
                    self.assertEqual(call('DELETE'), (200, {'removed_collections': 0}))
                    self.assertFalse(trees.registry.find_one({}))
                finally:
                    release.set()
                    api.shutdown()
                    thread.join()
                    trees.clear()
                    db.drop_collection(trees.registry.name)
