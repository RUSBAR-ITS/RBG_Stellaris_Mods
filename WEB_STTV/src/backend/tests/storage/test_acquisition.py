"""Index integrity, membership revisions, lazy reads and atomic failure boundaries."""

from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.storage import open_set
from sttv.storage.identity import digest
from sttv.storage.manifest import finalize
from sttv.storage.publication import Publication
from sttv.storage.settings import load as storage_settings
from sttv.enrichment.acquisition.configuration import load
from sttv.enrichment.acquisition.extraction import extract
from sttv.enrichment.acquisition.preparation import store
from sttv.enrichment.acquisition.storage import Index, empty
from technology_tree.support import SetFixture, assignment as a, block as b


class AcquisitionStorageTests(SetFixture):
    def setUp(self):
        super().setUp()
        self.acquisition, _ = load({'base': 'product', 'path': 'config/enrichment/acquisition/sources.json'}, self.work)

    def add_index(self, sources=('common/ascension_perks/one.txt',), fail=False):
        settings = storage_settings(self.variables)
        before = read_json(self.manifest)
        index = empty()
        index.update(configuration_revision=self.acquisition['revision'], membership_revision=digest(list(sources)))
        with Publication(settings) as publication:
            for i, source in enumerate(sources):
                document = extract({'source': {'file': source}, 'items': [a('p', b(
                    a('on_enabled', b(a('give_technology', 'parent')))))]}, self.acquisition)
                row = store(document, publication.directory / f'{i}.json')
                path = f'acquisition/{i}/{row["file_hash"]}.json'
                publication.accept_auxiliary(Path(row['path']), path, row['file_hash'], row['byte_size'])
                index['documents'].append({k: row[k] for k in ('source', 'file_hash', 'byte_size', 'coverage')} | {'path': path})
                index['targets'].setdefault('parent', []).append(path)
            index['coverage'] = {'parsed': True, 'diagnostics': []}
            index['revision'] = digest({k: v for k, v in index.items() if k not in ('revision', 'statistics')})
            before['acquisition'] = index
            finalize(before)
            def verify():
                if fail:
                    raise BuildError('cancelled', 'Synthetic cancellation before manifest publication')
            publication.publish(before, verify)

    def test_source_membership_changes_set_identity_and_old_evidence_is_stale(self):
        self.add_index()
        before = open_set(self.manifest)
        revision = before.manifest['set_id']
        self.add_index(('common/ascension_perks/one.txt', 'common/ascension_perks/two.txt'))
        after = open_set(self.manifest)
        self.assertNotEqual(revision, after.manifest['set_id'])
        with self.assertRaisesRegex(BuildError, 'snapshot changed'):
            before.check_snapshot()

    def test_unused_index_is_not_read_and_reading_verifies_hash(self):
        self.add_index()
        reader = open_set(self.manifest)
        descriptor = reader.manifest['acquisition']['documents'][0]
        path = reader.root / descriptor['path']
        path.write_text('{}', encoding='utf-8')
        reader = open_set(self.manifest)
        self.assertEqual(reader.bytes, 0)
        evidence = [row for row in reader.coverage()['documents'] if row['database'] == 'acquisition']
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]['status'], 'not_checked')
        with self.assertRaisesRegex(BuildError, 'document changed'):
            Index(reader, self.acquisition).relevant()

    def test_reuse_verifies_previously_read_documents_and_configuration(self):
        self.add_index()
        reader = open_set(self.manifest)
        index = Index(reader, self.acquisition)
        index.relevant()
        before = reader.bytes
        index.relevant()
        self.assertEqual(reader.bytes, before)
        altered = deepcopy(self.acquisition)
        altered['revision'] = digest('changed rules')
        with self.assertRaisesRegex(BuildError, 'Prepare a new set'):
            Index(reader, altered)
        path = reader.root / reader.manifest['acquisition']['documents'][0]['path']
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaisesRegex(BuildError, 'Used document changed'):
            index.relevant()

    def test_cancellation_keeps_previous_snapshot_and_corrupt_manifest_is_rejected(self):
        self.add_index()
        before = self.manifest.read_bytes()
        with self.assertRaisesRegex(BuildError, 'Synthetic cancellation'):
            self.add_index(('common/ascension_perks/two.txt',), fail=True)
        self.assertEqual(before, self.manifest.read_bytes())
        malformed = read_json(self.manifest)
        malformed['acquisition']['targets']['parent'] = ['undeclared.json']
        index = malformed['acquisition']
        index['revision'] = digest({k: v for k, v in index.items() if k not in ('revision', 'statistics')})
        with self.assertRaisesRegex(BuildError, 'Undeclared acquisition'):
            finalize(malformed)
