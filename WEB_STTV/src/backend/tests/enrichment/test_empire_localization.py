"""New catalog text roles and language-specific descriptor fallback."""

from types import SimpleNamespace

from enrichment.support import LocalizationFixture
from support import PRODUCT_ROOT, syntax
from sttv.common.json_io import read_json, json_text
from sttv.common.report import Report
from sttv.common.timing import performance
from sttv.database_sets.descriptors import prepare as link
from sttv.enrichment.localization.report import new_report
from sttv.enrichment.localization.selection import select_targets
from sttv.enrichment.localization.settings import load_settings
from sttv.enrichment.localization.snapshot import Snapshot
from sttv.script.parser import parse_text
from sttv.script.serialization import serialize_document
from sttv.storage.writing import write_document


class EmpireLocalizationTests(LocalizationFixture):
    def test_ascension_tradition_and_category_text_keys(self):
        for kind, suffix in [('ascension_perks', '_desc'), ('traditions', '_delayed'),
                             ('tradition_categories', '_desc')]:
            rules = read_json(PRODUCT_ROOT / f'config/enrichment/targets/{kind}.json')
            settings = SimpleNamespace(options={**rules, 'kind': kind}, selection_directory=f'common/{kind}')
            text = ('base={tradition_swap={name=variant}}' if kind != 'tradition_categories'
                    else 'base={desc=explicit} fallback={} ')
            doc = serialize_document(parse_text(text, syntax(), f'common/{kind}/sample.txt'))
            targets = select_targets({'documents': [doc]}, settings)
            if kind == 'tradition_categories':
                self.assertEqual(targets[0].field_keys['description'], 'explicit')
                self.assertEqual(targets[1].field_keys['description'], 'fallback_desc')
            else:
                self.assertEqual(targets[0].field_keys['description'], 'base' + suffix)
                self.assertEqual(targets[1].field_keys['description'], 'variant' + suffix)

    def test_dlc_fallback_per_language_keeps_metadata_and_missing_text(self):
        self.variables['DLC_METADATA_DIR'] = 'dlc_metadata'
        self.variable_file.write_text(json_text(self.variables), encoding='utf-8')
        self.config_file.write_text(json_text(self.options), encoding='utf-8')
        self.write_localization('EN_LOC_TIER_1', {'TITLE': 'Primary', 'ALT': 'Alternative'})
        self.write_localization('RU_LOC_TIER_1', {'ALT': 'Translation $STATIC$ [Owner.GetName]', 'STATIC': 'Static'})
        report, build = new_report(), Report()
        settings = load_settings(self.variable_file, self.config_file, Snapshot(report), 'dlcs',
                                 'unused.json', 'loc_report.json')
        results = []
        for i, (file, text) in enumerate([
            ('dlc_metadata/dlc_info.txt', 'dlcs={ dlc036={name=BioGenesis localizable_name=TITLE} dlc001={name=Missing localizable_name=ABSENT}}'),
            ('dlc/not_the_name/example.dlc', 'name=BioGenesis localizable_name=ALT steam_id=123')]):
            doc = serialize_document(parse_text(text, syntax(), file))
            results.append({'fragment': write_document(doc, self.work / f'{i}.json', 'dlcs', performance()), 'localization_files': []})
        counts = link('dlcs', results, settings, build, report)
        self.assertEqual(counts['matched_pairs'], 1)
        self.assertEqual(counts['without_descriptor'], 1)
        nodes = read_json(results[0]['fragment']['path'])['items'][0]['value']['items']
        loc = nodes[0]['enrichments']['localization']
        self.assertEqual(loc['en']['name']['key'], 'TITLE')
        self.assertEqual(loc['ru']['name']['requested_key'], 'TITLE')
        self.assertEqual(loc['ru']['name']['key'], 'ALT')
        self.assertEqual(loc['ru']['name']['text'], 'Translation Static [Owner.GetName]')
        self.assertEqual(loc['ru']['name']['fallback']['kind'], 'dlc_descriptor')
        self.assertIsNone(nodes[1]['enrichments']['localization']['en']['name']['text'])
        self.assertNotIn('owned', nodes[0]['enrichments']['dlc'])
        self.assertNotIn('description', loc['en'])

    def test_origin_and_variant_descriptions_are_separate_without_inheritance(self):
        rules = read_json(PRODUCT_ROOT / 'config/enrichment/targets/civics.json')
        settings = SimpleNamespace(options={**rules, 'kind': 'civics'}, selection_directory='common/governments/civics')
        doc = serialize_document(parse_text('origin_a={is_origin=yes description=effect_text '
            'swap_type={name=variant desc=variant_effect} swap_type={description=anonymous_effect}}',
            syntax(), 'common/governments/civics/not_origins.txt'))
        targets = select_targets({'documents': [doc]}, settings)
        self.assertEqual([t.field_keys for t in targets], [
            {'name': 'origin_a', 'description': 'origin_a_desc'}, {'description': 'effect_text'},
            {'name': 'variant', 'description': 'variant_desc'}, {'description': 'variant_effect'},
            {'description': 'anonymous_effect'}])
        self.assertTrue(all(target.parent is None for target in targets))
