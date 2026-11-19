"""Content-based freshness and rejection without implicit cache repair."""

import json
import os
from unittest.mock import patch

from sttv.common.errors import BuildError
from sttv.libraries.operation import library_operation
from .fixture import LibraryFixture


class FreshnessTests(LibraryFixture):
    def assert_stale(self):
        with self.assertRaises(BuildError) as error:
            self.prepare('reuse')
        self.assertEqual(error.exception.code, 'library_stale')
        self.assertIn('--rebuild-libraries', str(error.exception))

    def test_same_size_and_timestamp_byte_change(self):
        self.prepare()
        path = self.inline/'part.txt'
        stamp = path.stat()
        path.write_bytes(path.read_bytes().replace(b'amount', b'number'))
        os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        self.assertEqual(stamp.st_size, path.stat().st_size)
        self.assert_stale()

    def test_add_remove_rename_and_rules_change(self):
        self.prepare()
        extra = self.inline/'extra.txt'
        extra.write_text('a=1', encoding='utf-8')
        self.assert_stale()
        self.prepare()
        extra.rename(self.inline/'renamed.txt')
        self.assert_stale()
        self.prepare()
        (self.inline/'renamed.txt').unlink()
        self.assert_stale()
        self.prepare()
        path, options = self.configuration()
        options['libraries'][0]['source']['recursive'] = False
        path.write_text(json.dumps(options), encoding='utf-8')
        self.assert_stale()

    def test_primary_localization_and_output_changes_do_not_invalidate(self):
        self.prepare()
        self.write_script('unrelated.txt', 'another_object = {}')
        localization = self.game/'localisation'
        localization.mkdir()
        (localization/'unrelated.yml').write_text('l_english:\n key:0 "Changed"', encoding='utf-8')
        self.options['outputs']['report'] = 'other.json'
        self.persist()
        snapshot = self.prepare('reuse')
        self.assertEqual(snapshot.report['counts']['prepared_plans'], 0)

    def test_unavailable_sources_and_changed_inputs_before_publication(self):
        self.prepare()
        settings = self.settings()
        with library_operation(settings, 'reuse') as snapshot:
            (self.inline/'added.txt').write_text('a=1', encoding='utf-8')
            with self.assertRaisesRegex(BuildError, 'changed during'):
                snapshot.inventory.verify()
        (self.inline/'added.txt').unlink()
        settings.inline_directory.rename(self.game/'moved')
        with self.assertRaises(BuildError) as error:
            self.prepare('reuse')
        self.assertEqual(error.exception.code, 'source_unavailable')

    def test_rebuild_ignores_corrupt_existing_artifacts(self):
        self.prepare()
        for path in self.artifacts():
            path.write_text('broken', encoding='utf-8')
        self.prepare()
        self.prepare('reuse')

    def test_physical_hardlink_read_is_deduplicated(self):
        source = self.inline/'part.txt'
        (self.inline/'alias.txt').hardlink_to(source)
        snapshot = self.prepare()
        self.assertEqual(len(snapshot.inventory.rows), snapshot.inventory.reads + 1)

    def test_write_failure_preserves_snapshot_and_releases_ownership(self):
        self.prepare()
        before = {path: path.read_bytes() for path in self.artifacts()}
        with patch('sttv.libraries.storage.prepare_json', side_effect=OSError('Fixture write failure')):
            with self.assertRaisesRegex(OSError, 'Fixture'):
                self.prepare()
        self.assertEqual(before, {path: path.read_bytes() for path in before})
        self.assertFalse((self.manifest().parent / '.sttv-libraries.lock').exists())
