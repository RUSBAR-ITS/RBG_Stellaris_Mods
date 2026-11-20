"""Resource publication stays atomic and preserves source identities."""

from pathlib import Path
from unittest.mock import patch

from PIL import Image
from support import BuildFixture
from sttv.enrichment.assets import prepare_assets
from sttv.storage import open_set
from sttv.storage.audit import audit


class AssetOperationTests(BuildFixture):
    def setUp(self):
        super().setUp()
        self.variables['DLC_DIR'] = 'dlc'
        for tier in ('RU_LOC_TIER_1', 'RU_LOC_TIER_2', 'RU_LOC_TIER_3', 'EN_LOC_TIER_1'):
            directory = self.root / tier
            directory.mkdir()
            self.variables[tier] = str(directory)
            header = 'l_russian' if tier.startswith('RU') else 'l_english'
            (directory / 'base.yml').write_text(f'{header}:\n computing:0 "{tier}"\n', encoding='utf-8-sig')
        for folder, names in [('technologies', ['tech_a', 'tech_b', 'tech_a_variant']),
                              ('resources', ['physics_research', 'society_research', 'engineering_research'])]:
            directory = self.game / f'gfx/interface/icons/{folder}'
            directory.mkdir(parents=True)
            for name in names:
                Image.new('RGBA', (4, 3), (20, 30, 40, 80)).save(directory / f'{name}.dds')
        self.assertEqual(self.run_build()['status'], 'success')

    def test_prepare_reuse_priority_and_changed_source(self):
        before = open_set(self.database_path()).manifest
        first = prepare_assets(self.variable_file)
        self.assertEqual(first['status'], 'success', first['diagnostics'])
        after = open_set(self.database_path()).manifest
        self.assertEqual(before['set_id'], after['set_id'])
        self.assertEqual(after['presentation']['categories']['computing']['ru']['text'], 'RU_LOC_TIER_1')
        self.assertEqual(after['presentation']['categories']['computing']['en']['text'], 'EN_LOC_TIER_1')
        self.assertEqual(first['counts']['unique_images'], 1)
        repeat = prepare_assets(self.variable_file)
        self.assertEqual(repeat['status'], 'success', repeat['diagnostics'])
        self.assertFalse(repeat['published'])
        self.assertEqual(repeat['counts']['converted'], 0)
        self.assertEqual(repeat['counts']['documents_written'], 0)
        source = self.game / 'gfx/interface/icons/technologies/tech_a.dds'
        Image.new('RGBA', (5, 3), (200, 30, 40, 80)).save(source)
        changed = prepare_assets(self.variable_file)
        self.assertEqual(changed['status'], 'success', changed['diagnostics'])
        self.assertEqual(changed['counts']['converted'], 1)
        self.assertEqual(changed['counts']['unique_images'], 2)
        self.assertEqual(audit(self.database_path())['status'], 'success')

    def test_failed_manifest_switch_preserves_previous_publication(self):
        from sttv.storage import publication
        before = self.database_path().read_bytes()
        replace = publication.os.replace
        def fail(source, target):
            if Path(target) == self.database_path():
                raise OSError('Injected resource publication failure')
            return replace(source, target)
        with patch.object(publication.os, 'replace', side_effect=fail):
            result = prepare_assets(self.variable_file)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(self.database_path().read_bytes(), before)
        self.assertEqual(audit(self.database_path())['status'], 'success')
