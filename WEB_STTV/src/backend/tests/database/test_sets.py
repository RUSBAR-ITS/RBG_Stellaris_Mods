"""Set integrity, localization selection and publication failures."""

import copy
import json
from pathlib import Path
from unittest.mock import patch

from support import BuildFixture, PRODUCT_ROOT
from sttv.common.json_io import read_json
from sttv.database_sets import build_database_set
from sttv.database_sets.staging import canonical_hash
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

    def member(self, kind):
        return Path(self.variables['WORK_DIR']) / self.options['datasets'][kind]['outputs']['database']

    def test_full_set_identity_localization_and_reproducibility(self):
        result = self.run_set()
        self.assertEqual(result['status'], 'success', result['diagnostics'])
        hashes, first = {}, {}
        for kind in self.options['datasets']:
            first[kind] = self.member(kind).read_bytes()
            self.assertNotIn(b'\r\n', first[kind])
            self.assertTrue(first[kind].startswith(b'{\n  "dataset": {\n'))
            self.assertTrue(first[kind].endswith(b'\n'))
            db = read_json(self.member(kind))
            self.assertEqual(db.pop('dataset'), {'kind': kind, 'set_id': result['set_id']})
            hashes[kind] = canonical_hash({'identity_algorithm': 'sttv.document_hashes.v1',
                'format': db['format'], 'format_version': db['format_version'], 'documents': [
                    {'index': index, 'content_hash': canonical_hash(document)}
                    for index, document in enumerate(db['documents'])]})
        self.assertEqual(result['set_id'], canonical_hash(hashes))
        component = read_json(self.member('components'))['documents'][0]['items'][0]
        description = component['enrichments']['localization']['ru']['description']
        self.assertEqual(description['requested_key'], 'SMALL_DESC')
        self.assertEqual(description['key'], 'SHARED_DESC')
        self.assertEqual(description['fallback']['kind'], 'component_set')
        building = read_json(self.member('buildings'))['documents'][0]['items'][0]
        conditional = building['value']['items'][1]['enrichments']['localization']['en']
        self.assertEqual(set(conditional), {'description'})
        self.assertEqual(conditional['description']['text'], 'Conditional')
        self.assertEqual(self.run_set()['set_id'], result['set_id'])
        for kind, content in first.items():
            self.assertEqual(self.member(kind).read_bytes(), content)

    def test_failed_last_member_does_not_replace_any_database(self):
        self.assertEqual(self.run_set()['status'], 'success')
        first = {kind: self.member(kind).read_bytes() for kind in self.options['datasets']}
        (self.game / 'events/base.txt').write_text('broken = {', encoding='utf-8')
        result = self.run_set()
        self.assertEqual(result['status'], 'failed')
        self.assertTrue(all(not member['written'] for member in result['datasets'].values()))
        for kind, content in first.items():
            self.assertEqual(self.member(kind).read_bytes(), content)

    def test_streamed_localization_keeps_nonzero_document_addresses(self):
        original = (self.tech / 'base.txt').read_text(encoding='utf-8-sig')
        self.write_script('base.txt', 'tech_b = { area = physics tier = 1 category = { computing } }')
        self.write_script('second.txt', original[:original.index('tech_b =')])
        result = self.run_set()
        self.assertEqual(result['status'], 'success', result['diagnostics'])
        database = read_json(self.member('technologies'))
        ordinal, document = next((index, item) for index, item in enumerate(database['documents'])
            if item['source']['file'].endswith('/second.txt'))
        self.assertGreater(ordinal, 0)
        root_index, root = next((index, item) for index, item in enumerate(document['items'])
            if item.get('key', {}).get('text') == 'tech_a')
        variant = next(item for item in root['value']['items'] if item.get('key', {}).get('text') == 'technology_swap')
        inherited = variant['enrichments']['localization']['en']['description']['inherited_from']
        self.assertEqual(inherited, f'/documents/{ordinal}/items/{root_index}')
        counts = result['datasets']['technologies']['localization_counts']
        self.assertEqual(counts['technologies'], 2)
        self.assertEqual(counts['variants'], 1)
        self.assertEqual(result['performance']['rule_preparations'], 1 + sum(
            len(member['performance']['parallel']['workers']) for member in result['datasets'].values()))
        self.assertEqual(result['performance']['validated_documents'],
                         sum(member['build_counts']['parsed_files'] for member in result['datasets'].values()))

    def test_shared_source_change_blocks_publication(self):
        from sttv.database_sets import operation
        prepare = operation.prepare_member
        def changing(kind, *args):
            database = prepare(kind, *args)
            if kind == 'technologies':
                (self.static / 'base.txt').write_text('@external = 3', encoding='utf-8')
            return database
        with patch.object(operation, 'prepare_member', side_effect=changing):
            result = self.run_set()
        self.assertEqual(result['status'], 'failed')
        self.assertIn('input_changed', [row['code'] for row in result['diagnostics']])
        self.assertFalse(any(self.member(kind).exists() for kind in self.options['datasets']))

    def test_partial_publication_reports_actual_written_members(self):
        from sttv.database_sets import staging
        replace = staging.os.replace
        def failing(source, destination):
            if Path(destination) == self.member('components'):
                raise OSError('Simulated publication failure')
            return replace(source, destination)
        with patch.object(staging.os, 'replace', side_effect=failing):
            result = self.run_set()
        self.assertEqual(result['status'], 'failed')
        self.assertEqual([k for k,v in result['datasets'].items() if v['written']], ['technologies'])

    def test_duplicate_ids_and_colliding_paths_are_errors(self):
        (self.components / 'duplicate.txt').write_text('utility_component_template = { key = SMALL }', encoding='utf-8')
        result = self.run_set()
        self.assertEqual(result['diagnostics'][0]['code'], 'duplicate_object')
        self.options['datasets']['buildings']['outputs']['database'] = self.options['datasets']['components']['outputs']['database']
        self.assertEqual(self.run_set()['diagnostics'][0]['code'], 'output_collision')

    def test_individual_enrichment_cannot_change_set_member(self):
        self.assertEqual(self.run_set()['status'], 'success')
        config = copy.deepcopy(read_json(PRODUCT_ROOT / 'config/enrichment/localization.json'))
        config['database'] = self.options['datasets']['technologies']['outputs']['database']
        path = self.root / 'localization.json'
        path.write_text(json.dumps(config), encoding='utf-8')
        before = self.member('technologies').read_bytes()
        result = enrich_localization(self.variable_file, path)
        self.assertEqual(result['diagnostics'][0]['code'], 'set_member')
        self.assertEqual(self.member('technologies').read_bytes(), before)

    def test_description_priority_empty_values_and_explicit_building_key(self):
        directory = Path(self.variables['RU_LOC_TIER_1'])
        with (directory / 'base.yml').open('a', encoding='utf-8') as handle:
            handle.write('\n SMALL_DESC:0 ""\n')
        (self.buildings / 'base.txt').write_text('building_a = { desc = special_desc }', encoding='utf-8')
        result = self.run_set()
        self.assertEqual(result['status'], 'success', result['diagnostics'])
        component = read_json(self.member('components'))['documents'][0]['items'][0]['enrichments']['localization']
        self.assertEqual(component['ru']['description']['text'], '')
        self.assertNotIn('fallback', component['ru']['description'])
        self.assertIn('fallback', component['en']['description'])
        building = read_json(self.member('buildings'))['documents'][0]['items'][0]['enrichments']['localization']
        self.assertEqual(building['ru']['description']['requested_key'], 'special_desc')
        self.assertEqual(building['en']['description']['text'], 'Conditional')

    def test_member_change_changes_shared_identity_without_changing_other_content_hashes(self):
        first = self.run_set()
        with (self.buildings / 'base.txt').open('a', encoding='utf-8') as handle:
            handle.write('\nbuilding_b = { cost = 1 }')
        second = self.run_set()
        self.assertEqual(second['status'], 'success', second['diagnostics'])
        self.assertNotEqual(first['set_id'], second['set_id'])
        self.assertEqual(first['datasets']['components']['content_hash'], second['datasets']['components']['content_hash'])
        self.assertTrue(all(read_json(self.member(kind))['dataset']['set_id'] == second['set_id'] for kind in self.options['datasets']))
