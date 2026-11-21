import json
import os
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from pymongo.errors import ServerSelectionTimeoutError

from sttv_server.config import load_config
from sttv_server.database import connect
from sttv_server.http import make_server
from sttv_server.localization import determine_key, lookup


ROOT = Path(__file__).resolve().parents[1]
CONFIG = load_config(ROOT / 'config/server.json')
EXAMPLES = json.loads((ROOT / 'tests/fixtures/localization.json').read_text(encoding='utf-8'))


def post(url, payload):
    request = Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    try:
        response = urlopen(request, timeout=10)
    except HTTPError as error:
        response = error
    with response:
        return response.status, json.load(response)


class LocalizationTests(unittest.TestCase):
    def test_config_uses_rules_path_relative_to_server_file(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            rules_path = root / 'rules' / 'custom.json'
            rules_path.parent.mkdir()
            rules = {'example': {'suffix': '_custom'}}
            rules_path.write_text(json.dumps(rules), encoding='utf-8')
            path = root / 'server.json'
            path.write_text(json.dumps({'localization_keys_file': 'rules/custom.json'}), encoding='utf-8')
            self.assertEqual(load_config(path)['key_rules'], rules)

    def test_key_rules(self):
        rules = CONFIG['key_rules']
        for value in ('physics', 'society', 'engineering'):
            self.assertEqual(determine_key(rules, 'research_area', value), value.upper())
        self.assertEqual(determine_key(rules, 'research_category', 'computing'), 'computing')
        self.assertEqual(determine_key(rules, 'technology_name', 'tech_titans'), 'tech_titans')
        self.assertEqual(determine_key(rules, 'technology_description', 'tech_titans'), 'tech_titans_desc')
        self.assertIsNone(determine_key(rules, 'research_area', 'other'))
        self.assertIsNone(determine_key(rules, 'unknown', 'physics'))

    def test_batching_and_opaque_fragments(self):
        records = {
            'a': '[$opaque$ [Root.GetName]] £$opaque$£ $b$ $missing$ $number|Y$',
            'b': '§Y$c$§!', 'c': 'value', 'empty': '',
        }
        calls = []

        def fetch(language, keys):
            self.assertEqual(language, 'en')
            calls.append(keys)
            return [(key, records[key]) for key in keys if key in records]

        keys = ['a', 'b', 'a', 'empty', 'absent']
        result = lookup('en', keys, fetch)
        rendered = '[$opaque$ [Root.GetName]] £$opaque$£ §Yvalue§! $missing$ $number|Y$'
        self.assertEqual([row['key'] for row in result['items']], keys)
        self.assertEqual([row['text'] for row in result['items']], [rendered, '§Yvalue§!', rendered, '', None])
        self.assertEqual(calls, [['a', 'absent', 'b', 'empty'], ['c', 'missing', 'number']])

    def test_colored_static_references_preserve_dynamic_slots_and_plain_cached_values(self):
        records = {'sentence': '$energy|G$ $energy$ $energy|Y$ $PLANET|Y$ $unknown|Y$',
                   'energy': '$label$', 'label': 'Energy', 'PLANET': 'Planet'}
        result = lookup('en', ['sentence', 'energy'], lambda _, keys: [(k, records[k]) for k in keys if k in records])
        self.assertEqual([i['text'] for i in result['items']],
                         ['§GEnergy§! Energy §YEnergy§! $PLANET|Y$ $unknown|Y$', 'Energy'])

    def test_cycle_is_relative_to_the_requested_root(self):
        records = {'A': 'a:$B$:$C$', 'B': 'b:$A$', 'C': 'c', 'S': '$S$'}
        result = lookup('ru', ['A', 'B', 'S'], lambda _, keys: [(k, records[k]) for k in keys])
        self.assertEqual([i['text'] for i in result['items']], ['a:b:$A$:c', 'b:a:$B$:c', '$S$'])

    def test_long_chain(self):
        def fetch(_, keys):
            return [(k, f'${int(k) + 1}$' if int(k) < 1100 else 'done') for k in keys]

        self.assertEqual(lookup('ru', ['0'], fetch)['items'][0]['text'], 'done')

    def test_database_error(self):
        def unavailable(*args):
            raise ServerSelectionTimeoutError('test')

        with make_server(('127.0.0.1', 0), unavailable) as api:
            thread = threading.Thread(target=api.serve_forever)
            thread.start()
            try:
                url = f'http://127.0.0.1:{api.server_port}/api/localization/lookup'
                self.assertEqual(post(url, {'language': 'ru', 'keys': ['key']})[0], 503)
            finally:
                api.shutdown()
                thread.join()


@unittest.skipUnless(os.environ.get('STTV_API_URL'), 'requires running server on the VM')
class LiveApiTests(unittest.TestCase):
    def test_single_and_batch(self):
        url = os.environ['STTV_API_URL']
        with connect(CONFIG['mongodb']) as client:
            collection = client[CONFIG['mongodb']['database']][CONFIG['mongodb']['collection']]
            for language, expected in EXAMPLES.items():
                for keys in (['PHYSICS'], ['tech_titans'], list(expected),
                             ['PHYSICS', '__missing_example__', 'physics', 'PHYSICS'], []):
                    with self.subTest(language=language, keys=keys):
                        self.assertEqual(post(url, {'language': language, 'keys': keys}),
                                         (200, {'language': language, 'items': [
                                             {'key': k, 'text': expected.get(k)} for k in keys]}))
                for key in expected:
                    row = collection.find_one({'_id': {'language': language, 'key': key}})
                    raw = row['definitions'][row['selected']]['raw']
                    self.assertEqual(raw, '$concept_physics_research$' if key == 'physics_research' else expected[key])

    def test_invalid_requests(self):
        for body in ({'language': 'de', 'keys': ['PHYSICS']}, {'language': 'ru', 'keys': 'PHYSICS'},
                     {'language': 'ru', 'keys': [42]}, {'keys': []}):
            self.assertEqual(post(os.environ['STTV_API_URL'], body)[0], 400)
