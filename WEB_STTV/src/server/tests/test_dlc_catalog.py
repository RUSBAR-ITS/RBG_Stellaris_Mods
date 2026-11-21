import unittest
from unittest.mock import Mock, patch

from sttv_server.tree.dlcs import catalog, thumbnails
from sttv_server.tree.errors import BuildError


def fields(**values):
    return [{'kind': 'assignment', 'key': {'text': key}, 'operator': '=', 'value': {'text': value}}
            for key, value in values.items()]


def descriptor(name, path):
    return {'source': {'file': 'dlc/new_dlc/pack.dlc'}, 'tree': fields(name=name, thumbnail=path)}


class DlcCatalogTests(unittest.TestCase):
    def test_titles_and_descriptor_paths(self):
        data = {'dlc_descriptors': Mock()}
        data['dlc_descriptors'].find.return_value = [descriptor('One', 'images/cover.dds')]
        rows = [{'id': str(i), 'body': {'items': fields(name=name, localizable_name=f'GAME{i}')}}
                for i, name in enumerate(('One', 'Two', 'Three'))]
        strings = {'ru': {'sttv_0_name': '$translated$', 'translated': 'RU project', 'GAME1': 'RU fallback'},
                   'en': {'GAME0': 'EN game', 'sttv_0_name': 'unused'}}
        def read(language, keys):
            return ((key, strings[language][key]) for key in keys if key in strings[language])
        rules = {'dlc_project_name': {'prefix': 'sttv_', 'suffix': '_name'}}
        with patch('sttv_server.tree.dlcs.records', return_value=rows):
            result = catalog(data, rules, read)['items']
        self.assertEqual(result, [
            {'id': '0', 'name': {'ru': 'RU project', 'en': 'EN game'}, 'thumbnail': 'dlc/new_dlc/images/cover.png'},
            {'id': '1', 'name': {'ru': 'RU fallback', 'en': 'Two'}, 'thumbnail': None},
            {'id': '2', 'name': {'ru': 'Three', 'en': 'Three'}, 'thumbnail': None},
        ])

    def test_invalid_and_conflicting_descriptor_paths(self):
        collection = Mock()
        for rows in ([descriptor('One', '../other.png')], [descriptor('One', 'C:/other.png')],
                     [descriptor('One', 'cover.png'), descriptor('One', 'other.png')]):
            with self.subTest(rows=rows), self.assertRaises(BuildError):
                collection.find.return_value = rows
                thumbnails({'dlc_descriptors': collection})
