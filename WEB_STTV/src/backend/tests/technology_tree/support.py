"""Small structural fixtures and isolated ready database sets."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from sttv.common.paths import PRODUCT_ROOT
from sttv.common.json_io import read_json
from sttv.enrichment.technology_tree.inputs import record_for
from sttv.enrichment.technology_tree.representations import prepare
from sttv.enrichment.technology_tree.settings import resolve_rules


def value(text):
    return {'kind': 'scalar', 'text': str(text)}


def block(*items):
    return {'kind': 'block', 'items': list(items)}


def assignment(key, item):
    return {'kind': 'assignment', 'key': value(key), 'operator': '=',
            'value': item if isinstance(item, dict) else value(item)}


def logical(operator, *items):
    return {'kind': 'logical_operation', 'operator': operator, 'body': block(*items)}


def tech(key, parents=(), tier=1, area='physics', category='computing', extra=()):
    return assignment(key, block(assignment('tier', tier), assignment('area', area),
        assignment('category', block(value(category))),
        assignment('prerequisites', block(*(p if isinstance(p, dict) else value(p) for p in parents))), *extra))


def catalog(nodes):
    registry = read_json(PRODUCT_ROOT / 'config/datasets.json')['datasets']
    return [record_for('technologies', 'a' * 64, f'/items/{i}', n) for i, n in enumerate(nodes)]


def rules(*ids):
    original = resolve_rules(read_json(PRODUCT_ROOT / 'config/enrichment/technology_tree/rules.json'))
    if ids:
        by_id = {r['id']: r for r in original['rules']}
        original['rules'] = [by_id[k] for k in ids]
    return original


class SetFixture(unittest.TestCase):
    def setUp(self):
        base = PRODUCT_ROOT / 'data/tests'
        base.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.temporary.name)
        self.work = self.root / 'work'
        self.work.mkdir()
        self.variables = self.root / 'variables.json'
        self.save(self.variables, {'WORK_DIR': str(self.work), 'STELLARIS_ROOT': str(self.root / 'absent_game'),
                                   'TECH_PATH': 'common/technology'})
        from storage.fixtures import publish
        from sttv.common.datasets import KINDS
        self.manifest = publish(self.variables, {kind: [{
            'source': {'root': 'STELLARIS_ROOT', 'file': 'dlc_metadata/dlc_info.txt' if kind == 'dlcs' else f'common/{kind}/empty.txt'},
            'items': [], 'metadata': {'expansions': []}}] for kind in KINDS})
        self.options = read_json(PRODUCT_ROOT / 'config/enrichment/technology_tree.json')
        self.options['combination'] = {'base': 'work', 'path': 'combination.json'}
        self.options['rules'] = {'base': 'work', 'path': 'rules.json'}
        self.config = self.root / 'operation.json'
        self.save(self.config, self.options)
        self.save(self.work / 'rules.json', rules('same_area', 'highest_tier'))
        self.combo = read_json(PRODUCT_ROOT / 'config/enrichment/technology_tree/combinations/reference_default.json')
        self.save(self.work / 'combination.json', self.combo)
        self.db = {'documents': [{'source': {'root': 'STELLARIS_ROOT', 'file': 'common/technology/test.txt'},
            'items': [tech('parent'), tech('child', ['parent'])], 'metadata': {'expansions': []}}]}
        self.save_db()

    def tearDown(self):
        assert self.root.resolve().is_relative_to((PRODUCT_ROOT / 'data/tests').resolve())
        self.temporary.cleanup()

    def save(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

    def save_db(self):
        from storage.fixtures import publish
        publish(self.variables, {'technologies': self.db['documents']})

    def run_operation(self, **kwargs):
        from sttv.enrichment.technology_tree import enrich_technology_tree
        return enrich_technology_tree(self.variables, self.config, **kwargs)

    def assert_success(self, result):
        self.assertIn(result['status'], ('success', 'success_with_warnings'), result['error'])

    def read_db(self):
        from storage.fixtures import documents
        return {'documents': documents(self.manifest), **{'technology_tree': read_json(self.manifest).get('technology_tree')}}
