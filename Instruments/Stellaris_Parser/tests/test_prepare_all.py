"""Unified CLI coverage on a mixed script and localization fixture."""

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from document_package.package import Package
from script_fixture import make_fixture


def make_profile(root):
    path = make_fixture(root)
    config = json.loads(path.read_bytes())
    config['batch'].pop('directories')
    config['batch']['sources'] = ['common/**/*.txt', 'events/*.txt', 'dlc_metadata/dlc_info.txt',
                                  'dlc/**/*.dlc', 'common/technology/demo.txt']
    config['batch_size'] = 1
    config['localization'] = {
        'output': 'artifacts/localization',
        'reading': {'pattern': '*.yml', 'recursive': True, 'encoding': 'utf-8-sig'},
        'languages': {'ru': {'header': 'l_russian', 'sources': ['replace', 'russian']},
                      'en': {'header': 'l_english', 'sources': ['english']}},
        'directories': {name: 'locale/' + name for name in ('replace', 'russian', 'english')},
    }
    for name, text in {
        'game/dlc_metadata/dlc_info.txt': 'dlcs = { example = { name = demo } }',
        'game/dlc/sub/example.dlc': 'name = "demo"',
        'game/dlc/sub/ignored.txt': 'invalid = {',
        'game/common/technology/docs.txt': 'invalid = {',
        'game/common/technology/nested/more.txt': 'name = test_key',
        'locale/replace/one.yml': 'l_russian:\n test_key:0 "selected"',
        'locale/russian/two.yml': 'l_russian:\n test_key:0 "vanilla"',
        'locale/english/one.yml': 'l_english:\n test_key:0 "$other_key$"',
    }.items():
        source = root / name
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(text, encoding='utf-8')
    path.write_text(json.dumps(config), encoding='utf-8')
    return path


def files(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes() for p in directory.rglob('*') if p.is_file()}


class UnifiedTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.profile = make_profile(self.root)
        self.scripts = self.root / 'artifacts/scripts'
        self.dictionary = self.root / 'artifacts/localization'

    def cli(self, command, *args, ok=True):
        run = subprocess.run([sys.executable, '-B', '-m', 'stellaris_parser', command,
                              '--config', str(self.profile), *args], cwd=self.root,
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(run.returncode == 0, ok, run.stdout + run.stderr)
        return run

    def test_both_modes_match_standalone_outputs(self):
        self.cli('prepare-all', '--rebuild-libraries')
        baseline = files(self.scripts)
        self.assertEqual(set(baseline), {'events/demo.json', 'common/technology/demo.json',
                                        'common/technology/nested/more.json', 'dlc/sub/example.json',
                                        'dlc_metadata/dlc_info.json'})
        for name in ('dlc/sub/example.dlc', 'dlc_metadata/dlc_info.txt', 'common/technology/demo.txt'):
            self.cli('parse', '--reuse-libraries', '--output', 'single.json', name)
            saved = baseline[Path(name).with_suffix('.json').as_posix()]
            self.assertEqual((self.root / 'single.json').read_bytes(), saved)
            self.assertEqual(json.loads(saved)['source']['file'], name)
        self.cli('prepare', '--output', 'standalone')
        standalone = files(self.root / 'standalone')
        standalone.pop('prepare_report.json')
        self.assertEqual(files(self.dictionary), standalone)
        entries = [row for batch in Package(self.dictionary).batches() for row in batch]
        self.assertEqual([row['definitions'][0]['raw'] for row in entries], ['$other_key$', 'selected'])
        config = json.loads(self.profile.read_bytes())
        config['batch']['workers'] = 1
        self.profile.write_text(json.dumps(config))
        self.cli('prepare-all', '--reuse-libraries')
        self.assertEqual(files(self.scripts), baseline)
        self.assertEqual(files(self.dictionary), standalone)

    def test_localization_conflict_and_bad_script(self):
        self.cli('prepare-all', '--rebuild-libraries')
        conflict = self.root / 'locale/replace/duplicate.yml'
        conflict.write_text('l_russian:\n test_key:0 "conflict"')
        before = files(self.dictionary)
        other = self.scripts / 'events/demo.json'
        other.unlink()
        run = self.cli('prepare-all', '--reuse-libraries', ok=False)
        self.assertIn('test_key', run.stderr)
        self.assertIn('duplicate.yml', run.stderr)
        self.assertEqual(files(self.dictionary), before)
        self.assertTrue(other.is_file())
        conflict.unlink()
        (self.root / 'game/events/demo.txt').write_text('error = {')
        (self.dictionary / 'manifest.json').unlink()
        run = self.cli('prepare-all', '--reuse-libraries', ok=False)
        self.assertIn('events/demo.txt', run.stderr)
        self.assertEqual(files(self.dictionary), before)

    def test_no_overlapping_outputs_or_ambiguous_script_names(self):
        config = json.loads(self.profile.read_bytes())
        config['localization']['output'] = 'artifacts/scripts/localization'
        self.profile.write_text(json.dumps(config))
        self.assertIn('overlaps', self.cli('prepare-all', '--rebuild-libraries', ok=False).stderr)
        self.assertFalse(self.scripts.parent.exists())
        config['localization']['output'] = 'artifacts/localization'
        config['batch']['sources'].append('dlc/sub/example.txt')
        (self.root / 'game/dlc/sub/example.txt').write_text('item = yes')
        self.profile.write_text(json.dumps(config))
        self.assertIn('Conflicting output', self.cli('prepare-all', '--rebuild-libraries', ok=False).stderr)
        self.assertFalse(self.scripts.exists())
