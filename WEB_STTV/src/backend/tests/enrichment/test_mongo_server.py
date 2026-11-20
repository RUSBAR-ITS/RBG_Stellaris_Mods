"""MongoDB profile and localization read checks for the server."""

import json
import os
import unittest
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import urlopen

from document_package.errors import BuildError
from sttv.mongo.connection import database
from sttv.mongo.settings import settings
from sttv.server.http import make_server

CONFIG = Path(__file__).resolve().parents[4] / 'config'


class ServerTests(unittest.TestCase):
    def test_profiles(self):
        path = CONFIG / 'server.json'
        self.assertEqual(settings(path).name, 'local')
        for name in ['local', 'network']:
            self.assertEqual(settings(path, name).name, name)
        with self.assertRaises(BuildError):
            settings(path, 'wrong')

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
