"""Resource conversion, inheritance, source identity and reuse regression checks."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from PIL import Image
from sttv.common.paths import PRODUCT_ROOT
from sttv.common.errors import BuildError
from sttv.enrichment.assets.images import Images
from sttv.enrichment.assets.selection import attach
from sttv.enrichment.localization.snapshot import Snapshot
from sttv.storage.identity import source_hash
from sttv.storage.assets import verify_asset, check_assets


def scalar(value):
    return {'kind': 'scalar', 'text': value}


def assignment(key, value):
    return {'kind': 'assignment', 'key': scalar(key), 'value': value}


def block(items):
    return {'kind': 'block', 'items': items}


class ResourceTests(unittest.TestCase):
    def setUp(self):
        directory = PRODUCT_ROOT / 'data/stage18/tests'
        directory.mkdir(parents=True, exist_ok=True)
        self.temporary = TemporaryDirectory(dir=directory)
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.options = json.loads((PRODUCT_ROOT / 'config/enrichment/assets.json').read_text())
        self.source = root / 'source'
        self.source.mkdir()
        self.output = root / 'output'
        self.output.mkdir()
        self.staging = root / 'staging'
        self.staging.mkdir()
        self.settings = SimpleNamespace(options=self.options, source=self.source,
            storage=SimpleNamespace(root=self.output), localization=SimpleNamespace(selection_directory='common/technology'))
        self.report = {'inputs': [], 'diagnostics': [], 'counts': dict.fromkeys(
            ('references', 'reused', 'missing', 'converted', 'image_bytes_written', 'technologies', 'variants'), 0)}
        self.snapshot = Snapshot(self.report)

    def images(self, previous=None):
        return Images(self.settings, SimpleNamespace(directory=self.staging), previous or {}, self.snapshot, self.report)

    def test_dds_conversion_preserves_dimensions_alpha_and_deduplicates(self):
        image = Image.new('RGBA', (4, 3), (20, 80, 180, 97))
        image.save(self.source / 'a.dds')
        image.save(self.source / 'b.dds')
        images = self.images()
        first = images.get('a.dds', {})
        self.assertEqual(images.get('b.dds', {}), first)
        self.assertEqual(len(images.files), 1)
        row = images.files[first]
        verify_asset(self.output, row)
        with Image.open(self.output / row['path']) as converted:
            self.assertEqual(converted.size, image.size)
            self.assertEqual(converted.getpixel((0, 0)), (20, 80, 180, 97))

    def test_reuse_and_settings_change(self):
        Image.new('RGBA', (3, 3), (20, 30, 40, 255)).save(self.source / 'a.dds')
        first = self.images()
        identifier = first.get('a.dds', {})
        previous = {'settings_revision': first.revision, 'files': first.files, 'sources': first.sources}
        before = (self.output / first.files[identifier]['path']).stat().st_mtime_ns
        self.assertEqual(self.images(previous).get('a.dds', {}), identifier)
        self.assertEqual(self.report['counts']['reused'], 1)
        self.assertEqual((self.output / first.files[identifier]['path']).stat().st_mtime_ns, before)
        self.options['conversion']['compress_level'] = 1
        self.images(previous).get('a.dds', {})
        self.assertEqual(self.report['counts']['converted'], 2)

    def test_missing_corrupt_and_unsafe_inputs(self):
        images = self.images()
        self.assertIsNone(images.get('missing.dds', {'technology': 'example'}))
        (self.source / 'bad.dds').write_bytes(b'broken')
        self.assertIsNone(images.get('bad.dds', {}))
        self.assertEqual(len(self.report['diagnostics']), 2)
        with self.assertRaises(BuildError):
            images.get('../outside.dds', {})

    def test_damaged_output_does_not_pass_audit(self):
        Image.new('RGBA', (3, 3)).save(self.source / 'a.dds')
        images = self.images()
        row = images.files[images.get('a.dds', {})]
        (self.output / row['path']).write_bytes(b'broken')
        with self.assertRaises(BuildError):
            verify_asset(self.output, row)

    def test_inheritance_categories_and_unchanged_tree_source_hash(self):
        base = assignment('tech_a', block([assignment('icon', scalar('special')),
            assignment('category', block([scalar('computing')])),
            assignment('technology_swap', block([assignment('name', scalar('same')),
                                                assignment('inherit_icon', scalar('yes'))])),
            assignment('technology_swap', block([assignment('name', scalar('own'))]))]))
        base['enrichments'] = {'technology_tree': {'reference': {'parent_tech': 'root'}}}
        doc = {'document_id': 'example', 'source': {'file': 'common/technology/example.txt'}, 'items': [base]}
        before = source_hash(doc)
        calls = []
        def get(path, context):
            calls.append(path)
            return str(len(calls))
        categories = set()
        attach(doc, self.settings, SimpleNamespace(get=get), categories, self.report)
        self.assertEqual(calls, ['gfx/interface/icons/technologies/special.dds', 'gfx/interface/icons/technologies/own.dds'])
        self.assertEqual(categories, {'computing'})
        self.assertEqual(base['value']['items'][2]['enrichments']['presentation']['icon_asset_id'], '1')
        self.assertEqual(source_hash(doc), before)
        base['value']['items'].append(assignment('tier', scalar('4')))
        self.assertNotEqual(source_hash(doc), before)


if __name__ == '__main__':
    unittest.main()
