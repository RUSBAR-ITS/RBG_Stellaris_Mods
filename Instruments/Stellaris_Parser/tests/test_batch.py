"""Acceptance through the real single-file and spawned batch CLI entry points."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from script_fixture import make_fixture, SOURCES
from stellaris_parser.libraries.codec import decode
from stellaris_parser.script import nodes
from stellaris_parser.script.parser import parse_text
from stellaris_parser.script_settings import KINDS, ScriptSettings
from stellaris_parser.workspace import runtime_for

# Full results from the direct single-file parser before the library migration.
DIRECT = {
    'common/technology/demo.txt': 'c0516e7ea4f9e8e79a6870785bf84198f7cd504699bc55fdd98533d6ff0949cb',
    'events/demo.txt': '4d779cd9b2b9dce6e557fd66207489ee8bf0ddeea7fe8f2b5e4c614d0a51d0cd',
}


class BatchTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.config = make_fixture(self.root)
        self.settings = ScriptSettings(self.config)
        self.output = self.root / 'artifacts/scripts'

    def cli(self, action, *args, succeeds=True):
        result = subprocess.run([sys.executable, '-m', 'stellaris_parser', action, '--config',
                                 str(self.config), *map(str, args)], cwd=self.root,
                                capture_output=True, text=True, timeout=60)
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def manifest(self):
        return json.loads(self.settings.outputs['manifest'].read_bytes())

    def check_outputs(self):
        actual = {p.relative_to(self.output).as_posix() for p in self.output.rglob('*.json')}
        expected = {Path(name).with_suffix('.json').as_posix() for name in DIRECT}
        self.assertEqual(actual, expected)
        for name, checksum in DIRECT.items():
            output = self.output / Path(name).with_suffix('.json')
            self.assertIn(b'\n', output.read_bytes())
            result = json.loads(output.read_bytes())
            self.assertEqual(sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(), checksum)

    def test_rebuild_reuse_parallelism_and_isolation(self):
        # Invalid documentation must be filtered before it can fail the run.
        (self.root / 'mod/common/technology/docs.txt').write_text('bad = {')
        self.cli('parse-batch', '--workers', 1, '--rebuild-libraries')
        self.check_outputs()
        first = self.manifest()
        self.assertEqual(len(first['artifacts']), 5)
        self.assertEqual({p.name for p in self.settings.destination.iterdir()},
                         {path.name for path in self.settings.outputs.values()})
        self.cli('parse-batch', '--rebuild-libraries')
        self.assertEqual(self.manifest(), first)
        self.check_outputs()
        self.cli('parse-batch', '--reuse-libraries')
        self.check_outputs()
        # Override all batch defaults, including the output path relative to the current directory.
        self.cli('parse-batch', '--reuse-libraries', '--workers', 1, '--output', 'selected', 'events')
        self.assertEqual([p.relative_to(self.root / 'selected').as_posix()
                          for p in (self.root / 'selected').rglob('*.json')], ['events/demo.json'])
        for name in DIRECT:
            self.cli('parse', '--reuse-libraries', '--output', 'single.json', name)
            self.assertEqual((self.root / 'single.json').read_bytes(),
                             (self.output / Path(name).with_suffix('.json')).read_bytes())

    def test_round_trip_and_library_history(self):
        self.cli('parse', '--rebuild-libraries', '--output', 'single.json', 'events/demo.txt')
        self.cli('parse', '--reuse-libraries', '--output', 'single.json', 'events/demo.txt')
        for kind in KINDS:
            artifact = json.loads(self.settings.outputs[kind].read_bytes())
            catalog = decode(artifact['graph'], self.settings.rules)
            for rel, file in catalog['files'].items():
                text = SOURCES.get('mod/' + rel, SOURCES.get('game/' + rel))
                self.assertEqual(file['source'].text, text)
                if kind != 'inline_script':
                    original = parse_text(text, self.settings.syntax, rel, role='template')
                    self.assertEqual(file['items'], original.items)
            if kind == 'scripted_effect':
                file = catalog['files']['common/scripted_effects/source.txt']
                self.assertEqual([type(n) for n in file['items']], [
                    nodes.Assignment, nodes.InlineInvocation, nodes.InlineInvocation,
                    nodes.InlineInvocation, nodes.Assignment])
                history = file['expansions']
                self.assertEqual([r['parent_id'] for r in history],
                                 [None, history[0]['id'], None, None, history[3]['id']])
                self.assertEqual([r['definitions'] for r in history],
                                 [['alpha_one', 'alpha_two']] * 2 + [[]] + [['beta_one', 'beta_two']] * 2)
                self.assertEqual(history[2]['insertion']['count'], 0)
                for index, name in ((1, 'alpha'), (4, 'beta')):
                    for suffix in ('one', 'two'):
                        self.assertEqual(catalog['definition_calls'][f'{name}_{suffix}'],
                                         {'file': 'common/scripted_effects/source.txt', 'id': history[index]['id']})
            if kind == 'inline_script':
                self.assertIn('"$NAME$"', catalog['definitions']['catalog.txt'].text)

    def test_errors_are_local_and_outputs_are_protected(self):
        self.cli('parse-batch', '--rebuild-libraries', '--workers', 0, succeeds=False)
        self.cli('parse-batch', '--rebuild-libraries', '--reuse-libraries', succeeds=False)
        self.cli('parse-batch', '--workers', 1, '--rebuild-libraries')
        previous = self.output / 'events/demo.json'
        original = previous.read_bytes()
        (self.root / 'game/events/demo.txt').write_text('broken = {')
        other = self.output / 'common/technology/demo.json'
        other.unlink()
        result = self.cli('parse-batch', '--reuse-libraries', succeeds=False)
        self.assertIn('events/demo.txt', result.stderr)
        self.assertEqual(previous.read_bytes(), original)
        self.assertTrue(other.is_file())
        self.cli('parse-batch', '--reuse-libraries', '--output', 'mod', succeeds=False)
        self.cli('parse', '--reuse-libraries', '--output', self.settings.outputs['manifest'],
                 'events/demo.txt', succeeds=False)

    def test_snapshot_freshness_missing_damaged_and_failed_rebuild(self):
        self.cli('parse-batch', '--rebuild-libraries', '--workers', 1)
        before = self.manifest()
        library = self.root / 'mod/common/inline_scripts/emit.txt'
        library.write_text('amount = 3')
        self.assertIn('--rebuild-libraries', self.cli('parse-batch', '--reuse-libraries', succeeds=False).stderr)
        self.cli('parse-batch', '--rebuild-libraries', '--workers', 1)
        self.assertNotEqual(self.manifest()['library_set_id'], before['library_set_id'])
        saved = self.manifest()
        bad = self.root / 'game/common/scripted_effects/source.txt'
        bad.write_text('broken = {')
        self.cli('parse-batch', '--rebuild-libraries', succeeds=False)
        self.assertEqual(self.manifest(), saved)
        bad.write_text(SOURCES['game/common/scripted_effects/source.txt'])
        self.settings.outputs['scripted_effect'].unlink()
        self.assertIn('--rebuild-libraries', self.cli('parse-batch', '--reuse-libraries', succeeds=False).stderr)
        self.settings.outputs['scripted_effect'].write_text('{}')
        self.assertIn('checksum', self.cli('parse-batch', '--reuse-libraries', succeeds=False).stderr)

    def test_worker_reuses_memory_in_either_file_order(self):
        self.cli('parse-batch', '--rebuild-libraries', '--workers', 1)
        runtime = runtime_for(self.settings, 'reuse', 1)
        for name in SOURCES:
            if '/common/technology/' not in name and '/events/' not in name:
                (self.root / name).unlink()
        for path in self.settings.outputs.values():
            path.unlink()
        for name in [*DIRECT, *reversed(DIRECT)]:
            result = runtime.parse(name, self.settings.sources.find(name))
            self.assertEqual(sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(), DIRECT[name])

    def test_exact_exclusions_and_changed_root_priority(self):
        (self.root / 'mod/common/technology/docs.txt').write_text('invalid = {')
        (self.root / 'game/events/docs.txt').write_text('example = yes')
        self.cli('parse-batch', '--workers', 1, '--rebuild-libraries')
        self.assertTrue((self.output / 'events/docs.json').is_file())
        self.assertFalse((self.output / 'common/technology/docs.json').exists())
        cfg = json.loads(self.config.read_bytes())
        cfg['roots'].reverse()
        self.config.write_text(json.dumps(cfg))
        self.assertIn('--rebuild-libraries', self.cli('parse-batch', '--reuse-libraries', succeeds=False).stderr)

    def test_configured_extensionless_template_in_both_modes(self):
        template = 'traditions/tr_purity_imperfection_remediation_wilderness'
        library_path = self.root / 'game/common/inline_scripts' / template
        library_path.parent.mkdir()
        library_path.write_text('from_exception = yes')
        (self.root / 'game/events/demo.txt').write_text(f'inline_script = {template}')
        for flag in ('--rebuild-libraries', '--reuse-libraries'):
            self.cli('parse-batch', '--workers', 1, flag, 'events')
            result = json.loads((self.output / 'events/demo.json').read_bytes())
            self.assertEqual(result['items'][0]['key']['text'], 'from_exception')
            self.assertEqual(result['metadata']['expansions'][0]['target']['file'], template)
