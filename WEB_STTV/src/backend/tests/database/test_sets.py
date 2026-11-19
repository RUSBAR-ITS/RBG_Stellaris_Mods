"""Set integrity, localization selection and publication failures."""

import copy
import json
from pathlib import Path
from unittest.mock import patch

from support import BuildFixture, PRODUCT_ROOT
from sttv.common.json_io import read_json
from sttv.database_sets import build_database_set
from sttv.storage import open_set
from storage.fixtures import documents
from sttv.enrichment.localization import enrich_localization


class DatabaseSetTests(BuildFixture):
    def setUp(self):
        super().setUp()
        self.options = read_json(PRODUCT_ROOT / 'config/backend.json')
        self.components = self.game / 'common/component_templates'
        self.buildings = self.game / 'common/buildings'
        self.components.mkdir()
        self.buildings.mkdir()
        self.variables.update(COMPONENTS_DIR='common/component_templates', BUILDINGS_DIR='common/buildings')
        from sttv.common.datasets import REGISTRY
        for kind, spec in REGISTRY['datasets'].items():
            if kind in ('technologies', 'components', 'buildings'):
                continue
            directory = self.game / spec['directory']
            directory.mkdir(parents=True, exist_ok=True)
            self.variables[kind.upper() + '_DIR'] = spec['directory']
            contents = {'events': 'country_event = { id = example.1 title = tech_a desc = tech_a_desc }',
                        'terraform': 'terraform_link = { from = pc_a to = pc_b }',
                        'starbase_levels': 'level_one = { ship_size = small }'}.get(kind, 'example = {}')
            (directory / 'base.txt').write_text(contents, encoding='utf-8')
        (self.inline / 'component.txt').write_text('key = "$ID$" component_set = SHARED prerequisites = { tech_a }', encoding='utf-8')
        (self.components / 'base.txt').write_text('utility_component_template = { inline_script = { script = component ID = SMALL } }', encoding='utf-8')
        (self.buildings / 'base.txt').write_text('building_a = { prerequisites = { tech_a } desc = { trigger = { always = yes } text = special_desc } }', encoding='utf-8')
        for tier in ('RU_LOC_TIER_1', 'RU_LOC_TIER_2', 'RU_LOC_TIER_3', 'EN_LOC_TIER_1'):
            directory = self.root / tier
            directory.mkdir()
            self.variables[tier] = str(directory)
            header = 'l_russian' if tier.startswith('RU') else 'l_english'
            lines = {'tech_a': 'A', 'tech_a_desc': 'Base', 'tech_a_variant': 'Variant', 'tech_b': 'B',
                     'SMALL': 'Small', 'SHARED_DESC': 'Shared', 'building_a': 'Building',
                     'building_a_desc': 'Normal', 'special_desc': 'Conditional'}
            (directory / 'base.yml').write_text(header + ':\n' + '\n'.join(f' {k}:0 "{v}"' for k,v in lines.items()), encoding='utf-8-sig')

    def run_set(self):
        self.variable_file.write_text(json.dumps(self.variables), encoding='utf-8')
        self.config_file.write_text(json.dumps(self.options), encoding='utf-8')
        return build_database_set(self.variable_file, self.config_file, library_mode='rebuild')

    def test_full_set_identity_localization_and_reproducibility(self):
        result = self.run_set()
        self.assertEqual(result['status'], 'success', result['diagnostics'])
        manifest = self.database_path().read_bytes()
        reader = open_set(self.database_path())
        self.assertEqual(reader.manifest['set_id'], result['set_id'])
        self.assertEqual(len(reader.manifest['datasets']), 15)
        for path in reader.paths.values():
            content = path.read_bytes()
            self.assertNotIn(b'\r\n', content)
            self.assertTrue(content.startswith(b'{\n  '))
            self.assertTrue(content.endswith(b'\n'))
        component = documents(self.database_path(), 'components')[0]['items'][0]
        description = component['enrichments']['localization']['ru']['description']
        self.assertEqual(description['key'], 'SHARED_DESC')
        self.assertEqual(description['fallback']['source_ref']['database'], 'components')
        building = documents(self.database_path(), 'buildings')[0]['items'][0]
        self.assertEqual(building['value']['items'][1]['enrichments']['localization']['en']['description']['text'], 'Conditional')
        self.assertEqual(self.run_set()['set_id'], result['set_id'])
        self.assertEqual(self.database_path().read_bytes(), manifest)

    def test_failed_last_member_keeps_entire_snapshot(self):
        self.assertEqual(self.run_set()['status'], 'success')
        before = self.database_path().read_bytes()
        (self.game / 'events/base.txt').write_text('broken = {', encoding='utf-8')
        result = self.run_set()
        self.assertEqual(result['status'], 'failed')
        self.assertFalse(result['published'])
        self.assertEqual(self.database_path().read_bytes(), before)

    def test_localization_addresses_are_document_local(self):
        original = (self.tech / 'base.txt').read_text(encoding='utf-8-sig')
        self.write_script('base.txt', 'tech_b = { area = physics tier = 1 category = { computing } }')
        self.write_script('second.txt', original[:original.index('tech_b =')])
        result = self.run_set()
        self.assertEqual(result['status'], 'success', result['diagnostics'])
        document = next(d for d in documents(self.database_path()) if d['source']['file'].endswith('/second.txt'))
        index, root = next((i,n) for i,n in enumerate(document['items']) if n.get('key',{}).get('text') == 'tech_a')
        variant = next(n for n in root['value']['items'] if n.get('key',{}).get('text') == 'technology_swap')
        ref = variant['enrichments']['localization']['en']['description']['inherited_from']
        self.assertEqual(ref, {'database': 'technologies', 'document_id': document['document_id'], 'pointer': f'/items/{index}'})
        self.assertEqual(result['performance']['validated_documents'],
                         sum(m['build_counts']['parsed_files'] for m in result['datasets'].values()))

    def test_shared_source_change_blocks_publication(self):
        from sttv.database_sets import operation
        prepare = operation.prepare_member
        def changing(kind, *args):
            result = prepare(kind, *args)
            if kind == 'technologies':
                (self.static / 'base.txt').write_text('@external = 3', encoding='utf-8')
            return result
        with patch.object(operation, 'prepare_member', side_effect=changing):
            result = self.run_set()
        self.assertEqual(result['status'], 'failed')
        self.assertFalse(self.database_path().exists())

    def test_manifest_switch_failure_never_publishes_partial_set(self):
        from sttv.storage import publication
        replace = publication.os.replace
        def failing(source, target):
            if Path(target) == self.database_path():
                raise OSError('Injected failure')
            return replace(source, target)
        with patch.object(publication.os, 'replace', side_effect=failing):
            result = self.run_set()
        self.assertEqual(result['status'], 'failed')
        self.assertFalse(result['published'])
        self.assertFalse(any(m['written'] for m in result['datasets'].values()))
        self.assertFalse(self.database_path().exists())

    def test_duplicate_ids_and_colliding_reports_are_errors(self):
        (self.components / 'duplicate.txt').write_text('utility_component_template = { key = SMALL }', encoding='utf-8')
        result = self.run_set()
        self.assertEqual(result['diagnostics'][0]['code'], 'duplicate_object')
        self.options['datasets']['buildings']['outputs']['report'] = self.options['datasets']['components']['outputs']['report']
        self.assertEqual(self.run_set()['diagnostics'][0]['code'], 'output_collision')

    def test_member_change_changes_only_its_source_revision(self):
        first = self.run_set()
        before = open_set(self.database_path()).manifest
        with (self.buildings / 'base.txt').open('a', encoding='utf-8') as handle:
            handle.write('\nbuilding_b = { cost = 1 }')
        second = self.run_set()
        self.assertEqual(second['status'], 'success', second['diagnostics'])
        self.assertNotEqual(first['set_id'], second['set_id'])
        after = open_set(self.database_path()).manifest
        for kind in before['datasets']:
            if kind != 'buildings':
                self.assertEqual(before['datasets'][kind], after['datasets'][kind])
