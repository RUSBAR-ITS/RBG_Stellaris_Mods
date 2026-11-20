"""Configured empire identities and nested DLC indexes."""

from copy import deepcopy
from types import SimpleNamespace
import unittest

from support import PRODUCT_ROOT, syntax
from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.report import Report
from sttv.common.object_selection import pointer_indices
from sttv.database_sets.descriptors import relationships, verify
from sttv.script.nodes import Source
from sttv.script.parser import parse_source, parse_text
from sttv.script.serialization import serialize_document
from sttv.script.source_exceptions import SourceExceptions
from sttv.script.source_insertions import repair
from sttv.storage.objects import index_document, check_objects
from sttv.storage.writing import prepare


def document(text, kind='dlcs', file='dlc_metadata/dlc_info.txt'):
    return prepare(serialize_document(parse_text(text, syntax(), file)), kind)


class EmpireCatalogTests(unittest.TestCase):
    def test_root_kinds_preserve_unknown_fields_variants_and_comments(self):
        for kind in ('species_archetypes', 'species_classes', 'ethics', 'ethic_categories',
                     'authorities', 'civics', 'traits', 'graphical_culture', 'ship_categories',
                     'ascension_perks', 'traditions', 'tradition_categories'):
            doc = document('a={is_origin=yes unknown={ x=y } swap_type={ name=b }} b={leader_class=scientist}',
                           kind, f'common/{kind}/unexpected.txt')
            rows = index_document(kind, doc['document_id'], doc['items'], doc['source'])
            self.assertEqual([row['id'] for row in rows], ['a', 'b'])
            self.assertEqual(len(doc['items'][0]['value']['items']), 3)
            self.assertEqual(index_document(kind, 'empty', [], doc['source']), [])
            with self.assertRaises(BuildError):
                check_objects(kind, [*rows, {**rows[0], 'pointer': '/items/2'}], {doc['document_id']: doc})

    def test_nested_index_and_flat_descriptors(self):
        doc = document('dlcs={ dlc036={ name=BioGenesis show=no affects_gameplay=no } }')
        rows = index_document('dlcs', doc['document_id'], doc['items'], doc['source'])
        self.assertEqual([(r['id'], r['pointer']) for r in rows], [('dlc036', '/items/0/value/items/0')])
        self.assertIsNone(pointer_indices('dlcs', '/items/0', doc['source']))
        self.assertIsNone(pointer_indices('dlcs', '/items/0/value/items/0/value/items/0', doc['source']))
        descriptor = document('name=BioGenesis localizable_name=OTHER', file='dlc/unrelated/file.dlc')
        self.assertEqual(index_document('dlcs', descriptor['document_id'], descriptor['items'], descriptor['source']), [])
        catalog, descriptors, nodes = relationships('dlcs', [doc, descriptor])
        self.assertEqual(list(catalog), ['BioGenesis'])
        nodes['BioGenesis']['enrichments'] = {'dlc': {'descriptors': [{'database': 'dlcs', 'document_id': descriptor['document_id']}]}}
        verify('dlcs', [doc, descriptor])
        nodes['BioGenesis']['enrichments']['dlc']['descriptors'][0]['document_id'] = 'f' * 64
        with self.assertRaises(BuildError):
            verify('dlcs', [doc, descriptor])
        with self.assertRaises(BuildError):
            relationships('dlcs', [doc, descriptor, deepcopy(descriptor)])

    def test_repair_exact_scope_and_original_positions(self):
        options = read_json(PRODUCT_ROOT / 'config/parser/source_exceptions.json')
        report = Report()
        context = SimpleNamespace(exceptions=SourceExceptions(options, report, 'rules.json'), preparing=False, stack=[])
        raw = 'dlcs={ dlc002={ paradoxplaza_store_url ""\n name="Test" } }'
        original = Source(raw, 'dlc_metadata/dlc_info.txt')
        corrected = repair(original, syntax(), context)
        parsed = parse_source(corrected, syntax())
        name = parsed.items[0].value.items[0].value.items[1]
        self.assertEqual(name.origin['span']['start'], raw.index('name='))
        self.assertEqual(report.data['counts']['source_exceptions']['sttv_dlc_metadata_store_separator'], 1)
        self.assertEqual(original.text, raw)
        for text, file in [(raw.replace('dlc002', 'dlc003'), original.file),
                           (raw, 'other.txt'), (raw.replace('url ""', 'url = ""'), original.file),
                           (raw.replace('paradoxplaza', 'other = paradoxplaza'), original.file),
                           ('# ' + raw, original.file), ('x="paradoxplaza_store_url \\"\\""', original.file)]:
            source = Source(text, file)
            self.assertIs(repair(source, syntax(), context), source)
        with self.assertRaises(BuildError):
            repair(Source(raw + raw, original.file), syntax(), context)


if __name__ == '__main__':
    unittest.main()
