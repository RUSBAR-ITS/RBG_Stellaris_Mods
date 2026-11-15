"""Shared-library validation, isolation, refresh and filesystem boundaries."""

import json
import os
from pathlib import Path
from unittest.mock import patch

from support import BuildFixture, PRODUCT_ROOT
from sttv.common.schema import validate_schema


class StaticLibraryTests(BuildFixture):
    def configure(self, **changes):
        config = json.loads((PRODUCT_ROOT / 'config/parser/static_variables.json').read_text(encoding='utf-8'))
        config.update(changes)
        work = Path(self.variables['WORK_DIR'])
        work.mkdir(parents=True, exist_ok=True)
        file = work / 'static.json'
        file.write_text(json.dumps(config), encoding='utf-8')
        self.options['parser']['static_variables'] = {'base': 'work', 'path': 'static.json'}
        return file

    def test_library_updates_hashes_refresh_and_physical_deduplication(self):
        self.write_script('base.txt', 'value=@external')
        os.link(self.static / 'base.txt', self.static / 'alias.txt')
        before = self.hashes()
        first = self.run_build()
        self.assertEqual(first['status'], 'success', first)
        self.assertEqual(first['counts']['static_variables']['files'], 1)
        self.assertEqual(first['counts']['selected_files'], 3)
        self.assertEqual(len(first['static_variable_sources']), 1)
        self.assertEqual(before, self.hashes())
        (self.static / 'base.txt').write_text('@external=8', encoding='utf-8')
        second = self.run_build()
        self.assertEqual(second['status'], 'success', second)
        self.assertNotEqual(first['static_variable_sources'], second['static_variable_sources'])
        self.assertEqual(self.database()['documents'][0]['items'][0]['value']['text'], '8')
        self.assertEqual(second['format_version'], 3)
        validate_schema(second, 'report.schema.json')

    def test_global_failure_precedes_documents_and_preserves_database(self):
        self.assertEqual(self.run_build()['status'], 'success')
        previous = self.database_path().read_bytes()
        for content, code in [('ordinary=yes', 'invalid_static_library'),
                              ('inline_script=missing', 'invalid_static_library'),
                              ('@x=@absent', 'unknown_static_variable'),
                              ('@x=@x', 'static_variable_cycle')]:
            with self.subTest(content=content):
                (self.static / 'broken.txt').write_text(content, encoding='utf-8')
                result = self.run_build()
                self.assertIn(code, self.errors(result))
                self.assertEqual(result['counts']['parsed_files'], 0)
                self.assertEqual(self.database_path().read_bytes(), previous)

    def test_duplicate_global_names_identify_both_files(self):
        (self.static / 'duplicate.txt').write_text('@external=2', encoding='utf-8')
        result = self.run_build()
        error = next(d for d in result['diagnostics'] if d['code'] == 'duplicate_static_variable')
        self.assertIn('base.txt', error['message'])
        self.assertIn('duplicate.txt', error['message'])

    def test_empty_missing_and_recursive_library(self):
        self.write_script('base.txt', '@local=3 x=@local')
        (self.static / 'base.txt').unlink()
        self.assertEqual(self.run_build()['status'], 'success')
        self.static.rmdir()
        self.assertIn('source_unavailable', self.errors(self.run_build()))
        nested = self.static / 'nested'
        nested.mkdir(parents=True)
        (nested / 'base.txt').write_text('@external=4', encoding='utf-8')
        self.write_script('base.txt', 'x=@external')
        self.assertEqual(self.run_build()['status'], 'success')
        self.configure(recursive=False)
        self.assertIn('unknown_static_variable', self.errors(self.run_build()))

    def test_invalid_configuration_read_errors_and_output_protection(self):
        self.assertEqual(self.run_build()['status'], 'success')
        previous = self.database_path().read_bytes()
        for changes in ({'name_pattern': '['}, {'pattern': '../*.txt'}, {'encoding': 'not-an-encoding'}):
            self.configure(**changes)
            self.assertEqual(self.run_build()['status'], 'failed')
            self.assertEqual(self.database_path().read_bytes(), previous)
        config = self.configure()
        before = config.read_bytes()
        self.options['outputs']['database'] = 'static.json'
        self.assertIn('output_collision', self.errors(self.run_build()))
        self.assertEqual(config.read_bytes(), before)
        self.options['outputs']['database'] = 'database.json'
        config.unlink()
        self.assertEqual(self.run_build()['status'], 'failed')
        self.configure()
        (self.static / 'bad.txt').write_bytes(b'\xff')
        self.assertIn('source_read_error', self.errors(self.run_build()))

    def test_file_link_escape_is_rejected_before_reading_target(self):
        source = self.static / 'base.txt'
        resolve = Path.resolve

        def escaping(path, *args, **kwargs):
            return self.root / 'outside.txt' if path == source else resolve(path, *args, **kwargs)

        with patch.object(Path, 'resolve', escaping):
            result = self.run_build()
        self.assertIn('unsafe_source', self.errors(result))
