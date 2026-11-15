"""Calculation library selection, manifests, and source integrity."""

from unittest.mock import patch

from database.value_support import ValueFixture
from sttv.database import storage
from sttv.sources import verification


class ValueLibraryTests(ValueFixture):
    def test_configured_directory_is_excluded_but_calls_are_expanded(self):
        self.values = self.game/'common/alternative_values'
        self.values.mkdir()
        self.variables['SCRIPT_VALUES_DIR'] = 'common/alternative_values'
        (self.values/'nested').mkdir()
        (self.values/'nested/extra.txt').write_text('second={base=2}', encoding='utf-8')
        self.setup_values(caller='factor=value:constant v=value:second')
        self.options['sources'] = [dict(variable='STELLARIS_ROOT', pattern='*.txt', recursive=True,
                                       encoding='utf-8-sig')]
        _, report = self.document()
        self.assertEqual(report['counts']['selected_files'], 3)
        self.assertEqual(report['counts']['scripted_calls']['script_value']['files'], 2)
        self.assertEqual(len(report['script_value_sources']), 2)
        self.assertFalse(any('alternative_values' in d['source']['file'] for d in self.database()['documents']))

    def test_empty_library_unknown_target_and_invalid_definition(self):
        self.setup_values('', 'ordinary=3')
        self.document()
        self.write_script('base.txt', 'ordinary=value:missing')
        self.assertIn('unknown_script_value', self.errors(self.run_build()))
        self.setup_values('constant=3')
        self.assertIn('invalid_scripted_definition', self.errors(self.run_build()))

    def test_missing_and_outside_directories(self):
        self.variables['SCRIPT_VALUES_DIR'] = 'common/not_present'
        self.assertIn('source_unavailable', self.errors(self.run_build()))
        self.variables['SCRIPT_VALUES_DIR'] = str(self.root/'outside')
        self.assertIn('unsafe_source', self.errors(self.run_build()))

    def test_changed_library_blocks_publication(self):
        self.setup_values()
        self.document()
        before = self.database_path().read_bytes()
        original = verification.verify_inputs
        def changed(settings, report):
            (self.values/'definitions.txt').write_text('constant={base=99}', encoding='utf-8')
            return original(settings, report)
        with patch('sttv.builder.verify_inputs', side_effect=changed):
            self.assertIn('source_changed', self.errors(self.run_build()))
        self.assertEqual(self.database_path().read_bytes(), before)

    def test_database_can_be_read_without_sources_and_build_repeats(self):
        self.setup_values('x={base=value:y} y={base=4}', 'v=value:x v=value:x')
        before_sources = self.hashes()
        self.document()
        before = self.database_path().read_bytes()
        self.document()
        self.assertEqual(self.database_path().read_bytes(), before)
        self.assertEqual(self.hashes(), before_sources)
        (self.values/'definitions.txt').unlink()
        self.assertEqual(storage.read_database(self.database_path())['format_version'], 3)
