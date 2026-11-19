"""Explicit template exceptions preserve confinement and never enable broad fallback."""

import json
from pathlib import Path
from unittest.mock import patch

from support import BuildFixture, PRODUCT_ROOT
from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.script.inline import FileTemplates


class InlineExceptionTests(BuildFixture):
    def configure(self, entries):
        directory = Path(self.variables['WORK_DIR'])
        directory.mkdir(parents=True, exist_ok=True)
        self.exception_file = directory / 'exceptions.json'
        self.exception_file.write_text(json.dumps({'format_version': 1, 'inline_script_files': entries}),
                                       encoding='utf-8')
        self.options['parser']['exceptions'] = {'base': 'work', 'path': 'exceptions.json'}

    def entry(self, file):
        return {'file': file, 'reason': 'Explicit fixture permission.'}

    def test_exact_nested_override_preserves_actual_path_and_hash(self):
        self.write_script('base.txt', 'inline_script=outer')
        (self.inline / 'outer.txt').write_text('inline_script={script=allowed VALUE=yes}', encoding='utf-8')
        (self.inline / 'allowed').write_text('result=$VALUE$', encoding='utf-8')
        self.configure({})
        self.assertIn('missing_inline_template', self.errors(self.run_build()))
        self.configure({'allowed': self.entry('allowed')})
        (self.inline / 'allowed.txt').write_text('wrong=no', encoding='utf-8')
        before = self.hashes()
        result = self.run_build()
        self.assertEqual(result['status'], 'success', result)
        self.assertEqual(set(result['inline_sources']), {'outer.txt', 'allowed'})
        doc = self.database()['documents'][0]
        self.assertEqual(doc['items'][0]['key']['text'], 'result')
        self.assertEqual(doc['items'][0]['value']['text'], 'yes')
        self.assertEqual(doc['items'][0]['origin']['file'], 'allowed')
        self.assertEqual([c['target']['file'] for c in doc['metadata']['expansions']], ['outer.txt', 'allowed'])
        self.assertEqual(before, self.hashes())

    def test_missing_override_and_unlisted_neighbor_never_fall_back(self):
        self.configure({'allowed': self.entry('allowed')})
        (self.inline / 'allowed.txt').write_text('x=yes', encoding='utf-8')
        self.write_script('base.txt', 'inline_script=allowed')
        self.assertIn('missing_inline_template', self.errors(self.run_build()))
        (self.inline / 'unlisted').write_text('x=yes', encoding='utf-8')
        self.write_script('base.txt', 'inline_script=unlisted')
        self.assertIn('missing_inline_template', self.errors(self.run_build()))

    def test_unsafe_or_pattern_paths_are_rejected(self):
        for value in ('../outside', 'nested/../outside', '/absolute', 'C:/absolute',
                      'stream:secret', '*', 'folder/?', '.', 'folder/', 'bad\x00name'):
            for position in ('key', 'file'):
                with self.subTest(value=value, position=position):
                    self.configure({value if position == 'key' else 'allowed':
                                    self.entry(value if position == 'file' else 'allowed')})
                    result = self.run_build()
                    self.assertTrue({'schema_error', 'invalid_inline_path'}.intersection(self.errors(result)))
                    self.assertFalse(result['database_written'])

    def test_normalized_duplicate_names_are_rejected(self):
        self.configure({'nested/file': self.entry('a'), 'NESTED\\FILE': self.entry('b')})
        self.assertIn('duplicate_inline_exception', self.errors(self.run_build()))

    def test_resolved_link_cannot_escape_before_reading(self):
        options = read_json(PRODUCT_ROOT / 'config/parser/inline_scripts.json')
        loader = FileTemplates(self.inline, options, {'allowed': self.entry('link')})
        resolved = Path.resolve
        destination = self.game / 'outside.txt'

        def resolve(path, *args, **kwargs):
            return destination if path == self.inline / 'link' else resolved(path, *args, **kwargs)

        with patch.object(Path, 'resolve', resolve), patch.object(Path, 'read_bytes') as read:
            with self.assertRaises(BuildError) as error:
                loader.identity('allowed')
            self.assertEqual(error.exception.code, 'invalid_inline_path')
            read.assert_not_called()

    def test_invalid_config_is_fatal_and_output_cannot_replace_it(self):
        self.configure({})
        self.assertEqual(self.run_build()['status'], 'success')
        before = self.database_path().read_bytes()
        self.exception_file.write_text('{"format_version": 2, "inline_script_files": {}}', encoding='utf-8')
        self.assertIn('schema_error', self.errors(self.run_build()))
        self.assertEqual(before, self.database_path().read_bytes())
        self.exception_file.unlink()
        self.assertIn('json_read_error', self.errors(self.run_build()))
        self.assertEqual(before, self.database_path().read_bytes())
        self.configure({})
        original = self.exception_file.read_bytes()
        self.options['outputs']['report'] = 'exceptions.json'
        self.assertIn('output_collision', self.errors(self.run_build()))
        self.assertEqual(self.exception_file.read_bytes(), original)

    def test_alias_cycle_uses_actual_template_identity(self):
        self.configure({'allowed': self.entry('shared'), 'alias': self.entry('shared')})
        (self.inline / 'shared').write_text('inline_script=alias', encoding='utf-8')
        self.write_script('base.txt', 'inline_script=allowed')
        self.assertIn('inline_cycle', self.errors(self.run_build()))
