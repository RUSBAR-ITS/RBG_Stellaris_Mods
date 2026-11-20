"""Document identity, selective verification and atomic snapshot publication."""
from sttv.common.paths import work_directory


from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from support import PRODUCT_ROOT, syntax
from sttv.common.datasets import KINDS
from sttv.common.errors import BuildError
from sttv.common.timing import performance
from stellaris_parser.script.parser import parse_text
from stellaris_parser.script.serialization import serialize_document
from sttv.storage.audit import audit
from sttv.storage.identity import document_id, source_hash
from sttv.storage.manifest import create, finalize
from sttv.storage.publication import Publication
from sttv.storage.reader import open_set
from sttv.storage.settings import StorageSettings
from sttv.storage.writing import prepare, write_document


class StorageTests(unittest.TestCase):
    def setUp(self):
        base = work_directory() / 'tests'
        base.mkdir(exist_ok=True, parents=True)
        self.temp = TemporaryDirectory(dir=base)
        self.root = Path(self.temp.name)
        target = self.root / 'set'
        self.settings = StorageSettings(target, target / 'manifest.json', 'documents',
            self.root / 'staging', self.root / 'report.json', 1, [])

    def tearDown(self):
        self.temp.cleanup()

    def document(self, text='tech_a = { tier = 0 }', file='common/technology/a.txt'):
        return serialize_document(parse_text(text, syntax(), file))

    def publish(self, specs=None):
        members = {kind: [] for kind in KINDS}
        specs = specs or [('technologies', self.document()),
            ('events', self.document('country_event = { id = event.1 }', 'events/a.txt'))]
        with Publication(self.settings) as publication:
            for i, (kind, doc) in enumerate(specs):
                fragment = write_document(doc, publication.directory / f'{i}.json', kind, performance())
                members[kind].append(publication.accept(fragment, kind))
            manifest = create(members)
            publication.publish(manifest)
        return manifest

    def test_lazy_reader_and_full_audit_have_distinct_coverage(self):
        self.publish()
        reader = open_set(self.settings.manifest)
        identifier = reader.document_ids('technologies')[0]
        document = reader.read_document('technologies', identifier)
        self.assertEqual(document['items'][0]['key']['text'], 'tech_a')
        self.assertEqual(reader.coverage()['verified'], 1)
        self.assertEqual(reader.coverage()['not_checked'], 1)
        event = reader.paths[('events', reader.document_ids('events')[0])]
        event.write_bytes(event.read_bytes().replace(b'event.1', b'event.2'))
        reader.check_snapshot()
        report = audit(self.settings.manifest)
        self.assertEqual(report['status'], 'failed')
        self.assertEqual(report['diagnostics'][0]['code'], 'document_hash')

    def test_identity_and_source_hash_ignore_only_derived_root_tree(self):
        doc = prepare(self.document(), 'technologies')
        self.assertEqual(document_id('technologies', doc['source']),
            document_id('technologies', {**doc['source'], 'file': doc['source']['file'].upper()}))
        original = source_hash(doc)
        doc['items'][0]['enrichments'] = {'technology_tree': {'a': {'status': 'root'}}}
        self.assertEqual(source_hash(doc), original)
        doc['items'][0]['value']['items'][0]['value']['text'] = '1'
        self.assertNotEqual(source_hash(doc), original)

    def test_fragments_anonymous_objects_and_variants_are_indexed_correctly(self):
        manifest = self.publish([
            ('technologies', self.document('tech_a = { technology_swap = { name = alternate } }')),
            ('on_actions', self.document('on_day = {} on_day = {}', 'common/on_actions/a.txt')),
            ('terraform', self.document('terraform_link = {} terraform_link = {}', 'common/terraform/a.txt'))])
        reader = open_set(self.settings.manifest)
        self.assertEqual(len(reader.resolve_object('on_actions', 'on_day')), 2)
        self.assertEqual(len(manifest['datasets']['technologies']['objects']), 1)
        self.assertEqual([r['id'] for r in manifest['datasets']['terraform']['objects']], [None, None])
        with self.assertRaises(BuildError):
            self.publish([('technologies', self.document('tech_a = {} tech_a = {}'))])

    def test_failed_publication_and_old_reader_keep_the_previous_snapshot(self):
        self.publish()
        old = self.settings.manifest.read_bytes()
        reader = open_set(self.settings.manifest)
        with patch('sttv.storage.publication.os.replace', side_effect=OSError('injected')):
            with self.assertRaises(OSError):
                self.publish()
        self.assertEqual(self.settings.manifest.read_bytes(), old)
        self.publish([('technologies', self.document('tech_b = {}'))])
        identifier = reader.document_ids('technologies')[0]
        self.assertEqual(reader.read_document('technologies', identifier)['items'][0]['key']['text'], 'tech_a')
        with self.assertRaises(BuildError):
            reader.check_snapshot()

    def test_writer_lock_index_mismatch_and_unsafe_paths(self):
        manifest = self.publish()
        with Publication(self.settings):
            with self.assertRaises(BuildError):
                with Publication(self.settings):
                    pass
        bad = deepcopy(manifest)
        bad['datasets']['technologies']['objects'][0]['id'] = 'other'
        finalize(bad)
        self.settings.manifest.write_text(json.dumps(bad), encoding='utf-8')
        reader = open_set(self.settings.manifest)
        with self.assertRaises(BuildError):
            reader.read_document('technologies', reader.document_ids('technologies')[0])
        for path in ('../outside.json', 'C:/outside.json', '/absolute.json', 'x\\y.json'):
            bad = deepcopy(manifest)
            bad['datasets']['technologies']['documents'][0]['path'] = path
            with self.assertRaises(BuildError):
                finalize(bad)


if __name__ == '__main__':
    unittest.main()
