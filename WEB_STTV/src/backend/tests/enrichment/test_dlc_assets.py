"""Descriptor-relative thumbnails share the asset pipeline and remain confined."""
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from sttv.enrichment.assets.dlc import prepare
from sttv.common.errors import BuildError


def field(key, text):
    return {'kind': 'assignment', 'key': {'kind': 'scalar', 'text': key}, 'operator': '=',
            'value': {'kind': 'scalar', 'text': text}}


class DlcAssetTests(unittest.TestCase):
    def reader(self, path='thumbnail.png'):
        root = {'items': [{'enrichments': {'dlc': {'descriptors': [{'document_id': 'descriptor'}]}}}]}
        descriptor = {'source': {'file': 'dlc/example/example.dlc'}, 'items': [field('thumbnail', path)]}
        reader = Mock()
        reader.iter_objects.return_value = [{'id': 'dlc_test', 'document_id': 'catalog', 'pointer': '/items/0'}]
        reader.read_document.side_effect = lambda kind, identifier: root if identifier == 'catalog' else descriptor
        return reader

    def test_descriptor_relative_path_and_missing_placeholder(self):
        source = Path('WEB_STTV/data/tests/game').resolve()
        settings = SimpleNamespace(source=source, dlc_root=source / 'dlc', options={'dlc_thumbnails': {'field': 'thumbnail'}})
        images = Mock(); images.get.return_value = 'image_hash'
        report = {'counts': {}, 'diagnostics': []}
        self.assertEqual(prepare(self.reader(), settings, images, report), {'dlc_test': 'image_hash'})
        images.get.assert_called_once_with('dlc/example/thumbnail.png', {'dlc': 'dlc_test'})
        report = {'counts': {}, 'diagnostics': []}
        self.assertEqual(prepare(self.reader(''), settings, images, report), {'dlc_test': None})
        self.assertEqual(report['diagnostics'][0]['code'], 'dlc_thumbnail_missing')

    def test_traversal_and_absolute_thumbnail_paths_are_rejected(self):
        source = Path('WEB_STTV/data/tests/game').resolve()
        settings = SimpleNamespace(source=source, dlc_root=source / 'dlc', options={'dlc_thumbnails': {'field': 'thumbnail'}})
        for path in ('../outside.png', 'C:/outside.png', '/outside.png'):
            with self.subTest(path=path), self.assertRaises(BuildError):
                prepare(self.reader(path), settings, Mock(), {'counts': {}, 'diagnostics': []})
