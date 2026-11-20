"""Offline dictionary preparation and explicit live publication acceptance."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest



from document_package.errors import BuildError
from document_package.json_io import read_json
from document_package.package import Package
from stellaris_parser.localization.prepare import prepare
from stellaris_parser.settings import LocalizationSettings


class DictionaryTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        sources = {'ru': [], 'en': []}
        for tier in ('RU_LOC_TIER_1', 'RU_LOC_TIER_2', 'RU_LOC_TIER_3', 'EN_LOC_TIER_1'):
            directory = self.root / tier
            directory.mkdir()
            sources[tier[:2].lower()].append((tier, directory))
        options = {'batch_size': 1, 'reading': {'pattern': '*.yml', 'recursive': True, 'encoding': 'utf-8-sig'},
                   'languages': {'ru': {'header': 'l_russian'}, 'en': {'header': 'l_english'}}}
        self.config = LocalizationSettings(self.root / 'package', options, sources)

    def write(self, tier, name, entries):
        header = 'l_russian' if tier.startswith('RU') else 'l_english'
        lines = [header + ':', *(f' {key}:0 "{raw}"' for key, raw in entries)]
        (self.root / tier / name).write_text('\n'.join(lines), encoding='utf-8-sig')

    def package(self):
        prepare(self.config)
        return Package(self.config.directory)

    def test_priority_and_raw_source_preservation(self):
        self.write('RU_LOC_TIER_1', 'z.yml', [('K', '')])
        self.write('RU_LOC_TIER_1', 'a.yml', [('K', ''), ('k', '$Other$\\n[This.GetName]')])
        self.write('RU_LOC_TIER_3', 'v.yml', [('K', 'a'), ('K', 'b')])
        self.write('EN_LOC_TIER_1', 'en.yml', [('K', 'english')])
        package = self.package()
        english, russian, lower = (row for batch in package.batches() for row in batch)
        self.assertEqual(list(english['_id']), ['language', 'key'])
        self.assertEqual(english['_id']['language'], 'en')
        self.assertEqual(russian['definitions'][russian['selected']]['raw'], '')
        self.assertEqual([(d['file'], d['line']) for d in russian['definitions']],
                         [('a.yml', 2), ('z.yml', 2), ('v.yml', 2), ('v.yml', 3)])
        self.assertEqual(lower['definitions'][0]['raw'], '$Other$\\n[This.GetName]')
        report = read_json(self.config.directory / 'prepare_report.json')
        self.assertEqual(report['languages']['ru']['definitions'], 5)
        self.assertFalse(report['conflicts'][0]['blocking'])

    def test_selected_conflict_keeps_previous_manifest(self):
        self.write('RU_LOC_TIER_2', 'a.yml', [('K', 'old')])
        original = self.package().manifest
        self.write('RU_LOC_TIER_2', 'b.yml', [('K', 'different')])
        with self.assertRaisesRegex(BuildError, 'Conflicting definitions'):
            prepare(self.config)
        self.assertEqual(Package(self.config.directory).manifest, original)
        conflict = read_json(self.config.directory / 'prepare_report.json')['conflicts'][0]
        self.assertTrue(conflict['blocking'])
        self.assertEqual([s['file'] for s in conflict['sources']], ['a.yml', 'b.yml'])

    def test_damaged_batch_and_removed_source(self):
        self.write('EN_LOC_TIER_1', 'one.yml', [('obsolete', 'old')])
        original = self.package()
        digest = original.manifest['batches'][0]['sha256']
        (self.config.directory / 'batches' / f'{digest}.json').write_bytes(b'[]')
        with self.assertRaisesRegex(BuildError, 'Checksum mismatch'):
            list(original.batches())
        (self.root / 'EN_LOC_TIER_1/one.yml').unlink()
        self.assertEqual(self.package().manifest['documents'], 0)
