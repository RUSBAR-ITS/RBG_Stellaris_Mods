"""Explicit modes, independent contexts and unchanged source/output semantics."""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from support import PRODUCT_ROOT
from sttv.builder import build
from sttv.common.errors import BuildError
from sttv.libraries.operation import library_operation, add_mode_arguments
from sttv.sources.expansion import expansion_context
from sttv.script.parser import parse_text
from sttv.script.serialization import serialize_document
from .fixture import LibraryFixture


class LifecycleTests(LibraryFixture):
    def test_build_reuse_is_byte_identical_without_preparation_or_writes(self):
        first = self.run_build()
        self.assertEqual(first['status'], 'success', first['diagnostics'])
        previous = self.database_path().read_bytes()
        stamps = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.artifacts()}
        with patch('sttv.libraries.operation.prepare_snapshot', side_effect=AssertionError('Unexpected preparation')):
            second = build(self.variable_file, self.config_file, library_mode='reuse')
        self.assertEqual(second['status'], 'success', second['diagnostics'])
        self.assertEqual(previous, self.database_path().read_bytes())
        self.assertEqual(stamps, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.artifacts()})

    def test_contexts_have_independent_results_and_counters(self):
        self.prepare()
        settings = self.settings()
        with library_operation(settings, 'reuse') as snapshot:
            from sttv.libraries.codec import encode
            from sttv.libraries.inventory import digest
            original_payload = digest(encode(snapshot.payloads))
            contexts = [expansion_context(settings), expansion_context(settings)]
            before = dict(snapshot.shared)
            results = [parse_text('tech_a = { effect_a = { N = 4 } }', settings.syntax,
                       'common/technology/fixture.txt', expansion=context) for context in contexts]
            self.assertEqual(serialize_document(results[0]), serialize_document(results[1]))
            results[0].items[0].value.items.clear()
            self.assertTrue(results[1].items[0].value.items)
            results[0].items.clear()
            self.assertTrue(results[1].items)
            self.assertEqual(snapshot.shared, before)
            self.assertEqual(original_payload, digest(encode(snapshot.payloads)))
            self.assertIs(contexts[0].library.entries['effect_a'], contexts[1].library.entries['effect_a'])
            contexts[0].counts['failed'] += 1
            self.assertNotEqual(contexts[0].counts, contexts[1].counts)

    def test_explicit_mode_and_ownership(self):
        parser = argparse.ArgumentParser()
        add_mode_arguments(parser)
        for arguments in ([], ['--rebuild-libraries', '--reuse-libraries']):
            with self.assertRaises(SystemExit):
                parser.parse_args(arguments)
        with self.assertRaisesRegex(BuildError, 'Choose'):
            self.prepare(None)
        self.manifest().parent.mkdir(parents=True)
        lock = self.manifest().parent / '.sttv-libraries.lock'
        lock.write_text('another owner', encoding='utf-8')
        with self.assertRaisesRegex(BuildError, 'already owned'):
            self.prepare()
        self.assertEqual(lock.read_text(), 'another owner')

    def test_fresh_process_reuse(self):
        self.prepare()
        result = subprocess.run([sys.executable, '-B', '-m', 'sttv.libraries', '--reuse-libraries',
            '--variables', str(self.variable_file), '--config', str(self.config_file)],
            cwd=PRODUCT_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['counts']['prepared_plans'], 0)
        self.assertEqual(report['counts']['loaded_artifacts'], 5)

    def test_other_manifest_cannot_bypass_directory_ownership(self):
        self.prepare()
        from sttv.common.json_io import read_json
        library_options = read_json(PRODUCT_ROOT/'config/libraries.json')
        library_options['manifest'] = 'libraries/other_manifest.json'
        library_config = Path(self.variables['WORK_DIR'])/'other_libraries.json'
        library_config.write_text(json.dumps(library_options), encoding='utf-8')
        options = dict(self.options, libraries={'base': 'work', 'path': library_config.name})
        other_config = self.root/'other_backend.json'
        other_config.write_text(json.dumps(options), encoding='utf-8')
        with library_operation(self.settings(), 'reuse'):
            result = subprocess.run([sys.executable, '-B', '-m', 'sttv.libraries', '--reuse-libraries',
                '--variables', str(self.variable_file), '--config', str(other_config)],
                cwd=PRODUCT_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['code'], 'library_busy')

    def test_relocate_configuration_and_unsafe_destinations(self):
        path, options = self.configuration()
        for row in options['libraries']:
            row['output'] = 'relocated/' + row['id'] + '.json'
        options['manifest'], options['report'] = 'relocated/index.json', 'relocated/report.json'
        path.write_text(json.dumps(options), encoding='utf-8')
        self.prepare()
        self.prepare('reuse')
        options['manifest'] = '../outside.json'
        path.write_text(json.dumps(options), encoding='utf-8')
        with self.assertRaises(BuildError):
            self.prepare()

    def test_failed_preparation_preserves_existing_database(self):
        self.assertEqual(self.run_build()['status'], 'success')
        before = self.database_path().read_bytes()
        (self.effects/'duplicate.txt').write_bytes((self.effects/'effect.txt').read_bytes())
        result = build(self.variable_file, self.config_file, library_mode='rebuild')
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(before, self.database_path().read_bytes())
